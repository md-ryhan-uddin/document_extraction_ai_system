"""
URL Configuration for documents app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'pages', views.PageViewSet, basename='page')
router.register(r'blocks', views.ContentBlockViewSet, basename='contentblock')
router.register(r'logs', views.ExtractionLogViewSet, basename='extractionlog')

app_name = 'documents'

urlpatterns = [
    # Frontend views
    path('', views.home, name='home'),
    path('all-documents/', views.all_documents, name='all_documents'),
    path('viewer/<int:document_id>/', views.document_viewer, name='viewer'),

    # API endpoints
    path('api/', include(router.urls)),

    # Direct URL for block downloads
    # path('api/blocks/<int:block_id>/download/', views.download_content_block, name='block-download'),
]
