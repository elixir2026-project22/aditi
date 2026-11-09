const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL;

export const API_CONFIG = {
  BASE_URL: (
    configuredBaseUrl?.trim() || "http://127.0.0.1:8000"
  ).replace(/\/+$/, ""),

  API_PREFIX: "/api/v1",

  REQUEST_TIMEOUT_MS: 30_000,
} as const;

export function getApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/")
    ? path
    : `/${path}`;

  return `${API_CONFIG.BASE_URL}${API_CONFIG.API_PREFIX}${normalizedPath}`;
}