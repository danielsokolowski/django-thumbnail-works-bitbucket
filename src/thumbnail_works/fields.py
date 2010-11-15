# -*- coding: utf-8 -*-
#
#  This file is part of django-thumbnail-works.
#
#  django-thumbnail-works adds thumbnail support to the default ImageField.
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

from django.db.models.fields.files import ImageField, ImageFieldFile
from django.core.files.base import ContentFile

from thumbnail_works.exceptions import ThumbnailOptionError
from thumbnail_works.utils import get_width_height_from_string, \
    make_thumbnail_path, process_content_as_image
from thumbnail_works import settings




class ThumbnailSpec:
    """Thumbnail specification.
    
    The thumbnail specification is not a file-like object.
    
    The following attributes are available.
    
    ``ident``
        The thumbnail identifier as set in the ``thumbnails`` dictionary.
    ``ext``
        The thumbnail extension, which determined by the image format.
    ``width``
        The thumbnail width.
    ``height``
        The thumbnail height.
    ``url``
        The absolute thumbnail's URL.
    ``path``
        The absolute path of the thumbnail on the filesystem. Note that
        this is only set for thumbnails that are stored locally. For
        other storages a value of None is set.
    ``name``
        The path to the thumbnail relative to ``MEDIA_ROOT``.
    ``options``
        The thumbnail options as specified in ``EnhancedImageField.thumbnails``
        and after filling any missing options with the defaults.
        
    """
    
    DEFAULT_OPTIONS = {
        'size': None,
        'sharpen': False,
        'detail': False,
        'upscale': False,
        'format': settings.THUMBNAILS_FORMAT,
        }
    
    def __init__(self, ident, options, source):
        """Constructor
        
        ``ident``
            The thumbnail identifier as set in the ``thumbnails`` dictionary.
        ``options``
            The thumbnail options as set in the ``thumbnails`` dictionary.
        ``source``
            An instance of the ``EnhancedImageFieldFile``.
        
        
        
        """
        if self._options_are_valid(options):
            self.options = self._get_options(options)
        self.ident = self._get_ident(ident)
        self.ext = self._get_filename_extension_from_format()
        self.width, self.height = get_width_height_from_string(options['size'])
        self.url = make_thumbnail_path(source.url, self.ident)
        self.path = make_thumbnail_path(source.path, self.ident)
        self.name = make_thumbnail_path(source.name, self.ident)
    
    # Private API
    
    def _get_ident(self, ident):
        return ident.replace(' ', '_')
    
    def _get_filename_extension_from_format(self):
        """Returns an extension according to the format.
        
        """
        ext = self.options['format'].lower()
        if ext == 'jpeg':
            return '.jpg'
        return '.%s' % ext
    
    def _get_options(self, options):
        """This method ensures that all the available options have a value.
        
        """
        proc_opts = self.DEFAULT_OPTIONS.copy()
        proc_opts.update(options)
        return proc_opts
    
    def _options_are_valid(self, options):
        for option in options.keys():
            if option not in self.DEFAULT_OPTIONS.keys():
                raise ThumbnailOptionError('Invalid thumbnail option `%s`' % option)
        return True



class EnhancedImageFieldFile(ImageFieldFile):
    """Enhanced version of the default ImageFieldFile.
    
    The EnhancedImageFieldFile supports:
    
    - resizing the original image before saving it to the specified storage.
    - generating thumbnails of the original image on the same storage:
        - immediately after the original image is uploaded.
        - delayed generation when each thumbnail is accessed for the first time.
    - deleting the previously generated thumbnails from the specified storage.
    - a mechanism of accessing the thumbnails as attributes of the model's
      EnhancedImageField.
    
    Notes for development

    Throughout this object the following attributes that are inherited
    from ``ImageFieldFile`` are used:
    
    - instance: The instance of the model that contains the
      EnhancedImageField.
    - field: The instance of the EnhancedImageField.
    - storage: The ``storage`` attribute of the EnhancedImageField instance.
    - _committed: boolean attribute that indicates whether the file object
      has been committed to the database and therefore saved to the
      storage or the file has been deleted from the database and therefore
      deleted from the filesystem.
    
    Also the ``name`` attribute is set once the ``save()`` method has been
    called. ``name`` is the name of the file including the relative path
    from MEDIA_ROOT.
    
    """
    
    def __init__(self, *args, **kwargs):
        """Thumbnails are set as attributes of the ``EnhancedImageFieldFile``
        object.
        
        Each of the thumbnails that have been specified in the ``thumbnails``
        dictionary are eventually set as attributes of the
        ``EnhancedImageFieldFile`` object. Each thumbnail's identifier is
        used as the attribute's name.
        
        For example, the *avatar* thumbnail of a *photo* field, would be
        accessed as::
        
            photo.avatar
        
        At this point, it should be noted that ``photo.avatar`` in the
        above example is not a file object. It is an instance of the
        ``ThumbnailSpec`` class, which represents the thumbnail specification.
        So, whenever you read ``thumbnail``, this actually refers to a
        **thumbnail specification object**.
        
        If the ``THUMBNAILS_DELAYED_GENERATION`` setting has been enabled, then
        each thumbnail is set as an attribute of the ``EnhancedImageFieldFile``
        object only if the thumbnail file exists on the storage. This check
        is performed by the ``storage.exists()`` method, so if the thumbnail
        files are stored remotely, this can be slow.
        
        In the case that ``storage.exists()`` indicates that the file does
        not exist on the storage, the attribute of the ``EnhancedImageFieldFile``
        object that represents the thumbnail is set to None.
        
        If the ``THUMBNAILS_DELAYED_GENERATION`` is not enabled, then
        all thumbnails are set as attributes of the ``EnhancedImageFieldFile``
        object without performing any checks whether the file exists on the
        storage or not.
        
        If a thumbnail does not exist on the storage, it will be generated
        and set as an attribute of the ``EnhancedImageFieldFile`` object as
        soon as it is accessed for the first time.
        
        """
        super(EnhancedImageFieldFile, self).__init__(*args, **kwargs)
        
        # Set ThumbnailSpec objects as attributes only if thumbnail
        # definitions exist and the source image has been saved.
        if self._committed and self.field.thumbnails:
            for thumb_ident, proc_opts in self.field.thumbnails.items():
                thumb_spec = ThumbnailSpec(thumb_ident, proc_opts, self)
                if self.storage.exists(thumb_spec.name):
                    setattr(self, thumb_ident, thumb_spec)
                    # TODO: if delayed is disabled, do not run storage.exists() 
                    # TODO: always set the attribute , but be None if file does not exist on the storage
    
    def generate_thumbnail(self, thumb_ident, proc_opts, content=None):
        """Generates a thumbnail and returns the thumbnail specification.
        
        ``thumb_ident``
            The name of the thumbnail as defined in ``self.field.thumbnails``.
        ``proc_opts``
            The thumbnail options as defined in ``self.field.thumbnails``.
        ``content``: Image data.
        
        If the ``content`` argument is None, then the image data is read
        from the storage. If IOError occurs while trying to read the
        image data, returns None.
        
        """
        if content is None:
            try:
                content = ContentFile(self.storage.open(self.name).read())
            except IOError:
                return None
            
        thumb_spec = ThumbnailSpec(thumb_ident, proc_opts, self)
        processed_content = process_content_as_image(content, thumb_spec.options)
        path = make_thumbnail_path(self.name, thumb_ident, force_ext=thumb_spec.ext)
        path_saved = self.storage.save(path, processed_content)
        
        assert path == path_saved, 'The calculated \
        thumbnail path `%s` and the actual path where the thumbnail \
        was saved `%s` differ.'
        
        return thumb_spec
    
    def __getattr__(self, attribute):
        """Retrieves any ``EnhancedImageFieldFile`` instance attribute.
        
        If a thumbnail attribute is requested, but it has not been set as
        an ``EnhancedImageFieldFile`` instance attribute, then:
        
        1. Generate the thumbnail
        2. Set it as an ``EnhancedImageFieldFile`` instance attribute
        
        Developer Notes
        ---------------
        Here we use the ``EnhancedImageFieldFile`` instance's __dict__ in
        order to check or set the instance's attributes so as to avoid
        triggering a recursive call to this function.
        
        A good write-up on this exists at:  http://bit.ly/c2JL8H
        
        """
        if not self.__dict__.has_key(attribute):
            # Proceed to thumbnail generation only if a thumbnail attribute
            # is requested
            if self.field.thumbnails.has_key(attribute):
                # Generate thumbnail and set the thumbnail specification as
                # an attribute to the ``EnhancedImageFieldFile``.
                proc_opts = self.field.thumbnails[attribute]
                thumb_spec = self.generate_thumbnail(attribute, proc_opts)
                self.__dict__[attribute] = thumb_spec
        return self.__dict__[attribute]
    
    def save(self, name, content, save=True):
        """Saves the source image and generates thumbnails.
        
        ``name``
            The name of the file including the relative path from MEDIA_ROOT.
        ``content``
            The file data.
        
        If the ``process_source`` dictionary has been set on the
        ``EnhancedImageField`` field, then the source image is also
        processed before it is finally saved to the storage.
        
        After the source file is saved, if the THUMBNAILS_DELAYED_GENERATION
        setting has been enabled, no thumbnails are generated. The thumbnails
        will be generated the first time they are accessed.
        If THUMBNAILS_DELAYED_GENERATION is set to False, then all thumbnails
        are generated as soon as the source image is saved.
        
        """
        
        # Resize the source image if the process_source has been set.
        if self.field.process_source is not None:
            source_img_opts = self.field.process_source
            thumb_spec = ThumbnailSpec('dummy', source_img_opts, self)
            processed_content = process_content_as_image(content, thumb_spec.options)
            # The following sets the correct filename extension according
            # to the image format. 
            name = '%s%s' % (name.rsplit('.', 1)[0], thumb_spec.ext)
        else:
            processed_content = content
        
        super(EnhancedImageFieldFile, self).save(name, processed_content, save)
        
        if settings.THUMBNAILS_DELAYED_GENERATION:
            # Thumbnails will be generated on first access
            return
        
        # Generate all thumbnails
        if self._committed and self.field.thumbnails:
            for thumb_ident, proc_opts in self.field.thumbnails.items():
                thumb_spec = self.generate_thumbnail(thumb_ident, proc_opts, content=content)
    
    def delete(self, save=True):
        """Deletes the thumbnails and the source image.
        
        If the files are missing from the storage, no errors are raised.
        
        """
        # First try to delete the thumbnails
        if self._committed and self.field.thumbnails:
            for thumb_ident, proc_opts in self.field.thumbnails.items():
                path = make_thumbnail_path(self.name, thumb_ident)
                self.storage.delete(path)
        
        # Delete the source file
        super(EnhancedImageFieldFile, self).delete(save)



