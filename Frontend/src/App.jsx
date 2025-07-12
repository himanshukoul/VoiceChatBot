import "./App.css";
import VAD from "./components/VAD.jsx";
import socket from "./static/socket";
import { useState, useEffect } from "react";

function base64ToBlob(base64, mime = "audio/mpeg") {
  const binary = atob(base64);
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
  return new Blob([bytes], { type: mime });
}

export default function App() {
  const [isCompleted, setIsCompleted] = useState(true);
  const [userSaid, setUserSaid] = useState("");
  const [botSaid, setBotSaid] = useState("");
  const audioQueue = [];

  useEffect(() => {
    socket.connect();
    socket.on("user_said", (data) => setUserSaid(data.message));
    socket.on("bot_partial", (data) => setBotSaid(data.message));
    socket.on("bot_audio_chunk", (data) => {
      audioQueue.push(data.audio);
      if (audioQueue.length === 1) playNextAudio();
    });
    return () => socket.disconnect();
  }, []);

  const playNextAudio = () => {
    if (audioQueue.length === 0) {
      setIsCompleted(true);
      return;
    }
    const audio = new Audio();
    // const blob =  base64ToBlob(audioQueue[0], "audio/wav");
    const blob = base64ToBlob(audioQueue[0], "audio/mpeg");
    audio.src = URL.createObjectURL(blob);
    audio.onended = () => {
      audioQueue.shift();
      playNextAudio();
    };
    audio.play().catch(() => {
      audioQueue.shift();
      playNextAudio();
    });
  };

  return (
    <>
      <VAD isCompleted={isCompleted} setIsCompleted={setIsCompleted} />
      <p>
        <b>User:</b> {userSaid}
      </p>
      <p>
        <b>Bot:</b> {botSaid}
      </p>
    </>
  );
}
