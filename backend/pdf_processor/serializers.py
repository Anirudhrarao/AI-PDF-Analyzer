from rest_framework import serializers
from .models import UploadPDF

class PDFSerializers(serializers.ModelSerializer):
    class Meta:
        model = UploadPDF
        fields = "__all__"
        