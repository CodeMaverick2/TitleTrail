import os
import sys
import json
import base64
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import the scraper and models
from models import Property, RTC, ScrapingLog, DropdownMapping
from scraper import RTCScraper

class RTCScraperIntegration:
    def __init__(self):
        self.scraper = RTCScraper()
        
    def run_scraper(self, property_data=None, headless=True):
        """Run the scraper and save results to database"""
        # If property data is provided, create or update the Property record
        property_obj = None
        if property_data:
            property_obj, created = Property.objects.get_or_create(
                survey_number=property_data["survey_number"],
                hissa=property_data["hissa"],
                village=property_data["village"]["name"],
                hobli=property_data["hobli"]["name"],
                taluk=property_data["taluk"]["name"],
                district=property_data["district"]["name"],
                defaults={
                    "surnoc": property_data["surnoc"] if property_data["surnoc"] != "*" else None
                }
            )
            
            if created:
                print(f"Created new Property record: {property_obj}")
            else:
                print(f"Using existing Property record: {property_obj}")
        
        # Run the scraper to collect documents
        self.scraper.run(property_data, headless=headless)
        
        # After scraper runs, process the downloaded documents
        if property_obj:
            self._process_documents(property_obj)
            
        # Save dropdown mappings to database
        self._save_dropdown_mappings()
            
    def _process_documents(self, property_obj):
        """Process downloaded documents and save to database"""
        documents_dir = Path("documents")
        if not documents_dir.exists():
            print("No documents directory found")
            return
            
        for file_path in documents_dir.glob(f"{property_obj.survey_number}_{property_obj.hissa}_*.png"):
            try:
                # Parse period and year from filename
                filename = file_path.name
                period_year = filename.split('_')[-1].replace('.png', '').replace('_', '-')
                
                # Read the image file
                with open(file_path, "rb") as f:
                    image_data = f.read()
                
                # Create or update RTC record
                rtc, created = RTC.objects.update_or_create(
                    property=property_obj,
                    period=period_year[:7],  # e.g., "2012-13"
                    year=period_year[-2:],   # e.g., "13"
                    defaults={
                        "document_image": image_data,
                    }
                )
                
                # Create successful scraping log
                ScrapingLog.objects.create(
                    property=property_obj,
                    period=rtc.period,
                    year=rtc.year,
                    status="Success",
                )
                
                print(f"{'Created' if created else 'Updated'} RTC record for {period_year}")
                
            except Exception as e:
                print(f"Error processing document {file_path}: {str(e)}")
                # Create failed scraping log
                ScrapingLog.objects.create(
                    property=property_obj,
                    period=period_year[:7] if 'period_year' in locals() else "Unknown",
                    year=period_year[-2:] if 'period_year' in locals() else "Unknown",
                    status="Failed",
                    error_message=str(e)
                )
    
    def _save_dropdown_mappings(self):
        """Save dropdown mappings to database"""
        mapping_file = Path("dropdown_mappings.json")
        if not mapping_file.exists():
            print("No dropdown mappings file found")
            return
            
        try:
            with open(mapping_file, "r") as f:
                mappings = json.load(f)
                
            # Process period mappings
            for period_text, value in mappings.get("period_mapping", {}).items():
                DropdownMapping.objects.update_or_create(
                    dropdown_type="Period",
                    dropdown_value=period_text,
                    defaults={
                        "mapped_index": int(value)
                    }
                )
                
            # Process year mappings
            for year_text, value in mappings.get("year_mapping", {}).items():
                # Find the associated period if applicable
                period_mapping = None
                
                DropdownMapping.objects.update_or_create(
                    dropdown_type="Year",
                    dropdown_value=year_text,
                    defaults={
                        "mapped_index": int(value),
                        "period": period_mapping
                    }
                )
                
            print("Saved dropdown mappings to database")
                
        except Exception as e:
            print(f"Error saving dropdown mappings: {str(e)}")


def run_scraper_integration():
    """Function to run the scraper integration from command line"""
    integration = RTCScraperIntegration()
    
    # Use the default property data from RTCScraper
    property_data = RTCScraper().default_property
    
    # Run the scraper and save results to database
    integration.run_scraper(property_data, headless=False)
    
    print("Scraper integration completed")


if __name__ == "__main__":
    run_scraper_integration()