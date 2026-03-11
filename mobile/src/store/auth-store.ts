import { create } from "zustand";
import * as SecureStore from "expo-secure-store";
import api from "../services/api";

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loadToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  token: null,

  login: async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    await SecureStore.setItemAsync("access_token", data.access_token);
    await SecureStore.setItemAsync("refresh_token", data.refresh_token);
    const { data: user } = await api.get("/auth/me");
    set({ isAuthenticated: true, token: data.access_token, user });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync("access_token");
    await SecureStore.deleteItemAsync("refresh_token");
    set({ isAuthenticated: false, user: null, token: null });
  },

  loadToken: async () => {
    const token = await SecureStore.getItemAsync("access_token");
    if (token) {
      try {
        const { data: user } = await api.get("/auth/me");
        set({ isAuthenticated: true, token, user });
      } catch {
        set({ isAuthenticated: false });
      }
    }
  },
}));
