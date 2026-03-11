"use client";
import React, { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Settings, Hospital, Bell, Shield, Globe, Check } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import { useToast } from "@/contexts/toast-context";

export default function SettingsPage() {
  const { user } = useAuthStore();
  const { toast } = useToast();
  const [hospitalName, setHospitalName] = useState("Health1ERP Hospital");
  const [hospitalPhone, setHospitalPhone] = useState("+91 98765 43210");
  const [hospitalEmail, setHospitalEmail] = useState("admin@health1erp.com");
  const [hospitalAddress, setHospitalAddress] = useState("123 Medical Avenue, Mumbai, India");
  const [notifications, setNotifications] = useState({ email: true, sms: true, push: true, whatsapp: false });
  const [language, setLanguage] = useState("en");

  const handleSave = (section: string) => {
    toast("success", "Settings Saved", `${section} settings have been updated`);
  };

  return (
    <AppShell>
      <div className="page-header">
        <div><h1 className="page-title">Settings</h1><p className="page-subtitle">Configure hospital and account preferences</p></div>
      </div>

      <Tabs defaultValue="hospital">
        <TabsList>
          <TabsTrigger value="hospital"><Hospital className="h-4 w-4 mr-1.5" />Hospital</TabsTrigger>
          <TabsTrigger value="profile"><Settings className="h-4 w-4 mr-1.5" />Profile</TabsTrigger>
          <TabsTrigger value="notifications"><Bell className="h-4 w-4 mr-1.5" />Notifications</TabsTrigger>
          <TabsTrigger value="security"><Shield className="h-4 w-4 mr-1.5" />Security</TabsTrigger>
          <TabsTrigger value="language"><Globe className="h-4 w-4 mr-1.5" />Language</TabsTrigger>
        </TabsList>

        <TabsContent value="hospital">
          <Card><CardHeader><CardTitle>Hospital Information</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><label className="block text-sm font-medium text-gray-600 mb-1">Hospital Name</label><Input value={hospitalName} onChange={e => setHospitalName(e.target.value)} /></div>
                <div><label className="block text-sm font-medium text-gray-600 mb-1">Phone</label><Input value={hospitalPhone} onChange={e => setHospitalPhone(e.target.value)} /></div>
                <div><label className="block text-sm font-medium text-gray-600 mb-1">Email</label><Input value={hospitalEmail} onChange={e => setHospitalEmail(e.target.value)} /></div>
                <div><label className="block text-sm font-medium text-gray-600 mb-1">Address</label><Input value={hospitalAddress} onChange={e => setHospitalAddress(e.target.value)} /></div>
              </div>
              <Button variant="gradient" onClick={() => handleSave("Hospital")}>Save Changes</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="profile">
          <Card><CardHeader><CardTitle>My Profile</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center gap-6 mb-8">
                <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                  {user?.first_name?.[0]}{user?.last_name?.[0]}
                </div>
                <div>
                  <h2 className="text-xl font-bold">{user?.first_name} {user?.last_name}</h2>
                  <p className="text-gray-500">{user?.email}</p>
                  <Badge className="mt-1.5">{user?.role}</Badge>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><label className="block text-sm font-medium text-gray-600 mb-1">First Name</label><Input defaultValue={user?.first_name} /></div>
                <div><label className="block text-sm font-medium text-gray-600 mb-1">Last Name</label><Input defaultValue={user?.last_name} /></div>
                <div><label className="block text-sm font-medium text-gray-600 mb-1">Email</label><Input defaultValue={user?.email} /></div>
                <div><label className="block text-sm font-medium text-gray-600 mb-1">Phone</label><Input defaultValue={user?.phone || ""} /></div>
              </div>
              <Button variant="gradient" className="mt-4" onClick={() => handleSave("Profile")}>Update Profile</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card><CardHeader><CardTitle>Notification Preferences</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(notifications).map(([key, enabled]) => (
                <div key={key} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-gray-200 transition-colors">
                  <div>
                    <p className="font-medium capitalize text-gray-900">{key} Notifications</p>
                    <p className="text-sm text-gray-500">Receive notifications via {key}</p>
                  </div>
                  <button
                    onClick={() => setNotifications(prev => ({ ...prev, [key]: !prev[key as keyof typeof prev] }))}
                    className={`relative w-12 h-6 rounded-full transition-colors duration-200 ${enabled ? "bg-primary-600" : "bg-gray-300"}`}
                  >
                    <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${enabled ? "translate-x-6" : ""}`} />
                  </button>
                </div>
              ))}
              <Button variant="gradient" onClick={() => handleSave("Notifications")}>Save Preferences</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security">
          <Card><CardHeader><CardTitle>Security Settings</CardTitle></CardHeader>
            <CardContent className="space-y-4 max-w-lg">
              <div><label className="block text-sm font-medium text-gray-600 mb-1">Current Password</label><Input type="password" placeholder="Enter current password" /></div>
              <div><label className="block text-sm font-medium text-gray-600 mb-1">New Password</label><Input type="password" placeholder="Enter new password" /></div>
              <div><label className="block text-sm font-medium text-gray-600 mb-1">Confirm New Password</label><Input type="password" placeholder="Confirm new password" /></div>
              <Button variant="gradient" onClick={() => handleSave("Password")}>Change Password</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="language">
          <Card><CardHeader><CardTitle>Language & Localization</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3 max-w-lg">
                {[
                  { code: "en", label: "English", native: "English" },
                  { code: "hi", label: "Hindi", native: "हिन्दी" },
                  { code: "ar", label: "Arabic", native: "العربية" },
                  { code: "es", label: "Spanish", native: "Español" },
                  { code: "fr", label: "French", native: "Français" },
                  { code: "zh", label: "Chinese", native: "中文" },
                ].map(lang => (
                  <button
                    key={lang.code}
                    onClick={() => { setLanguage(lang.code); localStorage.setItem("language", lang.code); toast("success", "Language Changed", `Interface language set to ${lang.label}`); }}
                    className={`w-full flex items-center justify-between p-4 rounded-xl border transition-all duration-200 ${language === lang.code ? "border-primary-500 bg-primary-50 shadow-sm" : "border-gray-100 hover:bg-gray-50 hover:border-gray-200"}`}
                  >
                    <div className="text-left"><p className="font-medium text-gray-900">{lang.label}</p><p className="text-sm text-gray-500">{lang.native}</p></div>
                    {language === lang.code && <div className="h-6 w-6 rounded-full bg-primary-600 flex items-center justify-center"><Check className="h-3.5 w-3.5 text-white" /></div>}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}
