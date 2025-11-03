from django.contrib import admin
from .models import Document, Page, ContentBlock, TableCell, FormField, ExtractionLog


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'status', 'total_pages', 'uploaded_at', 'processing_time']
    list_filter = ['status', 'file_type', 'uploaded_at']
    search_fields = ['title', 'original_filename']
    readonly_fields = ['uploaded_at', 'processed_at', 'processing_time']

    fieldsets = (
        ('Document Info', {
            'fields': ('title', 'original_filename', 'file', 'file_type', 'file_size')
        }),
        ('Processing Status', {
            'fields': ('status', 'error_message', 'total_pages', 'processing_time')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['document', 'page_number', 'detected_language', 'detected_rotation', 'page_type', 'processed']
    list_filter = ['processed', 'detected_language', 'detected_rotation', 'page_type']
    search_fields = ['document__title']
    readonly_fields = ['width', 'height']

    fieldsets = (
        ('Page Info', {
            'fields': ('document', 'page_number', 'image', 'width', 'height')
        }),
        ('Processing', {
            'fields': ('detected_rotation', 'applied_rotation', 'detected_language', 'language_confidence', 'page_type', 'dpi', 'processed')
        }),
    )


class TableCellInline(admin.TabularInline):
    model = TableCell
    extra = 0
    readonly_fields = ['row_index', 'column_path', 'text']


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 0
    readonly_fields = ['field_name', 'field_label', 'field_type', 'field_value']


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ['page', 'block_number', 'block_type', 'confidence', 'is_handwritten', 'requires_review']
    list_filter = ['block_type', 'is_handwritten', 'requires_review']
    search_fields = ['page__document__title', 'text_content']
    readonly_fields = ['bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2', 'confidence']
    inlines = [TableCellInline, FormFieldInline]

    fieldsets = (
        ('Block Info', {
            'fields': ('page', 'block_number', 'block_type')
        }),
        ('Content', {
            'fields': ('text_content',)
        }),
        ('Bounding Box', {
            'fields': (('bbox_x1', 'bbox_y1'), ('bbox_x2', 'bbox_y2')),
            'classes': ('collapse',)
        }),
        ('Flags & Confidence', {
            'fields': ('confidence', 'is_handwritten', 'requires_review')
        }),
        ('Structured Data', {
            'fields': ('table_data', 'form_data', 'metadata'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TableCell)
class TableCellAdmin(admin.ModelAdmin):
    list_display = ['content_block', 'row_index', 'column_path', 'text', 'is_header', 'confidence']
    list_filter = ['is_header']
    search_fields = ['text', 'content_block__page__document__title']


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['field_name', 'field_type', 'field_value', 'is_filled', 'confidence']
    list_filter = ['field_type', 'is_filled']
    search_fields = ['field_name', 'field_label', 'field_value']


@admin.register(ExtractionLog)
class ExtractionLogAdmin(admin.ModelAdmin):
    list_display = ['document', 'page', 'timestamp', 'success', 'processing_time', 'tokens_used', 'retry_count']
    list_filter = ['success', 'timestamp']
    search_fields = ['document__title', 'error_message']
    readonly_fields = ['timestamp', 'processing_time', 'tokens_used']

    fieldsets = (
        ('Reference', {
            'fields': ('document', 'page', 'timestamp')
        }),
        ('Status', {
            'fields': ('success', 'error_message', 'retry_count')
        }),
        ('Metrics', {
            'fields': ('processing_time', 'tokens_used')
        }),
        ('Data', {
            'fields': ('request_data', 'response_data'),
            'classes': ('collapse',)
        }),
    )
