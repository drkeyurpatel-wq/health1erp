import React, { useEffect, useState } from "react";
import { View, FlatList, StyleSheet, RefreshControl } from "react-native";
import { Text, Card, Chip, FAB, Avatar } from "react-native-paper";
import api from "../services/api";

export function AppointmentsScreen() {
  const [queue, setQueue] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const { data } = await api.get("/appointments/queue");
      setQueue(data);
    } catch {}
  };

  useEffect(() => { loadData(); }, []);
  const onRefresh = async () => { setRefreshing(true); await loadData(); setRefreshing(false); };

  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <View style={styles.header}>
        <Text variant="headlineSmall" style={{ fontWeight: "bold" }}>Today's Queue</Text>
      </View>
      <FlatList
        data={queue}
        keyExtractor={item => item.appointment_id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        renderItem={({ item }) => (
          <Card style={styles.card}>
            <Card.Content style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
              <Avatar.Text size={40} label={String(item.token_number)} style={{ backgroundColor: "#2563eb" }} />
              <View style={{ flex: 1 }}>
                <Text variant="bodyLarge" style={{ fontWeight: "600" }}>{item.patient_name}</Text>
                <Text variant="bodySmall" style={{ color: "#64748b" }}>{item.doctor_name}</Text>
              </View>
              <Chip compact style={{ backgroundColor: item.status === "InProgress" ? "#fef3c7" : "#eff6ff" }}>
                {item.status}
              </Chip>
            </Card.Content>
          </Card>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No patients in queue</Text>}
      />
      <FAB icon="plus" label="Book" style={styles.fab} onPress={() => {}} />
    </View>
  );
}

const styles = StyleSheet.create({
  header: { padding: 16, paddingTop: 60 },
  card: { marginHorizontal: 12, marginBottom: 8, borderRadius: 8 },
  empty: { textAlign: "center", padding: 40, color: "#94a3b8" },
  fab: { position: "absolute", margin: 16, right: 0, bottom: 0, backgroundColor: "#2563eb" },
});
