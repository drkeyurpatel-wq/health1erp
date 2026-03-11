import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import * as Localization from "expo-localization";
import en from "./en.json";
import hi from "./hi.json";

i18n.use(initReactI18next).init({
  compatibilityJSON: "v3",
  resources: { en: { translation: en }, hi: { translation: hi } },
  lng: Localization.locale?.split("-")[0] || "en",
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
