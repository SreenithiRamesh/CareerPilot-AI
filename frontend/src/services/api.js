import axios from "axios";

import {
  resolveApiBaseURL,
} from "../utils/apiBaseURL";


const apiBaseURL = resolveApiBaseURL({
  configuredBaseURL:
    import.meta.env.VITE_API_BASE_URL,
  isProduction:
    import.meta.env.PROD,
});

const apiHostname =
  new URL(apiBaseURL).hostname;

const usesNgrokFreeDomain =
  apiHostname.endsWith(
    ".ngrok-free.dev"
  );

const api = axios.create({
  baseURL: apiBaseURL,

  headers: {
    "Content-Type": "application/json",

    ...(usesNgrokFreeDomain
      ? {
          "ngrok-skip-browser-warning":
            "true",
        }
      : {}),
  },
});


api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem(
        "careerpilot_token"
      );

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  }
);


export default api;
