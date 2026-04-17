import { useEffect, useMemo, useRef, useState } from "react";

export const STATES = ["idle", "listening", "thinking", "speaking", "error"];

export function useLyraSocket(url = "ws://127.0.0.1:8000/ws/assistant") {
  const [state, setState] = useState("idle");
  const [text, setText] = useState("Say 'Lyra' and give your command.");
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    socketRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setState("error");
    ws.onmessage = (evt) => {
      const payload = JSON.parse(evt.data);
      if (payload.state && STATES.includes(payload.state)) setState(payload.state);
      if (payload.text) setText(payload.text);
      if (payload.type === "action" && Array.isArray(payload.actions)) {
        payload.actions.forEach((action) => {
          if (action.kind === "open_url" && action.payload) {
            window.open(action.payload, "_blank", "noopener,noreferrer");
          }
        });
      }
    };
    return () => ws.close();
  }, [url]);

  const sendCommand = useMemo(
    () => (command) => {
      const ws = socketRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      ws.send(JSON.stringify({ text: command, source: "voice" }));
    },
    []
  );

  return { state, text, connected, sendCommand };
}
