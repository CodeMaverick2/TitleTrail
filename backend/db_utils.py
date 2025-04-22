import logging
import os
import django
from django.conf import settings
from django.db import transaction
from typing import Dict, Any, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_utils.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DBUtils")

# Configure Django settings if not already configured
if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DB_NAME'),
                'USER': os.environ.get('DB_USER'),
                'PASSWORD': os.environ.get('DB_PASSWORD'),
                'HOST': os.environ.get('DB_HOST', 'localhost'),
                'PORT': os.environ.get('DB_PORT', '5432'),
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
    )
    django.setup()

# Import models after Django is configured
from models import PropertyDetails, PropertyImage


def save_property_details(property_data: Dict[str, Any]) -> int:
    """
    Save property details to the database
    
    Args:
        property_data: Dictionary containing property details
        
    Returns:
        ID of the saved property details record
    """
    try:
        with transaction.atomic():
            # Create a new PropertyDetails object
            property_details = PropertyDetails(
                survey_number=property_data.get("Survey Number", ""),
                surnoc=property_data.get("Surnoc", ""),
                hissa=property_data.get("Hissa", ""),
                village=property_data.get("Village", ""),
                hobli=property_data.get("Hobli", ""),
                taluk=property_data.get("Taluk", ""),
                district=property_data.get("District", ""),
                owner_name=property_data.get("Owner Name", ""),
                owner_details=property_data.get("Owner Details", "")
            )
            
            # Save the object to the database
            property_details.save()
            
            logger.info(f"Saved property details with ID: {property_details.id}")
            
            return property_details.id
            
    except Exception as e:
        logger.error(f"Error saving property details: {str(e)}")
        raise


def save_property_image(property_id: int, image_data: bytes, metadata: Dict[str, Any]) -> int:
    """
    Save a property image to the database
    
    Args:
        property_id: ID of the property details record
        image_data: Binary image data
        metadata: Dictionary containing image metadata
        
    Returns:
        ID of the saved property image record
    """
    try:
        with transaction.atomic():
            # Create a new PropertyImage object
            property_image = PropertyImage(
                property_id=property_id,
                image_data=image_data,
                image_type=metadata.get("type", ""),
                year_period=metadata.get("year_period", ""),
                description=metadata.get("description", "")
            )
            
            # Save the object to the database
            property_image.save()
            
            logger.info(f"Saved property image with ID: {property_image.id} for property ID: {property_id}")
            
            return property_image.id
            
    except Exception as e:
        logger.error(f"Error saving property image: {str(e)}")
        raise


def get_property_details(property_id: int) -> Optional[Dict[str, Any]]:
    """
    Get property details by ID
    
    Args:
        property_id: ID of the property details record
        
    Returns:
        Dictionary containing property details or None if not found
    """
    try:
        property_details = PropertyDetails.objects.get(id=property_id)
        
        return {
            "id": property_details.id,
            "survey_number": property_details.survey_number,
            "surnoc": property_details.surnoc,
            "hissa": property_details.hissa,
            "village": property_details.village,
            "hobli": property_details.hobli,
            "taluk": property_details.taluk,
            "district": property_details.district,
            "owner_name": property_details.owner_name,
            "owner_details": property_details.owner_details,
            "created_at": property_details.created_at,
            "updated_at": property_details.updated_at
        }
        
    except PropertyDetails.DoesNotExist:
        logger.warning(f"Property details with ID {property_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error getting property details: {str(e)}")
        raise


def get_property_images(property_id: int) -> List[Dict[str, Any]]:
    """
    Get all images for a property
    
    Args:
        property_id: ID of the property details record
        
    Returns:
        List of dictionaries containing image metadata
    """
    try:
        property_images = PropertyImage.objects.filter(property_id=property_id)
        
        return [
            {
                "id": image.id,
                "image_type": image.image_type,
                "year_period": image.year_period,
                "description": image.description,
                "created_at": image.created_at
            }
            for image in property_images
        ]
        
    except Exception as e:
        logger.error(f"Error getting property images: {str(e)}")
        raise


def get_image_data(image_id: int) -> Optional[Tuple[bytes, Dict[str, Any]]]:
    """
    Get image data and metadata by ID
    
    Args:
        image_id: ID of the property image record
        
    Returns:
        Tuple containing image data and metadata or None if not found
    """
    try:
        property_image = PropertyImage.objects.get(id=image_id)
        
        metadata = {
            "id": property_image.id,
            "property_id": property_image.property_id,
            "image_type": property_image.image_type,
            "year_period": property_image.year_period,
            "description": property_image.description,
            "created_at": property_image.created_at
        }
        
        return property_image.image_data, metadata
        
    except PropertyImage.DoesNotExist:
        logger.warning(f"Property image with ID {image_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error getting image data: {str(e)}")
        raise