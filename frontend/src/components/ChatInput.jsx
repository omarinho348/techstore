import { useState } from "react";

export default function ChatInput({ onSend }) {

    const [text, setText] = useState("");

    function submit(event) {

        event.preventDefault();

        if (!text.trim()) {

            return;

        }

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
                    onChange={(event) =>
                        setText(event.target.value)
                    }
                />

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