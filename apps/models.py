from django.db import models

# Create your models here.
class FileUpload(models.Model):
    title = models.CharField(max_length = 200)
    file = models.FileField(upload_to = 'PDF/')
    
# class FileDownload(models.Model):
#     title = models.TextField(max_length = 200)
#     file = models.FileField(upload_to = 'JSON/')
