import fitz 
import pdfplumber
import spacy
from transformers import pipeline
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import UploadPDF
from .serializers import PDFSerializers
from django.contrib.postgres.search import SearchVector

class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    nlp = spacy.load("en_core_web_sm")

    def post(self, request, *args, **kwargs):
        file_serializer = PDFSerializers(data=request.data)

        if file_serializer.is_valid():
            pdf_instance = file_serializer.save()
            extracted_data = self.extract_text(pdf_instance.file.path)
            pdf_instance.text = extracted_data["text"]
            pdf_instance.summary = extracted_data["summary"]
            pdf_instance.metadata = extracted_data["metadata"]
            pdf_instance.entities = extracted_data["entities"]
            pdf_instance.classification = extracted_data["classification"]
            pdf_instance.save()

            return Response(
                {"message": "File uploaded successfully", "data": extracted_data},
                status=status.HTTP_201_CREATED,
            )
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def extract_text(self, pdf_path: str):
        data = {
            "text": "",
            "metadata": {},
            "tables": [],
            "summary": "",
            "entities": []
        }

        # Extract text and metadata
        doc = fitz.open(pdf_path)
        data["metadata"] = doc.metadata
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")
        data["text"] = full_text

        # Extract tables
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_table()
                if tables:
                    data["tables"].append(tables)

        # Summarize the text
        if len(full_text) > 500:
            data["summary"] = self.generate_summary(full_text)
        
        # Extract the entities
        data["entities"] = self.extract_entities(full_text)

        # Extract the categories 
        data["classification"] = self.classify_text(full_text)

        return data
    
    def generate_summary(self,text: str):
        """Summarize PDF content using Hugging Face Transformer"""
        summary = self.summarizer(text[:1024], max_length=150, min_length=50, do_sample=False)
        return summary[0]["summary_text"]

    def extract_entities(self, text: str):
        """Extract named entities using SpaCy."""
        doc = self.nlp(text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        return entities

    def classify_text(self, text: str):
        candidate_labels = ["Finance", "Legal", "Technical", "Health", "Education", "Invoice", "Resume", "Report", "Contract", "Research"]
        result = self.classifier(text[:1000], candidate_labels)
        return {
            "labels": result["labels"],
            "scores": result["scores"]
        }
    

class PDFSearchView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        label = request.GET.get('label', '')
        entity = request.GET.get('entity', '')
        results = UploadPDF.objects.all()
        if query:
            results = results.annotate(
                search=SearchVector('text', 'summary')
            ).filter(search=query)

        if label:
            results = results.filter(classification__labels__contains=[label])

        if entity:
            results = results.filter(entities__contains=[{"label": entity}])

        serializer = PDFSerializers(results, any=True)
        return Response(serializer.data)
    