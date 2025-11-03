#!/usr/bin/env python
"""
Script to reprocess all failed documents.
Run this after fixing bugs to retry processing.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docai_project.settings')
django.setup()

from documents.models import Document
from documents.services import DocumentProcessor

def reprocess_failed_documents():
    """Reprocess all documents with 'failed' status"""
    failed_docs = Document.objects.filter(status='failed')

    print(f"Found {failed_docs.count()} failed documents")

    if failed_docs.count() == 0:
        print("No failed documents to reprocess!")
        return

    processor = DocumentProcessor()

    for doc in failed_docs:
        print(f"\n{'='*60}")
        print(f"Reprocessing: {doc.title} (ID: {doc.id})")
        print(f"{'='*60}")

        # Delete existing pages
        doc.pages.all().delete()

        # Reset status
        doc.status = 'uploaded'
        doc.error_message = None
        doc.save()

        # Reprocess
        success = processor.process_document(doc)

        if success:
            print(f"✓ Successfully reprocessed: {doc.title}")
        else:
            print(f"✗ Failed to reprocess: {doc.title}")
            print(f"  Error: {doc.error_message}")

    print(f"\n{'='*60}")
    print("Reprocessing complete!")
    print(f"{'='*60}")

if __name__ == '__main__':
    reprocess_failed_documents()
