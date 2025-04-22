import os
import base64
import logging
import re
from typing import Dict, Optional, List, Any
from openai import OpenAI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ImageProcessor")

class LandRecordImageProcessor:
    """
    Process land record images using OpenAI's vision capabilities to extract
    structured information like survey number, hissa, village, etc.
    """
    
    def __init__(self):
        # Initialize OpenAI client using environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in your environment variables.")
        
        # Initialize the client which will use the API key from environment
        self.client = OpenAI()
        logger.info("OpenAI client initialized using environment variables")
        
        # Define the expected fields to extract
        self.expected_fields = [
            "Survey Number",
            "Surnoc",
            "Hissa",
            "Village",
            "Hobli",
            "Taluk",
            "District",
            "Owner Name",
            "Owner Details"
        ]
        
        # Known district mappings for common taluks
        self.taluk_to_district = {
            "Devanahalli": "Bangalore Rural",
            "Doddaballapura": "Bangalore Rural",
            "Nelamangala": "Bangalore Rural",
            "Hoskote": "Bangalore Rural",
            "Bangalore North": "Bangalore Urban",
            "Bangalore South": "Bangalore Urban",
            "Bangalore East": "Bangalore Urban",
            "Anekal": "Bangalore Urban",
            "Mysore": "Mysore",
            "Mandya": "Mandya",
            "Tumkur": "Tumkur",
            "Hassan": "Hassan",
            "Mangalore": "Dakshina Kannada",
            "Udupi": "Udupi",
            "Hubli": "Dharwad",
            "Dharwad": "Dharwad",
            "Belgaum": "Belgaum",
            "Gulbarga": "Gulbarga",
            "Bijapur": "Bijapur",
            "Bellary": "Bellary",
            "Raichur": "Raichur",
            "Shimoga": "Shimoga",
            "Chitradurga": "Chitradurga",
            "Davangere": "Davangere",
            "Kolar": "Kolar",
            "Chikkaballapur": "Chikkaballapur",
            "Ramanagara": "Ramanagara",
            "Chamarajanagar": "Chamarajanagar",
            "Kodagu": "Kodagu",
            "Chikmagalur": "Chikmagalur",
            "Haveri": "Haveri",
            "Gadag": "Gadag",
            "Koppal": "Koppal",
            "Bagalkot": "Bagalkot",
            "Bidar": "Bidar",
            "Yadgir": "Yadgir"
        }
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode an image file to base64 for API submission
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    def encode_image_bytes(self, image_bytes: bytes) -> str:
        """
        Encode image bytes to base64 for API submission
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Base64 encoded string of the image
        """
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image to extract land record details
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            # Encode the image
            base64_image = self.encode_image(image_path)
            
            # Process the image using the common method
            return self._process_image_with_base64(base64_image)
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            raise
            
    def process_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process image bytes to extract land record details
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            # Encode the image
            base64_image = self.encode_image_bytes(image_bytes)
            
            # Process the image using the common method
            return self._process_image_with_base64(base64_image)
        except Exception as e:
            logger.error(f"Error processing image bytes: {str(e)}")
            raise
            
    def _process_image_with_base64(self, base64_image: str) -> Dict[str, Any]:
        """
        Process a base64 encoded image to extract land record details
        
        Args:
            base64_image: Base64 encoded image
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            
            # Prepare the prompt for OpenAI
            prompt = f"""
            You are an expert in analyzing land record documents (RTC - Record of Rights, Tenancy and Crops) from Karnataka, India.
            
            Please carefully examine this Village Account Form No. 2 (RTC) document and extract the following specific information:
            
            1. Survey Number: Look for "Survey No." or "ಸರ್ವೆ ನಂ"
            2. Surnoc: This may appear as "Surnoc No." (might be marked with an asterisk "*"). If not found, set it to "*".
            3. Hissa: Look for "Hissa No." or "Sub-division Number" which is a subdivision number
            4. Village: The name of the village where the land is located
            5. Hobli: The administrative subdivision (look for "Hobli" or "ಹೋಬಳಿ")
            6. Taluk: The larger administrative division (also called Taluka or "ತಾಲೂಕು")
            7. District: The district name (e.g., "Bangalore", "Bangalore Rural")
            8. Owner Name: The name(s) of the landowner(s) - there may be multiple owners listed
            9. Owner Details: Additional information about the owners such as father's/husband's name, relationship, mutation register references (MR numbers), etc.
            
            IMPORTANT INSTRUCTIONS:
            1. First translate any Kannada text to English, then extract the information.
            2. For Owner Name, list all owners if multiple are present, separated by commas.
            3. DO NOT include any asterisks, bullets, or other formatting characters in your response.
            4. DO NOT include any notes or explanations in your field values.
            5. If any field is not visible or cannot be determined in the document, indicate with 'Not found' or 'N/A'.
            6. If the District is not explicitly mentioned but you know the Village and Taluk, please infer the District based on your knowledge (e.g., Devanahalli Taluk is in Bangalore Rural District).
            
            The document may be in Kannada or English or a mix of both. Look for tables with owner information, which typically includes names and shares.
            
            Pay special attention to the "Khatedar" or "ಖಾತೆದಾರ" section which lists the landowners.
            
            Format your response as a structured list with field names followed by the extracted values.
            For example:
            Survey Number: 22
            Surnoc: *
            Hissa: 1
            Village: Devenahalli
            Hobli: Kasaba
            Taluk: Devanahalli
            District: Bangalore Rural
            Owner Name: John Doe, Jane Smith
            Owner Details: John Doe (Father: James Doe, Share: 50%), Jane Smith (Husband: Mike Smith, Share: 50%)
            """
            
            # Call OpenAI API with vision capabilities
            logger.info(f"Sending image to OpenAI for analysis")
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use the current vision-capable model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # Request high detail for document analysis
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Extract and parse the response
            result = self._parse_response(response.choices[0].message.content)
            
            # Post-process the result to infer missing information
            result = self._post_process_result(result)
            
            logger.info(f"Successfully extracted information from image: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing image with base64: {str(e)}")
            raise
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the text response from OpenAI into a structured dictionary
        
        Args:
            response_text: The text response from OpenAI
            
        Returns:
            Dictionary with extracted fields
        """
        # Initialize result with default values
        result = {field: "N/A" for field in self.expected_fields}
        
        # Log the raw response for debugging
        logger.debug(f"Raw response from OpenAI: {response_text}")
        
        # Enhanced parsing logic
        lines = response_text.strip().split('\n')
        current_field = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for numbered list items (e.g., "1. Survey Number: 22")
            numbered_match = re.match(r'^\d+\.\s+(.+)$', line)
            if numbered_match:
                line = numbered_match.group(1)
            
            # Check for field: value format
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip()
                value = parts[1].strip()
                
                # Remove any leading numbers (e.g., "1. Survey Number")
                key = re.sub(r'^\d+\.\s+', '', key)
                
                # Map to our expected fields
                matched = False
                for field in self.expected_fields:
                    # Check for exact match or if the field name is contained in the key
                    if field.lower() == key.lower() or field.lower() in key.lower():
                        # Clean up the value - remove any ** or other formatting
                        value = re.sub(r'^\*+\s*|\s*\*+$', '', value)
                        result[field] = value
                        current_field = field
                        matched = True
                        break
                
                # If no match found but we have a current field, this might be additional info
                if not matched and current_field and current_field == "Owner Details":
                    result[current_field] += " " + line
            
            # Handle cases where the value might be on the next line
            elif current_field:
                result[current_field] += " " + line
        
        # Special handling for common field names
        field_mappings = {
            "survey no": "Survey Number",
            "survey": "Survey Number",
            "surnoc no": "Surnoc",
            "hissa no": "Hissa",
            "owner": "Owner Name",
            "owner information": "Owner Details",
            "owner details": "Owner Details"
        }
        
        # Check for alternative field names
        for alt_name, field_name in field_mappings.items():
            for key in list(result.keys()):
                if alt_name.lower() in key.lower() and key != field_name:
                    if result[key] != "N/A" and result[field_name] == "N/A":
                        result[field_name] = result[key]
        
        # Clean up any remaining formatting characters or notes
        for field in result:
            if result[field] != "N/A":
                # Remove any leading/trailing asterisks or other formatting
                result[field] = re.sub(r'^\*+\s*|\s*\*+$', '', result[field])
                # Remove any notes like "If any additional information is needed..."
                result[field] = re.sub(r'If any additional information.*$', '', result[field], flags=re.IGNORECASE).strip()
        
        # VALIDATION: Check if values are actually property details and not instructions
        instruction_keywords = ["look for", "find", "identify", "locate", "extract", "this may appear", "this is often"]
        for field in result:
            # Check if the value looks like an instruction (contains instruction keywords)
            if any(keyword in result[field].lower() for keyword in instruction_keywords):
                # If it looks like an instruction, replace with N/A
                logger.warning(f"Value for {field} looks like an instruction: '{result[field]}'. Replacing with 'N/A'.")
                result[field] = "N/A"
            
            # Limit the length to avoid database column size issues
            if field in ["Survey Number", "Surnoc", "Hissa"] and len(result[field]) > 45:
                logger.warning(f"Value for {field} exceeds 45 characters. Truncating.")
                result[field] = result[field][:45]
            elif field in ["Village", "Hobli", "Taluk", "District"] and len(result[field]) > 90:
                logger.warning(f"Value for {field} exceeds 90 characters. Truncating.")
                result[field] = result[field][:90]
        
        return result
    
    def _post_process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process the result to infer missing information
        
        Args:
            result: The parsed result from OpenAI
            
        Returns:
            Enhanced result with inferred information
        """
        # Infer district from taluk if district is missing
        if result["District"] == "N/A" or result["District"] == "Not found":
            taluk = result["Taluk"]
            if taluk != "N/A" and taluk != "Not found":
                # Clean up taluk name for matching
                taluk_clean = taluk.split('(')[0].strip()
                
                # Check if we have a district mapping for this taluk
                if taluk_clean in self.taluk_to_district:
                    result["District"] = self.taluk_to_district[taluk_clean]
                    logger.info(f"Inferred district '{result['District']}' from taluk '{taluk_clean}'")
        
        # Set default value for Surnoc if it's empty or not found
        if result["Surnoc"] == "N/A" or result["Surnoc"] == "Not found" or result["Surnoc"] == "":
            result["Surnoc"] = "*"
            logger.info("Set default value '*' for Surnoc")
        
        # Correct common spelling errors in place names
        if result["Village"] == "Devanahalli" and result["Taluk"] == "Devanahalli":
            # If both are the same, the village is likely Devenahalli (with an 'e')
            result["Village"] = "Devenahalli"
            logger.info(f"Corrected Village name from 'Devanahalli' to 'Devenahalli'")
        
        # If Taluk is Devenahalli (with an 'e'), correct it to Devanahalli (with an 'a')
        if result["Taluk"] == "Devenahalli":
            result["Taluk"] = "Devanahalli"
            logger.info(f"Corrected Taluk name from 'Devenahalli' to 'Devanahalli'")
        
        return result

    def process_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process image data directly from bytes
        
        Args:
            image_bytes: Raw image data as bytes
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            # Encode the image bytes
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Prepare the prompt for OpenAI
            prompt = f"""
            You are an expert in analyzing land record documents (RTC - Record of Rights, Tenancy and Crops) from Karnataka, India.
            
            Please carefully examine this Village Account Form No. 2 (RTC) document and extract the following specific information:
            
            1. Survey Number: Look for "Survey No." or "ಸರ್ವೆ ನಂ"
            2. Surnoc: This may appear as "Surnoc No." (might be marked with an asterisk "*"). If not found, set it to "*".
            3. Hissa: Look for "Hissa No." or "Sub-division Number" which is a subdivision number
            4. Village: The name of the village where the land is located
            5. Hobli: The administrative subdivision (look for "Hobli" or "ಹೋಬಳಿ")
            6. Taluk: The larger administrative division (also called Taluka or "ತಾಲೂಕು")
            7. District: The district name (e.g., "Bangalore", "Bangalore Rural")
            8. Owner Name: The name(s) of the landowner(s) - there may be multiple owners listed
            9. Owner Details: Additional information about the owners such as father's/husband's name, relationship, mutation register references (MR numbers), etc.
            
            IMPORTANT INSTRUCTIONS:
            1. First translate any Kannada text to English, then extract the information.
            2. For Owner Name, list all owners if multiple are present, separated by commas.
            3. DO NOT include any asterisks, bullets, or other formatting characters in your response.
            4. DO NOT include any notes or explanations in your field values.
            5. If any field is not visible or cannot be determined in the document, indicate with 'Not found' or 'N/A'.
            6. If the District is not explicitly mentioned but you know the Village and Taluk, please infer the District based on your knowledge (e.g., Devanahalli Taluk is in Bangalore Rural District).
            
            The document may be in Kannada or English or a mix of both. Look for tables with owner information, which typically includes names and shares.
            
            Pay special attention to the "Khatedar" or "ಖಾತೆದಾರ" section which lists the landowners.
            
            Format your response as a structured list with field names followed by the extracted values.
            For example:
            Survey Number: 22
            Surnoc: *
            Hissa: 1
            Village: Devenahalli
            Hobli: Kasaba
            Taluk: Devanahalli
            District: Bangalore Rural
            Owner Name: John Doe, Jane Smith
            Owner Details: John Doe (Father: James Doe, Share: 50%), Jane Smith (Husband: Mike Smith, Share: 50%)
            """
            
            # Call OpenAI API with vision capabilities
            logger.info("Sending image bytes to OpenAI for analysis")
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use the current vision-capable model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # Request high detail for document analysis
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Extract and parse the response
            result = self._parse_response(response.choices[0].message.content)
            
            # Post-process the result to infer missing information
            result = self._post_process_result(result)
            
            logger.info(f"Successfully extracted information from image bytes: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing image bytes: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python image_processor_new.py <path_to_image>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    processor = LandRecordImageProcessor()
    
    try:
        result = processor.process_image(image_path)
        print("\nExtracted Land Record Information:")
        print("=================================")
        for field, value in result.items():
            print(f"{field}: {value}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)