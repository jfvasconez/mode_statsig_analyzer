import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// 1. Import MUI components
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// 2. Create a default theme (can be customized later)
const theme = createTheme({
  // You can customize theme options here, e.g., palette, typography
  palette: {
    mode: 'light', // Default to light mode, can be 'dark'
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* 3. Apply ThemeProvider and CssBaseline */}
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Apply baseline styles */}
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
