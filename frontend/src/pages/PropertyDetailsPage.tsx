import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, FileText, Calendar, RefreshCw, Home, MapPin, User
} from 'lucide-react';
import Logo from '../components/Logo';
import PropertyCard from '../components/PropertyCard';
import ImageGallery from '../components/ImageGallery';
import LoadingSpinner from '../components/LoadingSpinner';
import { getPropertyDetails } from '../services/api';
import { PropertyDetails, PropertyImage } from '../types';

const PropertyDetailsPage: React.FC = () => {
  const { propertyId } = useParams<{ propertyId: string }>();
  const navigate = useNavigate();
  const [property, setProperty] = useState<PropertyDetails | null>(null);
  const [images, setImages] = useState<PropertyImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastImageCount, setLastImageCount] = useState(0);
  const [pollAttempts, setPollAttempts] = useState(0);
  const [allImagesLoaded, setAllImagesLoaded] = useState(false);

  const fetchPropertyData = useCallback(async () => {
    if (!propertyId) return;
    
    try {
      const data = await getPropertyDetails(parseInt(propertyId));
      setProperty(data.property_details);
      setImages(data.images);
      
      // Track image count for polling
      setLastImageCount(data.images.length);
    } catch (err) {
      console.error('Error fetching property details:', err);
      setError('Failed to load property details');
    } finally {
      setLoading(false);
    }
  }, [propertyId]);

  // Initial fetch
  useEffect(() => {
    fetchPropertyData();
  }, [fetchPropertyData]);

  // Polling mechanism
  useEffect(() => {
    if (!polling || !propertyId) return;
    
    const maxAttempts = 35; // Stop after 30 attempts (around 2 minutes)
    let pollTimer: number;
    
    const pollForUpdates = async () => {
      try {
        const data = await getPropertyDetails(parseInt(propertyId));
        
        // Update if there are new images
        if (data.images.length > lastImageCount) {
          setImages(data.images);
          setLastImageCount(data.images.length);
          setPollAttempts(0); // Reset attempts on successful update
        } else {
          // Increment attempt counter
          setPollAttempts(prev => {
            // Stop polling if max attempts reached
            if (prev >= maxAttempts - 1) {
              setPolling(false);
              setAllImagesLoaded(true); // Mark that we've loaded all available images
              return prev;
            }
            return prev + 1;
          });
        }
      } catch (err) {
        console.error('Polling error:', err);
        setPollAttempts(prev => prev + 1);
      }
    };

    pollTimer = window.setTimeout(pollForUpdates, 3000);
    
    return () => {
      window.clearTimeout(pollTimer);
    };
  }, [propertyId, polling, lastImageCount, pollAttempts]);

  const handleStartPolling = () => {
    setPolling(true);
    setPollAttempts(0);
    setAllImagesLoaded(false); // Reset the all images loaded state
  };

  const handleStopPolling = () => {
    setPolling(false);
    setAllImagesLoaded(true); // Assume user manually stopped because all needed images are loaded
  };

  const goBack = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" color="blue" />
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="min-h-screen p-6 flex flex-col items-center justify-center">
        <div className="mb-8">
          <Logo />
        </div>
        <div className="bg-red-50 p-6 rounded-lg shadow-md text-center">
          <h2 className="text-xl font-semibold text-red-700 mb-2">Error</h2>
          <p className="text-red-600 mb-4">{error || "Property not found"}</p>
          <button 
            onClick={goBack}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ArrowLeft size={16} className="inline mr-2" />
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-16">
      <header className="bg-white shadow-sm py-4">
        <div className="container mx-auto px-4 flex items-center justify-between">
          <div className="flex items-center">
            <button 
              onClick={goBack}
              className="mr-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft size={20} className="text-gray-700" />
            </button>
            <Logo />
          </div>
          
          {polling ? (
            <button 
              onClick={handleStopPolling}
              className="px-4 py-2 flex items-center text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
            >
              <RefreshCw size={16} className="animate-spin mr-2" />
              Stop Fetching
            </button>
          ) : images.length > 0 && !allImagesLoaded ? (
            <button 
              onClick={handleStartPolling}
              className="px-4 py-2 flex items-center text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
            >
              <RefreshCw size={16} className="mr-2" />
              Fetch Missing Years
            </button>
          ) : images.length > 0 && allImagesLoaded ? (
            <span className="px-4 py-2 flex items-center text-green-600 bg-green-50 rounded-lg">
              <FileText size={16} className="mr-2" />
              All Records Loaded
            </span>
          ) : null}
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-1">
            <PropertyCard property={property} />
          </div>
          
          <div className="md:col-span-2">
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                  <Calendar size={20} className="mr-2 text-blue-600" />
                  Property Records Timeline
                </h2>
                
                {images.length === 0 ? (
                  <div className="py-12 text-center">
                    <FileText size={48} className="mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500">
                      {polling ? (
                        <>
                          <RefreshCw size={16} className="inline animate-spin mr-2" />
                          Fetching property records...
                        </>
                      ) : allImagesLoaded ? (
                        "All property records have been fetched"
                      ) : (
                        "No property records available yet"
                      )}
                    </p>
                    {!polling && !allImagesLoaded && (
                      <button 
                        onClick={handleStartPolling}
                        className="mt-4 px-4 py-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
                      >
                        <RefreshCw size={16} className="inline mr-2" />
                        Fetch Records
                      </button>
                    )}
                  </div>
                ) : (
                  <ImageGallery images={images} />
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PropertyDetailsPage;