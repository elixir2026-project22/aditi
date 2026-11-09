import { API_CONFIG } from "../config/api";
import { ApiError } from "./api-error";

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export class HttpClient {
  async request<T>(
    url: string,
    options: RequestOptions = {},
  ): Promise<T> {
    const {
      timeoutMs = API_CONFIG.REQUEST_TIMEOUT_MS,
      signal: externalSignal,
      ...requestOptions
    } = options;

    const controller = new AbortController();

    let timedOut = false;

    const timeoutId = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, timeoutMs);

    const abortFromExternalSignal = () => {
      controller.abort(externalSignal?.reason);
    };

    if (externalSignal?.aborted) {
      abortFromExternalSignal();
    } else {
      externalSignal?.addEventListener(
        "abort",
        abortFromExternalSignal,
        { once: true },
      );
    }

    try {
      const response = await fetch(url, {
        ...requestOptions,
        signal: controller.signal,
        headers: {
          Accept: "application/json",
          ...requestOptions.headers,
        },
      });

      if (!response.ok) {
        const errorBody = await this.readErrorBody(response);

        throw new ApiError(
          this.getErrorMessage(response.status, errorBody),
          response.status,
          errorBody,
        );
      }

      if (response.status === 204) {
        return undefined as T;
      }

      try {
        return (await response.json()) as T;
      } catch {
        throw new ApiError(
          "The backend returned an invalid JSON response.",
          response.status,
        );
      }
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      if (timedOut) {
        throw new ApiError(
          `The request timed out after ${timeoutMs} milliseconds.`,
        );
      }

      if (externalSignal?.aborted) {
        throw error;
      }

      throw new ApiError(
        error instanceof Error
          ? `Unable to communicate with the Aditi backend: ${error.message}`
          : "Unable to communicate with the Aditi backend.",
      );
    } finally {
      clearTimeout(timeoutId);

      externalSignal?.removeEventListener(
        "abort",
        abortFromExternalSignal,
      );
    }
  }

  private async readErrorBody(
    response: Response,
  ): Promise<unknown> {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  private getErrorMessage(
    status: number,
    body: unknown,
  ): string {
    if (
      typeof body === "object" &&
      body !== null &&
      "detail" in body
    ) {
      const detail = body.detail;

      if (typeof detail === "string") {
        return detail;
      }
    }

    return `The backend request failed with HTTP status ${status}.`;
  }
}

export const httpClient = new HttpClient();