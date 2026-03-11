import React, { useEffect, useState } from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import { Text, Card, Chip, Button, Divider } from "react-native-paper";
import api from "../services/api";

export function IPDDetailScreen({ route, navigation }: any) {
  const { id } = route.params;
  const [admission, setAdmission] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);
  const [rounds, setRounds] = useState<any[]>([]);

  useEffect(() => {
    api.get(`/ipd/admissions/${id}`).then(r => setAdmission(r.data)).catch(() => {});
    api.get(`/ipd/admissions/${id}/ai-insights`).then(r => setInsights(r.data)).catch(() => {});
    api.get(`/ipd/admissions/${id}/rounds`).then(r => setRounds(r.data)).catch(() => {});
  }, [id]);

  if (!admission) return <View style={styles.container}><Text>Loading...</Text></View>;

  const riskColor = insights?.risk_score >= 0.7 ? "#ef4444" : insights?.risk_score >= 0.4 ? "#f59e0b" : "#22c55e";

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
            <View>
              <Text variant="titleLarge" style={{ fontWeight: "bold" }}>Admission</Text>
              <Text variant="bodySmall" style={{ color: "#64748b" }}>{admission.admission_type} | {admission.status}</Text>
            </View>
            {insights && (
              <View style={[styles.riskBadge, { backgroundColor: riskColor + "15" }]}>
                <Text style={{ color: riskColor, fontWeight: "bold", fontSize: 18 }}>
                  {(insights.risk_score * 100).toFixed(0)}%
                </Text>
                <Text style={{ color: riskColor, fontSize: 10 }}>AI Risk</Text>
              </View>
            )}
          </View>
          <View style={{ flexDirection: "row", gap: 8, marginTop: 8 }}>
            {admission.diagnosis_at_admission?.map((d: string, i: number) => (
              <Chip key={i} compact>{d}</Chip>
            ))}
          </View>
        </Card.Content>
      </Card>

      {/* AI Recommendations */}
      {insights?.recommendations?.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: "bold", marginBottom: 8 }}>AI Recommendations</Text>
            {insights.recommendations.map((r: string, i: number) => (
              <Text key={i} variant="bodySmall" style={{ marginBottom: 4, color: "#334155" }}>
                {"\u2022"} {r}
              </Text>
            ))}
          </Card.Content>
        </Card>
      )}

      {/* Actions */}
      <View style={styles.actions}>
        <Button mode="contained" onPress={() => navigation.navigate("NursingAssessment", { admissionId: id })}>
          Add Nursing Assessment
        </Button>
        <Button mode="outlined" style={{ marginTop: 8 }}>Add Doctor Round</Button>
        <Button mode="outlined" style={{ marginTop: 8 }}>Discharge</Button>
      </View>

      {/* Rounds */}
      <Text variant="titleMedium" style={styles.sectionTitle}>Recent Rounds</Text>
      {rounds.map((round: any) => (
        <Card key={round.id} style={styles.card}>
          <Card.Content>
            <Text variant="bodySmall" style={{ color: "#64748b" }}>{round.round_datetime}</Text>
            <Text variant="bodyMedium" style={{ marginTop: 4 }}>{round.findings || "No findings"}</Text>
            {round.instructions && <Text variant="bodySmall" style={{ color: "#334155", marginTop: 4 }}>Instructions: {round.instructions}</Text>}
          </Card.Content>
        </Card>
      ))}
      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  card: { margin: 12, marginBottom: 0, borderRadius: 12 },
  riskBadge: { alignItems: "center", justifyContent: "center", padding: 12, borderRadius: 12 },
  actions: { padding: 12 },
  sectionTitle: { fontWeight: "bold", paddingHorizontal: 16, marginTop: 16, marginBottom: 4 },
});
