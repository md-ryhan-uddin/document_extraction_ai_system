"""
Main document processing pipeline.
Orchestrates document ingestion, rotation detection, content extraction, and storage.
"""
import io
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image
import fitz  # PyMuPDF
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from ..models import Document, Page, ContentBlock, TableCell, FormField, ExtractionLog
from .rotation_detector import RotationDetector
from .ai_extractor import AIExtractor
# Import from __init__.py to ensure same singleton instance as views.py
from documents.services import cancellation_manager

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main document processing pipeline"""

    def __init__(self):
        self.rotation_detector = RotationDetector()
        self.ai_extractor = AIExtractor()

    def process_document(self, document: Document) -> bool:
        """
        Process a complete document.

        Args:
            document: Document model instance

        Returns:
            bool: True if successful, False otherwise
        """
        start_time = time.time()

        try:
            print(f"\n{'='*80}")
            print(f"📄 PROCESSING STARTED: Document #{document.id} - '{document.title}'")
            print(f"   File: {document.original_filename}")
            print(f"   Type: {document.file_type}")
            print(f"{'='*80}\n")
            logger.info(f"Starting processing for document: {document.title}")

            # Clear any previous cancellation flags
            cancellation_manager.clear_cancellation(document.id)

            # Update status
            document.status = 'processing'
            document.save()

            # Check for cancellation before starting
            print(f"[CHECKPOINT 1] Checking cancellation for doc {document.id}: {cancellation_manager.is_cancelled(document.id)}")
            if cancellation_manager.is_cancelled(document.id):
                print(f"[CHECKPOINT 1] CANCELLATION DETECTED! Stopping...")
                raise InterruptedError("Processing cancelled by user")

            # Determine file type and process accordingly
            file_path = document.file.path

            if document.file_type == 'pdf':
                pages = self._process_pdf(document, file_path)
            elif document.file_type in ['image', 'scanned']:
                pages = self._process_image(document, file_path)
            else:
                raise ValueError(f"Unsupported file type: {document.file_type}")

            # Check for cancellation after processing
            if cancellation_manager.is_cancelled(document.id):
                raise InterruptedError("Processing cancelled by user")

            # Update document
            document.total_pages = len(pages)
            document.status = 'completed'
            document.processed_at = timezone.now()
            document.processing_time = time.time() - start_time
            document.save()

            # Clear cancellation flag on success
            cancellation_manager.clear_cancellation(document.id)

            print(f"\n{'='*80}")
            print(f"✅ PROCESSING COMPLETED: Document #{document.id} - '{document.title}'")
            print(f"   Pages: {document.total_pages}")
            print(f"   Time: {document.processing_time:.2f}s")
            print(f"{'='*80}\n")
            logger.info(f"Document processed successfully in {document.processing_time:.2f}s")
            return True

        except InterruptedError as e:
            print(f"\n{'='*80}")
            print(f"❌ PROCESSING CANCELLED: Document #{document.id} - '{document.title}'")
            print(f"   Reason: {str(e)}")
            print(f"   Time before cancel: {time.time() - start_time:.2f}s")
            print(f"{'='*80}\n")
            logger.info(f"Document processing cancelled: {str(e)}")
            document.status = 'cancelled'
            document.error_message = str(e)
            document.processing_time = time.time() - start_time
            document.save()
            cancellation_manager.clear_cancellation(document.id)
            return False
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"💥 PROCESSING FAILED: Document #{document.id} - '{document.title}'")
            print(f"   Error: {str(e)}")
            print(f"   Time before failure: {time.time() - start_time:.2f}s")
            print(f"{'='*80}\n")
            logger.error(f"Document processing failed: {str(e)}", exc_info=True)
            document.status = 'failed'
            document.error_message = str(e)
            document.processing_time = time.time() - start_time
            document.save()
            cancellation_manager.clear_cancellation(document.id)
            return False

    def _process_pdf(self, document: Document, file_path: str) -> List[Page]:
        """Process a PDF document"""
        logger.info(f"Processing PDF: {file_path}")

        pages = []
        pdf_document = fitz.open(file_path)

        try:
            for page_num in range(len(pdf_document)):
                # Check for cancellation between pages
                print(f"[CHECKPOINT 2] Page {page_num + 1}: Checking cancellation for doc {document.id}: {cancellation_manager.is_cancelled(document.id)}")
                if cancellation_manager.is_cancelled(document.id):
                    print(f"[CHECKPOINT 2] CANCELLATION DETECTED at page {page_num + 1}! Stopping...")
                    logger.info(f"Cancellation detected at page {page_num + 1}")
                    raise InterruptedError("Processing cancelled by user")

                print(f"📑 Processing page {page_num + 1}/{len(pdf_document)} of Document #{document.id}")
                logger.info(f"Processing page {page_num + 1}/{len(pdf_document)}")

                # Get page
                pdf_page = pdf_document[page_num]

                # Render page to image at specified DPI
                dpi = settings.DEFAULT_DPI
                zoom = dpi / 72  # 72 is the default DPI
                mat = fitz.Matrix(zoom, zoom)
                pix = pdf_page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img_data = pix.tobytes("jpeg")
                image = Image.open(io.BytesIO(img_data))

                # Process page
                page = self._process_page(
                    document=document,
                    page_number=page_num + 1,
                    image=image,
                    dpi=dpi
                )
                pages.append(page)

        finally:
            pdf_document.close()

        return pages

    def _process_image(self, document: Document, file_path: str) -> List[Page]:
        """Process a single image file"""
        logger.info(f"Processing image: {file_path}")

        # Open image
        image = Image.open(file_path)

        # Process as single page
        page = self._process_page(
            document=document,
            page_number=1,
            image=image,
            dpi=settings.DEFAULT_DPI
        )

        return [page]

    def _process_page(
        self,
        document: Document,
        page_number: int,
        image: Image.Image,
        dpi: int
    ) -> Page:
        """
        Process a single page.

        Args:
            document: Parent document
            page_number: Page number (1-indexed)
            image: PIL Image of the page
            dpi: DPI used for processing

        Returns:
            Page: Created page instance
        """
        logger.info(f"Processing page {page_number}")

        # Check for cancellation before processing page
        print(f"[CHECKPOINT 3] Before processing page {page_number}: Checking cancellation for doc {document.id}: {cancellation_manager.is_cancelled(document.id)}")
        if cancellation_manager.is_cancelled(document.id):
            print(f"[CHECKPOINT 3] CANCELLATION DETECTED before processing page {page_number}! Stopping...")
            logger.info(f"Cancellation detected before processing page {page_number}")
            raise InterruptedError("Processing cancelled by user")

        # Step 1: Save original image (before rotation)
        original_to_save = image.copy()
        if original_to_save.mode == 'RGBA':
            rgb_image = Image.new('RGB', original_to_save.size, (255, 255, 255))
            rgb_image.paste(original_to_save, mask=original_to_save.split()[3])
            original_to_save = rgb_image
        elif original_to_save.mode not in ('RGB', 'L'):
            original_to_save = original_to_save.convert('RGB')

        # Step 2: Detect rotation
        logger.debug("Detecting rotation...")
        corrected_image, rotation_angle = self.rotation_detector.detect_and_correct(image)

        # Step 3: Create page record
        page = Page.objects.create(
            document=document,
            page_number=page_number,
            width=corrected_image.width,
            height=corrected_image.height,
            detected_rotation=rotation_angle,
            applied_rotation=rotation_angle,
            dpi=dpi,
            processed=False
        )

        # Save original image
        orig_buffer = io.BytesIO()
        original_to_save.save(orig_buffer, format='JPEG', quality=95)
        orig_buffer.seek(0)
        page.original_image.save(
            f'page_original_{document.id}_{page_number}.jpg',
            ContentFile(orig_buffer.read()),
            save=False
        )

        # Save corrected/rotated image
        # Convert RGBA to RGB if necessary (for PNG with transparency)
        if corrected_image.mode == 'RGBA':
            # Create a white background
            rgb_image = Image.new('RGB', corrected_image.size, (255, 255, 255))
            rgb_image.paste(corrected_image, mask=corrected_image.split()[3])  # Use alpha channel as mask
            corrected_image = rgb_image
        elif corrected_image.mode not in ('RGB', 'L'):
            # Convert other modes to RGB
            corrected_image = corrected_image.convert('RGB')

        img_buffer = io.BytesIO()
        corrected_image.save(img_buffer, format='JPEG', quality=95)
        img_buffer.seek(0)
        page.image.save(
            f'page_{document.id}_{page_number}.jpg',
            ContentFile(img_buffer.read()),
            save=True
        )

        # Check for cancellation before expensive AI call
        print(f"[CHECKPOINT 4] Before AI call on page {page_number}: Checking cancellation for doc {page.document.id}: {cancellation_manager.is_cancelled(page.document.id)}")
        if cancellation_manager.is_cancelled(page.document.id):
            print(f"[CHECKPOINT 4] CANCELLATION DETECTED before AI call! Stopping...")
            logger.info(f"Cancellation detected before AI extraction on page {page_number}")
            raise InterruptedError("Processing cancelled by user")

        # Step 3: Extract content using AI
        print(f"🤖 Calling AI API for page {page_number} of Document #{page.document.id}...")
        logger.debug("Extracting content with AI...")
        extraction_result = self._extract_content(page, corrected_image, retry_on_low_confidence=True)

        if extraction_result['success']:
            # Step 4: Store extracted content
            logger.debug("Storing extracted content...")
            self._store_extraction_result(page, extraction_result['data'])

            # Update page
            page.processed = True
            page.save()

        return page

    def _extract_content(
        self,
        page: Page,
        image: Image.Image,
        retry_on_low_confidence: bool = True,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Extract content from page using AI.

        Args:
            page: Page instance
            image: PIL Image
            retry_on_low_confidence: Whether to retry at higher DPI if confidence is low
            retry_count: Current retry count

        Returns:
            dict: Extraction result
        """
        # Check for cancellation before AI API call (redundant but safe)
        print(f"[CHECKPOINT 4b] Inside _extract_content: Checking cancellation for doc {page.document.id}: {cancellation_manager.is_cancelled(page.document.id)}")
        if cancellation_manager.is_cancelled(page.document.id):
            print(f"[CHECKPOINT 4b] CANCELLATION DETECTED in _extract_content! Stopping...")
            logger.info(f"Cancellation detected in _extract_content")
            return {
                'success': False,
                'error': 'Processing cancelled by user',
                'processing_time': 0.0,
                'tokens_used': 0,
                'retry_count': retry_count
            }

        # Extract content
        result = self.ai_extractor.extract_page_content(image, retry_count=retry_count)

        # Check for cancellation immediately after AI call (catches cancellations during API call)
        print(f"[CHECKPOINT 5] After AI call returned: Checking cancellation for doc {page.document.id}: {cancellation_manager.is_cancelled(page.document.id)}")
        if cancellation_manager.is_cancelled(page.document.id):
            print(f"[CHECKPOINT 5] CANCELLATION DETECTED after AI call! Stopping...")
            logger.info(f"Cancellation detected after AI extraction")
            return {
                'success': False,
                'error': 'Processing cancelled by user',
                'processing_time': result.get('processing_time', 0.0),
                'tokens_used': result.get('tokens_used', 0),
                'retry_count': retry_count
            }

        # Log extraction attempt
        ExtractionLog.objects.create(
            document=page.document,
            page=page,
            request_data={'dpi': page.dpi, 'retry_count': retry_count},
            response_data=result.get('data'),
            success=result['success'],
            error_message=result.get('error', ''),
            processing_time=result['processing_time'],
            tokens_used=result['tokens_used'],
            retry_count=retry_count
        )

        # Check if we should retry at higher DPI
        if (
            result['success'] and
            retry_on_low_confidence and
            retry_count == 0 and
            self._should_retry_at_higher_dpi(result['data'])
        ):
            logger.info("Low confidence detected, retrying at higher DPI...")

            # Check for cancellation before retry
            print(f"[CHECKPOINT 6] Before retry at higher DPI: Checking cancellation for doc {page.document.id}: {cancellation_manager.is_cancelled(page.document.id)}")
            if cancellation_manager.is_cancelled(page.document.id):
                print(f"[CHECKPOINT 6] CANCELLATION DETECTED before retry! Stopping...")
                logger.info(f"Cancellation detected before retry")
                return {
                    'success': False,
                    'error': 'Processing cancelled by user',
                    'processing_time': 0.0,
                    'tokens_used': 0,
                    'retry_count': retry_count
                }

            # Re-render page at higher DPI
            high_dpi_image = self._render_page_at_dpi(page, settings.HIGH_DPI)

            # Retry extraction
            return self._extract_content(
                page=page,
                image=high_dpi_image,
                retry_on_low_confidence=False,
                retry_count=retry_count + 1
            )

        return result

    def _should_retry_at_higher_dpi(self, data: Dict[str, Any]) -> bool:
        """Check if we should retry at higher DPI based on confidence scores"""
        # Check overall language confidence
        if data.get('language_confidence', 1.0) < settings.LOW_CONFIDENCE_THRESHOLD:
            return True

        # Check block confidences
        for block in data.get('content_blocks', []):
            if block.get('confidence', 1.0) < settings.LOW_CONFIDENCE_THRESHOLD:
                return True

        return False

    def _render_page_at_dpi(self, page: Page, dpi: int) -> Image.Image:
        """Re-render a page at specified DPI"""
        # This is a simplified version - in production you'd re-render from original
        # For now, just return the existing image
        return Image.open(page.image.path)

    def _store_extraction_result(self, page: Page, data: Dict[str, Any]):
        """
        Store extraction result in database.

        Args:
            page: Page instance
            data: Extracted data dictionary
        """
        # Update page metadata
        page.detected_language = data.get('detected_language', 'unknown')
        page.language_confidence = data.get('language_confidence', 0.0)
        page.page_type = data.get('page_type', '')
        page.save()

        # Store content blocks
        for block_data in data.get('content_blocks', []):
            self._store_content_block(page, block_data)

    def _store_content_block(self, page: Page, block_data: Dict[str, Any]):
        """Store a single content block"""
        bbox = block_data.get('bbox', {})

        # Create content block
        block = ContentBlock.objects.create(
            page=page,
            block_number=block_data['block_number'],
            block_type=block_data['block_type'],
            text_content=block_data.get('text_content', ''),
            bbox_x1=bbox.get('x1', 0),
            bbox_y1=bbox.get('y1', 0),
            bbox_x2=bbox.get('x2', 1),
            bbox_y2=bbox.get('y2', 1),
            confidence=block_data.get('confidence', 1.0),
            is_handwritten=block_data.get('is_handwritten', False),
            table_data=block_data.get('table_data', {}),
            form_data=block_data.get('form_data', {})
        )

        # Store table cells if present
        table_data = block_data.get('table_data', {})
        if table_data and table_data.get('rows'):
            self._store_table_cells(block, table_data)

        # Store form fields if present
        form_data = block_data.get('form_data', {})
        if form_data and form_data.get('fields'):
            self._store_form_fields(block, form_data)

    def _store_table_cells(self, block: ContentBlock, table_data: Dict[str, Any]):
        """Store table cells from table data"""
        for row_data in table_data.get('rows', []):
            row_index = row_data['row_index']
            for cell_data in row_data.get('cells', []):
                TableCell.objects.create(
                    content_block=block,
                    row_index=row_index,
                    column_path=cell_data['column_path'],
                    text=cell_data.get('text', ''),
                    rowspan=cell_data.get('rowspan', 1),
                    colspan=cell_data.get('colspan', 1),
                    is_header=False  # Can be enhanced
                )

        # Store headers as special rows
        for header_data in table_data.get('headers', []):
            TableCell.objects.create(
                content_block=block,
                row_index=-1,  # Special index for headers
                column_path=header_data['column_path'],
                text=header_data.get('text', ''),
                is_header=True
            )

    def _store_form_fields(self, block: ContentBlock, form_data: Dict[str, Any]):
        """Store form fields from form data"""
        for idx, field_data in enumerate(form_data.get('fields', [])):
            FormField.objects.create(
                content_block=block,
                field_name=field_data['field_name'],
                field_label=field_data.get('field_label', ''),
                field_type=field_data['field_type'],
                field_value=field_data.get('field_value', ''),
                is_filled=field_data.get('is_filled', False),
                field_order=idx
            )
