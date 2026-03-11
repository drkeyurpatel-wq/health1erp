import React, { useState } from "react";
import { View, StyleSheet, KeyboardAvoidingView, Platform } from "react-native";
import { TextInput, Button, Text, Surface } from "react-native-paper";
import { useAuthStore } from "../store/auth-store";

export function LoginScreen() {
  const { login } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError("");
    setLoading(true);
    try {
      await login(email, password);
    } catch {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={styles.header}>
        <Text variant="headlineLarge" style={styles.title}>Health1ERP</Text>
        <Text variant="bodyLarge" style={styles.subtitle}>Hospital Management System</Text>
      </View>
      <Surface style={styles.card}>
        <Text variant="titleLarge" style={styles.cardTitle}>Sign In</Text>
        {error ? <Text style={styles.error}>{error}</Text> : null}
        <TextInput label="Email" value={email} onChangeText={setEmail} mode="outlined" keyboardType="email-address" autoCapitalize="none" style={styles.input} />
        <TextInput label="Password" value={password} onChangeText={setPassword} mode="outlined" secureTextEntry style={styles.input} />
        <Button mode="contained" onPress={handleLogin} loading={loading} style={styles.button}>Sign In</Button>
      </Surface>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24, backgroundColor: "#f8fafc" },
  header: { alignItems: "center", marginBottom: 32 },
  title: { fontWeight: "bold", color: "#2563eb" },
  subtitle: { color: "#64748b", marginTop: 4 },
  card: { padding: 24, borderRadius: 16, elevation: 2 },
  cardTitle: { fontWeight: "bold", marginBottom: 16 },
  input: { marginBottom: 12 },
  button: { marginTop: 8 },
  error: { color: "#ef4444", marginBottom: 12 },
});
