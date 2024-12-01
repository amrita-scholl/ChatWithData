const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const path = require('path');
const cors = require('cors');
const axios = require('axios');  // Import axios to send the pre-signed URL to your Python API

const app = express();
const port = process.env.PORT || 3000;

// Middleware to parse JSON request body
app.use(express.json()); // Add this line to parse JSON requests

// Configure CORS
app.use(cors({
  origin: 'http://localhost:3001', // Adjust this to the origin of your React app
}));

// Configure AWS SDK
const s3 = new AWS.S3({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  signatureVersion: 'v4',
  region: 'ap-south-1',
});

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Upload endpoint
app.post('/upload', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  const file = req.file;
  const fileName = Date.now() + path.extname(file.originalname);
  
  console.log(fileName)

  const params = {
    Bucket: 'chat-with-document',
    Key: fileName,  // Use the unique file name
    Body: file.buffer,
    ContentType: file.mimetype
  };

  try {
    // Upload file to S3
    const data = await s3.upload(params).promise();

    // Generate a pre-signed URL
    const urlParams = {
      Bucket: 'chat-with-document',
      Key: fileName,  // Ensure the fileName is used to generate the URL
      Expires: 60 * 5, // URL expiration time in seconds (5 minutes)
    };

    const preSignedUrl = s3.getSignedUrl('getObject', urlParams);

    console.log('Generated pre-signed URL:', preSignedUrl);

    // Send the pre-signed URL to the Python API
    const response = await axios.post('http://localhost:5000/process-file', {
      url: preSignedUrl, // Send the pre-signed URL in the request body
    });

    const docId = response.data.doc_id;  // Assuming the Python API returns doc_id
    console.log('Received doc_id:', docId);

    // Send back the file URL and doc_id
    res.json({
      message: 'File uploaded successfully',
      fileUrl: preSignedUrl,
      doc_id: docId,  // Include doc_id in the response
    });
  } catch (error) {
    console.error(error);
    res.status(500).send('Error uploading file.');
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
