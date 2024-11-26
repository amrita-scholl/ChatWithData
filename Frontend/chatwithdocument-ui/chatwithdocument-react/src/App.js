import React, { useState } from 'react'; // Ensure this import is correct
import FileUpload from './components/UploadFile';
import ChatWindow from './components/ChatWindow';


function App() {

  const [uploadedFile, setUploadedFile] = useState(null);

  // Handle the uploaded file
  const handleFileUpload = (file) => {
    setUploadedFile(file);
  };

  return (
    <div className="App" style={{ display: 'flex', flexDirection: 'row', padding: '20px' }}>
      {/* File Upload Component */}
      <div style={{ flex: 1, marginRight: '20px' }}>
        <FileUpload onFileUpload={handleFileUpload} />
      </div>
      {/* Chat Window Component */}
      <div style={{ flex: 2 }}>
        <ChatWindow uploadedFile={uploadedFile} />
      </div>
    </div>
  );
}

export default App;
