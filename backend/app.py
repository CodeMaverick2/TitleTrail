import os
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import path
from django.core.wsgi import get_wsgi_application
from django.conf.urls.static import static
import tempfile
import base64

# Import our custom modules - using relative imports since we're in the backend directory
from image_processor import LandRecordImageProcessor
from scraper import RTCScraper

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
settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    MIDDLEWARE=[
        'django.middleware.common.CommonMiddleware',
    ],
    INSTALLED_APPS=[
        'django.contrib.staticfiles',
    ],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        },
    ],
    STATIC_URL='/static/',
    ALLOWED_HOSTS=['*'],
)

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
        
        # Run the scraper with the extracted property details
        logger.info("Running RTCScraper with extracted property details")
        scraper.run(
            property_details=formatted_property,
            headless=True,  # Run in headless mode for API
            image_callback=image_callback
        )
        
        # Prepare the response
        response = {
            "property_details": property_details,
            "scraped_documents": [
                {
                    "metadata": img["metadata"],
                    "image_url": f"data:image/png;base64,{img['image']}"
                }
                for img in scraped_images
            ]
        }
        
        return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# URL patterns
urlpatterns = [
    path('api/process-image/', process_image_api, name='process_image_api'),
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