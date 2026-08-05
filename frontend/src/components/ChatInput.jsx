import { useRef, useState } from "react";

import * as voiceService from "../services/voiceService";

import { getSessionId } from "../utils/storage";

export default function ChatInput({ onSend }) {

    const [text, setText] = useState("");

    const [recording, setRecording] = useState(false);

    const mediaRecorder = useRef(null);

    const chunks = useRef([]);

    async function startRecording() {

        try {

            const stream =
                await navigator.mediaDevices.getUserMedia({
                    audio: true,
                });

            const recorder =
                new MediaRecorder(stream);

            chunks.current = [];

            recorder.ondataavailable = (event) => {

                chunks.current.push(event.data);

            };

            recorder.onstop = async () => {

                const blob = new Blob(
                    chunks.current,
                    {
                        type: "audio/webm",
                    },
                );

                const response =
                    await voiceService.sendVoice(
                        blob,
                        getSessionId(),
                    );

                onSend(
                    response.transcript,
                    response.response,
                    response.audio_url,
                );

                stream
                    .getTracks()
                    .forEach((track) => track.stop());

            };

            recorder.start();

            mediaRecorder.current = recorder;

            setRecording(true);

        }

        catch (error) {

            console.error(error);

            alert("Unable to access microphone.");

        }

    }

    function stopRecording() {

        if (mediaRecorder.current) {

            mediaRecorder.current.stop();

            setRecording(false);

        }

    }

    function submit(event) {

        event.preventDefault();

        if (!text.trim()) return;

        onSend(text);

        setText("");

    }

    return (

        <form
            onSubmit={submit}
            className="border-t border-neutral-700 p-5"
        >

            <div className="flex gap-4">

                <input
                    className="flex-1 rounded-xl bg-neutral-800 p-4 outline-none"
                    placeholder="Ask TechStore AI..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                />

                <button
                    type="button"
                    onClick={
                        recording
                            ? stopRecording
                            : startRecording
                    }
                    className="rounded-xl bg-blue-600 px-5"
                >
                    {recording ? "⏹" : "🎤"}
                </button>

                <button
                    type="submit"
                    className="rounded-xl bg-green-600 px-8"
                >
                    Send
                </button>

            </div>

        </form>

    );

}