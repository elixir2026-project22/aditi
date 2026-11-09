import { getApiUrl } from "../../../core/config/api";
import { httpClient } from "../../../core/api/http-client";

import type {
  HealthResponse,
  LayoutsResponse,
  PathwayLayoutId,
  PathwaySceneResponse,
} from "../../../core/types";

export class PathwayApi {
  /**
   * Check whether the Aditi backend is reachable.
   */
  async checkHealth(): Promise<HealthResponse> {
    return httpClient.request<HealthResponse>(
      getApiUrl("/health"),
    );
  }

  /**
   * Retrieve the layouts registered by the backend.
   */
  async getAvailableLayouts(): Promise<PathwayLayoutId[]> {
    const response = await httpClient.request<LayoutsResponse>(
      getApiUrl("/pathways/layouts"),
    );

    return response.layouts as PathwayLayoutId[];
  }

  /**
   * Import an SBML document and generate its pathway scene.
   *
   * The File is sent directly as the request body.
   * This preserves its original XML bytes.
   */
  async importSBML(
    file: File,
    layoutId: PathwayLayoutId = "hierarchical",
    signal?: AbortSignal,
  ): Promise<PathwaySceneResponse> {
    if (!(file instanceof File)) {
      throw new TypeError("An SBML File object is required.");
    }

    if (file.size === 0) {
      throw new TypeError("The SBML file cannot be empty.");
    }

    const query = new URLSearchParams({
      layout_id: layoutId,
    });

    return httpClient.request<PathwaySceneResponse>(
      `${getApiUrl("/pathways/import/sbml")}?${query.toString()}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/sbml+xml",
        },
        body: file,
        signal,
        timeoutMs: 120_000,
      },
    );
  }
}

export const pathwayApi = new PathwayApi();