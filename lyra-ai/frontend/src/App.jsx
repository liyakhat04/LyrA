import { motion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import LyraOrb from "./components/LyraOrb";
import { useLyraSocket } from "./hooks/useLyraSocket";

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function Waveform({ active }) {
  const bars = useMemo(() => Array.from({ length: 24 }, (_, i) => i), []);
  return (
    <div className="waveform">
      {bars.map((b) => (
        <motion.span
          key={b}
          animate={{ height: active ? [6, 24, 10, 32, 12] : 8 }}
          transition={{ duration: 1.1, repeat: Infinity, delay: b * 0.03 }}
        />
      ))}
    </div>
  );
}

export default function App() {
  const { state, text, connected, sendCommand } = useLyraSocket();
  const [transcript, setTranscript] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [manualCommand, setManualCommand] = useState("");
  const [micEnabled, setMicEnabled] = useState(false);
  const [micError, setMicError] = useState("");
  const recognitionRef = useRef(null);
  const [voiceReady, setVoiceReady] = useState(false);
  const lastSpokenRef = useRef("");
  const audioCtxRef = useRef(null);
  const lastStateRef = useRef("idle");

  const playEarcon = (kind) => {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = audioCtxRef.current || new AudioContextClass();
    audioCtxRef.current = ctx;
    if (ctx.state === "suspended") ctx.resume();

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = kind === "listen" ? 740 : 520;
    gain.gain.value = 0.001;
    osc.connect(gain);
    gain.connect(ctx.destination);
    const now = ctx.currentTime;
    gain.gain.exponentialRampToValueAtTime(0.08, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + (kind === "listen" ? 0.14 : 0.18));
    osc.start(now);
    osc.stop(now + (kind === "listen" ? 0.15 : 0.2));
  };

  useEffect(() => {
    if (!SpeechRecognition) {
      setMicError("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-IN";

    recognition.onresult = (event) => {
      const heard = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
      setTranscript(heard);
      const withoutWakeWord = heard.replace(/^lyra[, ]*/i, "").trim();
      const directCommandPattern =
        /(open|play|search|google|weather|news|github|youtube|linkedin|instagram|moodle|model|who is|tell me about|information|meri playlist chala|tum best ho|good bye|exit|quit)/i;
      const commandToSend = heard.startsWith("lyra")
        ? withoutWakeWord
        : directCommandPattern.test(heard)
          ? heard
          : "";
      if (commandToSend) {
        // Interrupt current speech when user talks over LYRA.
        window.speechSynthesis?.cancel();
        sendCommand(commandToSend);
      }
    };
    recognition.onstart = () => {
      setIsListening(true);
      setMicError("");
      playEarcon("listen");
    };
    recognition.onerror = (event) => {
      setMicError(`Mic error: ${event.error}`);
      setIsListening(false);
      setMicEnabled(false);
    };
    recognition.onend = () => {
      setIsListening(false);
      if (!micEnabled) return;
      setTimeout(() => {
        try {
          recognition.start();
        } catch {
          setMicError("Failed to restart mic recognition.");
          setMicEnabled(false);
        }
      }, 300);
    };

    return () => {
      recognition.stop();
      recognitionRef.current = null;
    };
  }, [sendCommand, micEnabled]);

  const startVoice = async () => {
    setMicError("");
    if (!SpeechRecognition) {
      setMicError("Speech recognition is not supported in this browser.");
      return;
    }
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicEnabled(true);
      recognitionRef.current?.start();
    } catch {
      setMicEnabled(false);
      setMicError("Microphone permission denied. Allow mic access for localhost.");
    }
  };

  const stopVoice = () => {
    setMicEnabled(false);
    recognitionRef.current?.stop();
  };

  useEffect(() => {
    if (!("speechSynthesis" in window)) return;
    const bootstrapVoice = () => {
      // Prime voice list; some browsers load it lazily.
      window.speechSynthesis.getVoices();
      setVoiceReady(true);
    };
    bootstrapVoice();
    window.speechSynthesis.onvoiceschanged = bootstrapVoice;
    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, []);

  useEffect(() => {
    if (!voiceReady || state !== "speaking" || !text) return;
    if (lastSpokenRef.current === text) return;
    lastSpokenRef.current = text;

    const utterance = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();
    const preferred =
      voices.find((v) => /female|zira|aria|samantha/i.test(v.name)) ||
      voices.find((v) => /en-in|en_us|en-gb/i.test(v.lang.toLowerCase())) ||
      voices[0];
    if (preferred) utterance.voice = preferred;
    utterance.rate = 1.02;
    utterance.pitch = 1.1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  }, [state, text, voiceReady]);

  useEffect(() => {
    if (state === "speaking" && lastStateRef.current !== "speaking") {
      playEarcon("done");
    }
    lastStateRef.current = state;
  }, [state]);

  return (
    <main className="hud-bg">
      <div className="scanline" />
      <div className="sphere-stage">
        <LyraOrb state={state} />
      </div>
      <div className="overlay top">
        <h1>LYRA</h1>
        <p className="subtitle">State: {state}</p>
      </div>
      <div className="overlay bottom">
        <Waveform active={state === "speaking"} />
        <div className="status-grid">
          <p>Socket: <span>{connected ? "Connected" : "Offline"}</span></p>
          <p>Mic: <span>{isListening ? "Live" : "Idle"}</span></p>
          <p>Voice: <span>{voiceReady ? "Ready" : "Loading"}</span></p>
        </div>
        <div className="voice-row">
          <button onClick={startVoice}>Start Voice</button>
          <button onClick={stopVoice}>Stop Voice</button>
        </div>
        {micError ? <div className="mic-error">{micError}</div> : null}
        <div className="manual-row">
          <input
            value={manualCommand}
            onChange={(e) => setManualCommand(e.target.value)}
            placeholder="Type command (example: open youtube and play lofi)"
          />
          <button
            onClick={() => {
              const cmd = manualCommand.trim();
              if (!cmd) return;
              sendCommand(cmd);
              setManualCommand("");
            }}
          >
            Send
          </button>
        </div>
        <div className="caption">{text}</div>
        <div className="heard">Heard: {transcript || "..."}</div>
      </div>
    </main>
  );
}
