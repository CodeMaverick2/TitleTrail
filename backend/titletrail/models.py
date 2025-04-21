from django.db import models

class PropertyDetails(models.Model):
    """
    Model to store property details extracted from image processing
    """
    # Primary key (auto-generated)
    id = models.AutoField(primary_key=True)
    
    # Basic property information
    survey_number = models.CharField(max_length=50, blank=True, null=True)
    surnoc = models.CharField(max_length=50, blank=True, null=True)
    hissa = models.CharField(max_length=50, blank=True, null=True)
    
    # Location information
    village = models.CharField(max_length=100, blank=True, null=True)
    hobli = models.CharField(max_length=100, blank=True, null=True)
    taluk = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    
    # Owner information
    owner_name = models.TextField(blank=True, null=True)
    owner_details = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Property {self.id}: {self.survey_number} - {self.village}, {self.district}"
    
    class Meta:
        app_label = 'titletrail'  # Explicitly set the app label
        db_table = 'property_details'
        verbose_name = 'Property Detail'
        verbose_name_plural = 'Property Details'


class PropertyImage(models.Model):
    """
    Model to store images related to property details
    """
    # Primary key (auto-generated)
    id = models.AutoField(primary_key=True)
    
    # Foreign key to PropertyDetails
    property = models.ForeignKey(
        PropertyDetails, 
        on_delete=models.CASCADE,
        related_name='images'
    )
    
    # Image data
    image_data = models.BinaryField()
    
    # Image metadata
    image_type = models.CharField(max_length=50, blank=True, null=True)
    year_period = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image {self.id} for Property {self.property.id}"
    
    class Meta:
        app_label = 'titletrail'  # Explicitly set the app label
        db_table = 'property_images'
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'