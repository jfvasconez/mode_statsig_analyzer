import React, { useState, useRef, ChangeEvent, FormEvent } from 'react';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box'; // For layout
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import Paper from '@mui/material/Paper'; // Import Paper
import Stack from '@mui/material/Stack'; // Import Stack for layout
import UploadFileIcon from '@mui/icons-material/UploadFile'; // Import Icon
import Chip from '@mui/material/Chip'; // Use Chip for selected file
import LoadingButton from '@mui/lab/LoadingButton'; // Import LoadingButton

// Import axios for API calls (we'll use it in the handler)
// import axios from 'axios';

function UploadForm() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null); // Ref to access the hidden input

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setStatusMessage(null); // Clear previous messages
    setIsError(false);
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      if (file.type === 'text/csv') {
        setSelectedFile(file);
      } else {
        setSelectedFile(null);
        setStatusMessage('Please select a valid CSV file.');
        setIsError(true);
        // Clear the input value if invalid file type
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      }
    } else {
      setSelectedFile(null);
    }
  };

  const handleUploadClick = () => {
    // Trigger the hidden file input click
    fileInputRef.current?.click();
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); // Prevent default form submission
    if (!selectedFile) {
      setStatusMessage('Please select a file first.');
      setIsError(true);
      return;
    }

    setIsLoading(true);
    setStatusMessage(null);
    setIsError(false);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // --- TODO: Make API call with axios ---
      // const response = await axios.post('/api/experiments/', formData, {
      //   headers: {
      //     'Content-Type': 'multipart/form-data'
      //   }
      // });
      // setStatusMessage(response.data.message || 'Upload successful!'); // Use message from backend
      // setSelectedFile(null); // Clear selection on success
      // if(fileInputRef.current) {
      //   fileInputRef.current.value = "";
      // }
      // console.log('Upload response:', response.data);

      // Placeholder success
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay
      setStatusMessage(`Placeholder: Uploaded ${selectedFile.name} successfully! ID: TEMP_ID`);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

    } catch (error: any) {
      console.error('Upload error:', error);
      // Handle specific axios errors vs other errors
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setStatusMessage(`Error: ${error.response.data?.error || error.response.statusText || 'Upload failed'}`);
      } else if (error.request) {
        // The request was made but no response was received
        setStatusMessage('Error: No response from server. Is it running?');
      } else {
        // Something happened in setting up the request that triggered an Error
        setStatusMessage(`Error: ${error.message}`);
      }
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // Wrap form in Paper
    <Paper elevation={2} sx={{ mt: 4, p: { xs: 2, sm: 3 } }}> {/* Responsive padding */}
      <Box component="form" onSubmit={handleSubmit}>
        <Typography variant="h6" component="h2" gutterBottom sx={{ mb: 3 }}> {/* Increase bottom margin */}
          Upload Experiment CSV
        </Typography>

        {/* Use Stack for file input area layout */}
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}> {/* Increase bottom margin */}
          {/* Hidden file input */}
          <input
            type="file"
            accept=".csv, text/csv" // Be slightly more flexible with accept
            onChange={handleFileChange}
            ref={fileInputRef}
            style={{ display: 'none' }}
            id="csv-upload-input"
          />
          {/* Button to trigger file input */}
          <Button
            variant="outlined"
            onClick={handleUploadClick}
            disabled={isLoading}
            startIcon={<UploadFileIcon />} // Add icon
            size="medium" // Explicit size
          >
            Choose File
          </Button>
          {/* Use Chip for selected file name */}
          {selectedFile && (
            <Chip label={selectedFile.name} variant="outlined" />
          )}
        </Stack>

        {/* Use LoadingButton */}
        <LoadingButton
          type="submit"
          variant="contained"
          color="primary"
          size="large"
          disabled={!selectedFile} // Loading state handled by `loading` prop
          loading={isLoading} // Pass loading state
          fullWidth
          sx={{ mt: 2, mb: 2, py: 1.5 }}
        >
          <span>Upload and Analyze</span> { /* Wrap text in span for correct loading indicator position */}
        </LoadingButton>

        {statusMessage && (
          <Alert severity={isError ? 'error' : 'success'} sx={{ mt: 2 }}>
            {statusMessage}
          </Alert>
        )}
      </Box>
    </Paper>
  );
}

export default UploadForm; 