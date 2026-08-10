import { useRef, useState } from "react";

export default function ChatInput({ onSend }) {
    const [text, setText] = useState("");
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef(null);

    function submit(event) {
        event.preventDefault();

        if (!text.trim()) {
            return;
        }

        onSend(text);
        setText("");
    }

    async function handleImageButtonClick() {
        if (!file) {
            fileInputRef.current?.click();
            return;
        }

        if (typeof onSend !== "function" || !onSend.uploadImage) {
            return;
        }

        setIsUploading(true);
        try {
            await onSend.uploadImage(file);
            setFile(null);
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        } finally {
            setIsUploading(false);
        }
    }

    return (
        <form onSubmit={submit} className="border-t border-neutral-700 p-5">
            <div className="flex gap-4 items-center">
                <input
                    className="flex-1 rounded-xl bg-neutral-800 p-4 outline-none"
                    placeholder="Ask TechStore AI..."
                    value={text}
                    onChange={(event) => setText(event.target.value)}
                />

                <input
                    ref={fileInputRef}
                    id="chat-image-input"
                    type="file"
                    accept="image/*"
                    onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                    className="hidden"
                />

                <button
                    type="button"
                    onClick={handleImageButtonClick}
                    disabled={isUploading}
                    className="rounded-xl bg-blue-600 px-4 h-10 text-white disabled:cursor-not-allowed disabled:opacity-60"
                    title={file ? file.name : "Choose an image"}
                >
                    {isUploading ? "Sending?" : file ? "Send Image" : "Upload Image"}
                </button>

                <button type="submit" className="rounded-xl bg-green-600 px-8 h-10">
                    Send
                </button>
            </div>

            {file && !isUploading && (
                <p className="mt-2 text-xs text-neutral-400">Ready to send: {file.name}</p>
            )}
        </form>
    );
}
