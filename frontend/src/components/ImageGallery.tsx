import React, { useState, useEffect } from 'react';
import { Image as ImageIcon, X, ZoomIn, ZoomOut, Download, ChevronLeft } from 'lucide-react';
import { PropertyImage } from '../types';
import { getImage } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

interface ImageGalleryProps {
  images: PropertyImage[];
}

const ImageGallery: React.FC<ImageGalleryProps> = ({ images }) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedImageId, setSelectedImageId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [imageThumbnails, setImageThumbnails] = useState<Record<number, string>>({});
  const [sortedImages, setSortedImages] = useState(() => {
    return [...images].sort((a, b) => {
      // Extract years from year_period (e.g. "2019-20" -> 2019)
      const yearA = parseInt(a.year_period.split('-')[0]);
      const yearB = parseInt(b.year_period.split('-')[0]);
      return yearB - yearA;
    });
  });

  // Load image thumbnails on component mount
  useEffect(() => {
    const loadThumbnails = async () => {
      for (const image of sortedImages) {
        try {
          const imageData = await getImage(image.id);
          setImageThumbnails(prev => ({
            ...prev,
            [image.id]: imageData.image_url
          }));
        } catch (err) {
          console.error(`Error loading thumbnail for image ${image.id}:`, err);
        }
      }
    };
    
    loadThumbnails();
  }, [sortedImages]);

  const handleImageClick = async (imageId: number) => {
    // If we already have the image in thumbnails, show it immediately
    if (imageThumbnails[imageId]) {
      setSelectedImage(imageThumbnails[imageId]);
      setSelectedImageId(imageId);
      setZoomLevel(1); // Reset zoom level
      return;
    }
    
    setLoading(true);
    setSelectedImageId(imageId);
    setZoomLevel(1); // Reset zoom level
    
    try {
      const imageData = await getImage(imageId);
      setSelectedImage(imageData.image_url);
      
      // Cache the image
      setImageThumbnails(prev => ({
        ...prev,
        [imageId]: imageData.image_url
      }));
    } catch (err) {
      console.error('Error loading image:', err);
    } finally {
      setLoading(false);
    }
  };

  const closeModal = () => {
    setSelectedImage(null);
    setSelectedImageId(null);
  };

  const handleZoomIn = () => {
    setZoomLevel(prevZoom => Math.min(prevZoom + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel(prevZoom => Math.max(prevZoom - 0.25, 0.5));
  };

  const handleDownload = () => {
    if (!selectedImage) return;
    
    // Find the image metadata
    const imageMetadata = sortedImages.find(img => img.id === selectedImageId);
    const fileName = imageMetadata 
      ? `${imageMetadata.image_type}_${imageMetadata.year_period}.png`.replace(/\s+/g, '_')
      : `property-document-${selectedImageId}.png`;
    
    // Create a link element and trigger download
    const link = document.createElement('a');
    link.href = selectedImage;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Format the year period to be more readable
  const formatYearPeriod = (yearPeriod: string) => {
    const parts = yearPeriod.split('-');
    if (parts.length === 2) {
      return `${parts[0]}-${parts[1]}`;
    }
    return yearPeriod;
  };

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedImages.map((image) => (
          <div 
            key={image.id}
            onClick={() => handleImageClick(image.id)}
            className="bg-white rounded-lg overflow-hidden shadow hover:shadow-lg transition-all cursor-pointer border border-gray-200 hover:border-blue-400 transform hover:-translate-y-1 duration-200"
          >
            <div className="aspect-[3/2] bg-gray-50 flex items-center justify-center overflow-hidden">
              {imageThumbnails[image.id] ? (
                <img 
                  src={imageThumbnails[image.id]} 
                  alt={`${image.image_type} ${image.year_period}`}
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                />
              ) : (
                <div className="flex flex-col items-center justify-center h-full w-full bg-gray-100">
                  <ImageIcon size={36} className="text-gray-400 mb-2" />
                  <LoadingSpinner size="small" color="blue" />
                </div>
              )}
            </div>
            <div className="p-5">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-gray-800 text-lg">{image.image_type}</h3>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
                  {formatYearPeriod(image.year_period)}
                </span>
              </div>
              <p className="text-gray-600 line-clamp-2 text-sm">{image.description || 'Property document'}</p>
              <div className="mt-3 flex justify-end">
                <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                  View Document
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-gray-900 z-50 flex flex-col">
          {/* Header with title and controls */}
          <div className="bg-gray-800 text-white px-4 py-3 flex items-center justify-between">
            <button 
              onClick={closeModal}
              className="flex items-center space-x-2 hover:text-blue-300 transition-colors"
            >
              <ChevronLeft size={20} />
              <span>Back to gallery</span>
            </button>
            
            <div className="font-medium">
              {selectedImageId && (
                <span>
                  {sortedImages.find(img => img.id === selectedImageId)?.image_type} ({sortedImages.find(img => img.id === selectedImageId)?.year_period})
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Zoom controls */}
              <div className="flex items-center space-x-2 bg-gray-700 rounded-lg overflow-hidden">
                <button 
                  onClick={handleZoomOut}
                  className="p-1.5 hover:bg-gray-600 transition-colors"
                  title="Zoom Out"
                >
                  <ZoomOut size={18} className="text-white" />
                </button>
                <div className="px-2 text-white text-sm font-medium">{Math.round(zoomLevel * 100)}%</div>
                <button 
                  onClick={handleZoomIn}
                  className="p-1.5 hover:bg-gray-600 transition-colors"
                  title="Zoom In"
                >
                  <ZoomIn size={18} className="text-white" />
                </button>
              </div>
              
              {/* Download button */}
              <button 
                onClick={handleDownload}
                className="p-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center space-x-1"
                title="Download Document"
              >
                <Download size={18} className="text-white" />
                <span className="text-sm">Download</span>
              </button>
              
              {/* Close button */}
              <button 
                onClick={closeModal}
                className="p-1.5 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                title="Close"
              >
                <X size={18} className="text-white" />
              </button>
            </div>
          </div>
          
          {/* Main image container */}
          <div className="flex-1 bg-gray-900 overflow-auto flex items-center justify-center p-4">
            {loading ? (
              <div className="flex items-center justify-center h-full w-full">
                <LoadingSpinner size="large" color="blue" />
              </div>
            ) : (
              <div 
                className="relative flex items-center justify-center h-full w-full"
                style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
              >
                <img 
                  src={selectedImage} 
                  alt="Property document" 
                  className="max-w-full max-h-full object-contain shadow-xl"
                />
              </div>
            )}
          </div>
          
          {/* Footer with metadata */}
          {selectedImageId && (
            <div className="bg-gray-800 text-white p-4">
              <div className="max-w-5xl mx-auto flex flex-wrap justify-between items-center">
                <div>
                  <h3 className="font-semibold text-lg">
                    {sortedImages.find(img => img.id === selectedImageId)?.image_type || 'Property Record'}
                  </h3>
                  <p className="text-gray-300">
                    Period: {sortedImages.find(img => img.id === selectedImageId)?.year_period || ''}
                    {sortedImages.find(img => img.id === selectedImageId)?.description && (
                      <> - {sortedImages.find(img => img.id === selectedImageId)?.description}</>
                    )}
                  </p>
                </div>
                <button 
                  onClick={handleDownload} 
                  className="mt-2 sm:mt-0 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md flex items-center space-x-2"
                >
                  <Download size={18} />
                  <span>Download Document</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ImageGallery;