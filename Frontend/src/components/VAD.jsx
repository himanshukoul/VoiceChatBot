import React, { useEffect, useState, useRef } from "react";
import { MicVAD } from "@ricky0123/vad-web";
import { encodeWAV } from "@ricky0123/vad-web/dist/utils";
import socket from "../static/socket";
export default function VAD({ isCompleted, setIsCompleted }) {
  let [status, setStatus] = useState("Initializing...");
  let [isReady, setIsReady] = useState(false);
  let vadInstance = useRef(null);
  useEffect(() => {
    async function startVAD() {
      try {
        const myvad = await MicVAD.new({
          model: "v5",
          frameSamples: 512,
          minSpeechFrames: 4,
          preSpeechPadFrames: 2,
          onSpeechStart: () => {
            if (!isCompleted) {
              return;
            }
            setStatus("User is speaking...");
          },
          onSpeechEnd: (audio) => {
            if (!isCompleted) {
              return;
            }
            setIsCompleted(false);
            vadInstance.current?.pause();
            setStatus("Generating response...");
            encodeAndSend(audio);
          },
        });
        vadInstance.current = myvad;
        setIsReady(true);
        myvad.start();
      } catch (e) {
        console.log(e);
        setStatus("Error initializing VAD");
      }
    }
    startVAD();
    return () => {
      vadInstance.current?.pause();
    };
  }, []);

  useEffect(() => {
    if (!isReady) return;
    if (isCompleted) {
      vadInstance.current?.start();
      setStatus("Listening for speech...");
    } else {
      vadInstance.current?.pause();
      setStatus("Waiting for response...");
    }
  }, [isCompleted, isReady]);

  async function encodeAndSend(audio) {
    const wavBuffer = encodeWAV(audio);
    socket.emit("audio_blob", { wav: wavBuffer, filename: "audio.wav" });
  }
  return (
    <>
      <h2>VAD Runner</h2>
      <p>{status}</p>
    </>
  );
}
