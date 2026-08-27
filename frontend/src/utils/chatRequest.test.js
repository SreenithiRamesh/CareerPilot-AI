import {
  describe,
  expect,
  it,
} from "vitest";

import {
  completeChatRequest,
  createChatRequestId,
  getChatErrorMessage,
  getRetryableChatRequestId,
} from "./chatRequest";


describe("createChatRequestId", () => {
  it("creates an ID within the API limit", () => {
    const requestId =
      createChatRequestId();

    expect(typeof requestId).toBe("string");
    expect(requestId.length).toBeGreaterThan(0);
    expect(requestId.length).toBeLessThanOrEqual(64);
  });


  it("creates different IDs", () => {
    expect(
      createChatRequestId()
    ).not.toBe(
      createChatRequestId()
    );
  });
});


describe("getRetryableChatRequestId", () => {
  it("reuses the ID for the same fingerprint", () => {
    const requestRef = {
      current: null,
    };

    const firstRequestId =
      getRetryableChatRequestId(
        requestRef,
        "thread-1:message-1"
      );

    const retryRequestId =
      getRetryableChatRequestId(
        requestRef,
        "thread-1:message-1"
      );

    expect(retryRequestId).toBe(
      firstRequestId
    );
  });


  it("creates a new ID for different input", () => {
    const requestRef = {
      current: null,
    };

    const firstRequestId =
      getRetryableChatRequestId(
        requestRef,
        "thread-1:message-1"
      );

    const secondRequestId =
      getRetryableChatRequestId(
        requestRef,
        "thread-1:message-2"
      );

    expect(secondRequestId).not.toBe(
      firstRequestId
    );

    expect(
      requestRef.current.fingerprint
    ).toBe(
      "thread-1:message-2"
    );
  });
});


describe("completeChatRequest", () => {
  it("clears the matching completed request", () => {
    const requestRef = {
      current: {
        fingerprint:
          "thread-1:message-1",
        requestId:
          "request-1",
      },
    };

    completeChatRequest(
      requestRef,
      "request-1"
    );

    expect(requestRef.current).toBeNull();
  });


  it("preserves a different pending request", () => {
    const pendingRequest = {
      fingerprint:
        "thread-1:message-2",
      requestId:
        "request-2",
    };

    const requestRef = {
      current: pendingRequest,
    };

    completeChatRequest(
      requestRef,
      "request-1"
    );

    expect(requestRef.current).toBe(
      pendingRequest
    );
  });
});


describe("getChatErrorMessage", () => {
  it("returns string API detail", () => {
    const message =
      getChatErrorMessage({
        response: {
          data: {
            detail:
              "The request could not be completed.",
          },
        },
      });

    expect(message).toBe(
      "The request could not be completed."
    );
  });


  it("combines validation messages", () => {
    const message =
      getChatErrorMessage({
        response: {
          data: {
            detail: [
              {
                msg:
                  "Request ID is required.",
              },
              {
                msg:
                  "Message cannot be empty.",
              },
            ],
          },
        },
      });

    expect(message).toBe(
      "Request ID is required. "
      + "Message cannot be empty."
    );
  });


  it("returns the API message", () => {
    const message =
      getChatErrorMessage({
        response: {
          data: {
            message:
              "Service temporarily unavailable.",
          },
        },
      });

    expect(message).toBe(
      "Service temporarily unavailable."
    );
  });


  it("returns a network error message", () => {
    const message =
      getChatErrorMessage({
        message:
          "Network Error",
      });

    expect(message).toBe(
      "Network Error"
    );
  });


  it("returns the supplied fallback", () => {
    const message =
      getChatErrorMessage(
        {
          response: {
            data: {},
          },
        },
        "Please retry later."
      );

    expect(message).toBe(
      "Please retry later."
    );
  });
});