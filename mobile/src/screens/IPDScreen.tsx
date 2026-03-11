import React, { useEffect, useState } from "react";
import { View, ScrollView, StyleSheet, RefreshControl } from "react-native";
import { Text, Card, FAB, Chip, ProgressBar } from "react-native-paper";
import api from "../services/api";

export function IPDScreen({ navigation }: any) {
  const [dashboard, setDashboard] = useState<any>(null);
  const [admissions, setAdmissions] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [d, a] = await Promise.all([
        api.get("/ipd/dashboard"),
        api.get("/ipd/admissions?status_filter=Admitted"),
      ]);
      setDashboard(d.data);
      setAdmissions(a.data);
    } catch {}
  };

  useEffect(() => { loadData(); }, []);
  const onRefresh = async () => { setRefreshing(true); await loadData(); setRefreshing(false); };

  const riskColor = (score: number) => score >= 0.7 ? "#ef4444" : score >= 0.4 ? "#f59e0b" : "#22c55e";

  return (
    <View style={{ flex: 1 }}>
      <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
        {/* Stats */}
        <View style={styles.statsRow}>
          <Card style={styles.statCard}>
            <Card.Content>
              <Text variant="bodySmall">Admitted</Text>
              <Text variant="headlineMedium" style={{ fontWeight: "bold" }}>{dashboard?.total_admitted || 0}</Text>
            </Card.Content>
          </Card>
          <Card style={styles.statCard}>
            <Card.Content>
              <Text variant="bodySmall">Occupancy</Text>
              <Text variant="headlineMedium" style={{ fontWeight: "bold" }}>{dashboard?.occupancy_rate || 0}%</Text>
            </Card.Content>
          </Card>
          <Card style={styles.statCard}>
            <Card.Content>
              <Text variant="bodySmall">Critical</Text>
              <Text variant="headlineMedium" style={{ fontWeight: "bold", color: "#ef4444" }}>{dashboard?.critical_count || 0}</Text>
            </Card.Content>
          </Card>
        </View>

        {/* Ward Occupancy */}
        <Text variant="titleMedium" style={styles.sectionTitle}>Ward Occupancy</Text>
        {dashboard?.ward_stats?.map((ward: any) => (
          <Card key={ward.ward_id} style={styles.wardCard}>
            <Card.Content>
              <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4 }}>
                <Text variant="bodyMedium" style={{ fontWeight: "600" }}>{ward.ward_name}</Text>
                <Text variant="bodySmall">{ward.occupied}/{ward.total_beds}</Text>
              </View>
              <ProgressBar
                progress={ward.occupancy_rate / 100}
                color={ward.occupancy_rate > 90 ? "#ef4444" : ward.occupancy_rate > 70 ? "#f59e0b" : "#22c55e"}
              />
            </Card.Content>
          </Card>
        ))}

        {/* Admissions */}
        <Text variant="titleMedium" style={styles.sectionTitle}>Active Admissions</Text>
        {admissions.map((a: any) => (
          <Card key={a.id} style={styles.admissionCard} onPress={() => navigation.navigate("IPDDetail", { id: a.id })}>
            <Card.Content>
              <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
                <View>
                  <Text variant="bodyMedium" style={{ fontWeight: "600" }}>#{a.id.slice(0, 8)}</Text>
                  <Text variant="bodySmall" style={{ color: "#64748b" }}>
                    {a.diagnosis_at_admission?.join(", ") || "No diagnosis"}
                  </Text>
                </View>
                {a.ai_risk_score !== undefined && (
                  <Chip compact style={{ backgroundColor: riskColor(a.ai_risk_score) + "20" }}>
                    <Text style={{ color: riskColor(a.ai_risk_score), fontSize: 11 }}>
                      Risk: {(a.ai_risk_score * 100).toFixed(0)}%
                    </Text>
                  </Chip>
                )}
              </View>
            </Card.Content>
          </Card>
        ))}
        <View style={{ height: 80 }} />
      </ScrollView>

      <FAB icon="plus" label="Admit" style={styles.fab} onPress={() => {}} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  statsRow: { flexDirection: "row", padding: 12, gap: 8 },
  statCard: { flex: 1, borderRadius: 12 },
  sectionTitle: { fontWeight: "bold", paddingHorizontal: 16, marginTop: 16, marginBottom: 8 },
  wardCard: { marginHorizontal: 12, marginBottom: 8, borderRadius: 8 },
  admissionCard: { marginHorizontal: 12, marginBottom: 8, borderRadius: 8 },
  fab: { position: "absolute", margin: 16, right: 0, bottom: 0, backgroundColor: "#2563eb" },
});
