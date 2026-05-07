export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(status: number, message: string, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

type RequestBody = BodyInit | Record<string, unknown> | undefined;
type ApiRequestInit = Omit<RequestInit, "body"> & { body?: RequestBody };

function buildHeaders(
  body: RequestBody,
  extra?: HeadersInit,
  accept?: string,
): Headers {
  const headers = new Headers(extra);
  if (accept) {
    headers.set("Accept", accept);
  }
  if (
    body &&
    !(body instanceof FormData) &&
    !(body instanceof Blob) &&
    !(body instanceof URLSearchParams) &&
    typeof body !== "string"
  ) {
    headers.set("Content-Type", "application/json");
  }
  return headers;
}

function normalizeBody(body: RequestBody) {
  if (!body) {
    return undefined;
  }
  if (
    typeof body === "string" ||
    body instanceof FormData ||
    body instanceof URLSearchParams ||
    body instanceof Blob
  ) {
    return body;
  }
  return JSON.stringify(body);
}

export async function apiRequest<T>(
  path: string,
  init: ApiRequestInit = {},
): Promise<T> {
  const response = await fetch(path, {
    credentials: "include",
    ...init,
    headers: buildHeaders(init.body, init.headers),
    body: normalizeBody(init.body),
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === "object" && payload && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : response.statusText;
    throw new ApiError(response.status, message, payload);
  }

  return payload as T;
}

export async function streamSse<T>(
  path: string,
  init: ApiRequestInit = {},
  onEvent: (event: T) => void,
) {
  const response = await fetch(path, {
    credentials: "include",
    ...init,
    headers: buildHeaders(init.body, init.headers, "text/event-stream"),
    body: normalizeBody(init.body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(response.status, text || response.statusText, text);
  }

  if (!response.body) {
    throw new Error("Streaming response body is unavailable");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      const dataLine = chunk
        .split("\n")
        .find((line) => line.startsWith("data: "));
      if (!dataLine) {
        continue;
      }
      const payload = dataLine.slice(6);
      onEvent(JSON.parse(payload) as T);
    }
  }
}
