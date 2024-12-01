import React, { useState } from 'react';
import FileUpload from './components/UploadFile';
import ChatWindow from './components/ChatWindow';

function App() {
  const [messages, setMessages] = useState([]);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [docId, setDocId] = useState(null);

  const handleFileUpload = ({ uploadedFile, docId }) => {
    setUploadedFile(uploadedFile);
    setDocId(docId);
  };

  const handleNewFile = () => {
    // Reset the messages when a new file is uploaded
    setMessages([]);
  };

  return (
    <div
      className="App"
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        backgroundColor: '#282c34', // Dark background similar to ChatGPT
        color: '#ffffff', // Light text color for contrast
        fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
      }}
    >
      {/* Header Section */}
      <div
        style={{
          padding: '16px',
          backgroundColor: '#2C2F36', // Darker header background
          color: '#00BFAE', // Soft cyan text color
          textAlign: 'center',
          fontSize: '18px',
          fontWeight: 'bold',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        }}
      >
        BrewingChat - App
      </div>

      {/* Main Content */}
      <div
        style={{
          display: 'flex',
          flex: 1,
          flexDirection: 'row',
          padding: '20px',
          gap: '20px',
          overflow: 'hidden',
        }}
      >
        {/* File Upload Component */}
        <div
          style={{
            flex: 1,
            maxWidth: '400px',
            backgroundColor: '#3A3F47', // Darker gray for upload section
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            overflowY: 'auto',
          }}
        >
          <FileUpload onFileUpload={handleFileUpload} onNewFile={handleNewFile}/>
        </div>

        {/* Chat Window Component */}
        <div
          style={{
            flex: 2,
            backgroundColor: '#1F2124', // Very dark gray for chat area
            color: '#E4E8ED', // Light gray text for messages
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* <ChatWindow uploadedFile={uploadedFile} docId={docId} /> */}
          <ChatWindow uploadedFile={uploadedFile} docId={docId} messages={messages} setMessages={setMessages} />

        </div>
      </div>
    </div>
  );
}

export default App;
