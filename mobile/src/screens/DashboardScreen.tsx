import React, { useEffect, useState } from "react";
import { View, ScrollView, StyleSheet, RefreshControl } from "react-native";
import { Text, Card, Button, Chip } from "react-native-paper";
import { useAuthStore } from "../store/auth-store";
import api from "../services/api";

export function DashboardScreen({ navigation }: any) {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<any>(null);
  const [ipd, setIpd] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [s, i] = await Promise.all([
        api.get("/reports/daily-summary"),
        api.get("/ipd/dashboard"),
      ]);
      setStats(s.data);
      setIpd(i.data);
    } catch {}
  };

  useEffect(() => { loadData(); }, []);

  const onRefresh = async () => { setRefreshing(true); await loadData(); setRefreshing(false); };

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <View style={styles.header}>
        <Text variant="headlineSmall" style={styles.greeting}>Welcome, {user?.first_name}</Text>
        <Text variant="bodyMedium" style={styles.role}>{user?.role}</Text>
      </View>

      {/* Stats */}
      <View style={styles.row}>
        <Card style={[styles.statCard, { backgroundColor: "#eff6ff" }]}>
          <Card.Content>
            <Text variant="bodySmall" style={{ color: "#64748b" }}>Patients Today</Text>
            <Text variant="headlineMedium" style={{ fontWeight: "bold", color: "#2563eb" }}>{stats?.total_appointments || 0}</Text>
          </Card.Content>
        </Card>
        <Card style={[styles.statCard, { backgroundColor: "#f0fdfa" }]}>
          <Card.Content>
            <Text variant="bodySmall" style={{ color: "#64748b" }}>Admitted</Text>
            <Text variant="headlineMedium" style={{ fontWeight: "bold", color: "#0d9488" }}>{ipd?.total_admitted || 0}</Text>
          </Card.Content>
        </Card>
      </View>

      <View style={styles.row}>
        <Card style={[styles.statCard, { backgroundColor: "#fef3c7" }]}>
          <Card.Content>
            <Text variant="bodySmall" style={{ color: "#64748b" }}>Occupancy</Text>
            <Text variant="headlineMedium" style={{ fontWeight: "bold", color: "#d97706" }}>{ipd?.occupancy_rate || 0}%</Text>
          </Card.Content>
        </Card>
        <Card style={[styles.statCard, { backgroundColor: "#fef2f2" }]}>
          <Card.Content>
            <Text variant="bodySmall" style={{ color: "#64748b" }}>Critical</Text>
            <Text variant="headlineMedium" style={{ fontWeight: "bold", color: "#ef4444" }}>{ipd?.critical_count || 0}</Text>
          </Card.Content>
        </Card>
      </View>

      {/* Quick Actions */}
      <Text variant="titleMedium" style={styles.sectionTitle}>Quick Actions</Text>
      <View style={styles.actions}>
        <Button mode="outlined" onPress={() => navigation.navigate("IPD")} style={styles.actionBtn}>Admit</Button>
        <Button mode="outlined" onPress={() => navigation.navigate("Patients")} style={styles.actionBtn}>Find Patient</Button>
        <Button mode="outlined" onPress={() => navigation.navigate("Appointments")} style={styles.actionBtn}>Appointments</Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  header: { padding: 20, paddingTop: 60, backgroundColor: "#2563eb" },
  greeting: { color: "#fff", fontWeight: "bold" },
  role: { color: "#bfdbfe" },
  row: { flexDirection: "row", paddingHorizontal: 16, gap: 12, marginTop: 12 },
  statCard: { flex: 1, borderRadius: 12 },
  sectionTitle: { fontWeight: "bold", paddingHorizontal: 16, marginTop: 24, marginBottom: 8 },
  actions: { flexDirection: "row", paddingHorizontal: 16, gap: 8, flexWrap: "wrap" },
  actionBtn: { marginBottom: 8 },
});
