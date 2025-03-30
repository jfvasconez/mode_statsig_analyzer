import { useState } from 'react';
import './App.css'
import UploadForm from './components/UploadForm';
import ExperimentResults from './components/ExperimentResults';
import StatisticalSummary from './components/StatisticalSummary';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

function App() {
  const [experimentId, setExperimentId] = useState<string | null>(null);

  const handleExperimentProcessed = (id: string | undefined) => {
    console.log('Experiment processed with ID:', id);
    if (id) {
      setExperimentId(id);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ textAlign: 'center', my: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          sx={{
            fontWeight: 500,
            color: '#424242',
            letterSpacing: '0.015em'
          }}
        >
          Funnel Conversion Analyzer
        </Typography>
      </Box>

      <UploadForm onExperimentProcessed={handleExperimentProcessed} />

      <ExperimentResults experimentId={experimentId} />

      <StatisticalSummary />
    </Container>
  )
}

export default App
