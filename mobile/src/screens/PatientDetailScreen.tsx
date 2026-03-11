import React, { useEffect, useState } from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import { Text, Card, Chip, Button, Divider } from "react-native-paper";
import api from "../services/api";

export function PatientDetailScreen({ route }: any) {
  const { id } = route.params;
  const [patient, setPatient] = useState<any>(null);

  useEffect(() => {
    api.get(`/patients/${id}`).then(r => setPatient(r.data)).catch(() => {});
  }, [id]);

  if (!patient) return <View style={styles.container}><Text>Loading...</Text></View>;

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.headerCard}>
        <Card.Content>
          <Text variant="headlineSmall" style={{ fontWeight: "bold" }}>{patient.first_name} {patient.last_name}</Text>
          <View style={styles.chips}>
            <Chip compact>{patient.uhid}</Chip>
            <Chip compact>{patient.gender}</Chip>
            {patient.blood_group && <Chip compact>{patient.blood_group}</Chip>}
          </View>
          <Divider style={{ marginVertical: 12 }} />
          <Text variant="bodyMedium">Phone: {patient.phone}</Text>
          {patient.email && <Text variant="bodyMedium">Email: {patient.email}</Text>}
          <Text variant="bodyMedium">DOB: {patient.date_of_birth}</Text>
          {patient.allergies?.length > 0 && (
            <View style={{ marginTop: 8 }}>
              <Text variant="bodySmall" style={{ color: "#ef4444", fontWeight: "bold" }}>
                Allergies: {patient.allergies.join(", ")}
              </Text>
            </View>
          )}
        </Card.Content>
      </Card>

      <View style={styles.actions}>
        <Button mode="contained" style={styles.actionBtn}>Admit</Button>
        <Button mode="outlined" style={styles.actionBtn}>Order Lab</Button>
        <Button mode="outlined" style={styles.actionBtn}>Prescribe</Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  headerCard: { margin: 12, borderRadius: 12 },
  chips: { flexDirection: "row", gap: 8, marginTop: 8 },
  actions: { flexDirection: "row", paddingHorizontal: 12, gap: 8, marginTop: 8 },
  actionBtn: { flex: 1 },
});
