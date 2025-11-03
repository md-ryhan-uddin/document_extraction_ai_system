from django.db import models
from django.contrib.postgres.fields import ArrayField
import json


class Document(models.Model):
    """Main document model"""
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('image', 'Image'),
        ('scanned', 'Scanned Document'),
    ]

    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file_size = models.IntegerField()  # in bytes

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    error_message = models.TextField(blank=True, null=True)

    total_pages = models.IntegerField(default=0)

    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    # Processing info
    processing_time = models.FloatField(blank=True, null=True)  # in seconds

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.original_filename})"


class Page(models.Model):
    """Each page in a document"""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('bn', 'Bangla'),
        ('bn+en', 'Bangla + English'),
        ('unknown', 'Unknown'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='pages')
    page_number = models.IntegerField()

    # Image data
    image = models.ImageField(upload_to='pages/%Y/%m/%d/', blank=True, null=True)  # Rotated/corrected image
    original_image = models.ImageField(upload_to='pages/original/%Y/%m/%d/', blank=True, null=True)  # Original unrotated image
    width = models.IntegerField()
    height = models.IntegerField()

    # Rotation info
    detected_rotation = models.IntegerField(default=0)  # 0, 90, 180, 270
    applied_rotation = models.IntegerField(default=0)

    # Language detection
    detected_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='unknown')
    language_confidence = models.FloatField(default=0.0)

    # Page type
    page_type = models.CharField(max_length=50, blank=True)  # form, table, mixed, text, etc.

    # Processing
    processed = models.BooleanField(default=False)
    dpi = models.IntegerField(default=150)  # DPI used for processing

    class Meta:
        ordering = ['document', 'page_number']
        unique_together = ['document', 'page_number']

    def __str__(self):
        return f"{self.document.title} - Page {self.page_number}"


class ContentBlock(models.Model):
    """Content blocks extracted from pages"""
    BLOCK_TYPE_CHOICES = [
        ('paragraph', 'Paragraph'),
        ('heading', 'Heading'),
        ('table', 'Table'),
        ('form', 'Form'),
        ('list', 'List'),
        ('handwriting', 'Handwriting'),
        ('image', 'Image'),
        ('signature', 'Signature'),
        ('other', 'Other'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='content_blocks')
    block_number = models.IntegerField()  # Order on the page
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES)

    # Content
    text_content = models.TextField(blank=True)

    # Bounding box (normalized 0-1)
    bbox_x1 = models.FloatField()
    bbox_y1 = models.FloatField()
    bbox_x2 = models.FloatField()
    bbox_y2 = models.FloatField()

    # Confidence
    confidence = models.FloatField(default=1.0)

    # Flags
    is_handwritten = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    # JSON fields for structured data
    table_data = models.JSONField(default=dict, blank=True)  # Always present, empty dict if not a table
    form_data = models.JSONField(default=dict, blank=True)   # Always present, empty dict if not a form
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['page', 'block_number']
        unique_together = ['page', 'block_number']

    def __str__(self):
        return f"{self.page} - Block {self.block_number} ({self.block_type})"


class TableCell(models.Model):
    """Individual table cells with support for nested columns"""
    content_block = models.ForeignKey(ContentBlock, on_delete=models.CASCADE, related_name='table_cells')

    # Position in table
    row_index = models.IntegerField()
    column_path = models.JSONField()  # e.g., [0], [1, 2], [0, 1, 3] for nested columns

    # Content
    text = models.TextField(blank=True)
    value = models.JSONField(blank=True, null=True)  # For structured data

    # Spanning
    rowspan = models.IntegerField(default=1)
    colspan = models.IntegerField(default=1)

    # Cell type
    is_header = models.BooleanField(default=False)

    # Metadata
    confidence = models.FloatField(default=1.0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['content_block', 'row_index', 'column_path']

    def __str__(self):
        return f"Cell ({self.row_index}, {self.column_path})"


class FormField(models.Model):
    """Form fields extracted from documents"""
    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('select', 'Select'),
        ('date', 'Date'),
        ('signature', 'Signature'),
        ('other', 'Other'),
    ]

    content_block = models.ForeignKey(ContentBlock, on_delete=models.CASCADE, related_name='form_fields')

    # Field info
    field_name = models.CharField(max_length=255)
    field_label = models.CharField(max_length=255, blank=True)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)

    # Value
    field_value = models.TextField(blank=True)
    is_filled = models.BooleanField(default=False)

    # Position
    field_order = models.IntegerField(default=0)

    # Confidence
    confidence = models.FloatField(default=1.0)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['content_block', 'field_order']

    def __str__(self):
        return f"{self.field_name}: {self.field_value[:50]}"


class ExtractionLog(models.Model):
    """Log of extraction attempts for debugging"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='extraction_logs')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='extraction_logs', blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    # Request/Response
    request_data = models.JSONField()
    response_data = models.JSONField(blank=True, null=True)

    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    # Metadata
    processing_time = models.FloatField()  # in seconds
    tokens_used = models.IntegerField(default=0)
    retry_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.document} - {self.timestamp} ({status})"
