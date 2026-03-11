"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Heart, Eye, EyeOff, ArrowRight, Shield, Brain, Globe, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/store/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email.trim() || !password.trim()) { setError("Please fill in all fields"); return; }
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const features = [
    { icon: Brain, title: "AI-Powered CDSS", desc: "Clinical decision support with risk scoring" },
    { icon: Activity, title: "Real-time Monitoring", desc: "Live bed management and vitals tracking" },
    { icon: Globe, title: "Multilingual", desc: "6 languages with medical translation" },
    { icon: Shield, title: "Enterprise Security", desc: "Role-based access with audit logging" },
  ];

  return (
    <div className="min-h-screen flex">
      {/* Left - Branding Panel */}
      <div className="hidden lg:flex lg:w-[55%] bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 text-white p-12 flex-col justify-between relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 h-64 w-64 rounded-full bg-white/20 blur-3xl" />
          <div className="absolute bottom-20 right-20 h-96 w-96 rounded-full bg-teal-400/20 blur-3xl" />
          <div className="absolute top-1/2 left-1/2 h-48 w-48 rounded-full bg-blue-300/20 blur-2xl" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Heart className="h-6 w-6" />
            </div>
            <div>
              <span className="text-2xl font-bold tracking-tight">Health1ERP</span>
              <p className="text-xs text-blue-200">v2.0 Enterprise</p>
            </div>
          </div>
        </div>

        <div className="relative z-10 max-w-lg">
          <h2 className="text-4xl font-bold mb-4 leading-tight">
            Next-Gen Hospital<br />Management System
          </h2>
          <p className="text-blue-100 text-lg mb-10 leading-relaxed">
            AI-powered clinical decision support, real-time bed management,
            multilingual discharge summaries, and complete hospital workflow automation.
          </p>

          <div className="grid grid-cols-2 gap-4">
            {features.map(f => (
              <div key={f.title} className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <f.icon className="h-5 w-5 text-teal-300 mb-2" />
                <h3 className="text-sm font-semibold mb-1">{f.title}</h3>
                <p className="text-xs text-blue-200">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <p className="text-blue-300 text-sm relative z-10">
          Trusted by 500+ healthcare providers worldwide
        </p>
      </div>

      {/* Right - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-10">
            <div className="h-10 w-10 rounded-xl bg-primary-600 flex items-center justify-center">
              <Heart className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">Health1ERP</span>
          </div>

          <div className="bg-white rounded-2xl shadow-card p-8 border border-gray-100">
            <h1 className="text-2xl font-bold text-gray-900 mb-1">Welcome back</h1>
            <p className="text-gray-500 text-sm mb-8">Sign in to access your hospital dashboard</p>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="bg-red-50 text-red-700 px-4 py-3 rounded-xl text-sm border border-red-100 flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-red-500 shrink-0" />
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Email Address</label>
                <Input
                  type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@health1erp.com" required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={password} onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password" required
                    className="pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                  <span className="text-gray-600">Remember me</span>
                </label>
                <a href="#" className="text-sm text-primary-600 hover:text-primary-700 font-medium">Forgot password?</a>
              </div>

              <Button type="submit" className="w-full" loading={loading} variant="gradient" size="lg">
                Sign in <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </form>

            <div className="mt-6 p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-xs font-medium text-gray-500 mb-2">Demo Credentials</p>
              <div className="space-y-1 text-xs text-gray-600">
                <p><span className="font-medium">Admin:</span> admin@health1erp.com / Admin@123</p>
                <p><span className="font-medium">Doctor:</span> doctor@health1erp.com / Doctor@123</p>
                <p><span className="font-medium">Nurse:</span> nurse@health1erp.com / Nurse@123</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
