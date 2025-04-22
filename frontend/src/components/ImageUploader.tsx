import React, { useRef, useState } from 'react';
import { Upload, Image } from 'lucide-react';

interface ImageUploaderProps {
  onImageSelect: (file: File) => void;
  selectedImage: File | null;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageSelect, selectedImage }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelection = (file: File) => {
    onImageSelect(file);
    const imageUrl = URL.createObjectURL(file);
    setPreviewUrl(imageUrl);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleImageSelection(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageSelection(e.dataTransfer.files[0]);
    }
  };

  const handleClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="w-full animate-fade-in">
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          gradient-border group cursor-pointer transition-all duration-500
          ${isDragging ? 'scale-102' : 'hover:scale-101'}
        `}
      >
        <div className={`
          bg-white rounded-xl p-8 md:p-10
          flex flex-col items-center justify-center
          transition-all duration-300
          ${isDragging ? 'bg-blue-50' : ''}
          min-h-[240px]
        `}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleChange}
            accept="image/*"
            className="hidden"
          />

          {previewUrl ? (
            <div className="w-full flex flex-col items-center animate-scale-in">
              <div className="relative w-full max-w-md h-64 overflow-hidden rounded-lg shadow-lg group-hover:shadow-xl transition-shadow duration-300">
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <img 
                  src={previewUrl} 
                  alt="Document preview" 
                  className="w-full h-full object-cover transform transition-transform duration-500 group-hover:scale-105"
                />
              </div>
              <p className="mt-4 text-primary-600 font-medium animate-fade-in">
                {selectedImage?.name}
              </p>
              <p className="text-sm text-gray-500 mt-1 animate-fade-in">
                Click or drag to replace
              </p>
            </div>
          ) : (
            <div className="transform transition-transform duration-300 group-hover:scale-105">
              <div className="mb-4 p-4 bg-gradient-to-br from-blue-500 to-violet-500 rounded-full shadow-glow">
                <Image size={40} className="text-white" />
              </div>
              <p className="text-lg font-medium text-gray-700 mb-2">
                Drag & drop your document here
              </p>
              <p className="text-gray-500 mb-4">
                or click to browse
              </p>
              <p className="text-sm text-gray-400">
                Supported formats: JPG, PNG, PDF
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageUploader;