"use client";
import React, { useEffect, useState, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ScanLine, Eye, FileText, Brain, RefreshCw,
  ChevronDown, ChevronUp, Maximize2, ZoomIn, ZoomOut,
  RotateCw, FlipHorizontal, Contrast, Ruler, X,
} from "lucide-react";
import { Modal } from "@/components/ui/modal";
import api from "@/lib/api";

interface RadiologyStudy {
  order_id: string;
  exam_name: string;
  modality: string;
  body_part: string | null;
  clinical_indication: string | null;
  status: string;
  ordered_at: string | null;
  report: {
    report_id: string;
    findings: string | null;
    impression: string | null;
    ai_findings: string | null;
  } | null;
  images: string[];
}

interface ViewerConfig {
  windowing_presets: Array<{ name: string; window_center: number; window_width: number }>;
  tools: string[];
}

interface RadiologyViewerProps {
  patientId: string;
  onStudyCount?: (count: number) => void;
}

export function RadiologyViewer({ patientId, onStudyCount }: RadiologyViewerProps) {
  const [studies, setStudies] = useState<RadiologyStudy[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedStudy, setExpandedStudy] = useState<string | null>(null);

  // Viewer state
  const [viewerOpen, setViewerOpen] = useState(false);
  const [viewerData, setViewerData] = useState<any>(null);
  const [viewerLoading, setViewerLoading] = useState(false);
  const [activePreset, setActivePreset] = useState<string>("Default");
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [inverted, setInverted] = useState(false);
  const [flippedH, setFlippedH] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [activeTool, setActiveTool] = useState("window_level");

  const loadStudies = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/radiology/patient/${patientId}/studies?include_pending=true`);
      setStudies(data.studies || []);
      onStudyCount?.(data.total_studies || 0);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, [patientId, onStudyCount]);

  useEffect(() => { loadStudies(); }, [loadStudies]);

  const openViewer = async (orderId: string) => {
    setViewerLoading(true);
    setViewerOpen(true);
    try {
      const { data } = await api.get(`/radiology/viewer/${orderId}`);
      setViewerData(data);
      setActivePreset(data.viewer_config?.windowing_presets?.[0]?.name || "Default");
      setZoom(100);
      setRotation(0);
      setInverted(false);
      setFlippedH(false);
      setCurrentImageIndex(0);
    } catch {
      setViewerData(null);
    } finally {
      setViewerLoading(false);
    }
  };

  const resetViewer = () => {
    setZoom(100);
    setRotation(0);
    setInverted(false);
    setFlippedH(false);
  };

  const modalityColor: Record<string, string> = {
    CT: "bg-blue-100 text-blue-700",
    MRI: "bg-purple-100 text-purple-700",
    XRay: "bg-amber-100 text-amber-700",
    Ultrasound: "bg-emerald-100 text-emerald-700",
    PET: "bg-red-100 text-red-700",
  };

  if (loading) {
    return (
      <div className="space-y-2 animate-pulse">
        {[1, 2].map(i => <div key={i} className="h-10 bg-gray-100 rounded-lg" />)}
      </div>
    );
  }

  if (studies.length === 0) {
    return (
      <div className="text-center py-6">
        <ScanLine className="h-8 w-8 text-gray-300 mx-auto mb-2" />
        <p className="text-sm text-gray-500">No radiology studies available</p>
        <p className="text-xs text-gray-400 mt-1">Studies will appear here once completed</p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Badge variant="secondary" dot>{studies.length} stud{studies.length !== 1 ? "ies" : "y"}</Badge>
          <Button size="sm" variant="ghost" onClick={loadStudies} className="h-7">
            <RefreshCw className="h-3 w-3 mr-1" />Refresh
          </Button>
        </div>

        {studies.map(study => (
          <div key={study.order_id} className="border border-gray-200 rounded-xl overflow-hidden">
            <button
              onClick={() => setExpandedStudy(expandedStudy === study.order_id ? null : study.order_id)}
              className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-2">
                <ScanLine className="h-4 w-4 text-purple-500" />
                <span className="text-sm font-medium">{study.exam_name}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${modalityColor[study.modality] || "bg-gray-100 text-gray-600"}`}>
                  {study.modality}
                </span>
                <Badge variant={study.status === "Completed" ? "success" : "warning"} className="text-[10px]">
                  {study.status}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                {study.ordered_at && (
                  <span className="text-xs text-gray-400">
                    {new Date(study.ordered_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}
                  </span>
                )}
                {expandedStudy === study.order_id ? (
                  <ChevronUp className="h-4 w-4 text-gray-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                )}
              </div>
            </button>

            {expandedStudy === study.order_id && (
              <div className="p-3 space-y-3">
                {study.clinical_indication && (
                  <p className="text-xs text-gray-600">
                    <span className="font-medium">Indication:</span> {study.clinical_indication}
                  </p>
                )}

                {/* Report */}
                {study.report && (
                  <div className="bg-white border border-gray-100 rounded-lg p-3 space-y-2">
                    <div className="flex items-center gap-1">
                      <FileText className="h-3.5 w-3.5 text-gray-600" />
                      <span className="text-xs font-semibold text-gray-700">Radiology Report</span>
                    </div>
                    {study.report.findings && (
                      <div>
                        <p className="text-[10px] font-semibold text-gray-500 uppercase">Findings</p>
                        <p className="text-xs text-gray-700 whitespace-pre-wrap">{study.report.findings}</p>
                      </div>
                    )}
                    {study.report.impression && (
                      <div>
                        <p className="text-[10px] font-semibold text-gray-500 uppercase">Impression</p>
                        <p className="text-xs text-gray-800 font-medium whitespace-pre-wrap">{study.report.impression}</p>
                      </div>
                    )}
                    {study.report.ai_findings && (
                      <div className="bg-blue-50 rounded p-2 border border-blue-100">
                        <div className="flex items-center gap-1 mb-1">
                          <Brain className="h-3 w-3 text-blue-600" />
                          <span className="text-[10px] font-semibold text-blue-700">AI Analysis</span>
                        </div>
                        <p className="text-xs text-blue-700">{study.report.ai_findings}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Image viewer button */}
                {study.images.length > 0 && (
                  <Button
                    size="sm"
                    variant="default"
                    onClick={() => openViewer(study.order_id)}
                    className="w-full"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Open Image Viewer ({study.images.length} image{study.images.length !== 1 ? "s" : ""})
                  </Button>
                )}
                {study.images.length === 0 && study.status === "Completed" && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => openViewer(study.order_id)}
                    className="w-full"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Open Study Viewer
                  </Button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* ── PACS Image Viewer Modal ──────────────────────────────── */}
      <Modal
        open={viewerOpen}
        onClose={() => setViewerOpen(false)}
        title={viewerData ? `${viewerData.exam?.name} — PACS Viewer` : "Loading..."}
        size="full"
      >
        {viewerLoading ? (
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
          </div>
        ) : viewerData ? (
          <div className="flex flex-col h-[80vh]">
            {/* Toolbar */}
            <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-700">
              <div className="flex items-center gap-1">
                {[
                  { tool: "window_level", icon: <Contrast className="h-4 w-4" />, label: "W/L" },
                  { tool: "zoom", icon: <ZoomIn className="h-4 w-4" />, label: "Zoom" },
                  { tool: "measure_length", icon: <Ruler className="h-4 w-4" />, label: "Measure" },
                ].map(t => (
                  <button
                    key={t.tool}
                    onClick={() => setActiveTool(t.tool)}
                    className={`flex items-center gap-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
                      activeTool === t.tool
                        ? "bg-blue-600 text-white"
                        : "text-gray-300 hover:bg-gray-700"
                    }`}
                  >
                    {t.icon}{t.label}
                  </button>
                ))}
                <div className="w-px h-6 bg-gray-700 mx-1" />
                <button onClick={() => setZoom(z => Math.min(z + 25, 400))} className="p-1.5 text-gray-300 hover:bg-gray-700 rounded">
                  <ZoomIn className="h-4 w-4" />
                </button>
                <button onClick={() => setZoom(z => Math.max(z - 25, 25))} className="p-1.5 text-gray-300 hover:bg-gray-700 rounded">
                  <ZoomOut className="h-4 w-4" />
                </button>
                <span className="text-xs text-gray-400 w-12 text-center">{zoom}%</span>
                <div className="w-px h-6 bg-gray-700 mx-1" />
                <button onClick={() => setRotation(r => (r + 90) % 360)} className="p-1.5 text-gray-300 hover:bg-gray-700 rounded" title="Rotate">
                  <RotateCw className="h-4 w-4" />
                </button>
                <button onClick={() => setFlippedH(!flippedH)} className="p-1.5 text-gray-300 hover:bg-gray-700 rounded" title="Flip Horizontal">
                  <FlipHorizontal className="h-4 w-4" />
                </button>
                <button onClick={() => setInverted(!inverted)} className={`p-1.5 rounded ${inverted ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-700"}`} title="Invert">
                  <Contrast className="h-4 w-4" />
                </button>
                <button onClick={resetViewer} className="px-2 py-1.5 text-xs text-gray-300 hover:bg-gray-700 rounded">Reset</button>
              </div>

              {/* Window presets */}
              <div className="flex items-center gap-1">
                {(viewerData.viewer_config?.windowing_presets || []).map((preset: any) => (
                  <button
                    key={preset.name}
                    onClick={() => setActivePreset(preset.name)}
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      activePreset === preset.name
                        ? "bg-amber-600 text-white"
                        : "text-gray-300 hover:bg-gray-700"
                    }`}
                  >
                    {preset.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Image viewport */}
            <div className="flex-1 bg-black flex items-center justify-center relative overflow-hidden">
              {viewerData.images && viewerData.images.length > 0 ? (
                <div
                  className="relative transition-transform duration-200"
                  style={{
                    transform: `scale(${zoom / 100}) rotate(${rotation}deg) ${flippedH ? "scaleX(-1)" : ""}`,
                    filter: inverted ? "invert(1)" : "none",
                  }}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={viewerData.images[currentImageIndex]}
                    alt={`${viewerData.exam?.name} - Image ${currentImageIndex + 1}`}
                    className="max-h-[70vh] object-contain"
                  />
                </div>
              ) : (
                <div className="text-center text-gray-500">
                  <ScanLine className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                  <p className="text-lg font-medium text-gray-400">PACS Viewer</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {viewerData.exam?.name} — {viewerData.exam?.modality}
                  </p>
                  <p className="text-xs text-gray-600 mt-4">
                    Images would be loaded from PACS/DICOM server in production.
                  </p>
                  <p className="text-xs text-gray-600">
                    Configure your PACS integration URL in settings to enable viewing.
                  </p>
                </div>
              )}

              {/* Image navigation */}
              {viewerData.images && viewerData.images.length > 1 && (
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-gray-900/80 rounded-full px-3 py-1.5">
                  <button
                    onClick={() => setCurrentImageIndex(i => Math.max(0, i - 1))}
                    disabled={currentImageIndex === 0}
                    className="text-gray-300 hover:text-white disabled:text-gray-600 text-xs"
                  >
                    Prev
                  </button>
                  <span className="text-xs text-gray-300">
                    {currentImageIndex + 1} / {viewerData.images.length}
                  </span>
                  <button
                    onClick={() => setCurrentImageIndex(i => Math.min(viewerData.images.length - 1, i + 1))}
                    disabled={currentImageIndex >= viewerData.images.length - 1}
                    className="text-gray-300 hover:text-white disabled:text-gray-600 text-xs"
                  >
                    Next
                  </button>
                </div>
              )}

              {/* Study info overlay */}
              <div className="absolute top-3 left-3 text-xs text-gray-400 space-y-1">
                <p>{viewerData.exam?.name}</p>
                <p>{viewerData.exam?.modality} — {viewerData.exam?.body_part || "N/A"}</p>
                <p>Preset: {activePreset}</p>
              </div>
            </div>

            {/* Report panel at bottom */}
            {viewerData.report && (
              <div className="px-4 py-3 bg-gray-900 border-t border-gray-700 max-h-40 overflow-y-auto">
                <div className="grid grid-cols-2 gap-4">
                  {viewerData.report.findings && (
                    <div>
                      <p className="text-[10px] font-semibold text-gray-400 uppercase">Findings</p>
                      <p className="text-xs text-gray-200 whitespace-pre-wrap">{viewerData.report.findings}</p>
                    </div>
                  )}
                  {viewerData.report.impression && (
                    <div>
                      <p className="text-[10px] font-semibold text-amber-400 uppercase">Impression</p>
                      <p className="text-xs text-gray-200 font-medium whitespace-pre-wrap">{viewerData.report.impression}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">Failed to load viewer data.</div>
        )}
      </Modal>
    </>
  );
}
