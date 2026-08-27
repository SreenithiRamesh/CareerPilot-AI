export const createChatRequestId = () => {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return [
    Date.now().toString(36),
    Math.random().toString(36).slice(2),
    Math.random().toString(36).slice(2),
  ].join("-");
};


export const getRetryableChatRequestId = (
  requestRef,
  fingerprint
) => {
  const pendingRequest =
    requestRef.current;

  if (
    pendingRequest &&
    pendingRequest.fingerprint === fingerprint
  ) {
    return pendingRequest.requestId;
  }

  const requestId =
    createChatRequestId();

  requestRef.current = {
    fingerprint,
    requestId,
  };

  return requestId;
};


export const completeChatRequest = (
  requestRef,
  requestId
) => {
  if (
    requestRef.current?.requestId === requestId
  ) {
    requestRef.current = null;
  }
};


export const getChatErrorMessage = (
  error,
  fallbackMessage = (
    "Unable to complete the request. "
    + "Please try again."
  )
) => {
  const detail =
    error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (
    Array.isArray(detail) &&
    detail.length > 0
  ) {
    return detail
      .map((item) => {
        if (typeof item?.msg === "string") {
          return item.msg;
        }

        return String(item);
      })
      .join(" ");
  }

  const responseMessage =
    error?.response?.data?.message;

  if (typeof responseMessage === "string") {
    return responseMessage;
  }

  if (
    !error?.response &&
    typeof error?.message === "string"
  ) {
    return error.message;
  }

  return fallbackMessage;
};