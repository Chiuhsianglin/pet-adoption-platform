/**
 * Adoption application types
 */

export type HousingType = 'apartment' | 'house' | 'rental' | 'owned'

export type ApplicationStatus = 
  | 'draft' 
  | 'submitted' 
  | 'under_review' 
  | 'approved' 
  | 'rejected' 
  | 'completed'

export interface OtherPet {
  species: string
  age: number
  vaccinated: boolean
}

export interface EnvironmentPhoto {
  id?: number
  file_url?: string
  file_key?: string
  url?: string
  preview?: string
}

export interface PersonalInfo {
  name: string
  phone: string
  email: string
  address: string
  id_number: string
  occupation: string
  monthly_income: number
}

export interface LivingEnvironment {
  housing_type: HousingType
  space_size: number
  has_yard: boolean
  family_members: number
  has_allergies: boolean
  other_pets: OtherPet[]
  environment_photos?: EnvironmentPhoto[]
}

export interface PetExperience {
  previous_experience: string
  pet_knowledge: string
  care_schedule: string
  veterinarian_info: string
  emergency_fund: number
}

export interface AdoptionApplicationCreate {
  pet_id: number
  personal_info: PersonalInfo
  living_environment: LivingEnvironment
  pet_experience: PetExperience
}

export interface AdoptionApplicationUpdate {
  personal_info?: PersonalInfo
  living_environment?: LivingEnvironment
  pet_experience?: PetExperience
}

export interface AdoptionApplication {
  id: number
  application_id: string
  pet_id: number
  applicant_id: number
  status: ApplicationStatus
  personal_info: PersonalInfo
  living_environment: LivingEnvironment
  pet_experience: PetExperience
  review_notes?: string
  reviewed_by?: number
  reviewed_at?: string
  created_at: string
  updated_at: string
  submitted_at?: string
}

export interface AdoptionApplicationListItem {
  id: number
  application_id: string
  pet_id: number
  applicant_id: number
  status: ApplicationStatus
  created_at: string
  submitted_at?: string
}

export interface AdoptionApplicationList {
  total: number
  applications: AdoptionApplicationListItem[]
}

// Form step type
export type FormStep = 1 | 2 | 3 | 4

// Form validation errors
export interface FormErrors {
  personal_info?: Partial<Record<keyof PersonalInfo, string>>
  living_environment?: Partial<Record<keyof LivingEnvironment, string>>
  pet_experience?: Partial<Record<keyof PetExperience, string>>
}
