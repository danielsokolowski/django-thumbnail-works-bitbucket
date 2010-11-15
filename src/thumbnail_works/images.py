
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    from PIL import Image, ImageFilter
except ImportError:
    import Image
    import ImageFilter

from cropresize import crop_resize

from django.core.files.base import ContentFile

from thumbnail_works import settings

from thumbnail_works.exceptions import ThumbnailOptionError
from thumbnail_works.utils import get_width_height_from_string


class ImageProcessor:
    """Adds image processing support to ImageFieldFile or derived classes
    
    expects:
    
    self.identifier
    self.proc_opts
    
    self.instance
    
    self.field
    self.name
    
    generate_image_name()
    
    """
    
    DEFAULT_OPTIONS = {
        'size': None,
        'sharpen': False,
        'detail': False,
        'upscale': False,
        'format': settings.THUMBNAILS_FORMAT,
        }
    
    def setup_image_processing_options(self, proc_opts):
        """Sets the image processing options for the image object.
        
        If ``proc_opts`` is None, then ``self.proc_opts`` is set to None,
        which means that no processing should be performed on this image.
        
        This method checks the provided options and also ensures that the
        final dictionary contains all the supported options.
        
        """
        if proc_opts is None:
            self.proc_opts = None
        elif not isinstance(proc_opts, dict):
            raise ThumbnailOptionError('A dictionary object is required')
        else:
            for option in proc_opts.keys():
                if option not in self.DEFAULT_OPTIONS.keys():
                    raise ThumbnailOptionError('Invalid thumbnail option `%s`' % option)
            self.proc_opts = self.DEFAULT_OPTIONS.copy()
            self.proc_opts.update(proc_opts)
    
    def get_image_extension(self):
        """Returns the extension in accordance to the image format."""
        if not isinstance(self.proc_opts, dict):
            return
        ext = self.proc_opts['format'].lower()
        if ext == 'jpeg':
            return '.jpg'
        return '.%s' % ext
    
    def generate_image_name(self, name=None, force_ext=None):
        """
        THUMBNAILS_DIRNAME
        For urls and filesystem paths
        
        self.name: images/photo.jpg
        thumbnail: images/<THUMBNAILS_DIRNAME>/photo.<identifier>.<extension>
        """
        if name is None:
            if self.name is None:
                raise Exception('We need a name')
            name = self.name
        root_dir = os.path.dirname(name)  # images
        filename = os.path.basename(name)    # photo.jpg
        base_filename, default_ext = os.path.splitext(filename)
        if force_ext is not None:
            ext = force_ext
        else:
            ext = self.get_image_extension()
            if ext is None:
                ext = default_ext
        if self.identifier is None:
            image_filename = '%s%s' % (base_filename, ext)
            return os.path.join(root_dir, image_filename)
        else:
            image_filename = '%s.%s%s' % (base_filename, self.identifier, ext)
            if settings.THUMBNAILS_DIRNAME:
                return os.path.join(root_dir, settings.THUMBNAILS_DIRNAME, image_filename)
            return os.path.join(root_dir, image_filename)
    
    def process_image(self, content):
    
        # Image.open() accepts a file-like object, but it is needed
        # to rewind it back to be able to get the data,
        content.seek(0)
        im = Image.open(content)
        
        # Convert to RGB if necessary
        if im.mode not in ('L', 'RGB', 'RGBA'):
            im = im.convert('RGB')
        
        # Process
        size = self.proc_opts['size']
        upscale = self.proc_opts['upscale']
        if size is not None:
            new_size = get_width_height_from_string(size)
            im = self._resize(im, new_size, upscale)
        
        sharpen = self.proc_opts['sharpen']
        if sharpen:
            im = self._sharpen(im)
        
        detail = self.proc_opts['detail']
        if detail:
            im = self._detail(im)
        
        # Save image data
        format = self.proc_opts['format']
        buffer = StringIO()
    
        if format == 'JPEG':
            im.save(buffer, format, quality=settings.THUMBNAILS_QUALITY)
        else:
            im.save(buffer, format)
        
        data = buffer.getvalue()
        
        return ContentFile(data)


    def _resize(self, im, size, upscale):
        return crop_resize(im, size, exact_size=upscale)
    
    def _sharpen(self, im):
        return im.filter(ImageFilter.SHARPEN)
    
    def _detail(self, im):
        return im.filter(ImageFilter.DETAIL)

