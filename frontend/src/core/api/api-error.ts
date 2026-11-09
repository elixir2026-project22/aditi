export class ApiError extends Error {
  public readonly status: number | null;
  public readonly detail: unknown;

  constructor(
    message: string,
    status: number | null = null,
    detail: unknown = null,
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.detail = detail;

    Object.setPrototypeOf(this, ApiError.prototype);
  }

  get isNetworkError(): boolean {
    return this.status === null;
  }

  get isClientError(): boolean {
    return (
      this.status !== null &&
      this.status >= 400 &&
      this.status < 500
    );
  }

  get isServerError(): boolean {
    return this.status !== null && this.status >= 500;
  }
}