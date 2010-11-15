
=====
Usage
=====

This section contains information, including examples, about how to use
*django-thumbnail-works* in your existing Django projects or applications.


The EnhancedImageField
======================

.. autoclass:: thumbnail_works.fields.EnhancedImageField



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