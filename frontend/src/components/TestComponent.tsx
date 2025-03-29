import { useState } from 'react';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';

const TestComponent = () => {
  const [count, setCount] = useState(0);

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 2, bgcolor: 'background.paper' }}>
      <Typography variant="h6" gutterBottom>Test MUI Components</Typography>

      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <Button variant="contained" color="primary" onClick={() => setCount(count + 1)}>
          Click Me: {count}
        </Button>
        <Button variant="outlined" color="secondary">Outlined Button</Button>
        <Chip label="Test Chip" color="success" variant="outlined" />
      </Stack>

      <Typography variant="body1">
        If you can see styled buttons and a chip above, MUI is working correctly.
      </Typography>
    </Paper>
  );
};

export default TestComponent; 