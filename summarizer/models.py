from django.db import models

class Report(models.Model):
    file = models.FileField(upload_to='reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ocr_text = models.TextField(blank=True, null=True)
    #summary_json = models.JSONField(blank=True, null=True)
