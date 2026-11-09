/**
 * Shared pathway API contracts.
 *
 * These interfaces mirror the JSON response models
 * exposed by the Aditi Python backend.
 */

/**
 * Biological entity types supported by the pathway graph.
 */
export type PathwayNodeType =
  | "metabolite"
  | "reaction";

/**
 * Directional roles of pathway graph edges.
 */
export type PathwayEdgeRole =
  | "reactant"
  | "product";

/**
 * Node returned by the pathway visualization API.
 */
export interface PathwaySceneNode {
  identity: string;
  node_type: PathwayNodeType;
  label: string;
  x: number;
  y: number;
}

/**
 * Directed edge connecting two pathway nodes.
 *
 * The backend serializes Decimal coefficients as JSON strings.
 */
export interface PathwaySceneEdge {
  source_identity: string;
  target_identity: string;
  role: PathwayEdgeRole;
  coefficient: string;
}

/**
 * Spatial boundaries of a generated pathway scene.
 */
export interface PathwaySceneBounds {
  min_x: number;
  min_y: number;
  max_x: number;
  max_y: number;
  width: number;
  height: number;
}

/**
 * Complete response returned by the pathway visualization API.
 */
export interface PathwaySceneResponse {
  pathway_identity: string;
  nodes: PathwaySceneNode[];
  edges: PathwaySceneEdge[];
  bounds: PathwaySceneBounds;
}

/**
 * Layout identifiers currently registered by the backend.
 */
export type PathwayLayoutId =
  | "hierarchical"
  | "force-directed";