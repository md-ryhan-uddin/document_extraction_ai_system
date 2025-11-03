"""
Force cancel all processing documents and clean database.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docai_project.settings')
django.setup()

from documents.models import Document
from documents.services import cancellation_manager

def force_cancel_all():
    """Force cancel all processing documents"""

    print("\n" + "="*80)
    print("FORCE CANCELLING ALL PROCESSING DOCUMENTS")
    print("="*80 + "\n")

    # Get all processing documents
    processing_docs = Document.objects.filter(status='processing')

    if not processing_docs.exists():
        print("[OK] No documents are currently processing.\n")
        return

    print(f"Found {processing_docs.count()} stuck processing documents:\n")

    for doc in processing_docs:
        print(f"   #{doc.id}: {doc.title}")

        # Request cancellation (in case thread is still alive)
        cancellation_manager.request_cancellation(doc.id)

        # Force update status
        doc.status = 'cancelled'
        doc.error_message = 'Force cancelled by administrator'
        doc.save()

        print(f"      [CANCELLED]")

    # Clear all cancellation flags
    cancellation_manager.reset()

    print("\n" + "="*80)
    print("[SUCCESS] ALL PROCESSING DOCUMENTS HAVE BEEN CANCELLED")
    print("="*80 + "\n")

def delete_all_documents():
    """Delete all documents from database"""

    print("\n" + "="*80)
    print("DELETING ALL DOCUMENTS FROM DATABASE")
    print("="*80 + "\n")

    count = Document.objects.count()

    if count == 0:
        print("[OK] Database is already empty.\n")
        return

    print(f"Found {count} documents:\n")

    for doc in Document.objects.all():
        print(f"   #{doc.id}: {doc.title} [{doc.status}]")

    # Delete all
    Document.objects.all().delete()

    # Clear cancellation manager
    cancellation_manager.reset()

    print("\n" + "="*80)
    print(f"[SUCCESS] DELETED ALL {count} DOCUMENTS")
    print("="*80 + "\n")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--delete-all':
        confirm = input("WARNING: This will DELETE ALL documents! Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            delete_all_documents()
        else:
            print("[CANCELLED]\n")
    else:
        force_cancel_all()
        print("To delete all documents, run: python force_cancel_all.py --delete-all\n")
