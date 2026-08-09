import { useState } from "react";

export default function ChatInput({ onSend }) {

    const [text, setText] = useState("");
    const [file, setFile] = useState(null);

    function submit(event) {

        event.preventDefault();

        if (!text.trim()) {

            return;

        }

        onSend(text);

        setText("");

    }

    async function submitFile(event) {
        event.preventDefault();

        if (!file) return;

        // notify parent to handle image upload
        if (typeof onSend === "function" && onSend.uploadImage) {
            await onSend.uploadImage(file);
        }

        setFile(null);
        // reset input value if present
        const input = document.getElementById("chat-image-input");
        if (input) input.value = null;
    }

    return (

        <form
            onSubmit={submit}
            className="border-t border-neutral-700 p-5"
        >

            <div className="flex gap-4 items-center">

                <input
                    className="flex-1 rounded-xl bg-neutral-800 p-4 outline-none"
                    placeholder="Ask TechStore AI..."
                    value={text}
                    onChange={(event) =>
                        setText(event.target.value)
                    }
                />

                <label className="flex items-center gap-2 bg-neutral-800 rounded-xl px-3 h-10 cursor-pointer">
                    <input
                        id="chat-image-input"
                        type="file"
                        accept="image/*"
                        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                        className="hidden"
                    />
                    <span className="text-sm">📷</span>
                    <span className="text-sm">Upload</span>
                </label>

                <button
                    type="submit"
                    className="rounded-xl bg-green-600 px-8 h-10"
                >
                    Send
                </button>

                <button
                    type="button"
                    onClick={submitFile}
                    className="rounded-xl bg-blue-600 px-4 h-10 text-white"
                >
                    Send Image
                </button>

            </div>

        </form>

    );
}