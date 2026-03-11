import axios from "axios";
import * as SecureStore from "expo-secure-store";

const API_URL = "http://localhost:8000/api/v1";

const api = axios.create({ baseURL: API_URL, headers: { "Content-Type": "application/json" } });

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await SecureStore.deleteItemAsync("access_token");
      await SecureStore.deleteItemAsync("refresh_token");
    }
    return Promise.reject(error);
  }
);

export default api;
