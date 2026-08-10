import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

const MALE_VOICE_HINTS = [
    "male", "david", "mark", "guy", "daniel", "alex", "fred",
    "george", "james", "thomas", "ryan", "eric", "brian",
];

function pickMaleVoice(voices) {
    if (!voices?.length) return null;

    // Prefer an English voice whose name hints at a male voice
    const englishVoices = voices.filter((voice) => voice.lang?.startsWith("en"));
    const pool = englishVoices.length ? englishVoices : voices;

    const match = pool.find((voice) =>
        MALE_VOICE_HINTS.some((hint) => voice.name.toLowerCase().includes(hint))
    );

    return match || pool[0] || null;
}

export default function MessageBubble({
    role,
    message,
    status,
    agent,
}) {

    const isUser = role === "user";
    const canSpeak = !isUser && message && !status;

    const [speechState, setSpeechState] = useState("idle"); // idle | playing | paused
    const [speechError, setSpeechError] = useState("");
    const utteranceRef = useRef(null);
    const voiceRef = useRef(null);

    useEffect(() => {
        const synth = window.speechSynthesis;
        if (!synth) return;

        function loadVoice() {
            voiceRef.current = pickMaleVoice(synth.getVoices());
        }

        loadVoice();
        synth.addEventListener("voiceschanged", loadVoice);

        return () => {
            synth.removeEventListener("voiceschanged", loadVoice);
            if (speechState !== "idle") {
                synth.cancel();
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    function handleSpeak() {
        setSpeechError("");

        const synth = window.speechSynthesis;
        if (!synth) {
            setSpeechError("Text-to-speech isn't supported in this browser.");
            return;
        }

        if (speechState === "playing") {
            synth.pause();
            setSpeechState("paused");
            return;
        }

        if (speechState === "paused") {
            synth.resume();
            setSpeechState("playing");
            return;
        }

        // idle: stop any other bubble currently speaking, then start fresh
        synth.cancel();

        const utterance = new SpeechSynthesisUtterance(message);
        utterance.voice = voiceRef.current;
        utterance.pitch = 0.85;   // slightly lower pitch, reads more masculine
        utterance.rate = 0.95;    // slightly slower than default (1.0), less rushed
        utterance.volume = 1;

        utterance.onend = () => setSpeechState("idle");
        utterance.onerror = () => {
            setSpeechError("Playback failed.");
            setSpeechState("idle");
        };

        utteranceRef.current = utterance;
        synth.speak(utterance);
        setSpeechState("playing");
    }

    return (

        <div
            className={`mb-6 flex ${
                isUser
                    ? "justify-end"
                    : "justify-start"
            }`}
        >

            <div
                className={`max-w-3xl rounded-2xl px-5 py-4 ${
                    isUser
                        ? "bg-green-600"
                        : "bg-neutral-800"
                }`}
            >

                {

                    !isUser &&
                    agent && (

                        <div
                            className="
                                mb-2
                                text-xs
                                font-semibold
                                text-blue-400
                            "
                        >

                            🤖 {agent}

                        </div>

                    )

                }

                {

                    !isUser &&
                    status && (

                        <div
                            className="
                                mb-2
                                text-sm
                                italic
                                text-neutral-400
                            "
                        >

                            {status}

                        </div>

                    )

                }

                <div className="space-y-3 leading-7 text-neutral-100">

                    <ReactMarkdown
                        components={{
                            p: ({ children }) => (
                                <p className="m-0 text-[15px] leading-7">
                                    {children}
                                </p>
                            ),
                            strong: ({ children }) => (
                                <strong className="font-semibold text-white">
                                    {children}
                                </strong>
                            ),
                            ul: ({ children }) => (
                                <ul className="m-0 list-disc space-y-2 pl-5">
                                    {children}
                                </ul>
                            ),
                            ol: ({ children }) => (
                                <ol className="m-0 list-decimal space-y-2 pl-5">
                                    {children}
                                </ol>
                            ),
                            li: ({ children }) => (
                                <li className="pl-1">{children}</li>
                            ),
                            h1: ({ children }) => (
                                <h1 className="m-0 text-xl font-bold text-white">
                                    {children}
                                </h1>
                            ),
                            h2: ({ children }) => (
                                <h2 className="m-0 text-lg font-semibold text-white">
                                    {children}
                                </h2>
                            ),
                            h3: ({ children }) => (
                                <h3 className="m-0 text-base font-semibold text-white">
                                    {children}
                                </h3>
                            ),
                            blockquote: ({ children }) => (
                                <blockquote className="border-l-4 border-neutral-500 pl-4 italic text-neutral-300">
                                    {children}
                                </blockquote>
                            ),
                        }}
                    >

                        {message}

                    </ReactMarkdown>

                </div>

                {canSpeak && (
                    <div className="mt-3 flex items-center gap-2">
                        <button
                            type="button"
                            onClick={handleSpeak}
                            aria-label={speechState === "playing" ? "Pause" : "Read response aloud"}
                            title={speechState === "playing" ? "Pause" : "Read response aloud"}
                            className="rounded-lg p-1.5 text-neutral-400 hover:bg-neutral-700 hover:text-white"
                        >
                            {speechState === "playing" ? (
                                <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden="true">
                                    <rect x="6" y="5" width="4" height="14" rx="1" />
                                    <rect x="14" y="5" width="4" height="14" rx="1" />
                                </svg>
                            ) : (
                                <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                                    <path d="M11 5 6 9H2v6h4l5 4V5Z" />
                                    <path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13" />
                                </svg>
                            )}
                        </button>

                        {speechError && (
                            <span className="text-xs text-red-300">{speechError}</span>
                        )}
                    </div>
                )}

            </div>

        </div>

    );

}