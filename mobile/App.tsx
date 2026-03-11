import React, { useEffect } from "react";
import { StatusBar } from "expo-status-bar";
import { Provider as PaperProvider, MD3LightTheme } from "react-native-paper";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NavigationContainer } from "@react-navigation/native";
import { AppNavigator } from "./src/navigation/AppNavigator";
import { useAuthStore } from "./src/store/auth-store";
import "./src/i18n";

const queryClient = new QueryClient();

const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: "#2563eb",
    secondary: "#0d9488",
    error: "#ef4444",
  },
};

export default function App() {
  const { loadToken } = useAuthStore();

  useEffect(() => {
    loadToken();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <PaperProvider theme={theme}>
        <NavigationContainer>
          <AppNavigator />
          <StatusBar style="auto" />
        </NavigationContainer>
      </PaperProvider>
    </QueryClientProvider>
  );
}
