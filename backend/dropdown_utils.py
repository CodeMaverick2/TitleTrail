import logging
import time
from typing import Dict, List, Tuple, Optional
from playwright.sync_api import Page, TimeoutError

logger = logging.getLogger("RTCScraper")

class DropdownHandler:
    """
    Utility class for handling dropdown selections and mappings
    """
    
    @staticmethod
    def wait_for_enabled(page: Page, selector: str, timeout: int = 60):
        """
        Wait for an element to be enabled (not disabled) and populated with options
        
        Args:
            page: The Playwright page object
            selector: CSS selector for the element
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if the element becomes enabled within the timeout
            
        Raises:
            TimeoutError: If the element doesn't become enabled within the timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if element is enabled
            if not page.locator(selector).get_attribute("disabled"):
                # Also check if it has options (for dropdowns)
                if selector.endswith("option"):
                    # Already a specific option selector
                    options_count = page.locator(selector).count()
                else:
                    # General dropdown selector, check for options
                    options_count = page.locator(f"{selector} option").count()
                
                if options_count > 1:  # More than just the default option
                    logger.info(f"Element {selector} is now enabled with {options_count} options")
                    return True
                else:
                    logger.debug(f"Element {selector} is enabled but has only {options_count} options, waiting for more...")
            
            # Try clicking on the dropdown to ensure it's populated
            try:
                page.locator(selector).click()
            except:
                pass
                
            time.sleep(1)
        
        raise TimeoutError(f"Timeout waiting for element {selector} to be enabled with options")
    
    @staticmethod
    def get_dropdown_options(page: Page, selector: str) -> Dict[str, str]:
        """
        Extract all options from a dropdown and return a mapping of text to value
        
        Args:
            page: The Playwright page object
            selector: CSS selector for the dropdown element
            
        Returns:
            Dictionary mapping option text to option value
        """
        # Wait for the dropdown to have options
        max_retries = 3
        retry_count = 0
        options_map = {}
        
        while retry_count < max_retries and not options_map:
            # Wait a moment for the dropdown to populate
            page.wait_for_selector(selector, state="attached")
            time.sleep(1)  # Give time for options to load
            
            options = page.locator(f"{selector} option").all()
            
            for option in options:
                value = option.get_attribute("value")
                text = option.text_content().strip() if option.text_content() else ""
                
                if value and value != "0":  # Skip the default/blank option
                    options_map[text] = value
            
            if not options_map:
                logger.warning(f"No options found for {selector} on attempt {retry_count+1}, retrying...")
                retry_count += 1
                # Try clicking on the dropdown to ensure it's populated
                try:
                    page.locator(selector).click()
                    time.sleep(1)
                except:
                    pass
        
        return options_map
    
    @staticmethod
    def find_best_match(target_name: str, options_map: Dict[str, str]) -> str:
        """
        Find the best matching option value for a given name
        
        Args:
            target_name: The name to match against dropdown options
            options_map: Dictionary mapping option text to option value
            
        Returns:
            The value of the best matching option, or None if no match found
        """
        if not options_map:
            logger.warning(f"No options available to match against '{target_name}'")
            return None
        
        # Create a normalized version of the options map for matching
        normalized_options = {}
        for text, value in options_map.items():
            # Store both the original text and a normalized version (lowercase, no extra spaces)
            normalized_text = text.lower().strip()
            normalized_options[normalized_text] = (text, value)
            
            # Also store a version with common words removed for better matching
            simplified_text = normalized_text
            for word in ["district", "taluk", "hobli", "village"]:
                simplified_text = simplified_text.replace(word, "").strip()
            if simplified_text and simplified_text != normalized_text:
                normalized_options[simplified_text] = (text, value)
        
        # Normalize the target name
        target_lower = target_name.lower().strip()
        
        # 1. Try exact match (case insensitive)
        if target_lower in normalized_options:
            original_text, value = normalized_options[target_lower]
            return value
        
        # 2. Try simplified target (remove common words)
        simplified_target = target_lower
        for word in ["district", "taluk", "hobli", "village"]:
            simplified_target = simplified_target.replace(word, "").strip()
        
        if simplified_target in normalized_options:
            original_text, value = normalized_options[simplified_target]
            return value
        
        # 3. Try contains match (target in option or option in target)
        best_match = None
        best_match_length = 0
        
        for norm_text, (original_text, value) in normalized_options.items():
            # Check if one string contains the other
            if target_lower in norm_text or norm_text in target_lower:
                # Prefer longer matches as they're likely more specific
                match_length = len(norm_text)
                if match_length > best_match_length:
                    best_match = (original_text, value)
                    best_match_length = match_length
        
        if best_match:
            original_text, value = best_match
            return value
        
        # 4. Try word-by-word matching
        target_words = set(target_lower.split())
        best_match = None
        best_match_score = 0
        
        for norm_text, (original_text, value) in normalized_options.items():
            option_words = set(norm_text.split())
            # Count how many words match
            common_words = target_words.intersection(option_words)
            score = len(common_words)
            if score > best_match_score:
                best_match = (original_text, value)
                best_match_score = score
        
        if best_match and best_match_score > 0:
            original_text, value = best_match
            return value
        
        # 5. If no match found, return the first option as fallback
        if options_map:
            first_text = next(iter(options_map.keys()))
            first_value = options_map[first_text]
            logger.warning(f"No match found for '{target_name}'. Using first option: {first_text}")
            return first_value
        
        return None
    
    @staticmethod
    def select_hissa(page: Page, hissa_selector: str, requested_hissa: str):
        """
        Select the appropriate Hissa option from the dropdown
        
        Args:
            page: The Playwright page object
            hissa_selector: CSS selector for the Hissa dropdown
            requested_hissa: The requested Hissa value
            
        Returns:
            The selected Hissa value
        """
        # Get all dropdown options
        all_options = page.locator(f"{hissa_selector} option").all()
        valid_options = []
        
        for option in all_options:
            value = option.get_attribute("value")
            text = option.text_content().strip() if option.text_content() else ""
            
            # Skip the default/blank option and "Select Hissa" option
            if value and value != "0" and "select" not in text.lower():
                valid_options.append({"text": text, "value": value})
        
        selected_value = None
        
        # First try exact match
        for option in valid_options:
            if option["text"] == requested_hissa or option["value"] == requested_hissa:
                selected_value = option["value"]
                break
        
        # Special case for Hissa "1" - check for "1A" if "1" is not available
        if not selected_value and requested_hissa == "1":
            for option in valid_options:
                if option["text"] == "1A" or option["value"] == "1A":
                    selected_value = option["value"]
                    break
        
        # If still no match, use the first option
        if not selected_value and valid_options:
            selected_value = valid_options[0]["value"]
        
        # Select the Hissa
        if selected_value:
            page.locator(hissa_selector).select_option(selected_value)
        else:
            logger.warning("No valid Hissa options found")
            
        return selected_value