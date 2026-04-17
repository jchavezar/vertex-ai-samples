import type { Message } from '../types';

interface Props {
  message: Message;
}

function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user';
  const isError = message.content.startsWith('[error]');

  const prefix = isUser ? '> ' : '< ';
  const className = [
    'message',
    isUser ? 'message-user' : 'message-assistant',
    isError ? 'message-error' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={className}>
      <span className="message-prefix">{prefix}</span>
      <span className="message-content">{message.content}</span>
    </div>
  );
}

export default MessageBubble;
