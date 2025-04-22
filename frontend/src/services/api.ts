import { PropertyDetails, PropertyImage } from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000'; // Backend Flask server URL

// Process image API
export const processImage = async (image: File): Promise<{ property_id: number }> => {
  try {
    const formData = new FormData();
    formData.append('image', image);

    const response = await fetch(`${API_BASE_URL}/api/process-image/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error processing image:', error);
    throw error;
  }
};

// Get property details API
export const getPropertyDetails = async (propertyId: number): Promise<{
  property_details: PropertyDetails;
  images: PropertyImage[];
}> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/property/${propertyId}/`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching property details:', error);
    throw error;
  }
};

// Get image API
export const getImage = async (imageId: number): Promise<{
  image_url: string;
  metadata: PropertyImage;
}> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/image/${imageId}/`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching image:', error);
    throw error;
  }
};

// Search properties API
export const searchProperties = async (params: Record<string, string>): Promise<{
  properties: PropertyDetails[];
}> => {
  try {
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE_URL}/api/search/?${queryParams}`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error searching properties:', error);
    throw error;
  }
};