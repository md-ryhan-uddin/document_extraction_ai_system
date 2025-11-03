"""
REST API Serializers for document models.
"""
from rest_framework import serializers
from .models import Document, Page, ContentBlock, TableCell, FormField, ExtractionLog


class TableCellSerializer(serializers.ModelSerializer):
    """Serializer for table cells"""

    class Meta:
        model = TableCell
        fields = [
            'id', 'row_index', 'column_path', 'text', 'value',
            'rowspan', 'colspan', 'is_header', 'confidence', 'metadata'
        ]


class FormFieldSerializer(serializers.ModelSerializer):
    """Serializer for form fields"""

    class Meta:
        model = FormField
        fields = [
            'id', 'field_name', 'field_label', 'field_type',
            'field_value', 'is_filled', 'field_order', 'confidence', 'metadata'
        ]


class ContentBlockSerializer(serializers.ModelSerializer):
    """Serializer for content blocks"""
    table_cells = TableCellSerializer(many=True, read_only=True)
    form_fields = FormFieldSerializer(many=True, read_only=True)

    class Meta:
        model = ContentBlock
        fields = [
            'id', 'block_number', 'block_type', 'text_content',
            'bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2',
            'confidence', 'is_handwritten', 'requires_review',
            'table_data', 'form_data', 'metadata',
            'table_cells', 'form_fields'
        ]


class PageSerializer(serializers.ModelSerializer):
    """Serializer for pages"""
    content_blocks = ContentBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = [
            'id', 'page_number', 'image', 'width', 'height',
            'detected_rotation', 'applied_rotation',
            'detected_language', 'language_confidence',
            'page_type', 'processed', 'dpi',
            'content_blocks'
        ]


class PageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for page lists (without content blocks)"""

    class Meta:
        model = Page
        fields = [
            'id', 'page_number', 'image', 'width', 'height',
            'detected_rotation', 'detected_language', 'page_type', 'processed'
        ]


class DocumentSerializer(serializers.ModelSerializer):
    """Full serializer for documents with all pages and content"""
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'original_filename', 'file', 'file_type', 'file_size',
            'status', 'error_message', 'total_pages',
            'uploaded_at', 'processed_at', 'processing_time',
            'pages'
        ]
        read_only_fields = ['uploaded_at', 'processed_at', 'processing_time', 'status']


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for document lists (without pages)"""

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'original_filename', 'file_type', 'file_size',
            'status', 'total_pages', 'uploaded_at', 'processed_at', 'processing_time'
        ]


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload"""

    class Meta:
        model = Document
        fields = ['title', 'file']

    def create(self, validated_data):
        """Create document and determine file type"""
        uploaded_file = validated_data['file']

        # Determine file type
        file_type = 'image'
        if uploaded_file.name.lower().endswith('.pdf'):
            file_type = 'pdf'
        elif uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
            file_type = 'image'

        # Create document
        document = Document.objects.create(
            title=validated_data.get('title', uploaded_file.name),
            original_filename=uploaded_file.name,
            file=uploaded_file,
            file_type=file_type,
            file_size=uploaded_file.size,
            status='uploaded'
        )

        return document


class ExtractionLogSerializer(serializers.ModelSerializer):
    """Serializer for extraction logs"""

    class Meta:
        model = ExtractionLog
        fields = [
            'id', 'document', 'page', 'timestamp',
            'request_data', 'response_data',
            'success', 'error_message',
            'processing_time', 'tokens_used', 'retry_count'
        ]


class SearchResultSerializer(serializers.Serializer):
    """Serializer for search results"""
    document_id = serializers.IntegerField()
    document_title = serializers.CharField()
    page_id = serializers.IntegerField()
    page_number = serializers.IntegerField()
    block_id = serializers.IntegerField()
    block_type = serializers.CharField()
    text_content = serializers.CharField()
    confidence = serializers.FloatField()
    relevance_score = serializers.FloatField(required=False)
