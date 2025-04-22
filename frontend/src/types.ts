export interface PropertyDetails {
  id: number;
  survey_number: string;
  surnoc: string;
  hissa: string;
  village: string;
  hobli: string;
  taluk: string;
  district: string;
  owner_name: string;
  owner_details: string;
  created_at: string;
  updated_at: string;
}

export interface PropertyImage {
  id: number;
  property_id: number;
  image_type: string;
  year_period: string;
  description: string;
  created_at: string;
}

export interface ApiError {
  error: string;
}