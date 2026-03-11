import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const http = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let queue = [];

function resolveQueue(newToken) {
  queue.forEach((p) => p.resolve(newToken));
  queue = [];
}

function rejectQueue(err) {
  queue.forEach((p) => p.reject(err));
  queue = [];
}

async function doRefresh() {
  const refreshToken = localStorage.getItem("refresh_token");

  const res = await axios.post(
    `${API_BASE_URL}/api/v1/auth/refresh`,
    refreshToken ? { refresh_token: refreshToken } : undefined,
    { withCredentials: true }
  );

  const data = res.data;
  if (!data?.access_token) throw new Error("No access_token on refresh");

  localStorage.setItem("access_token", data.access_token);
  if (data.refresh_token) localStorage.setItem("refresh_token", data.refresh_token);

  return data.access_token;
}

http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({
            resolve: (newToken) => {
              original.headers.Authorization = `Bearer ${newToken}`;
              resolve(http(original));
            },
            reject,
          });
        });
      }

      isRefreshing = true;
      try {
        const newToken = await doRefresh();
        resolveQueue(newToken);
        original.headers.Authorization = `Bearer ${newToken}`;
        return http(original);
      } catch (e) {
        rejectQueue(e);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
