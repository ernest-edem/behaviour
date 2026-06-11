export type UserRole = "user" | "clinician" | "admin";

export interface AuthUser {
  id: number;
  email: string;
  name: string;
  role: UserRole;
}

export interface JWTPayload {
  sub: string;        // user id
  email?: string;
  role: "user" | "clinician" | "admin";
  exp: number;
}

export type RiskLevel = 'low' | 'mild' | 'moderate' | 'high' | 'critical';

export type PredictedCondition =
  | 'diabetes'
  | 'hypertension'
  | 'cardiovascular_disease'
  | 'stress_related_disorder';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
}

export interface AssessmentCreate {
  age: number;
  gender: string;
  weight: number;
  height: number;
  bmi: number;
  physical_activity: number;
  diet_quality: number;
  sleep_hours: number;
  stress_level: number;
  smoking: number;
  alcohol_use: number;
  blood_pressure: number;
  blood_glucose: number;
  medication_adherence: number;
  emotional_wellbeing: number;
}

export interface Assessment extends AssessmentCreate {
  id: number;
  user_id: number;
  created_at: string;
}

export interface Prediction {
  id: number;
  assessment_id: number;
  predicted_condition: PredictedCondition;
  risk_level: RiskLevel;
  confidence_score: number;
  behavioral_phenotype: string;
  prediction_source: string;
  created_at: string;
}

export interface DiseasePredictionResult {
  assessment_id: number;
  behavioral_phenotype: string;
  predictions: Prediction[];
}

export interface ExplanationItem {
  feature_name: string;
  contribution: number;
  importance_rank: number;
  explanation_text: string;
}

export interface PredictionExplanation {
  prediction_id: number;
  predicted_condition: PredictedCondition;
  risk_level: RiskLevel;
  behavioral_phenotype: string;
  explanations: ExplanationItem[];
}
