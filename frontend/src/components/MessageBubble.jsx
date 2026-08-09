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

            </div>

        </div>

    );

}