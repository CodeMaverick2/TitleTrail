import React from 'react';
import { MapPin, User, Calendar, FileText, LayoutGrid } from 'lucide-react';
import { PropertyDetails } from '../types';

interface PropertyCardProps {
  property: PropertyDetails;
}

const PropertyCard: React.FC<PropertyCardProps> = ({ property }) => {
  // Format the date nicely
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 p-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-semibold text-white mb-1">Property Details</h2>
            <p className="text-blue-100 text-sm">
              Record ID: {property.id}
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3">
            <LayoutGrid size={28} className="text-white" />
          </div>
        </div>
      </div>
      
      <div className="p-6 space-y-7">
        <div className="flex items-start">
          <MapPin size={22} className="text-blue-600 mr-4 mt-1 flex-shrink-0" />
          <div className="w-full">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Location</h3>
            <p className="font-semibold text-gray-800 mt-1 text-lg">
              {property.village}, {property.hobli}
            </p>
            <p className="text-gray-700">
              {property.taluk}, {property.district}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {property.district && (
                <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                  {property.district} District
                </span>
              )}
              {property.taluk && (
                <span className="px-3 py-1 bg-green-50 text-green-700 text-xs rounded-full">
                  {property.taluk} Taluk
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-start">
          <FileText size={22} className="text-blue-600 mr-4 mt-1 flex-shrink-0" />
          <div className="w-full">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Survey Details</h3>
            <div className="grid grid-cols-3 gap-x-6 gap-y-3 mt-2 bg-gray-50 p-3 rounded-lg">
              <div>
                <p className="text-xs text-gray-500">Survey Number</p>
                <p className="font-semibold text-gray-800 text-lg">{property.survey_number}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Surnoc</p>
                <p className="font-semibold text-gray-800 text-lg">{property.surnoc}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Hissa</p>
                <p className="font-semibold text-gray-800 text-lg">{property.hissa}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-start">
          <User size={22} className="text-blue-600 mr-4 mt-1 flex-shrink-0" />
          <div className="w-full">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Ownership</h3>
            <p className="font-semibold text-gray-800 mt-1 text-lg">{property.owner_name}</p>
            {property.owner_details && (
              <div className="mt-1 p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-400">
                <p className="text-sm text-gray-700">{property.owner_details}</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-start">
          <Calendar size={22} className="text-blue-600 mr-4 mt-1 flex-shrink-0" />
          <div className="w-full">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Record Information</h3>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2 mt-2">
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-xs text-gray-500">Created</p>
                <p className="text-sm text-gray-700">{formatDate(property.created_at)}</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-xs text-gray-500">Last Updated</p>
                <p className="text-sm text-gray-700">{formatDate(property.updated_at)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyCard;