
=====
Usage
=====

This section contains information, including examples, about how to use
*django-thumbnail-works* in your existing Django projects or applications.


The EnhancedImageField
======================
*django-thumbnail-works* provides an enhanced version of the default Django's
``ImageField``, which can generate thumbnails of the original image and also
process the original image before it is saved on the remote server.


EnhancedImageField attributes and methods
-----------------------------------------

The ``EnhancedImageField`` derives from the default ``ImageField`` and thus
all attributes and methods of the default ``ImageField`` are inherited.

In addittion to the default attributes, the ``EnhancedImageField`` also
supports the following:

- ``process_source``: A dictionary of thumbnail options as described in the
  following section. If this is set, the original image will be processed
  using the provided options before it is saved on the remote server.
  Contrariwise, if this attribute is not set, the uploaded image is saved in
  its original form, without any further processing.
- ``thumbnails``: A dictionary of thumbnail definitions. The format of each
  thumbnail definition is::

    <thumbnail_name> : <thumbnail_options>


Thumbnail options
-----------------

Thumbnail options is a dict of options that will be used during the thumbnail
generation. Supported options are:

``size``
    A string of the WIDTHxHEIGHT which represents the size of
    the thumbnail.
``sharpen``
    Boolean option. If set, the ``ImageFilter.SHARPEN`` filter will
    be applied to the thumbnail.
``detail``
    Boolean option. If set, the ``ImageFilter.DETAIL`` filter will
    be applied to the thumbnail.
``upscale``
    Boolean option. By default, image resizing occurs only if
    any of the image dimensions is longer than the dimension
    indicated by the ``size`` option. If this is enabled, the
    resizing occurs even if the former condition is not met.
``format``
    This is the format in which the thumbnail should be saved.
    Valid values are those supported by PIL.


Example
-------

The following code snippet illustrates how to use the ``EnhancedImageField``::

    from thumbnail_works.fields import EnhancedImageField
    
    class MyModel(models.Model):
        photo = EnhancedImageField(
            process_source = dict(
                size='512x384', sharpen=True, upscale=True, format='JPEG'),
            thumbnails = {
                'small': dict(size='80x60'),
                'medium': dict(size='256x192', detail=True),
            }
        )


Accessing the thumbnails
------------------------
Thumbnails can be accessed as attributes of the ``EnhancedImageField`` instance.
For example::

    photo = EnhancedImageField(
        thumbnails = {
            'small': dict(size='80x60'),
            'medium': dict(size='256x192'),
        }
    )

The thumbnail objects can be accessed 