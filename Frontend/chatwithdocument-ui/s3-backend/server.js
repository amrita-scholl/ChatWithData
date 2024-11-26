const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const path = require('path');
const cors = require('cors'); // Add this line

const app = express();
const port = process.env.PORT || 3000;

// Configure CORS
app.use(cors({
  origin: 'http://localhost:3001', // Adjust this to the origin of your React app
}));

// Configure AWS SDK
// AWS.config.update({
//   accessKeyId: process.env.AWS_ACCESS_KEY_ID,
//   secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
//   signatureVersion: 'v4',
//   region: 'ap-south-1',
// });

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
    Key: file.originalname,
    Body: file.buffer,
    ContentType: file.mimetype
  };

  try {
    // Upload file to S3
    const data = await s3.upload(params).promise();

    // Generate a pre-signed URL
    const urlParams = {
      Bucket: 'chat-with-document',
      Key: file.originalname,
      Expires: 60 * 5 // URL expiration time in seconds
    };

    const preSignedUrl = s3.getSignedUrl('getObject', urlParams);

    console.log('Generated pre-signed URL:', preSignedUrl);

    res.json({
      message: 'File uploaded successfully',
      fileUrl: preSignedUrl
    });
  } catch (error) {
    console.error(error);
    res.status(500).send('Error uploading file.');
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