class EnhancedImageField(ImageField):
    """An enhanced version of Django's ``ImageField`` that supports thumbnails.
    
    *django-thumbnail-works* provides an enhanced version of the default Django's
    ``ImageField``, which can generate thumbnails of the original image and also
    process the original image before it is saved on the remote server.
    
    The ``EnhancedImageField`` derives from the default ``ImageField`` and thus
    all attributes and methods of the default ``ImageField`` are inherited.
    
    In addition to the default arguments, the ``EnhancedImageField`` also
    supports the following:
    
    ``process_source``
        A dictionary of *image processing options*. The same options that can
        be used for the thumbnail generation can also be set in this attribute.
        If this is set, the original image will be processed using the provided
        options before it is saved on the remote server. Contrariwise, if this
        attribute is not set, the uploaded image is saved in its original form,
        without any further processing.
    ``thumbnails``
        A dictionary of *thumbnail definitions*. The format of each thumbnail
        definition is::
    
            <thumbnail_identifier> : <image_processing_options>
        
        Where:
        
        **thumbnail_identifier**
            Is a string that uniquely identifies the thumbnail. Note that this
            identifier is used to access each thumbnail and is also used in the
            generated filename of the thumbnail image file. See the example
            at ghe end of this section for a more clear explanation.
        **image_processing_options**
            This is a dictionary of options that will be used during the thumbnail
            generation. Supported options are:
            
            ``size``
                A string of the format ``WIDTHxHEIGHT`` which represents the
                size of the thumbnail.
            ``sharpen``
                Boolean option. If set, the ``ImageFilter.SHARPEN`` filter will
                be applied to the thumbnail.
            ``detail``
                Boolean option. If set, the ``ImageFilter.DETAIL`` filter will
                be applied to the thumbnail.
            ``upscale``
                Boolean option. By default, image resizing occurs only if
                any of the source image dimensions is bigger than the dimension
                indicated by the ``size`` option. If the ``upscale`` option is
                set to True, resizing occurs even if the generated thumbnail
                is bigger than the source image.
            ``format``
                This is the format in which the thumbnail should be saved.
                Valid values are those supported by PIL.
    
    The following code snippet illustrates how to use the ``EnhancedImageField``::

        from django.db import models
        from thumbnail_works.fields import EnhancedImageField
        
        class MyModel(models.Model):
            photo = EnhancedImageField(
                process_source = dict(
                    size='512x384', sharpen=True, upscale=True, format='JPEG'),
                thumbnails = {
                    'avatar': dict(size='80x60'),
                    'medium': dict(size='256x192', detail=True),
                }
            )
    
    """
    attr_class = EnhancedImageFieldFile
    
    def __init__(self, process_source=None, thumbnails={}, **kwargs):
        self.process_source = process_source
        self.thumbnails = thumbnails
        super(EnhancedImageField, self).__init__(**kwargs)

