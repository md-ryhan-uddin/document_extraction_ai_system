"""
Custom middleware for rate limiting and resource management
Configurable via .env file
"""
from django.core.cache import cache
from django.http import JsonResponse
import time
import os


class DocumentProcessingLimitMiddleware:
    """
    Middleware to limit concurrent document processing per user/IP
    All limits configurable via environment variables
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_concurrent = int(os.getenv('MAX_CONCURRENT_PROCESSING', '3'))
        self.daily_limit = int(os.getenv('UPLOAD_DAILY_LIMIT', '50'))

    def __call__(self, request):
        # Only apply to document upload endpoint
        if request.path == '/api/documents/' and request.method == 'POST':
            # Get user identifier (IP address)
            ip_address = self.get_client_ip(request)

            try:
                # Check concurrent processing limit
                processing_key = f'processing_{ip_address}'
                concurrent_count = cache.get(processing_key, 0)

                if concurrent_count >= self.max_concurrent:
                    return JsonResponse({
                        'error': 'Too many concurrent uploads',
                        'detail': f'You can only process {self.max_concurrent} documents at a time. Please wait for current processing to complete.',
                        'retry_after': 30,
                        'limit': self.max_concurrent,
                        'current': concurrent_count
                    }, status=429)

                # Check daily upload limit
                daily_key = f'daily_uploads_{ip_address}_{time.strftime("%Y%m%d")}'
                daily_count = cache.get(daily_key, 0)

                if daily_count >= self.daily_limit:
                    return JsonResponse({
                        'error': 'Daily limit exceeded',
                        'detail': f'You have reached the maximum of {self.daily_limit} documents per day. Please try again tomorrow.',
                        'retry_after': 86400,  # 24 hours
                        'limit': self.daily_limit,
                        'used': daily_count
                    }, status=429)
            except Exception as e:
                # Log cache error but don't block the upload
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Cache error in rate limiting middleware: {str(e)}")
                # Continue with the request even if cache fails

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class FileSizeLimitMiddleware:
    """
    Middleware to enforce file size limits before processing
    Configurable via MAX_FILE_SIZE_MB environment variable
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
        self.max_file_size = self.max_file_size_mb * 1024 * 1024

    def __call__(self, request):
        if request.path == '/api/documents/' and request.method == 'POST':
            if request.FILES:
                file = request.FILES.get('file')
                if file and file.size > self.max_file_size:
                    file_size_mb = file.size / (1024 * 1024)
                    return JsonResponse({
                        'error': 'File too large',
                        'detail': f'Maximum file size is {self.max_file_size_mb}MB. Your file is {file_size_mb:.1f}MB.',
                        'max_size_mb': self.max_file_size_mb,
                        'file_size_mb': round(file_size_mb, 1)
                    }, status=413)

        response = self.get_response(request)
        return response
