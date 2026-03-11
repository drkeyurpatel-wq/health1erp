import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createStackNavigator } from "@react-navigation/stack";
import { Ionicons } from "@expo/vector-icons";
import { useAuthStore } from "../store/auth-store";

import { LoginScreen } from "../screens/LoginScreen";
import { DashboardScreen } from "../screens/DashboardScreen";
import { PatientListScreen } from "../screens/PatientListScreen";
import { PatientDetailScreen } from "../screens/PatientDetailScreen";
import { IPDScreen } from "../screens/IPDScreen";
import { IPDDetailScreen } from "../screens/IPDDetailScreen";
import { NursingAssessmentScreen } from "../screens/NursingAssessmentScreen";
import { AppointmentsScreen } from "../screens/AppointmentsScreen";

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function DashboardStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="DashboardHome" component={DashboardScreen} />
    </Stack.Navigator>
  );
}

function PatientStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="PatientList" component={PatientListScreen} options={{ title: "Patients" }} />
      <Stack.Screen name="PatientDetail" component={PatientDetailScreen} options={{ title: "Patient" }} />
    </Stack.Navigator>
  );
}

function IPDStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="IPDHome" component={IPDScreen} options={{ title: "IPD" }} />
      <Stack.Screen name="IPDDetail" component={IPDDetailScreen} options={{ title: "Admission" }} />
      <Stack.Screen name="NursingAssessment" component={NursingAssessmentScreen} options={{ title: "Nursing Assessment" }} />
    </Stack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ color, size }) => {
          const icons: Record<string, string> = {
            Dashboard: "grid-outline",
            Patients: "people-outline",
            IPD: "bed-outline",
            Appointments: "calendar-outline",
          };
          return <Ionicons name={icons[route.name] as any} size={size} color={color} />;
        },
        tabBarActiveTintColor: "#2563eb",
        tabBarInactiveTintColor: "gray",
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardStack} />
      <Tab.Screen name="Patients" component={PatientStack} />
      <Tab.Screen name="IPD" component={IPDStack} />
      <Tab.Screen name="Appointments" component={AppointmentsScreen} />
    </Tab.Navigator>
  );
}

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
    </Stack.Navigator>
  );
}

export function AppNavigator() {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <MainTabs /> : <AuthStack />;
}
