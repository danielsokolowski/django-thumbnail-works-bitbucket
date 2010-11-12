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

import os

from django.db.models.fields.files import ImageField, ImageFieldFile

from thumbnail_works.exceptions import ImageSizeError
from thumbnail_works.utils import get_width_height_from_string



class Thumbnail:
    
    def __init__(self, name, size, source):
        self.name = self._get_name(name)
        self.width, self.height = get_width_height_from_string(size)
        self.url = self._get_url(source.url)
    
    def _get_name(self, name):
        return name.replace(' ', '_')
    
    def _get_url(self, source_url):
        """
        source: /media/images/photo.jpg
        thumbnail: /media/images/photo.<thumbname>.jpg
        """
        root_dir = os.path.dirname(source_url)  # /media/images
        filename = os.path.basename(source_url)
        base_filename, ext = os.path.splitext(filename)
        return os.path.join(root_dir, '%s.%s.%s' % (base_filename, self.name, ext))
    
        
        
class EnhancedImageFieldFile(ImageFieldFile):
    
    def __init__(self, *args, **kwargs):
        super(EnhancedImageFieldFile, self).__init__(*args, **kwargs)
        
        # Set thumbnail objects as instance attributes
        if self.field.thumbnails:
            for thumbnail_name, thumbnail_size in self.field.thumbnails.items():
                thumbnail_obj = Thumbnail(thumbnail_name, thumbnail_size, self)
                setattr(self, thumbnail_name, thumbnail_obj)
    
    def save(self, name, content, save=True):
        
        # Before saving, resize the source image if a size has been set
        width, height = get_width_height_from_string(self.field.resize_source)
        
        super(EnhancedImageFieldFile, self).save(name, content, save)
        
        name = self.field.generate_filename(self.instance, name)
        self.name = self.storage.save(name, content)
        setattr(self.instance, self.field.name, self.name)

        # Update the filesize cache
        self._size = len(content)
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()
        


class EnhancedImageField(ImageField):
    attr_class = EnhancedImageFieldFile
    
    def __init__(self, resize_source=None, thumbnails={}, **kwargs):
        """
        resize_source: image size in WIDTHxHEIGHT. If set, the uploaded image
        will be resized to this size.
        
        Thumbnails format:
        
            <thumbnail_name> : <size>
        
        """
        self.resize_source = resize_source
        self.thumbnails = thumbnails
        super(EnhancedImageField, self).__init__(**kwargs)

