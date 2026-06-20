export type Voice = "Kore" | "Puck" | "Aoede" | "Charon" | "Fenrir";

export interface VoicesResponse {
  voices: Voice[];
}

export interface SynthesizeRequest {
  text: string;
  voice: Voice;
  style_prompt?: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
}
