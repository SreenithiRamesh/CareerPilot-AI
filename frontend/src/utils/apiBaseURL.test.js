import {
  describe,
  expect,
  it,
} from "vitest";

import {
  resolveApiBaseURL,
} from "./apiBaseURL";


describe(
  "resolveApiBaseURL",
  () => {
    it(
      "requires an explicitly configured API URL",
      () => {
        expect(() => {
          resolveApiBaseURL({
            configuredBaseURL:
              undefined,
            isProduction:
              false,
          });
        }).toThrow(
          "VITE_API_BASE_URL must be configured"
        );
      }
    );


    it(
      "requires an API URL in production",
      () => {
        expect(() => {
          resolveApiBaseURL({
            configuredBaseURL:
              "",
            isProduction:
              true,
          });
        }).toThrow(
          "VITE_API_BASE_URL must be configured"
        );
      }
    );


    it(
      "requires HTTPS in production",
      () => {
        expect(() => {
          resolveApiBaseURL({
            configuredBaseURL:
              "http://api.example.com",
            isProduction:
              true,
          });
        }).toThrow(
          "VITE_API_BASE_URL must use HTTPS"
        );
      }
    );


    it(
      "accepts an HTTPS production URL",
      () => {
        expect(
          resolveApiBaseURL({
            configuredBaseURL:
              "https://api.example.com",
            isProduction:
              true,
          })
        ).toBe(
          "https://api.example.com"
        );
      }
    );


    it(
      "allows HTTP outside production",
      () => {
        expect(
          resolveApiBaseURL({
            configuredBaseURL:
              "http://localhost:8000",
            isProduction:
              false,
          })
        ).toBe(
          "http://localhost:8000"
        );
      }
    );


    it(
      "removes trailing slashes",
      () => {
        expect(
          resolveApiBaseURL({
            configuredBaseURL:
              "https://api.example.com///",
            isProduction:
              true,
          })
        ).toBe(
          "https://api.example.com"
        );
      }
    );


    it(
      "trims surrounding whitespace",
      () => {
        expect(
          resolveApiBaseURL({
            configuredBaseURL:
              "  https://api.example.com/  ",
            isProduction:
              true,
          })
        ).toBe(
          "https://api.example.com"
        );
      }
    );


    it(
      "rejects malformed URLs",
      () => {
        expect(() => {
          resolveApiBaseURL({
            configuredBaseURL:
              "api.example.com",
            isProduction:
              false,
          });
        }).toThrow(
          "absolute HTTP or HTTPS URL"
        );
      }
    );


    it(
      "rejects unsupported protocols",
      () => {
        expect(() => {
          resolveApiBaseURL({
            configuredBaseURL:
              "ftp://api.example.com",
            isProduction:
              false,
          });
        }).toThrow(
          "must use HTTP or HTTPS"
        );
      }
    );


    it(
      "rejects protocol-relative URLs",
      () => {
        expect(() => {
          resolveApiBaseURL({
            configuredBaseURL:
              "//api.example.com",
            isProduction:
              false,
          });
        }).toThrow(
          "absolute HTTP or HTTPS URL"
        );
      }
    );
  }
);