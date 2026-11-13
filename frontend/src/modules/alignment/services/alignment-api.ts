
import { getApiUrl } from "../../../core/config/api";
import { httpClient } from "../../../core/api/http-client";

import type {
  SequenceAlignmentRequest,
  SequenceAlignmentResponse,
} from "../../../core/types";

export class AlignmentApi {
  /**
   * Submit two biological sequences for pairwise alignment.
   */
  async align(
    request: SequenceAlignmentRequest,
    signal?: AbortSignal,
  ): Promise<SequenceAlignmentResponse> {
    return httpClient.request<SequenceAlignmentResponse>(
      getApiUrl("/alignments/pairwise"),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
        signal,
        timeoutMs: 120_000,
      },
    );
  }
}

export const alignmentApi = new AlignmentApi();
