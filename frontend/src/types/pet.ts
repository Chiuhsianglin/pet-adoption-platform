/**
 * Pet Management Types
 * Types for pet publishing and management system
 */

// Pet enums
export enum PetSpecies {
  DOG = 'dog',
  CAT = 'cat',
  RABBIT = 'rabbit',
  BIRD = 'bird',
  OTHER = 'other',
}

export enum PetGender {
  MALE = 'male',
  FEMALE = 'female',
  UNKNOWN = 'unknown',
}

export enum PetSize {
  SMALL = 'small',
  MEDIUM = 'medium',
  LARGE = 'large',
}

export enum PetStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  AVAILABLE = 'available',
  PENDING = 'pending',
  ADOPTED = 'adopted',
  UNAVAILABLE = 'unavailable',
  REJECTED = 'rejected',
}

// Pet interfaces
export interface PetPhoto {
  id: number;
  file_id?: number;
  url: string;
  file_url?: string;
  file_key?: string;
  is_primary: boolean;
  display_order?: number;
  created_at?: string;
}

export interface Pet {
  id: number;
  name: string;
  species: PetSpecies;
  breed?: string;
  age_years?: number;  // 出生年份 (Birth Year, e.g., 2023)
  age_months?: number;  // 出生月份 (Birth Month, 1-12)
  weight_kg?: number;
  gender?: PetGender;
  size?: PetSize;
  color?: string;
  description?: string;
  behavioral_info?: string;
  health_status?: string;
  vaccination_status: boolean;
  sterilized: boolean;
  special_needs?: string;
  microchip_id?: string;
  house_trained?: boolean;
  good_with_kids?: boolean;
  good_with_pets?: boolean;
  energy_level?: string;
  adoption_fee?: number;
  status: PetStatus;
  shelter_id: number;
  shelter_name?: string;
  created_by: number;
  version?: number;
  last_modified_by?: number;
  created_at: string;
  updated_at: string;
  photos?: PetPhoto[];
  primary_photo_url?: string;
}

export interface PetCreate {
  name: string;
  species: PetSpecies;
  breed?: string;
  age_years?: number;  // 出生年份 (Birth Year, e.g., 2023)
  age_months?: number;  // 出生月份 (Birth Month, 1-12)
  weight_kg?: number;
  gender?: PetGender;
  size?: PetSize;
  color?: string;
  description?: string;
  behavioral_info?: string;
  health_status?: string;
  vaccination_status: boolean;
  sterilized: boolean;
  special_needs?: string;
  microchip_id?: string;
  house_trained?: boolean;
  good_with_kids?: boolean;
  good_with_pets?: boolean;
  energy_level?: string;
  adoption_fee?: number;
}

export interface PetUpdate extends Partial<PetCreate> {}

export interface PetListParams {
  page?: number;
  limit?: number;
  status?: PetStatus;
  species?: PetSpecies;
  search?: string;
}

export interface PetListResponse {
  pets: Pet[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface PetHistoryEntry {
  id: number;
  pet_id: number;
  change_type: string;
  old_status?: PetStatus;
  new_status?: PetStatus;
  reason?: string;
  notes?: string;
  changed_by: number;
  created_at: string;
}

export interface PetHistoryResponse {
  history: PetHistoryEntry[];
}

export interface PetReviewSubmit {
  notes?: string;
}

export interface PetReviewAction {
  reason: string;
  notes?: string;
}

export interface PetStatusUpdate {
  status: PetStatus;
  reason?: string;
}
