# TitleTrail

A comprehensive system for tracking property records from Karnataka, India.

### Demo - [Drive Link](https://drive.google.com/file/d/1dr5xxWZ0gAEgsFPfTj1AAlmeQF3lzkPi/view?usp=sharing)
## Project Overview

TitleTrail is a full-stack application that allows users to:
- Extract property information from land record images using AI
- Retrieve historical records for properties from the Karnataka land records database
- View and compare property records across different time periods
- Store and access property records digitally

The system consists of a Django backend with image processing capabilities and a React frontend that provides an intuitive user interface.

## Table of Contents

- [Getting Started](#getting-started)
  - [Clone the Repository](#clone-the-repository)
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [API Documentation](#api-documentation)
- [Technical Approach](#technical-approach)
- [Challenges and Solutions](#challenges-and-solutions)

## Getting Started

### Clone the Repository

First, clone the TitleTrail repository from GitHub:

```bash
git clone https://github.com/CodeMaverick2/TitleTrail.git
cd TitleTrail
```

## Setup Instructions

### Backend Setup

#### Prerequisites

- Python 3.10+
- PostgreSQL database
- OpenAI API key

#### Installation Steps

1. **Create and Configure Environment Variables**
   
   Create a `.env` file in the root directory with the following variables:
   ```
   DEBUG=True
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key
   ```

2. **Create a Virtual Environment**
   ```bash
   cd backend
   python3 -m venv venv
   ```

   Activate the virtual environment:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Install Playwright browsers:
   ```bash
   playwright install
   ```

4. **Initialize the Database**
   
   Make sure PostgreSQL is running and the database specified in your `.env` file exists.
   ```bash
   python init_db.py
   ```

5. **Run the Backend Server**
   ```bash
   python app.py
   ```
   The server will run at `http://127.0.0.1:8000`

### Frontend Setup

#### Installation Steps

1. **Navigate to the Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure API Endpoint**
   
   Ensure the API endpoint in `src/services/api.ts` points to your backend server:
   ```javascript
   const API_BASE_URL = 'http://127.0.0.1:8000'; 
   ```

4. **Start the Development Server**
   ```bash
   npm run dev
   ```
   The frontend will run at `http://localhost:5173`

5. **Accessing the Application**
   
   Open your browser and navigate to `http://localhost:5173` to access the TitleTrail application.

## API Documentation

The backend provides the following REST API endpoints, with the first three being actively used by the frontend:

### Process Image API (Used in Frontend)

- **Endpoint**: `/api/process-image/`
- **Method**: `POST`
- **Description**: Uploads and processes an image to extract property details
- **Used For**: Called when a user uploads a property document image
- **Request Format**: 
  - Multipart form data with an `image` field
- **Response Format**:
  ```json
  {
    "property_id": 123,
    "property_details": {
      "Survey Number": "22",
      "Surnoc": "*",
      "Hissa": "1",
      "Village": "Devenahalli",
      "Hobli": "Kasaba",
      "Taluk": "Devanahalli",
      "District": "Bangalore Rural",
      "Owner Name": "John Doe",
      "Owner Details": "...",
    }
  }
  ```

### Get Property Details API (Used in Frontend)

- **Endpoint**: `/api/property/{property_id}/`
- **Method**: `GET`
- **Description**: Retrieves property details and associated images by ID
- **Used For**: Fetching property information and historical images for display
- **Response Format**:
  ```json
  {
    "property_details": {
      "id": 123,
      "survey_number": "22",
      "surnoc": "*",
      "hissa": "1",
      "village": "Devenahalli",
      "hobli": "Kasaba",
      "taluk": "Devanahalli",
      "district": "Bangalore Rural",
      "owner_name": "John Doe",
      "owner_details": "...",
      "created_at": "2025-04-22T12:00:00Z",
      "updated_at": "2025-04-22T12:00:00Z"
    },
    "images": [
      {
        "id": 1,
        "property_id": 123,
        "image_type": "RTC Document",
        "year_period": "2019-20",
        "description": "...",
        "created_at": "2025-04-22T12:05:00Z"
      },
      // ...more images
    ]
  }
  ```

### Get Image API (Used in Frontend)

- **Endpoint**: `/api/image/{image_id}/`
- **Method**: `GET`
- **Description**: Retrieves a specific image by ID
- **Used For**: Loading individual property document images in the gallery
- **Response Format**:
  ```json
  {
    "image_url": "data:image/png;base64,...",
    "metadata": {
      "id": 1,
      "property_id": 123,
      "image_type": "RTC Document",
      "year_period": "2019-20",
      "description": "...",
      "created_at": "2025-04-22T12:05:00Z"
    }
  }
  ```

### Search Properties API (Not Currently Used in Frontend)

- **Endpoint**: `/api/search/`
- **Method**: `GET`
- **Description**: Searches for properties based on various parameters
- **Query Parameters**: 
  - `survey_number`: Survey number
  - `village`: Village name
  - `hobli`: Hobli name
  - `taluk`: Taluk name
  - `district`: District name
  - `owner_name`: Owner name
- **Response Format**:
  ```json
  {
    "properties": [
      {
        "id": 123,
        "survey_number": "22",
        "surnoc": "*",
        "hissa": "1",
        "village": "Devenahalli",
        "hobli": "Kasaba",
        "taluk": "Devanahalli",
        "district": "Bangalore Rural",
        "owner_name": "John Doe",
        "created_at": "2025-04-22T12:00:00Z",
        "updated_at": "2025-04-22T12:00:00Z"
      },
      // ...more properties
    ]
  }
  ```

## Technical Approach

TitleTrail implements an end-to-end workflow for processing property records, from image upload to displaying historical data. Here's a detailed breakdown of the approach:

### 1. Image Processing and Data Extraction

When a user uploads an image of a property record:

1. The frontend sends the image to the backend's `/api/process-image/` endpoint.
2. The `LandRecordImageProcessor` class processes the image using OpenAI's vision capabilities:
   - The image is encoded to base64 and sent to OpenAI's API.
   - A carefully crafted prompt instructs the AI to extract specific fields: Survey Number, Surnoc, Hissa, Village, Hobli, Taluk, District, Owner Name, and Owner Details.
   - The AI processes both English and Kannada text in the document, translating if necessary.
   - The response is parsed and structured into a standardized format.
   - Post-processing is applied to infer missing information (e.g., inferring a district from a taluk) and to correct common errors.

3. The extracted property details are stored in the PostgreSQL database using Django ORM.

### 2. Web Scraping and Historical Record Retrieval

After extracting property details, the system initiates a background process to retrieve historical records:

1. The `RTCScraper` class uses Playwright to automate interaction with the Karnataka land records website:
   - Navigates to the website and selects "Old Year" records.
   - Fills the search form dynamically with the extracted property details.
   - Intelligently matches extracted location values (District, Taluk, Hobli, Village) with dropdown options using fuzzy matching.
   - Extracts all available period and year options from the website's dropdown menus.

2. For each year in the configured range (e.g., 2012-2021), the scraper:
   - Dynamically determines the appropriate period and year dropdown values.
   - Selects those values and clicks "Fetch details".
   - Opens the document view in a new tab.
   - Takes a screenshot of the document and saves it.
   - Creates metadata for the image including its year period, survey number, etc.

3. Each retrieved document is then stored in the database as a `PropertyImage` object.

### 3. Frontend Presentation

The frontend provides an intuitive interface for users:

1. The user uploads a property document image through the `ImageUploader` component.
2. After processing, the user is redirected to the `PropertyDetailsPage` which displays:
   - A `PropertyCard` with the extracted details (Survey Number, Hissa, Village, Owner, etc.)
   - An `ImageGallery` showing the historical documents retrieved by the scraper.
   
3. The page automatically polls for new images as they're being retrieved by the background process.
4. Users can view, zoom, and download any document in the gallery.

### 4. Data Flow

The complete end-to-end data flow is:

1. User uploads an image → Frontend sends image to backend
2. Backend processes image with AI → Extracts property details
3. Backend stores property details and returns property ID → Frontend redirects to property details page
4. Backend initiates scraping in background → Retrieves historical records over multiple years
5. Frontend polls for new images → Updates gallery as images become available
6. User interacts with property details and document gallery

## Challenges and Solutions

### Challenge 1: Dynamic Form Handling on the Karnataka Land Records Website

**Problem:** The Karnataka Land Records website uses a complex series of cascading dropdown menus where selecting one field affects the available options in subsequent fields. Additionally, many fields don't have exact text matches to what we extract from the image.

**Solution:** I implemented a sophisticated dropdown handling system that:

1. Uses a `DropdownHandler` class to intelligently work with the website's dynamic forms
2. Implements multi-level fuzzy matching to find the best option in each dropdown:
   - Exact match (case insensitive)
   - Simplified text match (removing words like "district" or "taluk")
   - Contains match (checking if one string contains the other)
   - Word-by-word matching (counting common words)

This approach successfully handles variations in spelling, formatting, and additional descriptive text in dropdown options.

### Challenge 2: Handling Historical Period and Year Selection

**Problem:** The website organizes historical records by periods and years, but these aren't consistent or predictable. Previously, I had hardcoded values for periods and years, which was fragile and prone to failure.

**Solution:** I developed a fully dynamic approach:

1. The system extracts all available period and year options from the website in real-time
2. It builds a comprehensive mapping of period values to year values
3. For each target year (e.g., "2018-19"), the system:
   - Checks for exact matches in the extracted options
   - Searches for periods containing the target year
   - Parses and matches by year components
   
This dynamic approach ensures the system works reliably even if the website changes its period/year structure or adds new options.

### Challenge 3: Accurate Information Extraction from Multilingual Documents

**Problem:** Property documents often contain a mix of English and Kannada text, with inconsistent formatting and varying layouts.

**Solution:** I leveraged OpenAI's vision capabilities with:

1. A carefully crafted prompt that:
   - Instructs the AI to translate Kannada text first
   - Lists specific fields to extract and their possible locations/formats
   - Provides examples of expected output format
   
2. Robust post-processing that:
   - Handles cases where fields are missing
   - Infers information where possible (e.g., district from taluk)
   - Corrects common spelling errors
   - Validates values to ensure they're actual property details and not instructions

This approach achieves high accuracy in extracting information from diverse document formats.

### Challenge 4: Asynchronous Processing for Better User Experience

**Problem:** Retrieving historical records can take several minutes, but users expect immediate feedback.

**Solution:** I implemented a background processing system:

1. The image is processed immediately and property details are returned to the user
2. Historical record retrieval runs in a background thread
3. The frontend polls for new images periodically
4. Users can see records as they become available, with visual indicators of the ongoing process

This solution provides a responsive user experience while still performing resource-intensive operations.

---
