import re
import time
import json
import logging
import os
import sys
from typing import Dict, List, Tuple, Optional
from playwright.sync_api import Playwright, sync_playwright, Page, TimeoutError
from datetime import datetime
import base64
from asgiref.sync import sync_to_async

# Import our utility modules
from dropdown_utils import DropdownHandler
from document_processor import DocumentProcessor

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO to WARNING to reduce verbosity
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("RTCScraper")
# Only log critical information
logger.setLevel(logging.WARNING)

class RTCScraper:
    def __init__(self):
        self.base_url = "https://landrecords.karnataka.gov.in/Service2/"
        self.period_mapping = {}  # Maps period names to dropdown indices
        self.year_mapping = {}    # Maps years to dropdown indices
        self.period_to_year_mapping = {}  # Maps period values to valid year values
        
        # Dropdown mappings for location fields
        self.dropdown_mappings = {
            "district": {},
            "taluk": {},
            "hobli": {},
            "village": {}
        }
        
        # Default property details for testing
        self.default_property = {
            "survey_number": "22",
            "surnoc": "*",
            "hissa": "48", 
            "village": {
                "name": "Devenahalli"
            },
            "hobli": {
                "name": "Kasaba"
            },
            "taluk": {
                "name": "Devanahalli"
            },
            "district": {
                "name": "Bangalore Rural"
            }
        }
        
        # Year range to scrape
        self.year_range = ["2012-13", "2013-14", "2014-15", "2015-16", 
                           "2016-17", "2017-18", "2018-19", "2019-20", "2020-21"]
        
        # Initialize utility classes
        self.dropdown_handler = DropdownHandler()
        self.document_processor = DocumentProcessor()

    def run(self, property_details=None, headless=False, image_callback=None):
        """
        Main method to run the scraper
        
        Args:
            property_details: Dictionary containing property details
            headless: Whether to run the browser in headless mode
            image_callback: Optional callback function to handle scraped images
        """
        if not property_details:
            property_details = self.default_property
            
        with sync_playwright() as playwright:
            try:
                self._run_workflow(playwright, property_details, headless, image_callback)
            except Exception as e:
                logger.error(f"Scraping failed: {str(e)}")

    def _run_workflow(self, playwright: Playwright, property_details: Dict, headless: bool, image_callback=None):
        """
        Run the scraper workflow
        
        Args:
            playwright: Playwright instance
            property_details: Dictionary containing property details
            headless: Whether to run the browser in headless mode
            image_callback: Optional callback function to handle scraped images
        """
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
                    period_value, year_value = self.document_processor.get_values_for_year_period(
                        year_period, 
                        self.period_mapping, 
                        self.year_mapping, 
                        self.period_to_year_mapping
                    )
                    
                    if period_value and year_value:
                        # Get and save the document
                        self.document_processor.get_document_for_period(
                            page, 
                            year_period, 
                            property_details, 
                            period_value, 
                            year_value,
                            image_callback
                        )
                    else:
                        logger.warning(f"Could not determine dropdown values for year period {year_period}")
                except Exception as e:
                    logger.error(f"Error processing year period {year_period}: {str(e)}")
                    # Continue with next year period
            
            logger.info("Scraping completed successfully")
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            raise
        finally:
            context.close()
            browser.close()
    
    def _fill_initial_form(self, page: Page, property_details: Dict):
        """Fill the initial property search form"""
        # Navigate to the website
        page.goto(self.base_url)
        
        # Click "Old Year" button
        page.get_by_role("button", name="Old Year").click()
        
        # ----- DISTRICT SELECTION -----
        # Wait for the district dropdown to be fully loaded
        district_selector = "#ctl00_MainContent_ddlODist"
        page.wait_for_selector(district_selector, state="visible")
        
        # Make sure the dropdown is enabled
        DropdownHandler.wait_for_enabled(page, district_selector)
        
        # Try to ensure the dropdown is populated by clicking on it
        try:
            page.locator(district_selector).click()
            time.sleep(1)  # Give time for options to appear
        except:
            pass
            
        # Get all district options
        district_options = DropdownHandler.get_dropdown_options(page, district_selector)
        self.dropdown_mappings["district"] = district_options
        
        # Find the best match for the requested district
        district_name = property_details["district"]["name"]
        district_value = DropdownHandler.find_best_match(district_name, district_options)
        
        if not district_value:
            raise ValueError(f"Could not select district '{district_name}'")
        
        # Select the district
        page.locator(district_selector).select_option(district_value)
        
        # ----- TALUK SELECTION -----
        # Wait for Taluk dropdown to be enabled
        taluk_selector = "#ctl00_MainContent_ddlOTaluk"
        DropdownHandler.wait_for_enabled(page, taluk_selector)
        
        # Get all taluk options
        taluk_options = DropdownHandler.get_dropdown_options(page, taluk_selector)
        self.dropdown_mappings["taluk"] = taluk_options
        
        # Find the best match for the requested taluk
        taluk_name = property_details["taluk"]["name"]
        taluk_value = DropdownHandler.find_best_match(taluk_name, taluk_options)
        
        # Select the taluk
        page.locator(taluk_selector).select_option(taluk_value)
        
        # ----- HOBLI SELECTION -----
        # Wait for Hobli dropdown to be enabled
        hobli_selector = "#ctl00_MainContent_ddlOHobli"
        DropdownHandler.wait_for_enabled(page, hobli_selector)
        
        # Get all hobli options
        hobli_options = DropdownHandler.get_dropdown_options(page, hobli_selector)
        self.dropdown_mappings["hobli"] = hobli_options
        
        # Find the best match for the requested hobli
        hobli_name = property_details["hobli"]["name"]
        hobli_value = DropdownHandler.find_best_match(hobli_name, hobli_options)
        
        # Select the hobli
        page.locator(hobli_selector).select_option(hobli_value)
        
        # ----- VILLAGE SELECTION -----
        # Wait for Village dropdown to be enabled
        village_selector = "#ctl00_MainContent_ddlOVillage"
        DropdownHandler.wait_for_enabled(page, village_selector)
        
        # Get all village options
        village_options = DropdownHandler.get_dropdown_options(page, village_selector)
        self.dropdown_mappings["village"] = village_options
        
        # Find the best match for the requested village
        village_name = property_details["village"]["name"]
        village_value = DropdownHandler.find_best_match(village_name, village_options)
        
        # Select the village
        page.locator(village_selector).select_option(village_value)
        
        # Enter survey number
        page.get_by_placeholder("Survey Number").click()
        page.get_by_placeholder("Survey Number").fill(property_details["survey_number"])
        
        # Click Go button twice (as per working example)
        page.get_by_role("button", name="Go").click()
        time.sleep(2)  # Add a small delay between clicks
        page.get_by_role("button", name="Go").click()
        
        # ----- SURNOC SELECTION -----
        # Wait for Surnoc dropdown to be enabled
        surnoc_selector = "#ctl00_MainContent_ddlOSurnocNo"
        DropdownHandler.wait_for_enabled(page, surnoc_selector)
        
        # Select surnoc (using the provided value directly)
        page.locator(surnoc_selector).select_option(property_details["surnoc"])
        
        # ----- HISSA SELECTION -----
        # Wait for Hissa dropdown to be enabled
        hissa_selector = "#ctl00_MainContent_ddlOHissaNo"
        DropdownHandler.wait_for_enabled(page, hissa_selector)
        
        # Get all available Hissa options
        try:
            # Use the specialized Hissa selection method
            DropdownHandler.select_hissa(page, hissa_selector, property_details["hissa"])
                
        except Exception as e:
            logger.error(f"Error selecting Hissa: {str(e)}")
            raise
    
    def _extract_and_save_dropdown_mappings(self, page: Page):
        """Extract all dropdown options for period and year, and their mappings"""
        try:
            # Wait for Period dropdown to be enabled
            period_selector = "#ctl00_MainContent_ddlOPeriod"
            DropdownHandler.wait_for_enabled(page, period_selector)
            
            # Get all period options using our helper method
            self.period_mapping = DropdownHandler.get_dropdown_options(page, period_selector)
            
            # For each period, get the corresponding year options
            for period_text, period_value in self.period_mapping.items():
                # Select the period
                page.locator(period_selector).select_option(period_value)
                page.wait_for_load_state("networkidle")
                time.sleep(1)  # Wait for year dropdown to update
                
                # Extract year options for this period using our helper method
                year_selector = "#ctl00_MainContent_ddlOYear"
                period_years = DropdownHandler.get_dropdown_options(page, year_selector)
                
                # Update the year mapping with all years
                self.year_mapping.update(period_years)
                
                # Store the years available for this period
                self.period_to_year_mapping[period_value] = period_years
            
        except Exception as e:
            logger.error(f"Error extracting dropdown mappings: {str(e)}")
            raise

# Main entry point
if __name__ == "__main__":
    scrapper = RTCScraper()
    scrapper.run(headless=False)