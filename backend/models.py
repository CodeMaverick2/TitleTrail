from django.db import models

class Property(models.Model):
    # Stores property details
    survey_number = models.CharField(max_length=50)
    surnoc = models.CharField(max_length=50, blank=True, null=True)
    hissa = models.CharField(max_length=50)
    village = models.CharField(max_length=100)
    hobli = models.CharField(max_length=100)
    taluk = models.CharField(max_length=100)
    district = models.CharField(max_length=100)

class RTC(models.Model):
    # Stores RTC document details
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    period = models.CharField(max_length=50)
    year = models.CharField(max_length=4)
    owner = models.CharField(max_length=255)
    ownership_details = models.TextField(blank=True, null=True)
    document_image = models.BinaryField()  # Store image as binary data

class DropdownMapping(models.Model):
    # Stores dropdown mappings for Period and Year
    DROPDOWN_TYPE_CHOICES = [
        ('Period', 'Period'),
        ('Year', 'Year'),
    ]
    dropdown_type = models.CharField(max_length=10, choices=DROPDOWN_TYPE_CHOICES)
    dropdown_value = models.CharField(max_length=50)
    mapped_index = models.IntegerField()
    period = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

class ScrapingLog(models.Model):
    # Tracks scraping attempts and errors
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    period = models.CharField(max_length=50)
    year = models.CharField(max_length=4)
    status = models.CharField(max_length=20)  # e.g., "Success", "Failed"
    error_message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
