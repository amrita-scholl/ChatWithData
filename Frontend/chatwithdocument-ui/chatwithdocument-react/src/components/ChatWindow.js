import React, { useState } from 'react';

function ChatWindow({ uploadedFile, docId, messages, setMessages }) {
  // const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    if (input.trim() && docId) {
      // Add the user's message once
      setMessages((prevMessages) => [...prevMessages, { text: input, type: 'user' }]);
      setInput(''); // Clear input
      setLoading(true); // Show loading indicator

      try {
        const response = await fetch('http://localhost:5000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            doc_id: docId,
            query: input,
          }),
        });

        const data = await response.json();

        // Add only the assistant's response
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: data.response || 'Sorry, something went wrong.', type: 'assistant' },
        ]);
      } catch (error) {
        console.error('Error:', error);

        // Add an error message from the assistant
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: 'Error: Unable to fetch response.', type: 'assistant' },
        ]);
      } finally {
        setLoading(false); // Hide loading indicator
      }
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        maxHeight: '600px',
        border: '1px solid #333', // Dark border color
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.2)', // Darker shadow for depth
        overflow: 'hidden',
        backgroundColor: '#2F2F2F', // Dark background for the entire chat window
      }}
    >
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
          backgroundColor: '#1F1F1F', // Darker background for the chat area
          color: '#E4E8ED', // Light gray text for readability
        }}
      >
        {uploadedFile && (
          <div
            style={{
              backgroundColor: '#333', // Dark background for file info
              padding: '10px',
              marginBottom: '10px',
              borderRadius: '8px',
              fontSize: '14px',
              color: '#E4E8ED', // Light text for the file info
              textAlign: 'center',
            }}
          >
            Uploaded File: {uploadedFile.name}
          </div>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '10px',
            }}
          >
            <div
              style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: '12px',
                backgroundColor: message.type === 'user' ? '#00BFAE' : '#333', // Green for user, darker for assistant
                color: '#E4E8ED', // Light text color
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word',
                fontSize: '14px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)', // Darker shadow for messages
              }}
            >
              {message.text}
            </div>
          </div>
        ))}
        {loading && (
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-start',
              marginBottom: '10px',
            }}
          >
            <div
              style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: '12px',
                backgroundColor: '#555', // Darker background for loading indicator
                color: '#E4E8ED', // Light text for loading indicator
                fontStyle: 'italic',
                fontSize: '14px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)', // Darker shadow for loading message
              }}
            >
              Assistant is typing...
            </div>
          </div>
        )}
      </div>
      <div
        style={{
          padding: '10px',
          backgroundColor: '#2F2F2F', // Dark background for input area
          borderTop: '1px solid #333', // Dark border for the top of the input area
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            borderRadius: '8px',
            padding: '8px',
            backgroundColor: '#333', // Dark background for input field
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2)', // Darker shadow for input area
          }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              fontSize: '14px',
              padding: '8px',
              backgroundColor: '#555', // Dark background for input field
              color: '#E4E8ED', // Light text for input
            }}
          />
          <button
            onClick={handleSendMessage}
            style={{
              marginLeft: '8px',
              padding: '8px 16px',
              backgroundColor: '#00BFAE', // Soft cyan color for button
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;
