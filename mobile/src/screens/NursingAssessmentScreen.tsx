import React, { useState } from "react";
import { View, ScrollView, StyleSheet, Alert } from "react-native";
import { Text, TextInput, Button, Card, Chip } from "react-native-paper";
import api from "../services/api";

export function NursingAssessmentScreen({ route, navigation }: any) {
  const { admissionId } = route.params;
  const [loading, setLoading] = useState(false);
  const [vitals, setVitals] = useState({
    temperature: "", bp_systolic: "", bp_diastolic: "",
    pulse: "", spo2: "", respiratory_rate: "",
    pain_score: "", gcs: "",
  });
  const [notes, setNotes] = useState("");

  const updateVital = (key: string, value: string) => setVitals({ ...vitals, [key]: value });

  const submit = async () => {
    setLoading(true);
    try {
      const vitalsPayload: Record<string, number | undefined> = {};
      for (const [k, v] of Object.entries(vitals)) {
        if (v) vitalsPayload[k] = parseFloat(v);
      }
      const { data } = await api.post(`/ipd/admissions/${admissionId}/nursing`, {
        assessment_datetime: new Date().toISOString(),
        vitals: vitalsPayload,
        notes: notes || undefined,
      });
      const ews = data.ai_early_warning_score;
      if (ews !== null && ews >= 7) {
        Alert.alert("Critical Alert", `High Early Warning Score: ${ews}. Immediate attention required!`);
      } else {
        Alert.alert("Success", `Assessment saved. EWS: ${ews || "N/A"}`);
      }
      navigation.goBack();
    } catch (err: any) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to save");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={{ fontWeight: "bold", marginBottom: 16 }}>Vitals</Text>
          <View style={styles.row}>
            <TextInput label="Temp (C)" value={vitals.temperature} onChangeText={v => updateVital("temperature", v)} mode="outlined" keyboardType="decimal-pad" style={styles.input} />
            <TextInput label="BP Sys" value={vitals.bp_systolic} onChangeText={v => updateVital("bp_systolic", v)} mode="outlined" keyboardType="number-pad" style={styles.input} />
          </View>
          <View style={styles.row}>
            <TextInput label="BP Dia" value={vitals.bp_diastolic} onChangeText={v => updateVital("bp_diastolic", v)} mode="outlined" keyboardType="number-pad" style={styles.input} />
            <TextInput label="Pulse" value={vitals.pulse} onChangeText={v => updateVital("pulse", v)} mode="outlined" keyboardType="number-pad" style={styles.input} />
          </View>
          <View style={styles.row}>
            <TextInput label="SpO2 (%)" value={vitals.spo2} onChangeText={v => updateVital("spo2", v)} mode="outlined" keyboardType="decimal-pad" style={styles.input} />
            <TextInput label="Resp Rate" value={vitals.respiratory_rate} onChangeText={v => updateVital("respiratory_rate", v)} mode="outlined" keyboardType="number-pad" style={styles.input} />
          </View>
          <View style={styles.row}>
            <TextInput label="Pain (0-10)" value={vitals.pain_score} onChangeText={v => updateVital("pain_score", v)} mode="outlined" keyboardType="number-pad" style={styles.input} />
            <TextInput label="GCS (3-15)" value={vitals.gcs} onChangeText={v => updateVital("gcs", v)} mode="outlined" keyboardType="number-pad" style={styles.input} />
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <TextInput label="Notes" value={notes} onChangeText={setNotes} mode="outlined" multiline numberOfLines={3} />
        </Card.Content>
      </Card>

      <View style={styles.info}>
        <Chip icon="brain">AI will auto-calculate Early Warning Score (NEWS2)</Chip>
      </View>

      <Button mode="contained" onPress={submit} loading={loading} style={styles.submitBtn}>
        Save Assessment
      </Button>
      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  card: { margin: 12, marginBottom: 0, borderRadius: 12 },
  row: { flexDirection: "row", gap: 12, marginBottom: 8 },
  input: { flex: 1 },
  info: { padding: 12 },
  submitBtn: { margin: 12 },
});
