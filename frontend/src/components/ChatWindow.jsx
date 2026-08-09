import MessageBubble from "./MessageBubble";

export default function ChatWindow({ messages, userName }) {

    const displayName = userName?.trim() || "there";

    return (

        <div className="flex-1 overflow-y-auto p-8">

            {messages.length === 0 ? (

                <div className="flex h-full items-center justify-center">

                    <div className="max-w-xl rounded-3xl border border-white/10 bg-white/5 px-8 py-10 text-center shadow-2xl backdrop-blur-xl">

                        <p className="text-3xl font-semibold text-white">
                            Hi {displayName}, what can I help you with?
                        </p>

                        <p className="mt-3 text-sm leading-6 text-neutral-300">
                            Start a new conversation or pick up where you left off.
                        </p>

                    </div>

                </div>

            ) : null}

            {messages.map((message, index) => (

                <MessageBubble
    key={index}
    role={message.role}
    message={message.message}
    status={message.status}
    agent={message.agent}
/>

            ))}

        </div>

    );

}