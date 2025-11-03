#!/usr/bin/env python
"""
Simple schema validation without Django dependencies.
Checks if all properties are in required arrays.
"""

# The schema (copied directly)
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

def validate_schema_required(schema, path=""):
    """Check if all properties are in required arrays."""
    errors = []

    if not isinstance(schema, dict):
        return errors

    if schema.get('type') == 'object' and 'properties' in schema:
        properties = schema['properties']
        required = schema.get('required', [])

        property_keys = set(properties.keys())
        required_set = set(required)

        missing = property_keys - required_set
        if missing:
            errors.append({
                'path': path or 'root',
                'missing': sorted(list(missing))
            })

    # Recursively check nested structures
    if 'properties' in schema:
        for prop_name, prop_schema in schema['properties'].items():
            new_path = f"{path}.{prop_name}" if path else prop_name
            errors.extend(validate_schema_required(prop_schema, new_path))

    if 'items' in schema:
        new_path = f"{path}[]"
        errors.extend(validate_schema_required(schema['items'], new_path))

    return errors


if __name__ == '__main__':
    print("=" * 70)
    print("AI JSON Schema Validation Check")
    print("=" * 70)
    print()

    errors = validate_schema_required(EXTRACTION_SCHEMA['schema'])

    if errors:
        print(f"[FAIL] Found {len(errors)} validation error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. Path: {error['path']}")
            print(f"   Missing in 'required': {', '.join(error['missing'])}")
            print()
        print("Fix: Add the missing fields to the 'required' array in ai_extractor.py")
        exit(1)
    else:
        print("[PASS] Schema validation PASSED!")
        print()
        print("All object properties are correctly listed in 'required' arrays.")
        print("The schema is ready for strict mode.")
        exit(0)
