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

VERSION = (0, 1, 1, 'final', 0)

def get_version():
    version = '%d.%d.%d' % (VERSION[0], VERSION[1], VERSION[2])
    return version


long_description = """
django-thumbnail-works provides an enhanced ImageField that generates and
manages thumbnails of the uploaded image.

Warning: This software is not production-ready!

Features
--------
- Provides the ``EnhancedImageField`` model field which is based on the
  default Django ``ImageField``.
- Supports named thumbnails which can be accessed as attributes of the
  ``EnhancedImageField`` instance.
- Uses the Django storages API to manage thumbnails.
- Allows processing the original image before saving in the same manner that
  thumbnails are processed.
- Individual processing options for each thumbnail.
- Supports automatic image resizing and cropping, sharpen and detail filters
  and specifying the output format of each image.
- Supports thumbnail generation on first access.

More information
----------------
More information about the installation, configuration and usage of this app
can be found in the *HELP* file inside the distribution package or in the
project's
`wiki <http://www.codetrax.org/projects/django-thumbnail-works/wiki>`_.

Bugs and new features
---------------------
In case you run into any problems while using this application it is highly
recommended you file a bug report at the project's
`issue tracker <http://www.codetrax.org/projects/django-thumbnail-works/issues>`_.

"""
