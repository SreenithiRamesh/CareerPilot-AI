function normalizeBaseURL(value) {
  return value?.trim().replace(/\/+$/, "") || "";
}


function parseAbsoluteURL(value) {
  try {
    return new URL(value);
  }
  catch {
    throw new Error(
      "VITE_API_BASE_URL must be an "
      + "absolute HTTP or HTTPS URL."
    );
  }
}


export function resolveApiBaseURL({
  configuredBaseURL,
  isProduction,
}) {
  const normalizedBaseURL =
    normalizeBaseURL(
      configuredBaseURL
    );

  if (!normalizedBaseURL) {
    throw new Error(
      "VITE_API_BASE_URL must be configured."
    );
  }

  const parsedURL =
    parseAbsoluteURL(
      normalizedBaseURL
    );

  if (
    parsedURL.protocol !== "http:"
    && parsedURL.protocol !== "https:"
  ) {
    throw new Error(
      "VITE_API_BASE_URL must use HTTP or HTTPS."
    );
  }

  if (
    isProduction
    && parsedURL.protocol !== "https:"
  ) {
    throw new Error(
      "VITE_API_BASE_URL must use HTTPS "
      + "in production."
    );
  }

  return normalizedBaseURL;
}