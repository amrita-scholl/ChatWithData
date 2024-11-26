import React, { useState } from 'react';

function ChatWindow({ uploadedFile }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSendMessage = () => {
    if (input.trim()) {
      setMessages([...messages, { text: input, type: 'user' }]);
      setInput('');
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '10px', height: '400px', overflowY: 'auto' }}>
      <h3>Chat Window</h3>
      <div style={{ marginBottom: '10px' }}>
        {uploadedFile && (
          <div style={{ padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px', marginBottom: '10px' }}>
            <p><strong>Uploaded File:</strong> {uploadedFile.name}</p>
          </div>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              margin: '5px 0',
              padding: '10px',
              borderRadius: '5px',
              backgroundColor: message.type === 'user' ? '#d1e7dd' : '#f8d7da',
              alignSelf: message.type === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            {message.text}
          </div>
        ))}
      </div>
      <div>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message"
          style={{ width: 'calc(100% - 60px)', padding: '5px' }}
        />
        <button onClick={handleSendMessage} style={{ padding: '5px 10px', marginLeft: '10px' }}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
