"""
Custom throttling classes for document processing
Configurable via environment variables
"""
from rest_framework.throttling import AnonRateThrottle
from django.core.cache import cache
from django.conf import settings
import time
import os


class DocumentUploadThrottle(AnonRateThrottle):
    """
    Rate limit for document uploads
    Configurable via .env file
    """

    def __init__(self):
        super().__init__()
        # Get rate from environment or use default
        rate_per_hour = os.getenv('UPLOAD_RATE_PER_HOUR', '10')
        self.rate = f'{rate_per_hour}/hour'
        self.scope = 'document_upload'

    def allow_request(self, request, view):
        """
        Check if request should be allowed
        """
        if request.method != 'POST':
            return True

        # Get client IP
        ip = self.get_ident(request)

        # Daily limit check (configurable)
        daily_limit = int(os.getenv('UPLOAD_DAILY_LIMIT', '50'))
        daily_key = f'daily_upload_{ip}_{time.strftime("%Y%m%d")}'
        daily_count = cache.get(daily_key, 0)

        if daily_count >= daily_limit:
            self.wait_time = 86400  # 24 hours
            return False

        # Check hourly rate with parent class
        allowed = super().allow_request(request, view)

        if allowed:
            # Increment daily counter
            cache.set(daily_key, daily_count + 1, 86400)

        return allowed


class ConcurrentProcessingThrottle:
    """
    Limit concurrent document processing per IP
    Configurable via .env file
    """

    def allow_request(self, request, view):
        """
        Check if user can start new processing
        """
        if request.method != 'POST':
            return True

        ip = self.get_ident(request)
        max_concurrent = int(os.getenv('MAX_CONCURRENT_PROCESSING', '3'))

        # Check concurrent processing
        processing_key = f'processing_{ip}'
        concurrent = cache.get(processing_key, 0)

        if concurrent >= max_concurrent:
            return False

        return True

    def get_ident(self, request):
        """
        Get client identifier (IP address)
        """
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

    def wait(self):
        """
        Return wait time in seconds
        """
        return int(os.getenv('THROTTLE_WAIT_TIME', '60'))


class FileSizeValidator:
    """
    Validate file size before upload
    Configurable via MAX_FILE_SIZE_MB in .env
    """

    def __init__(self):
        self.max_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
        self.max_size_bytes = self.max_size_mb * 1024 * 1024

    def __call__(self, file):
        if file.size > self.max_size_bytes:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                f'File too large. Maximum size is {self.max_size_mb}MB. '
                f'Your file is {file.size / (1024*1024):.1f}MB.'
            )


def track_processing_start(ip_address):
    """
    Track when document processing starts
    """
    key = f'processing_{ip_address}'
    count = cache.get(key, 0)
    timeout = int(os.getenv('PROCESSING_TIMEOUT', '3600'))  # 1 hour default
    cache.set(key, count + 1, timeout)


def track_processing_end(ip_address):
    """
    Track when document processing ends
    """
    key = f'processing_{ip_address}'
    count = cache.get(key, 0)
    if count > 0:
        timeout = int(os.getenv('PROCESSING_TIMEOUT', '3600'))
        cache.set(key, count - 1, timeout)
