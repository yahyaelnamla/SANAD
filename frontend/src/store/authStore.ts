"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { AUTH_TOKEN_STORAGE_KEY } from "@/lib/constants";
import { ApiClientError } from "@/services/apiClient";
import * as authService from "@/services/authService";
import * as saasService from "@/services/saasService";
import { useConversationStore } from "@/store/conversationStore";
import { useOfflineQueryStore } from "@/store/offlineQueryStore";
import type { LoginPayload, RegisterPayload, UserProfile } from "@/types/auth";

interface AuthState {
  accessToken: string | null;
  user: UserProfile | null;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  completeSso: (payload: {
    provider: "google" | "microsoft";
    session_id?: string;
    code?: string;
    email?: string;
  }) => Promise<boolean>;
  logout: () => void;
  hydrateProfile: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      user: null,
      isLoading: false,

      login: async (payload) => {
        set({ isLoading: true });
        try {
          const tokenResponse = await authService.login(payload);
          set({ accessToken: tokenResponse.access_token });
          const profile = await authService.getProfile(tokenResponse.access_token);
          useConversationStore.getState().bindSessionToUser(profile.id);
          set({ user: profile });
        } finally {
          set({ isLoading: false });
        }
      },

      register: async (payload) => {
        set({ isLoading: true });
        try {
          await authService.register(payload);
          await get().login({ email: payload.email, password: payload.password });
        } finally {
          set({ isLoading: false });
        }
      },

      completeSso: async (payload) => {
        set({ isLoading: true });
        try {
          const response = await saasService.completeSso(payload);
          set({ accessToken: response.access_token });
          const profile = await authService.getProfile(response.access_token);
          useConversationStore.getState().bindSessionToUser(profile.id);
          set({ user: profile });
          return response.is_new_user || !profile.onboarding_completed;
        } finally {
          set({ isLoading: false });
        }
      },

      logout: () => {
        useConversationStore.getState().clearForUserChange();
        useOfflineQueryStore.getState().clear();
        set({ accessToken: null, user: null });
      },

      hydrateProfile: async () => {
        const token = get().accessToken;
        if (!token) return;
        try {
          const profile = await authService.getProfile(token);
          set({ user: profile });
        } catch (err) {
          if (err instanceof ApiClientError && err.status === 401) {
            get().logout();
          }
        }
      },
    }),
    {
      name: AUTH_TOKEN_STORAGE_KEY,
      partialize: (state) => ({ accessToken: state.accessToken, user: state.user }),
    },
  ),
);
