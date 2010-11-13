# -*- coding: utf-8 -*-
#
#  This file is part of django-thumbnail-works.
#
#  django-thumbnail-works provides an enhanced ImageField that generates and
#  manages thumbnails of the uploaded image.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-thumbnail-works
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-thumbnail-works
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import copy


from django.db.models.fields.files import ImageField, ImageFieldFile


from thumbnail_works.exceptions import ImageSizeError
from thumbnail_works.utils import get_width_height_from_string, \
    get_thumbnail_path, process_content_as_image
from thumbnail_works import settings
from thumbnail_works import image_processors




class Thumbnail:
    
    def __init__(self, name, size, source):
        self.name = self._get_name(name)    # the thumbnail name as set in the dictionary
        self.width, self.height = get_width_height_from_string(size)
        self.url = get_thumbnail_path(source.url, self.name)
    
    def _get_name(self, name):
        return name.replace(' ', '_')


        
class EnhancedImageFieldFile(ImageFieldFile):
    """Enhanced version of the default ImageFieldFile.
    
    The EnhancedImageFieldFile supports:
    
    - resizing the original image before saving it to the specified storage.
    - generating thumbnails of the original image on the same storage.
    - deleting the previously generated thumbnails from the specified storage.
    - a mechanism of accessing the thumbnails as attributes of the model's
      EnhancedImageField.
      
    For instance, we have the following model definition::
      
        from thumbnail_works.fields import EnhancedImageField
          
        class MyModel(models.Model):
            photo = EnhancedImageField(
                resize_source = '512x384',
                thumbnails = {'avatar': '80x60', 'large': '200x150',}
            )
    
    Thumbnail attributes can be accessed as follows::
    
        photo.avatar.url
    
    For information about the attributes of each thimbnail object, read the
    ``Thumbnail`` docstring.
    
    """
    
    def __init__(self, *args, **kwargs):
        """Constructor.
        
        Notes for development:
        
        Throughout this class the following attributes that are inherited
        from ``ImageFieldFile`` are used:
        
        - instance: The instance of the model that contains the
          EnhancedImageField.
        - field: The instance of the EnhancedImageField.
        - storage: The ``storage`` attribute of the EnhancedImageField instance.
        - _committed: boolean attribute that indicates whether the file object
          has been committed to the database and therefore saved to the
          storage or the file has been deleted from the database and therefore
          deleted from the filesystem.
        
        If the sourc eimage has been saved and thumbnails have been specified,
        instanciate the latter using the ``Thumbnail`` class and add them as
        attributes to the ``EnhancedImageFieldFile`` object.
        
        """
        super(EnhancedImageFieldFile, self).__init__(*args, **kwargs)
        
        # Set thumbnail objects as attributes only if thumbnail definitions
        # exist and the source image has been saved.
        if self._committed and self.field.thumbnails:
            for thumb_name, thumb_size in self.field.thumbnails.items():
                thumb_obj = Thumbnail(thumb_name, thumb_size, self)
                setattr(self, thumb_name, thumb_obj)
    
    def save(self, name, content, save=True):
        """
        name: is the path on the filesystem of the original image
        """
        print name
        print dir(content)
        
        # Before saving, resize the source image if a size has been set
        #content = copy.copy(content)
        processed_content = process_content_as_image(
            content, resize_to=self.field.resize_source, sharpen=True)
        
        super(EnhancedImageFieldFile, self).save(name, processed_content, save)
        
        # self.name has been re-set in the save() above
        # use self.name to generate the thumbnail filename
        print 'self.name:', self.name
        
        # Generate thumbnails
        if self.field.thumbnails:
            for thumb_name, thumb_size in self.field.thumbnails.items():
                #new_content = copy.deepcopy(content)
                print "Doing: ", thumb_name, thumb_size
                """
                img_obj = ImageObject()
                im = img_obj.get_img_data_from_file(content)
                image_processors.resize(im, thumbnail_size)
                thumbnail_content = img_obj.get_file_for_img_data(im)
                """
                processed_content = process_content_as_image(
                    content, resize_to=thumb_size, sharpen=True)
                path = get_thumbnail_path(name, thumb_name)
                print path
                path_saved = self.storage.save(path, processed_content)
                
                # check if path == path_saved
    
                
    def delete(self, save=True):
        source_path = copy.copy(self.name)
        super(EnhancedImageFieldFile, self).delete(save)
        
        """
        # Delete thumbnails
        if self.field.thumbnails:
            for thumbnail_name, thumbnail_size in self.field.thumbnails.items():
                path = get_thumbnail_path(source_path, thumbnail_name)
                self.storage.delete(path)
                
      """


class EnhancedImageField(ImageField):
    """An enhanced version of the Django ImageField that supports thumbnails.
    
    """
    attr_class = EnhancedImageFieldFile
    
    def __init__(self, resize_source=None, thumbnails={}, **kwargs):
        """Constructor
        
        Accepts regular ImageField keyword arguments and also:
        
        ``resize_source``
            A string of the WIDTHxHEIGHT which represents the size to which
            the uploaded image will be resized before saved to the storage.
            If not set, the uploaded image is not resized.
        ``thumbnails``
            A dictionary of thumbnail definitions. The format of each
            thumbnail definition is::

                <thumbnail_name> : <size>
        
        """
        self.resize_source = resize_source
        self.thumbnails = thumbnails
        super(EnhancedImageField, self).__init__(**kwargs)

