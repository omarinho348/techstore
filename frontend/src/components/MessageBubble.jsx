import ReactMarkdown from "react-markdown";

export default function MessageBubble({ role, message }) {

    const isUser = role === "user";

    return (

        <div
            className={`mb-6 flex ${
                isUser ? "justify-end" : "justify-start"
            }`}
        >

            <div
                className={`max-w-3xl rounded-2xl px-5 py-4 ${
                    isUser
                        ? "bg-green-600"
                        : "bg-neutral-800"
                }`}
            >

                <ReactMarkdown>

                    {message}

                </ReactMarkdown>

            </div>

        </div>

    );

}