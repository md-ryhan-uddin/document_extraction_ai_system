"""
AI-based document content extraction service.
Uses advanced language models with structured output (json_schema) to extract content from documents.
"""
import base64
import io
import time
import logging
from typing import Dict, Any, List, Optional
from PIL import Image
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)


class AIExtractor:
    """Extracts document content using AI API with structured output"""

    # JSON Schema for structured output
    EXTRACTION_SCHEMA = {
        "name": "document_extraction",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "page_type": {
                    "type": "string",
                    "description": "Type of page: form, table, mixed, text, invoice, etc.",
                },
                "detected_language": {
                    "type": "string",
                    "enum": ["en", "bn", "bn+en", "unknown"],
                    "description": "Primary language(s) detected"
                },
                "language_confidence": {
                    "type": "number",
                    "description": "Confidence score for language detection (0-1)"
                },
                "content_blocks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "block_number": {"type": "integer"},
                            "block_type": {
                                "type": "string",
                                "enum": ["paragraph", "heading", "table", "form", "list", "handwriting", "image", "signature", "other"]
                            },
                            "text_content": {"type": "string"},
                            "bbox": {
                                "type": "object",
                                "properties": {
                                    "x1": {"type": "number"},
                                    "y1": {"type": "number"},
                                    "x2": {"type": "number"},
                                    "y2": {"type": "number"}
                                },
                                "required": ["x1", "y1", "x2", "y2"],
                                "additionalProperties": False
                            },
                            "confidence": {"type": "number"},
                            "is_handwritten": {"type": "boolean"},
                            "table_data": {
                                "type": "object",
                                "properties": {
                                    "headers": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "text": {"type": "string"},
                                                "column_path": {
                                                    "type": "array",
                                                    "items": {"type": "integer"}
                                                },
                                                "level": {"type": "integer"}
                                            },
                                            "required": ["text", "column_path", "level"],
                                            "additionalProperties": False
                                        }
                                    },
                                    "rows": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "row_index": {"type": "integer"},
                                                "cells": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "text": {"type": "string"},
                                                            "column_path": {
                                                                "type": "array",
                                                                "items": {"type": "integer"}
                                                            },
                                                            "rowspan": {"type": "integer"},
                                                            "colspan": {"type": "integer"}
                                                        },
                                                        "required": ["text", "column_path", "rowspan", "colspan"],
                                                        "additionalProperties": False
                                                    }
                                                }
                                            },
                                            "required": ["row_index", "cells"],
                                            "additionalProperties": False
                                        }
                                    }
                                },
                                "required": ["headers", "rows"],
                                "additionalProperties": False
                            },
                            "form_data": {
                                "type": "object",
                                "properties": {
                                    "fields": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "field_name": {"type": "string"},
                                                "field_label": {"type": "string"},
                                                "field_type": {
                                                    "type": "string",
                                                    "enum": ["text", "checkbox", "radio", "select", "date", "signature", "other"]
                                                },
                                                "field_value": {"type": "string"},
                                                "is_filled": {"type": "boolean"}
                                            },
                                            "required": ["field_name", "field_label", "field_type", "field_value", "is_filled"],
                                            "additionalProperties": False
                                        }
                                    }
                                },
                                "required": ["fields"],
                                "additionalProperties": False
                            }
                        },
                        "required": ["block_number", "block_type", "text_content", "bbox", "confidence", "is_handwritten", "table_data", "form_data"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["page_type", "detected_language", "language_confidence", "content_blocks"],
            "additionalProperties": False
        }
    }

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the AI extractor.

        Args:
            api_key: AI API key (defaults to settings)
            model: Model name (defaults to settings)
        """
        self.api_key = api_key or settings.API_KEY
        self.model = model or settings.MODEL_NAME
        self.client = OpenAI(api_key=self.api_key)

    def extract_page_content(
        self,
        image: Image.Image,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Extract content from a single page image.

        Args:
            image: PIL Image of the page
            retry_count: Current retry attempt

        Returns:
            dict: Extracted content with structure matching the schema
        """
        start_time = time.time()

        try:
            # Convert image to base64
            image_base64 = self._image_to_base64(image)

            # Create the prompt
            prompt = self._create_extraction_prompt()

            # Call AI API
            logger.info(f"Calling AI API with model {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": self.EXTRACTION_SCHEMA
                },
                temperature=0.1,
            )

            processing_time = time.time() - start_time

            # Extract the content
            content = response.choices[0].message.content
            import json
            result = json.loads(content)

            logger.info(f"Extraction completed in {processing_time:.2f}s")
            logger.info(f"Tokens used: {response.usage.total_tokens}")

            return {
                "success": True,
                "data": result,
                "processing_time": processing_time,
                "tokens_used": response.usage.total_tokens,
                "retry_count": retry_count
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Extraction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "tokens_used": 0,
                "retry_count": retry_count
            }

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Save to bytes
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)

        # Encode to base64
        return base64.b64encode(buffer.read()).decode('utf-8')

    def _create_extraction_prompt(self) -> str:
        """Create the extraction prompt for AI model"""
        return """You are an advanced document analysis system. Extract ALL content from this document page with maximum accuracy.

**Instructions:**
1. **Detect page type**: Identify if this is a form, table, mixed content, invoice, text document, etc.
2. **Detect language**: Identify if the text is in English (en), Bangla (bn), mixed (bn+en), or unknown.
3. **Extract all content blocks** in reading order:
   - Paragraphs, headings, lists, tables, forms, handwriting, images, signatures
   - For each block, provide:
     - Accurate text transcription (preserve exact text including Bangla characters)
     - Block type classification
     - Bounding box coordinates (normalized 0-1 relative to page dimensions)
     - Confidence score (0-1)
     - Whether it's handwritten

4. **For TABLES** (even if block is not a table, always include empty table_data):
   - Extract complete table structure with nested columns (headers at multiple levels)
   - Use column_path to represent hierarchy: [0] for top-level, [0,1] for sub-column, [0,1,2] for sub-sub-column
   - Capture all rows and cells with exact text
   - Note any merged cells (rowspan/colspan)

5. **For FORMS** (even if block is not a form, always include empty form_data):
   - Extract all form fields with labels
   - Identify field types (text, checkbox, radio, select, date, signature)
   - Capture current values if filled
   - Note which fields are filled vs empty

6. **Bounding boxes**: Provide normalized coordinates (0-1) where:
   - x1, y1 = top-left corner
   - x2, y2 = bottom-right corner

7. **IMPORTANT**: Every block MUST have both table_data and form_data fields:
   - If not a table: table_data = {"headers": [], "rows": []}
   - If not a form: form_data = {"fields": []}

8. **Language confidence**: Provide a score (0-1) indicating confidence in language detection.

Extract everything accurately, preserving the exact structure and content of the document."""

    def validate_extraction(self, result: Dict[str, Any]) -> bool:
        """
        Validate that the extraction result meets quality standards.

        Args:
            result: Extraction result dictionary

        Returns:
            bool: True if valid, False otherwise
        """
        if not result.get('success'):
            return False

        data = result.get('data', {})

        # Check required fields
        if not all(key in data for key in ['page_type', 'detected_language', 'content_blocks']):
            logger.warning("Missing required fields in extraction result")
            return False

        # Check if we have content
        if not data['content_blocks']:
            logger.warning("No content blocks extracted")
            return False

        # Check each block has required structure
        for block in data['content_blocks']:
            if not all(key in block for key in ['block_type', 'table_data', 'form_data']):
                logger.warning(f"Block {block.get('block_number')} missing required fields")
                return False

        return True
