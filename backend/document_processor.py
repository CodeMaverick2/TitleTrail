import os
import time
import base64
import logging
import re
from typing import Dict, List, Tuple, Optional, Any, Callable
from playwright.sync_api import Page, TimeoutError
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DocumentProcessor")

class DocumentProcessor:
    """
    Utility class to process and save documents from the land records website
    """
    
    def __init__(self):
        # Create documents directory if it doesn't exist
        self.documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
        os.makedirs(self.documents_dir, exist_ok=True)
    
    def get_values_for_year_period(
        self, 
        year_period: str, 
        period_mapping: Dict[str, str],
        year_mapping: Dict[str, str],
        period_to_year_mapping: Dict[str, Dict[str, str]]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Find the appropriate period and year dropdown values for a given year period
        
        Args:
            year_period: The year period string (e.g., "2018-19")
            period_mapping: Dictionary mapping period text to dropdown values
            year_mapping: Dictionary mapping year text to dropdown values
            period_to_year_mapping: Dictionary mapping period values to available year values
            
        Returns:
            Tuple of (period_value, year_value) or (None, None) if not found
        """
        try:
            # First, try to find an exact match in the year mapping
            if year_period in year_mapping:
                # Find which period this year belongs to
                for period_value, years in period_to_year_mapping.items():
                    if year_period in years:
                        return period_value, year_mapping[year_period]
            
            # If no exact match, try to find a period that contains this year
            for period_text, period_value in period_mapping.items():
                # Check if the period text contains our year period
                if year_period in period_text:
                    # Find the corresponding year value
                    years = period_to_year_mapping.get(period_value, {})
                    for year_text, year_value in years.items():
                        if year_period in year_text:
                            return period_value, year_value
            
            # If still no match, try to parse the year period and find the closest match
            start_year = year_period.split('-')[0]
            for period_text, period_value in period_mapping.items():
                if start_year in period_text:
                    # Find the corresponding year value
                    years = period_to_year_mapping.get(period_value, {})
                    for year_text, year_value in years.items():
                        if start_year in year_text:
                            return period_value, year_value
            
            # No match found
            logger.warning(f"Could not find dropdown values for year period {year_period}")
            return None, None
            
        except Exception as e:
            logger.error(f"Error finding values for year period {year_period}: {str(e)}")
            return None, None
    
    def get_document_for_period(
        self, 
        page: Page, 
        year_period: str, 
        property_details: Dict[str, Any],
        period_value: str,
        year_value: str,
        image_callback: Optional[Callable] = None
    ):
        """
        Get and save the document for a specific period and year
        
        Args:
            page: Playwright page object
            year_period: The year period string (e.g., "2018-19")
            property_details: Dictionary containing property details
            period_value: The period dropdown value to select
            year_value: The year dropdown value to select
            image_callback: Optional callback function to handle the image data
        """
        try:
            # Select the period
            period_selector = "#ctl00_MainContent_ddlOPeriod"
            page.locator(period_selector).select_option(period_value)
            time.sleep(1)  # Wait for year dropdown to update
            
            # Select the year
            year_selector = "#ctl00_MainContent_ddlOYear"
            page.locator(year_selector).select_option(year_value)
            
            # Click the "Fetch details" button first
            try:
                page.get_by_role("button", name="Fetch details").click()
                logger.info(f"Clicked 'Fetch details' button for {year_period}")
                time.sleep(2)  # Wait for the details to load
            except Exception as e:
                logger.warning(f"Could not click 'Fetch details' button: {str(e)}")
            
            # Open the document in a new tab by clicking the "View" button
            try:
                with page.expect_popup() as page1_info:
                    page.get_by_role("button", name="View").click()
                    logger.info(f"Clicked 'View' button for {year_period}")
                
                # Get the new page/tab
                document_page = page1_info.value
                
                # Wait for the page to load
                document_page.wait_for_load_state("networkidle", timeout=30000)
                
                # Take a screenshot of the document
                filename = self._generate_filename(property_details, year_period)
                filepath = os.path.join(self.documents_dir, filename)
                
                # Take the screenshot and save it
                document_page.screenshot(path=filepath)
                logger.info(f"Saved screenshot for {year_period} to {filepath}")
                
                # Create metadata for the image
                metadata = {
                    "year_period": year_period,
                    "survey_number": property_details.get("survey_number", ""),
                    "surnoc": property_details.get("surnoc", ""),
                    "hissa": property_details.get("hissa", ""),
                    "village": property_details.get("village", {}).get("name", ""),
                    "hobli": property_details.get("hobli", {}).get("name", ""),
                    "taluk": property_details.get("taluk", {}).get("name", ""),
                    "district": property_details.get("district", {}).get("name", ""),
                    "timestamp": datetime.now().isoformat(),
                    "url": document_page.url
                }
                
                # If a callback is provided, read the file and call the callback
                if image_callback:
                    with open(filepath, "rb") as f:
                        image_data = f.read()
                    image_callback(image_data, metadata)
                
                # Close the document page/tab
                document_page.close()
                
            except TimeoutError:
                logger.warning(f"Timeout waiting for document for {year_period}")
            except Exception as e:
                logger.error(f"Error capturing document for {year_period}: {str(e)}")
            
            # Wait for the main page to be active again
            page.wait_for_selector(period_selector, state="visible", timeout=10000)
            
        except Exception as e:
            logger.error(f"Error getting document for {year_period}: {str(e)}")
            # Try to go back to the search page if needed
            try:
                # Check if we need to go back
                if page.locator(period_selector).count() == 0:
                    page.go_back()
                    page.wait_for_selector(period_selector, state="visible", timeout=10000)
            except:
                pass
    
    def _generate_filename(self, property_details: Dict[str, Any], year_period: str) -> str:
        """
        Generate a filename for the document based on property details and year period
        
        Args:
            property_details: Dictionary containing property details
            year_period: The year period string (e.g., "2018-19")
            
        Returns:
            A filename string
        """
        # Clean up values for filename
        survey = property_details.get("survey_number", "").replace("/", "-")
        surnoc = property_details.get("surnoc", "").replace("*", "star")
        hissa = property_details.get("hissa", "").replace("/", "-")
        village = property_details.get("village", {}).get("name", "").replace(" ", "_")
        
        # Generate a timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Create the filename - using .png extension for screenshots
        filename = f"RTC_{village}_{survey}_{surnoc}_{hissa}_{year_period}_{timestamp}.png"
        
        # Remove any invalid characters
        filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
        
        return filename