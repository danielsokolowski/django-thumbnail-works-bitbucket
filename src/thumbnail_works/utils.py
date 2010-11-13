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

from thumbnail_works.exceptions import ImageSizeError


def get_width_height_from_string(size):
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

