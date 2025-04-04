import fitz
import pdfplumber
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import UploadPDF
from .serializers import PDFSerializers

class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = PDFSerializers(data=request.data)

        if file_serializer.is_valid():
            pdf_instance = file_serializer.save()
            extracted_data = self.extract_text(pdf_instance.file.path)
            return Response(
                {"message": "File uploaded successfully", "data": extracted_data},
                status=status.HTTP_201_CREATED,
            )
        
    def extract_text(self, pdf_path: str):
        data = {
            "text": "",
            "metadata": {},
            "tables": []
        }

        doc = fitz.open(pdf_path)
        data["metadata"] = doc.metadata
        for page in doc:
            data["text"] = page.get_text("text")
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_table()
                if tables:
                    data["tables"].append(tables)
        
        return data