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


from thumbnail_works.core import ImageObject, Thumbnail
from thumbnail_works.exceptions import ImageSizeError
from thumbnail_works.utils import get_width_height_from_string, get_thumbnail_path
from thumbnail_works import settings
from thumbnail_works import image_processors





        
class EnhancedImageFieldFile(ImageFieldFile):
    
    def __init__(self, *args, **kwargs):
        super(EnhancedImageFieldFile, self).__init__(*args, **kwargs)
        
        # Set thumbnail objects as instance attributes
        if self.field.thumbnails:
            for thumbnail_name, thumbnail_size in self.field.thumbnails.items():
                thumbnail_obj = Thumbnail(thumbnail_name, thumbnail_size, self)
                setattr(self, thumbnail_name, thumbnail_obj)
    
    def save(self, name, content, save=True):
        """
        name: is the path on the filesystem of the original image
        """
        
        
        # Before saving, resize the source image if a size has been set
        #content = copy.copy(content)
        img_obj = ImageObject()
        im = img_obj.get_img_data_from_file(content)
        im = image_processors.resize(im, self.field.resize_source)
        im = image_processors.sharpen(im)
        resized_content = img_obj.get_file_for_img_data(im)
        
        super(EnhancedImageFieldFile, self).save(name, resized_content, save)
        
        # self.name has been re-set in the save() above
        # use self.name to generate the thumbnail filename
        
        # Generate thumbnails
        if self.field.thumbnails:
            for thumbnail_name, thumbnail_size in self.field.thumbnails.items():
                #new_content = copy.deepcopy(content)
                print "Doing: ", thumbnail_name, thumbnail_size
                img_obj = ImageObject()
                im = img_obj.get_img_data_from_file(content)
                image_processors.resize(im, thumbnail_size)
                thumbnail_content = img_obj.get_file_for_img_data(im)
                path = get_thumbnail_path(name, thumbnail_name)
                print path
                path_saved = self.storage.save(path, thumbnail_content)
                
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

