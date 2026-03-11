"use client";
import { useEffect, useRef } from "react";

export function useRealtime(eventType: string, callback: (data: any) => void) {
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    const ws = new WebSocket(`${wsUrl}/api/v1/ipd/ws/bed-status`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === eventType) {
          callback(message.data);
        }
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      // Reconnect after 5 seconds
      setTimeout(() => {
        if (wsRef.current?.readyState === WebSocket.CLOSED) {
          wsRef.current = new WebSocket(`${wsUrl}/api/v1/ipd/ws/bed-status`);
        }
      }, 5000);
    };

    return () => {
      ws.close();
    };
  }, [eventType, callback]);
}
