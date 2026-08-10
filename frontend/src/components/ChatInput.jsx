import { useRef, useState } from "react";

export default function ChatInput({ onSend, onVoice }) {
    const [text, setText] = useState("");
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [voiceError, setVoiceError] = useState("");
    const fileInputRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const mediaStreamRef = useRef(null);

    async function submit(event) {
        event.preventDefault();
        if (!text.trim()) return;
        setText("");
        await onSend(text);
    }

    async function toggleRecording() {
        setVoiceError("");
        if (isRecording) {
            mediaRecorderRef.current?.stop();
            return;
        }

        if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
            setVoiceError("Voice recording is not supported in this browser.");
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);
            const chunks = [];
            mediaStreamRef.current = stream;
            mediaRecorderRef.current = recorder;

            recorder.ondataavailable = ({ data }) => {
                if (data.size) chunks.push(data);
            };
            recorder.onstop = async () => {
                setIsRecording(false);
                stream.getTracks().forEach((track) => track.stop());
                mediaStreamRef.current = null;
                const audioBlob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
                try {
                    await onVoice(audioBlob);
                } catch (error) {
                    setVoiceError(error.message || "Voice transcription failed.");
                }
            };

            recorder.start();
            setIsRecording(true);
        } catch {
            setVoiceError("Microphone access was not granted.");
        }
    }

    async function handleImageButtonClick() {
        if (!file) {
            fileInputRef.current?.click();
            return;
        }
        if (typeof onSend !== "function" || !onSend.uploadImage) return;

        setIsUploading(true);
        try {
            await onSend.uploadImage(file);
            setFile(null);
            if (fileInputRef.current) fileInputRef.current.value = "";
        } finally {
            setIsUploading(false);
        }
    }

    return (
        <form onSubmit={submit} className="border-t border-neutral-700 p-5">
            <div className="flex gap-4 items-center">
                <div className="relative flex-1">
                    <input
                        className="w-full rounded-xl bg-neutral-800 p-4 pr-14 outline-none"
                        placeholder="Ask TechStore AI..."
                        value={text}
                        onChange={(event) => setText(event.target.value)}
                    />
                    <button
                        type="button"
                        onClick={toggleRecording}
                        aria-label={isRecording ? "Stop recording" : "Start voice input"}
                        title={isRecording ? "Stop recording" : "Start voice input"}
                        className={`absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 ${isRecording ? "bg-red-600 text-white" : "text-neutral-300 hover:bg-neutral-700 hover:text-white"}`}
                    >
                        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                            <rect x="9" y="2" width="6" height="12" rx="3" />
                            <path d="M5 11a7 7 0 0 0 14 0M12 18v4M8 22h8" />
                        </svg>
                    </button>
                </div>

                <input ref={fileInputRef} id="chat-image-input" type="file" accept="image/*" onChange={(event) => setFile(event.target.files?.[0] ?? null)} className="hidden" />
                <button type="button" onClick={handleImageButtonClick} disabled={isUploading} className="rounded-xl bg-blue-600 px-4 h-10 text-white disabled:cursor-not-allowed disabled:opacity-60" title={file ? file.name : "Choose an image"}>
                    {isUploading ? "Sending..." : file ? "Send Image" : "Upload Image"}
                </button>
                <button type="submit" className="rounded-xl bg-green-600 px-8 h-10">Send</button>
            </div>

            {isRecording && <p className="mt-2 text-xs text-red-300">Recording... Click the microphone to stop and send.</p>}
            {file && !isUploading && <p className="mt-2 text-xs text-neutral-400">Ready to send: {file.name}</p>}
            {voiceError && <p className="mt-2 text-xs text-red-300">{voiceError}</p>}
        </form>
    );
}
