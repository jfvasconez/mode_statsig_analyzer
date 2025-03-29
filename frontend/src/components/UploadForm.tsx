import { useState, useRef, ChangeEvent, FormEvent } from 'react';
import {
  Button,
  Paper,
  Typography,
  Alert,
  Chip,
  Box
} from '@mui/material';
import { LoadingButton } from '@mui/lab';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import axios from 'axios';

interface UploadFormProps {
  onExperimentProcessed?: (experimentId: string) => void;
}

// Component for uploading and analyzing experiment CSV files
const UploadForm = ({ onExperimentProcessed }: UploadFormProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    success: boolean;
    message: string;
    experimentId?: string;
  } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      // Reset status when a new file is selected
      setUploadStatus(null);
    }
  };

  const handleFileSelect = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!selectedFile) {
      setUploadStatus({
        success: false,
        message: 'Please select a file first.',
      });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post('/api/experiments/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Upload response:', response.data);

      // Check if the experiment_id exists in the response
      const experimentId = response.data.experiment_id;

      if (!experimentId) {
        console.error('No experiment_id in response:', response.data);
      }

      setUploadStatus({
        success: true,
        message: 'File uploaded and processed successfully.',
        experimentId
      });

      // Clear the file selection
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Notify parent component
      if (onExperimentProcessed && experimentId) {
        onExperimentProcessed(experimentId);
      } else {
        console.error('Could not process experiment ID:', experimentId);
      }

    } catch (error: any) {
      console.error('Upload error:', error);

      let errorMessage = 'Error uploading file. Please try again.';

      // Extract more specific error message if available
      if (error.response && error.response.data) {
        errorMessage = error.response.data.message || error.response.data.error || errorMessage;
      }

      setUploadStatus({
        success: false,
        message: errorMessage,
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 4,
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: '0 3px 10px rgba(0,0,0,0.08)',
      }}
    >
      <Typography
        variant="h6"
        gutterBottom
        color="primary"
        sx={{
          fontWeight: 500,
          mb: 2.5
        }}
      >
        Upload Experiment CSV
      </Typography>

      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          ref={fileInputRef}
          style={{ display: 'none' }}
        />

        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<UploadFileIcon />}
            onClick={handleFileSelect}
            sx={{
              mr: 2,
              px: 2.5,
              py: 1,
              borderRadius: 1.5,
              textTransform: 'none',
              fontWeight: 500
            }}
          >
            Choose File
          </Button>

          {selectedFile && (
            <Chip
              label={selectedFile.name}
              variant="outlined"
              color="primary"
              sx={{
                maxWidth: '250px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                borderRadius: 1.5,
                height: 32
              }}
            />
          )}
        </Box>

        <LoadingButton
          type="submit"
          variant="contained"
          color="primary"
          size="large"
          loading={isUploading}
          disabled={!selectedFile}
          sx={{
            py: 1.2,
            px: 4,
            textTransform: 'none',
            fontWeight: 500,
            borderRadius: 1.5,
            boxShadow: '0 2px 6px rgba(25, 118, 210, 0.3)'
          }}
        >
          <span>Upload and Analyze</span>
        </LoadingButton>

        {uploadStatus && (
          <Alert
            severity={uploadStatus.success ? 'success' : 'error'}
            sx={{
              mt: 3,
              borderRadius: 1.5,
              '& .MuiAlert-icon': {
                alignItems: 'center'
              }
            }}
          >
            {uploadStatus.message}
          </Alert>
        )}
      </form>
    </Paper>
  );
};

export default UploadForm; 