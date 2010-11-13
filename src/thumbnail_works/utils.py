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


def make_thumbnail_path(source_path, thumbnail_name, force_ext=None):
    """
    THUMBNAILS_DIRNAME
    For urls and filesystem paths
    
    source_path: /media/images/photo.jpg
    thumbnail: /media/images/photo.<thumbname>.jpg
    """
    root_dir = os.path.dirname(source_path)  # /media/images
    filename = os.path.basename(source_path)
    base_filename, ext = os.path.splitext(filename)
    if force_ext:
        ext = force_ext
    thumb_filename = '%s.%s%s' % (base_filename, thumbnail_name, ext)
    if settings.THUMBNAILS_DIRNAME:
        return os.path.join(root_dir, settings.THUMBNAILS_DIRNAME, thumb_filename)
    return os.path.join(root_dir, '%s.%s%s' % (base_filename, thumbnail_name, ext))


def process_content_as_image(content, options):
    
    # Image.open() accepts a file-like object, but it is needed
    # to rewind it back to be able to get the data,
    content.seek(0)
    im = Image.open(content)
    
    # Convert to RGB if necessary
    if im.mode not in ('L', 'RGB', 'RGBA'):
        im = im.convert('RGB')
    
    # Process
    size = options['size']
    upscale = options['upscale']
    if size is not None:
        new_size = get_width_height_from_string(size)
        im = image_processors.resize(im, new_size, upscale)
    
    sharpen = options['sharpen']
    if sharpen:
        im = image_processors.sharpen(im)
    
    detail = options['detail']
    if detail:
        im = image_processors.detail(im)
    
    # Save image data
    format = options['format']
    buffer = StringIO.StringIO()

    if format == 'JPEG':
        im.save(buffer, format, quality=settings.THUMBNAILS_QUALITY)
    else:
        im.save(buffer, format)
    
    data = buffer.getvalue()
    
    return ContentFile(data)

