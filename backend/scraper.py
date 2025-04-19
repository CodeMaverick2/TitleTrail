import re
import time
import json
import logging
from typing import Dict, List, Tuple, Optional
from playwright.sync_api import Playwright, sync_playwright, Page, TimeoutError
import os
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("RTCScraper")

class RTCScraper:
    def __init__(self):
        self.base_url = "https://landrecords.karnataka.gov.in/Service2/"
        self.period_mapping = {}  # Maps period names to dropdown indices
        self.year_mapping = {}    # Maps years to dropdown indices
        self.period_to_year_mapping = {}  # Maps period values to valid year values
        
        # Default property details for testing
        self.default_property = {
            "survey_number": "22",
            "surnoc": "*",
            "hissa": "48", 
            "village": {
                "name": "Devanahalli",
                "index": "61"
            },
            "hobli": {
                "name": "Kasaba",
                "index": "2" 
            },
            "taluk": {
                "name": "Devenahalli",
                "index": "3"
            },
            "district": {
                "name": "Bangalore Rural",
                "index": "21"
            }
        }
        
        # Year range to scrape
        self.year_range = ["2012-13", "2013-14", "2014-15", "2015-16", 
                           "2016-17", "2017-18", "2018-19", "2019-20", "2020-21"]

        # Mapping of fiscal years to period text patterns
        self.fiscal_year_patterns = {
            "2012-13": ["2012-2013", "2012-13"],
            "2013-14": ["2013-2014", "2013-14"],
            "2014-15": ["2014-2015", "2014-15"],
            "2015-16": ["2015-2016", "2015-16"],
            "2016-17": ["2016-2017", "2016-17"],
            "2017-18": ["2017-2018", "2017-18"],
            "2018-19": ["2018-2019", "2018-19"],
            "2019-20": ["2019-2020", "2019-20"],
            "2020-21": ["2020-2021", "2020-21"]
        }

    def run(self, property_details=None, headless=False):
        """Main method to run the scraper"""
        if not property_details:
            property_details = self.default_property
            
        with sync_playwright() as playwright:
            try:
                self._run_workflow(playwright, property_details, headless)
            except Exception as e:
                logger.error(f"Scraping failed: {str(e)}")

    def _run_workflow(self, playwright: Playwright, property_details: Dict, headless: bool):
        """Run the scraper workflow"""
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        try:
            page = context.new_page()
            page.set_default_timeout(60000)  # 60 seconds timeout
            
            # Navigate to the website and fill initial form
            self._fill_initial_form(page, property_details)
            
            # Extract all dropdown options for period and year
            self._extract_and_save_dropdown_mappings(page)
            
            # Process each year in the range
            for year_period in self.year_range:
                try:
                    logger.info(f"Processing year period: {year_period}")
                    
                    # Find the right period and year values for this year range
                    period_value, year_value = self._get_values_for_year_period(year_period)
                    
                    if period_value and year_value:
                        # Get and save the document
                        self._get_document_for_period(page, year_period, property_details, period_value, year_value)
                    else:
                        logger.warning(f"Could not determine dropdown values for year period {year_period}")
                except Exception as e:
                    logger.error(f"Error processing year period {year_period}: {str(e)}")
                    # Take a screenshot of the error state
                    error_file = f"error_{year_period.replace('-', '_')}.png"
                    page.screenshot(path=error_file)
                    logger.info(f"Error screenshot saved to {error_file}")
                    # Continue with next year period
            
            logger.info("Scraping completed successfully")
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            # Take screenshot of error state if possible
            try:
                if 'page' in locals():
                    screenshot_path = "error_screenshot.png"
                    page.screenshot(path=screenshot_path)
                    logger.info(f"Error screenshot saved to {screenshot_path}")
            except:
                pass
            raise
        finally:
            context.close()
            browser.close()
    
    def _fill_initial_form(self, page: Page, property_details: Dict):
        """Fill the initial property search form"""
        # Navigate to the website
        page.goto(self.base_url)
        logger.info("Navigated to land records website")
        
        # Click "Old Year" button
        page.get_by_role("button", name="Old Year").click()
        logger.info("Clicked on 'Old Year' button")
        
        # Select District and wait for Taluk dropdown to be enabled
        logger.info(f"Selecting District: {property_details['district']['index']}")
        page.locator("#ctl00_MainContent_ddlODist").select_option(property_details["district"]["index"])
        
        # Wait for Taluk dropdown to be enabled
        logger.info("Waiting for Taluk dropdown to be enabled...")
        self._wait_for_enabled(page, "#ctl00_MainContent_ddlOTaluk")
        
        # Select Taluk and wait for Hobli dropdown to be enabled
        logger.info(f"Selecting Taluk: {property_details['taluk']['index']}")
        page.locator("#ctl00_MainContent_ddlOTaluk").select_option(property_details["taluk"]["index"])
        
        # Wait for Hobli dropdown to be enabled
        logger.info("Waiting for Hobli dropdown to be enabled...")
        self._wait_for_enabled(page, "#ctl00_MainContent_ddlOHobli")
        
        # Select Hobli and wait for Village dropdown to be enabled
        logger.info(f"Selecting Hobli: {property_details['hobli']['index']}")
        page.locator("#ctl00_MainContent_ddlOHobli").select_option(property_details["hobli"]["index"])
        
        # Wait for Village dropdown to be enabled
        logger.info("Waiting for Village dropdown to be enabled...")
        self._wait_for_enabled(page, "#ctl00_MainContent_ddlOVillage")
        
        # Select Village
        logger.info(f"Selecting Village: {property_details['village']['index']}")
        page.locator("#ctl00_MainContent_ddlOVillage").select_option(property_details["village"]["index"])
        
        # Enter survey number
        logger.info(f"Entering Survey Number: {property_details['survey_number']}")
        page.get_by_placeholder("Survey Number").click()
        page.get_by_placeholder("Survey Number").fill(property_details["survey_number"])
        
        # Click Go button twice (as per working example)
        logger.info("Clicking Go button")
        page.get_by_role("button", name="Go").click()
        time.sleep(2)  # Add a small delay between clicks
        page.get_by_role("button", name="Go").click()
        
        # Wait for Surnoc dropdown to be enabled
        logger.info("Waiting for Surnoc dropdown to be enabled...")
        self._wait_for_enabled(page, "#ctl00_MainContent_ddlOSurnocNo")
        
        # Select surnoc
        logger.info(f"Selecting Surnoc: {property_details['surnoc']}")
        page.locator("#ctl00_MainContent_ddlOSurnocNo").select_option(property_details["surnoc"])
        
        # Wait for Hissa dropdown to be enabled
        logger.info("Waiting for Hissa dropdown to be enabled...")
        self._wait_for_enabled(page, "#ctl00_MainContent_ddlOHissaNo")
        
        # Select hissa
        logger.info(f"Selecting Hissa: {property_details['hissa']}")
        page.locator("#ctl00_MainContent_ddlOHissaNo").select_option(property_details["hissa"])
    
    def _wait_for_enabled(self, page: Page, selector: str, timeout: int = 60):
        """Wait for an element to be enabled (not disabled)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not page.locator(selector).get_attribute("disabled"):
                logger.info(f"Element {selector} is now enabled")
                return True
            time.sleep(1)
        raise TimeoutError(f"Timeout waiting for element {selector} to be enabled")
    
    def _extract_and_save_dropdown_mappings(self, page: Page):
        """Extract all dropdown options for period and year, and their mappings"""
        try:
            logger.info("Extracting period dropdown values...")
            
            # Wait for Period dropdown to be enabled
            self._wait_for_enabled(page, "#ctl00_MainContent_ddlOPeriod")
            
            # Get all period options
            period_options = page.locator("#ctl00_MainContent_ddlOPeriod option").all()
            for option in period_options:
                value = option.get_attribute("value")
                if value and value != "0":  # Skip the default/blank option
                    text = option.text_content().strip()
                    self.period_mapping[text] = value
                    logger.debug(f"Found period option: {text} -> {value}")
            
            logger.info(f"Found {len(self.period_mapping)} period options")
            
            # For each period, get the corresponding year options
            for period_text, period_value in self.period_mapping.items():
                logger.info(f"Getting year options for period: {period_text}")
                
                # Select the period
                page.locator("#ctl00_MainContent_ddlOPeriod").select_option(period_value)
                page.wait_for_load_state("networkidle")
                time.sleep(1)  # Wait for year dropdown to update
                
                # Extract year options for this period
                year_options = page.locator("#ctl00_MainContent_ddlOYear option").all()
                
                period_years = {}
                for option in year_options:
                    value = option.get_attribute("value")
                    if value and value != "0":  # Skip the default/blank option
                        text = option.text_content().strip()
                        period_years[text] = value
                        self.year_mapping[text] = value
                        logger.debug(f"Found year option: {text} -> {value}")
                
                # Store the years available for this period
                self.period_to_year_mapping[period_value] = period_years
                logger.info(f"Found {len(period_years)} year options for period {period_text}")
            
            # Save all mappings to a JSON file for future reference
            mappings_data = {
                "period_mapping": self.period_mapping,
                "year_mapping": self.year_mapping,
                "period_to_year_mapping": self.period_to_year_mapping
            }
            
            with open("dropdown_mappings.json", "w") as f:
                json.dump(mappings_data, f, indent=2)
            
            logger.info("Saved dropdown mappings to dropdown_mappings.json")
            
        except Exception as e:
            logger.error(f"Error extracting dropdown mappings: {str(e)}")
            
            # If we already have mappings saved, try to load them
            if os.path.exists("dropdown_mappings.json"):
                with open("dropdown_mappings.json", "r") as f:
                    mappings = json.load(f)
                    self.period_mapping = mappings.get("period_mapping", {})
                    self.year_mapping = mappings.get("year_mapping", {})
                    self.period_to_year_mapping = mappings.get("period_to_year_mapping", {})
                logger.info("Loaded existing dropdown mappings from file")
            else:
                raise
    
    def _get_values_for_year_period(self, year_period: str) -> Tuple[str, str]:
        """Get the correct period and year dropdown values for a given year period"""
        # First check if we have saved mappings and try to use them
        if os.path.exists("dropdown_mappings.json") and not self.period_mapping:
            with open("dropdown_mappings.json", "r") as f:
                mappings = json.load(f)
                self.period_mapping = mappings.get("period_mapping", {})
                self.year_mapping = mappings.get("year_mapping", {})
                self.period_to_year_mapping = mappings.get("period_to_year_mapping", {})
        
        # Improved fallback: Use pattern matching to find the right period
        # Look for the fiscal year pattern in period text
        patterns = self.fiscal_year_patterns.get(year_period, [year_period])
        
        # First look for direct matches in period texts
        for pattern in patterns:
            for period_text, period_value in self.period_mapping.items():
                # Skip the "Select Period" option
                if period_text == "Select Period":
                    continue
                    
                if pattern in period_text:
                    # Found a period that contains our year pattern
                    if period_value in self.period_to_year_mapping:
                        years = self.period_to_year_mapping[period_value]
                        if years:
                            # Look for the best year match
                            best_year_value = None
                            for year_text, year_val in years.items():
                                # Skip "Select Year" option
                                if year_text == "Select Year":
                                    continue
                                    
                                # Look for specific matching patterns in year text
                                if (pattern in year_text) or (year_period in year_text):
                                    best_year_value = year_val
                                    break
                            
                            # If found a specific match, use it
                            if best_year_value:
                                logger.info(f"Pattern match found for {year_period}: Period={period_value}, Year={best_year_value}")
                                return period_value, best_year_value
                            
                            # Otherwise use the first available year
                            first_year_text = next((k for k in years.keys() if k != "Select Year"), None)
                            if first_year_text:
                                first_year = years[first_year_text]
                                logger.info(f"Period match found for {year_period}, using first available year: Period={period_value}, Year={first_year}")
                                return period_value, first_year
        
        # If no direct matches, try the more general period that likely contains all years
        general_periods = ["2001-08-25 00:00:00 To 2020-03-10 17:17:00"]
        for period_text in general_periods:
            if period_text in self.period_mapping:
                period_value = self.period_mapping[period_text]
                if period_value in self.period_to_year_mapping:
                    years = self.period_to_year_mapping[period_value]
                    
                    # Try to find a year that matches our fiscal year
                    for year_text, year_val in years.items():
                        if any(pattern in year_text for pattern in patterns):
                            logger.info(f"Found year match in general period for {year_period}: Period={period_value}, Year={year_val}")
                            return period_value, year_val
        
        # Final fallback - get any non-default period and year
        logger.warning(f"Could not find specific match for {year_period}, using fallback values")
        for period_value, years in self.period_to_year_mapping.items():
            if years and period_value != "0":
                for year_val in years.values():
                    if year_val != "0":
                        period_text = next((k for k, v in self.period_mapping.items() if v == period_value), "Unknown")
                        logger.info(f"Using fallback values for {year_period}: Period={period_text} (value={period_value}), Year={year_val}")
                        return period_value, year_val
        
        # Absolute last resort: use hard-coded values known to work
        logger.warning(f"No valid dropdown values found for {year_period}. Using hardcoded values.")
        return "15-164943", "113"  # Values known to work from example
    
    def _get_document_for_period(self, page: Page, period_name: str, property_details: Dict, 
                               period_value: str, year_value: str):
        """Get document for a specific period using direct values"""
        try:
            logger.info(f"Processing period: {period_name}, using period_value={period_value}, year_value={year_value}")
            
            # Wait for period dropdown to be enabled
            self._wait_for_enabled(page, "#ctl00_MainContent_ddlOPeriod")
            
            # Select period and wait for year dropdown to update
            page.locator("#ctl00_MainContent_ddlOPeriod").select_option(period_value)
            page.wait_for_load_state("networkidle")
            time.sleep(1)  # Wait for the year dropdown to update
            
            # Wait for year dropdown to be enabled
            self._wait_for_enabled(page, "#ctl00_MainContent_ddlOYear")
            
            # Select year
            page.locator("#ctl00_MainContent_ddlOYear").select_option(year_value)
            
            # Click Fetch details button
            logger.info("Clicking 'Fetch details' button")
            page.get_by_role("button", name="Fetch details").click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Wait for document to load
            
            # Check if document section exists
            if page.locator("div:nth-child(5) > div:nth-child(2)").count() == 0:
                logger.warning(f"Document section not found for period {period_name}")
                return
            
            # Click the document section (may need to click twice as per example)
            logger.info("Clicking on document section")
            page.locator("div:nth-child(5) > div:nth-child(2)").click()
            page.locator("div:nth-child(5) > div:nth-child(2)").click()
            
            # Check if View button exists
            view_button = page.get_by_role("button", name="View")
            if view_button.count() == 0:
                logger.warning(f"View button not found for period {period_name}")
                return
                
            # Open document in a new tab
            with page.expect_popup() as page1_info:
                logger.info("Clicking 'View' button to open document")
                view_button.click()
            
            document_page = page1_info.value
            document_page.wait_for_load_state("networkidle")
            time.sleep(2)  # Wait for document to fully render
            
            # Capture the document image
            image_data = self._capture_document_image(document_page)
            
            # Save the document
            self._save_document_data(period_name, property_details, image_data)
            
            # Close the document tab
            document_page.close()
            
            logger.info(f"Successfully processed document for period {period_name}")
            
        except Exception as e:
            logger.error(f"Error processing document for period {period_name}: {str(e)}")
            raise
    
    def _capture_document_image(self, page: Page) -> bytes:
        """Capture the document image from the page"""
        # Take a screenshot of the document
        document_element = page.locator("body")
        screenshot = document_element.screenshot()
        return screenshot
    
    def _save_document_data(self, period: str, property_details: Dict, image_data: bytes):
        """Save the document data"""
        # Create a directory for saving documents if it doesn't exist
        os.makedirs("documents", exist_ok=True)
        
        # Generate a filename based on property details and period
        filename = f"documents/{property_details['survey_number']}_{property_details['hissa']}_{period.replace('-', '_')}.png"
        
        # Save the image to file
        with open(filename, "wb") as f:
            f.write(image_data)
        
        logger.info(f"Saved document image to {filename}")


if __name__ == "__main__":
    scraper = RTCScraper()
    scraper.run(headless=False)  # Set to True for production use