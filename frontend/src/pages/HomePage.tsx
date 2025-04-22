import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload } from 'lucide-react';
import Logo from '../components/Logo';
import ImageUploader from '../components/ImageUploader';
import LoadingSpinner from '../components/LoadingSpinner';
import { processImage } from '../services/api';

const HomePage: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleImageSelect = (file: File) => {
    setSelectedImage(file);
    setError(null);
  };

  const handleFetchDetails = async () => {
    if (!selectedImage) {
      setError("Please select an image first");
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const response = await processImage(selectedImage);
      navigate(`/property/${response.property_id}`);
    } catch (err) {
      setError("Failed to process image. Please try again.");
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 py-12">
      <div className="w-full max-w-4xl mx-auto text-center">
        <div className="mb-12">
          <Logo />
        </div>

        <div className="glass-effect rounded-2xl shadow-lg overflow-hidden transition-all duration-300 transform hover:shadow-xl">
          <div className="p-8 md:p-12">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">
              Property Record Processing
            </h1>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Upload your property document image to extract details and access historical records
            </p>

            <ImageUploader 
              onImageSelect={handleImageSelect} 
              selectedImage={selectedImage}
            />

            {error && (
              <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-lg">
                {error}
              </div>
            )}

            <button
              onClick={handleFetchDetails}
              disabled={isProcessing || !selectedImage}
              className={`
                mt-8 px-8 py-3 rounded-xl text-lg font-semibold
                transition-all duration-300 flex items-center justify-center mx-auto
                ${!selectedImage 
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-blue-600 to-violet-600 text-white hover:shadow-lg hover:shadow-primary-500/25'
                }
              `}
            >
              {isProcessing ? (
                <LoadingSpinner size="small" color="white" />
              ) : (
                <>
                  <Upload size={20} className="mr-2" />
                  Fetch Property Details
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;