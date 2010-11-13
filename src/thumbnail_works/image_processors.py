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

from PIL import Image, ImageFilter


def resize(im, size):
    """
    The resize happens only if any of the following conditions is met:
    
        - the original width is greater than the requested width
        - the original height is greater than the requested height
    
    """
    
    # Requested dimensions
    width_req, height_req = size
    # Source image dimensions
    width_source, height_source = im.size
    
    # Determine orientation
    landscape_orientation = True
    if width_source < height_source:
        landscape_orientation = False
    
    # Determine if resize is needed. (Also creates the temporary resized file)
    if width_source > width_req or height_source > height_req:
        # Do resize
        # the thumbnail() method is used for resizing as it maintains the original
        # image's aspect ratio (resize() does not).
        im.thumbnail((width_req, height_req), Image.ANTIALIAS)
        
    return im
  

def sharpen(im):
    im = im.filter(ImageFilter.SHARPEN)
    return im
