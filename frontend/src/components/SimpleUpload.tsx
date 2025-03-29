import { useState, useRef, ChangeEvent } from 'react';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import UploadFileIcon from '@mui/icons-material/UploadFile';

const SimpleUpload = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 2, bgcolor: 'background.paper' }}>
      <Typography variant="h6" gutterBottom color="primary">
        Simple Upload Test
      </Typography>

      <input
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        ref={fileInputRef}
        style={{ display: 'none' }}
      />

      <Button
        variant="contained"
        color="primary"
        startIcon={<UploadFileIcon />}
        onClick={() => fileInputRef.current?.click()}
        sx={{ mr: 2 }}
      >
        Choose File
      </Button>

      {selectedFile && (
        <Typography variant="body1" display="inline">
          Selected: {selectedFile.name}
        </Typography>
      )}
    </Paper>
  );
};

export default SimpleUpload; 