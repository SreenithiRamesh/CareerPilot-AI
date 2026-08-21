import axios from "axios";


const apiBaseURL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


const api = axios.create({
  baseURL: apiBaseURL,

  headers: {
    "Content-Type": "application/json",
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