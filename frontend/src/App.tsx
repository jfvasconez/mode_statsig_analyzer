import './App.css'
import UploadForm from './components/UploadForm';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';

function App() {
  return (
    <Container maxWidth="md">
      <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ mt: 4 }}>
        Funnel Conversion Analyzer
      </Typography>
      <UploadForm />
      {/* Placeholder for Results Display */}
    </Container>
  )
}

export default App
