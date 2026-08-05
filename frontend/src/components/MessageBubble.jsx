import ReactMarkdown from "react-markdown";

export default function MessageBubble({
    role,
    message,
    status,
    agent,
}) {

    const isUser = role === "user";

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

                <ReactMarkdown>

                    {message}

                </ReactMarkdown>

            </div>

        </div>

    );

}