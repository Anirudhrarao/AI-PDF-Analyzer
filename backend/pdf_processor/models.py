from django.db import models



class UploadPDF(models.Model):
    file = models.FileField(upload_to="pdfs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, null=True)
    entities = models.JSONField(blank=True, null=True)
    classification = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.file.name