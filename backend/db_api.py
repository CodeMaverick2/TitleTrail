import os
import sys
import django
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import base64

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DBAPI")

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import models
from titletrail.models import PropertyDetails, PropertyImage

def store_property_details(property_data: Dict[str, Any]) -> int:
    """
    Store property details in the database
    
    Args:
        property_data: Dictionary containing property details from image processing
        
    Returns:
        ID of the stored property details record
    """
    try:
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
        
        logger.info(f"Stored property details with ID: {property_details.id}")
        
        return property_details.id
        
    except Exception as e:
        logger.error(f"Error storing property details: {str(e)}")
        raise

def store_property_image(property_id: int, image_data: bytes, metadata: Dict[str, Any]) -> int:
    """
    Store a property image in the database
    
    Args:
        property_id: ID of the property details record
        image_data: Binary image data
        metadata: Dictionary containing image metadata
        
    Returns:
        ID of the stored property image record
    """
    try:
        # Get the PropertyDetails object
        property_details = PropertyDetails.objects.get(id=property_id)
        
        # Create a new PropertyImage object
        property_image = PropertyImage(
            property=property_details,  # Use the property object, not property_id
            image_data=image_data,
            image_type=metadata.get("type", ""),
            year_period=metadata.get("year_period", ""),
            description=metadata.get("description", "")
        )
        
        # Save the object to the database
        property_image.save()
        
        logger.info(f"Stored property image with ID: {property_image.id} for property ID: {property_id}")
        
        return property_image.id
        
    except Exception as e:
        logger.error(f"Error storing property image: {str(e)}")
        raise

def get_property_details_by_id(property_id: int) -> Optional[Dict[str, Any]]:
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

def get_property_images_by_property_id(property_id: int) -> List[Dict[str, Any]]:
    """
    Get all images for a property
    
    Args:
        property_id: ID of the property details record
        
    Returns:
        List of dictionaries containing image metadata
    """
    try:
        property_images = PropertyImage.objects.filter(property__id=property_id)
        
        return [
            {
                "id": image.id,
                "property_id": image.property.id,
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

def get_image_data_by_id(image_id: int) -> Optional[Tuple[bytes, Dict[str, Any]]]:
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
            "property_id": property_image.property.id,
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

def get_image_base64_by_id(image_id: int) -> Optional[Dict[str, Any]]:
    """
    Get image data as base64 and metadata by ID
    
    Args:
        image_id: ID of the property image record
        
    Returns:
        Dictionary containing base64 encoded image data and metadata or None if not found
    """
    result = get_image_data_by_id(image_id)
    
    if result is None:
        return None
        
    image_data, metadata = result
    
    # Convert image data to base64
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    return {
        "image": f"data:image/png;base64,{base64_image}",
        "metadata": metadata
    }

def search_properties(search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search for properties based on search parameters
    
    Args:
        search_params: Dictionary containing search parameters
        
    Returns:
        List of dictionaries containing property details
    """
    try:
        # Start with all properties
        query = PropertyDetails.objects.all()
        
        # Apply filters based on search parameters
        if "survey_number" in search_params:
            query = query.filter(survey_number__icontains=search_params["survey_number"])
        
        if "village" in search_params:
            query = query.filter(village__icontains=search_params["village"])
        
        if "hobli" in search_params:
            query = query.filter(hobli__icontains=search_params["hobli"])
        
        if "taluk" in search_params:
            query = query.filter(taluk__icontains=search_params["taluk"])
        
        if "district" in search_params:
            query = query.filter(district__icontains=search_params["district"])
        
        if "owner_name" in search_params:
            query = query.filter(owner_name__icontains=search_params["owner_name"])
        
        # Get the results
        properties = query.order_by('-created_at')
        
        # Convert to list of dictionaries
        return [
            {
                "id": prop.id,
                "survey_number": prop.survey_number,
                "surnoc": prop.surnoc,
                "hissa": prop.hissa,
                "village": prop.village,
                "hobli": prop.hobli,
                "taluk": prop.taluk,
                "district": prop.district,
                "owner_name": prop.owner_name,
                "created_at": prop.created_at,
                "updated_at": prop.updated_at
            }
            for prop in properties
        ]
        
    except Exception as e:
        logger.error(f"Error searching properties: {str(e)}")
        raise