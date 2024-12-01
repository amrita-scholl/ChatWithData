import axios from 'axios';
import React, { useState } from 'react';

const FileUpload = ({ onFileUpload,onNewFile }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://localhost:3000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const uploadedFile = selectedFile;
      const docId = response.data.doc_id;

      // Notify the parent to reset the chat when a new file is uploaded
      if (onNewFile) {
        onNewFile(); // Reset the chat messages
      }
      
      // Pass uploadedFile and docId back to parent via onFileUpload callback
      if (onFileUpload) {
        onFileUpload({ uploadedFile, docId });
      }

      setError('');
    } catch (err) {
      setError('Error uploading file.');
      console.error(err);
    }
  };

  return (
    <div
      style={{
        backgroundColor: '#3A3F47', // Dark gray background for the file upload section
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        color: '#E4E8ED', // Light gray text color
        fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
      }}
    >
      <h1
        style={{
          color: '#00BFAE', // Soft cyan color for the heading
          fontSize: '20px',
          marginBottom: '10px',
        }}
      >
        Upload Document
      </h1>
      <input
        type="file"
        onChange={handleFileChange}
        style={{
          backgroundColor: '#4E555D', // Darker input field background
          color: '#E4E8ED', // Light text color for input
          padding: '10px',
          borderRadius: '8px',
          border: '1px solid #555',
          width: '100%',
          marginBottom: '10px',
        }}
      />
      <button
        onClick={handleUpload}
        style={{
          backgroundColor: '#00BFAE', // Soft cyan button color
          color: '#ffffff',
          padding: '12px 20px',
          borderRadius: '8px',
          border: 'none',
          cursor: 'pointer',
          fontSize: '16px',
          width: '100%',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        }}
      >
        Upload
      </button>
      {error && (
        <p
          style={{
            color: '#FF6F61', // Error message color (soft red)
            marginTop: '10px',
          }}
        >
          {error}
        </p>
      )}
    </div>
  );
};

export default FileUpload;
