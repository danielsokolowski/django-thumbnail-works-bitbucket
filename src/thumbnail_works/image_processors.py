
import StringIO
from PIL import Image

from django.core.files.base import ContentFile
from django.core.files import File

from thumbnail_works.utils import get_width_height_from_string
from thumbnail_works import settings


def resize(imagefile, size):
    
    # PIL_Image.open() accepts a file-like object, but it is needed
    # to rewind it back to be able to get the data
    imagefile.seek(0)
    im = PIL_Image.open(imagefile)
    
    # Requested dimensions
    width_req, height_req = get_width_height_from_string(size)
    # Source image dimensions
    width_source, height_source = im.size
    
    # Determine orientation
    landscape_orientation = True
    if width_source < height_source:
        landscape_orientation = False
    
    # Convert to RGB if necessary
    if im.mode not in ('L', 'RGB', 'RGBA'):
        im = im.convert('RGB')
    
    """
    The resize happens only if any of the following conditions is met:
    
        - the original width is greater than the requested width
        - the original height is greater than the requested height
    
    """
    
    # Determine if resize is needed. (Also creates the temporary resized file)
    if width_source > width_req or height_source > height_req:
        # Do resize
        # the thumbnail() method is used for resizing as it maintains the original
        # image's aspect ratio (resize() does not).
        im.thumbnail((width_req, height_req), Image.ANTIALIAS)
        
    
    io = StringIO.StringIO()
    
    if settings.THUMBNAILS_FORMAT == 'JPEG':
        im.save(io, 'JPEG', quality=settings.THUMBNAILS_QUALITY)
    elif settings.THUMBNAILS_FORMAT == 'PNG':
        im.save(io, 'PNG')
    
    #return ContentFile(io.getvalue())
    return File(io)
  
