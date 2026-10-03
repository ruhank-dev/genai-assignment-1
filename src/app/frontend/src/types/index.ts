export type CorruptionKind = "salt_and_pepper" | "gaussian_blur" | "rectangular_occlusion";

export interface HealthResponse {
  status: string;
  models_loaded: Record<string, boolean>;
  providers: string[];
}

export interface UniversalRestoreResponse {
  original_image: string;
  corrupted_image: string;
  restored_image: string;
  error_map: string;
  error_reference: "clean_upload" | "input";
  corruption_applied: Record<string, string | number> | null;
  inference_time_ms: number;
}

export interface HardRoutedRestoreResponse {
  original_image: string;
  restored_image: string;
  class_probabilities: Record<string, number>;
  predicted_class: string;
  selected_expert: string;
  inference_time: { classifier_ms: number; specialist_ms: number; total_ms: number };
}

export interface SoftMoERestoreResponse {
  original_image: string;
  restored_image: string;
  routing_weights: Record<string, number>;
  dominant_expert: string;
  inference_time_ms: number;
}

export interface SketchGenerateResponse {
  original_image: string;
  sketch_image: string;
  selected_style: number;
  style_description: string;
  inference_time_ms: number;
}
