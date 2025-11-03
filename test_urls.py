import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'document_ai_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    from django.urls import get_resolver
    from documents import urls as doc_urls
    
    print("=== Document App URL Patterns ===")
    for pattern in doc_urls.urlpatterns:
        print(f"  {pattern}")
    
    print("\n=== Checking for block download URLs ===")
    resolver = get_resolver()
    for pattern in resolver.url_patterns:
        if 'api' in str(pattern.pattern):
            print(f"  {pattern}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
