"""
Middleware to serve media files in production
Since WhiteNoise only handles static files, we need custom middleware for media files
"""
from django.conf import settings
from django.http import FileResponse, Http404
from django.utils._os import safe_join
import os


class MediaFileMiddleware:
    """
    Serve media files in production when DEBUG=False
    This is necessary because Django doesn't serve media files in production by default
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.media_url = settings.MEDIA_URL
        self.media_root = str(settings.MEDIA_ROOT)
    
    def __call__(self, request):
        # Only handle media file requests
        if request.path.startswith(self.media_url):
            # Get the file path
            relative_path = request.path[len(self.media_url):]
            file_path = safe_join(self.media_root, relative_path)
            
            # Check if file exists
            if file_path and os.path.isfile(file_path):
                # Serve the file
                return FileResponse(open(file_path, 'rb'))
            else:
                raise Http404("Media file not found")
        
        # Continue with normal request processing
        response = self.get_response(request)
        return response
