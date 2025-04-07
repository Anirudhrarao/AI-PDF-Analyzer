from django.urls import path
from .views import UploadPDFView, PDFSearchView

urlpatterns = [
    path("upload/", UploadPDFView.as_view(), name="upload_pdf"), 
    path('api/search/', PDFSearchView.as_view(), name='pdf-search'),
]
