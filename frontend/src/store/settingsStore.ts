"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { DEFAULT_LOCALE, SETTINGS_STORAGE_KEY } from "@/lib/constants";
import type { Locale } from "@/types/common";

export type FanarModelPreference = "auto" | "sadiq" | "c2" | "guard";

interface SettingsState {
  locale: Locale;
  sidebarCollapsed: boolean;
  mobileSidebarOpen: boolean;
  showAdvancedMetrics: boolean;
  evaluationMode: boolean;
  advancedAnalysisMode: boolean;
  fanarModelPreference: FanarModelPreference;
  setLocale: (locale: Locale) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setMobileSidebarOpen: (open: boolean) => void;
  setShowAdvancedMetrics: (show: boolean) => void;
  setEvaluationMode: (enabled: boolean) => void;
  setAdvancedAnalysisMode: (enabled: boolean) => void;
  setFanarModelPreference: (model: FanarModelPreference) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      locale: DEFAULT_LOCALE,
      sidebarCollapsed: false,
      mobileSidebarOpen: false,
      showAdvancedMetrics: false,
      evaluationMode: false,
      advancedAnalysisMode: false,
      fanarModelPreference: "auto" as FanarModelPreference,
      setLocale: (locale) => set({ locale }),
      setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
      setMobileSidebarOpen: (mobileSidebarOpen) => set({ mobileSidebarOpen }),
      setShowAdvancedMetrics: (showAdvancedMetrics) => set({ showAdvancedMetrics }),
      setEvaluationMode: (evaluationMode) => set({ evaluationMode }),
      setAdvancedAnalysisMode: (advancedAnalysisMode) => set({ advancedAnalysisMode }),
      setFanarModelPreference: (fanarModelPreference) => set({ fanarModelPreference }),
    }),
    {
      name: SETTINGS_STORAGE_KEY,
      partialize: (state) => ({
        locale: state.locale,
        sidebarCollapsed: state.sidebarCollapsed,
        showAdvancedMetrics: state.showAdvancedMetrics,
        evaluationMode: state.evaluationMode,
        advancedAnalysisMode: state.advancedAnalysisMode,
        fanarModelPreference: state.fanarModelPreference,
      }),
    },
  ),
);
