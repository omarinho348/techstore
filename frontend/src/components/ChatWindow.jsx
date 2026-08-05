import MessageBubble from "./MessageBubble";

export default function ChatWindow({ messages }) {

    return (

        <div className="flex-1 overflow-y-auto p-8">

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