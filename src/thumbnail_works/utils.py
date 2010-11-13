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
import StringIO
from PIL import Image

from django.core.files.base import ContentFile
from django.core.files import File

from thumbnail_works.exceptions import ImageSizeError
from thumbnail_works import image_processors
from thumbnail_works import settings


def get_width_height_from_string(size):
    """Returns a (WIDTH, HEIGHT) tuple.
    
    Accepts a string in the form WIDTHxHEIGHT
    
    Raises ImageSizeError when on invalid image size.  
    
    """
    try:
        bits = size.split('x', 1)
    except AttributeError:
        raise ImageSizeError('size must be a string of the form WIDTHxHEIGHT')
    if len(bits) != 2:
        raise ImageSizeError('size must be a string of the form WIDTHxHEIGHT')
    try:
        size_x = int(bits[0])
        size_y = int(bits[1])
    except ValueError:
        raise ImageSizeError('size\'s WIDTH and HEIGHT must be integers')
    return size_x, size_y


def get_thumbnail_path(source_path, thumbnail_name):
    """
    For urls and filesystem paths
    
    source: /media/images/photo.jpg
    thumbnail: /media/images/photo.<thumbname>.jpg
    """
    root_dir = os.path.dirname(source_path)  # /media/images
    filename = os.path.basename(source_path)
    base_filename, ext = os.path.splitext(filename)
    return os.path.join(root_dir, '%s.%s.%s' % (base_filename, thumbnail_name, ext))


def process_content_as_image(content, resize_to=None, sharpen=False):
    
    # Image.open() accepts a file-like object, but it is needed
    # to rewind it back to be able to get the data,
    content.seek(0)
    im = Image.open(content)
    
    # Convert to RGB if necessary
    if im.mode not in ('L', 'RGB', 'RGBA'):
        im = im.convert('RGB')
    
    # Process
    if resize_to is not None:
        im = image_processors.resize(im, get_width_height_from_string(resize_to))
    if sharpen:
        im = image_processors.sharpen(im)
    
    io = StringIO.StringIO()
    
    if settings.THUMBNAILS_FORMAT == 'JPEG':
        im.save(io, 'JPEG', quality=settings.THUMBNAILS_QUALITY)
    elif settings.THUMBNAILS_FORMAT == 'PNG':
        im.save(io, 'PNG')
    
    return ContentFile(io.getvalue())

