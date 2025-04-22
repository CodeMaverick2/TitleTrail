import os
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import path
from django.core.wsgi import get_wsgi_application
from django.conf.urls.static import static
import tempfile
import base64
from pathlib import Path
from dotenv import load_dotenv

# Add CORS headers
class CORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*' 
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

dotenv_path = Path(__file__).resolve().parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)
    print(f"APP: Loaded environment variables from {dotenv_path}")

from image_processor import LandRecordImageProcessor
from scraper import RTCScraper
from db_api import (
    store_property_details,
    store_property_image,
    get_property_details_by_id,
    get_property_images_by_property_id,
    get_image_base64_by_id,
    search_properties
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("API")

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

@csrf_exempt
def process_image_api(request):
    """
    API endpoint to process an uploaded image
    
    Accepts a POST request with an image file, processes it using the image processor,
    and then passes the extracted information to the scraper.
    
    Returns:
        JsonResponse with the extracted information and scraping results
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are supported'}, status=405)
    
    try:
        # Check if we have a file in the request
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Read the image data
        image_data = image_file.read()
        
        # Initialize the image processor
        image_processor = LandRecordImageProcessor()
        
        # Process the image to extract property details
        logger.info("Processing image with LandRecordImageProcessor")
        property_details = image_processor.process_image_bytes(image_data)
        
        # Format the property details for the scraper
        formatted_property = {
            "survey_number": property_details.get("Survey Number", ""),
            "surnoc": property_details.get("Surnoc", "*"),
            "hissa": property_details.get("Hissa", ""),
            "village": {
                "name": property_details.get("Village", "")
            },
            "hobli": {
                "name": property_details.get("Hobli", "")
            },
            "taluk": {
                "name": property_details.get("Taluk", "")
            },
            "district": {
                "name": property_details.get("District", "")
            }
        }
        
        # Initialize the scraper
        scraper = RTCScraper()
        
        # Create a callback function to handle scraped images
        scraped_images = []
        
        def image_callback(image_data, metadata):
            # Convert image data to base64 for JSON response
            base64_image = base64.b64encode(image_data).decode('utf-8')
            scraped_images.append({
                "image": base64_image,
                "metadata": metadata
            })
        
        # Store property details in the database first
        logger.info("Storing property details in the database")
        property_id = store_property_details(property_details)
        
        # Prepare the response early - only include property_id and property_details
        logger.info(f"Preparing response with property_id: {property_id}")
        response = {
            "property_id": property_id,
            "property_details": property_details
        }
        
        # Run the scraper with the extracted property details in a separate thread
        # This allows us to return the response to the client immediately
        import threading
        
        def run_scraper():
            logger.info("Running RTCScraper with extracted property details in background thread")
            try:
                scraper.run(
                    property_details=formatted_property,
                    headless=True,  # Run in headless mode for API
                    image_callback=image_callback,
                    clear_documents=True  # Clear documents folder before scraping
                )
                logger.info("RTCScraper completed successfully")
                
                # Store scraped images in the database
                logger.info(f"Storing {len(scraped_images)} scraped images in the database")
                for i, img in enumerate(scraped_images):
                    try:
                        # Convert base64 back to binary
                        image_binary = base64.b64decode(img["image"])
                        
                        # Store the image
                        image_id = store_property_image(
                            property_id=property_id,
                            image_data=image_binary,
                            metadata=img["metadata"]
                        )
                        logger.info(f"Stored image {i+1}/{len(scraped_images)} with ID: {image_id}")
                    except Exception as e:
                        logger.error(f"Error storing image {i+1}/{len(scraped_images)}: {str(e)}")
                        # Continue with the next image
            except Exception as e:
                logger.error(f"Error running RTCScraper: {str(e)}")
        
        # Start the scraper in a background thread
        scraper_thread = threading.Thread(target=run_scraper)
        scraper_thread.daemon = True  # Allow the thread to be terminated when the main thread exits
        scraper_thread.start()
        
        logger.info("Returning JSON response")
        return JsonResponse(response)
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing request: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_property_api(request, property_id):
    """
    API endpoint to get property details by ID
    
    Args:
        request: HTTP request
        property_id: ID of the property to retrieve
        
    Returns:
        JsonResponse with property details and image metadata
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are supported'}, status=405)
    
    try:
        # Get property details
        property_details = get_property_details_by_id(property_id)
        
        if property_details is None:
            return JsonResponse({'error': 'Property not found'}, status=404)
        
        # Get property images
        property_images = get_property_images_by_property_id(property_id)
        
        # Prepare the response
        response = {
            "property_details": property_details,
            "images": property_images
        }
        
        return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"Error getting property details: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_image_api(request, image_id):
    """
    API endpoint to get image data by ID
    
    Args:
        request: HTTP request
        image_id: ID of the image to retrieve
        
    Returns:
        JsonResponse with image data and metadata
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are supported'}, status=405)
    
    try:
        # Get image data
        image_data = get_image_base64_by_id(image_id)
        
        if image_data is None:
            return JsonResponse({'error': 'Image not found'}, status=404)
        
        # Prepare the response
        response = {
            "image_url": image_data["image"],
            "metadata": image_data["metadata"]
        }
        
        return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"Error getting image data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def search_properties_api(request):
    """
    API endpoint to search for properties
    
    Args:
        request: HTTP request with search parameters
        
    Returns:
        JsonResponse with search results
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are supported'}, status=405)
    
    try:
        # Get search parameters from query string
        search_params = {}
        
        for param in ['survey_number', 'village', 'hobli', 'taluk', 'district', 'owner_name']:
            if param in request.GET:
                search_params[param] = request.GET[param]
        
        # Search for properties
        properties = search_properties(search_params)
        
        # Prepare the response
        response = {
            "properties": properties
        }
        
        return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"Error searching properties: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# URL patterns
urlpatterns = [
    path('api/process-image/', process_image_api, name='process_image_api'),
    path('api/property/<int:property_id>/', get_property_api, name='get_property_api'),
    path('api/image/<int:image_id>/', get_image_api, name='get_image_api'),
    path('api/search/', search_properties_api, name='search_properties_api'),
]

# WSGI application
application = get_wsgi_application()

if __name__ == "__main__":
    # Run the Django development server
    from django.core.management import execute_from_command_line
    import sys
    
    # Default port
    port = 8000
    
    # Check if port is specified in command line arguments
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
        sys.argv = [sys.argv[0]]  # Reset argv for Django
    
    sys.argv = [sys.argv[0], 'runserver', f'0.0.0.0:{port}']
    logger.info(f"Starting Django development server on port {port}")
    execute_from_command_line(sys.argv)