export type ApiResult<T> = {
  ok: boolean;
  status: number;
  data?: T;
  error?: string;
};

async function parseResponse(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiGet<T>(path: string): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`/api${path}`);
    const data = await parseResponse(response);

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        error: typeof data === "string" ? data : JSON.stringify(data, null, 2),
      };
    }

    return {
      ok: true,
      status: response.status,
      data: data as T,
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      error: error instanceof Error ? error.message : "Unknown request error",
    };
  }
}

export async function apiPost<T>(
  path: string,
  body: unknown,
): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`/api${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await parseResponse(response);

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        error: typeof data === "string" ? data : JSON.stringify(data, null, 2),
      };
    }

    return {
      ok: true,
      status: response.status,
      data: data as T,
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      error: error instanceof Error ? error.message : "Unknown request error",
    };
  }
}
