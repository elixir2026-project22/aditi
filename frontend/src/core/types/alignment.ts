
export type SequenceAlphabet = "dna" | "rna" | "protein";

export type AlignmentType = "global" | "local";

export type AlignmentScoringMethod =
  | "simple"
  | "substitution_matrix";

export type AlignmentGapModel = "linear" | "affine";

export interface BiologicalSequenceInput {
  name: string;
  residues: string;
  alphabet: SequenceAlphabet;
  description?: string | null;
}

export interface AlignmentScoringInput {
  method: AlignmentScoringMethod;
  match_score?: number;
  mismatch_score?: number;
  matrix_name?: "BLOSUM62" | null;
}

export interface AlignmentGapInput {
  model: AlignmentGapModel;
  gap_penalty?: number;
  gap_open_penalty?: number;
  gap_extension_penalty?: number;
}

export interface SequenceAlignmentRequest {
  first_sequence: BiologicalSequenceInput;
  second_sequence: BiologicalSequenceInput;
  alignment_type: AlignmentType;
  scoring: AlignmentScoringInput;
  gap: AlignmentGapInput;
}

export interface AlignedSequence {
  sequence_identity: string;
  sequence_name: string;
  residues: string;
  position_mapping: Array<number | null>;
}

export interface AlignmentScore {
  score: number;
  scoring_scheme: string;
  gap_open_penalty: number;
  gap_extension_penalty: number;
  substitution_matrix: string | null;
  match_score: number | null;
  mismatch_score: number | null;
}

export interface SequenceAlignmentResponse {
  alignment_type: AlignmentType;
  aligned_sequences: AlignedSequence[];
  alignment_length: number;
  sequence_count: number;
  score: AlignmentScore;
  identical_positions: number;
  similar_positions: number | null;
  gap_count: number;
  gap_percentage: number;
  identity_percentage: number;
  similarity_percentage: number | null;
}
