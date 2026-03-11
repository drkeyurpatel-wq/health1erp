import React, { useEffect, useState } from "react";
import { View, FlatList, StyleSheet } from "react-native";
import { Searchbar, List, Text, Avatar, Chip } from "react-native-paper";
import api from "../services/api";

export function PatientListScreen({ navigation }: any) {
  const [patients, setPatients] = useState<any[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const params = search ? `?q=${search}` : "";
    api.get(`/patients${params}`).then(r => setPatients(r.data.items || [])).catch(() => {});
  }, [search]);

  return (
    <View style={styles.container}>
      <Searchbar placeholder="Search by name, UHID, phone..." value={search} onChangeText={setSearch} style={styles.search} />
      <FlatList
        data={patients}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <List.Item
            title={`${item.first_name} ${item.last_name}`}
            description={`${item.uhid} | ${item.phone} | ${item.gender}`}
            left={() => (
              <Avatar.Text size={40} label={`${item.first_name[0]}${item.last_name[0]}`} style={{ marginLeft: 8 }} />
            )}
            right={() => item.blood_group ? <Chip compact>{item.blood_group}</Chip> : null}
            onPress={() => navigation.navigate("PatientDetail", { id: item.id })}
            style={styles.item}
          />
        )}
        ListEmptyComponent={<Text style={styles.empty}>No patients found</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  search: { margin: 12, borderRadius: 12 },
  item: { backgroundColor: "#fff", marginHorizontal: 12, marginBottom: 4, borderRadius: 8 },
  empty: { textAlign: "center", padding: 40, color: "#94a3b8" },
});
