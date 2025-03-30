// frontend/src/components/StatisticalSummary.tsx
// Component that displays a statistical summary table for A/B test results

import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Button,
  Collapse,
  Tabs,
  Tab,
  styled,
  Paper,
  Chip
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, ReferenceLine } from 'recharts';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ConfidenceChart from './ConfidenceChart';

// Custom styled components
const StyledTableCell = styled(TableCell)(({ theme }) => ({
  borderBottom: '1px solid #e0e0e0',
  padding: '16px 8px',
  '&.header': {
    color: '#5f6368',
    borderBottom: '1px solid #e0e0e0',
    fontWeight: 500,
    fontSize: '0.75rem',
    letterSpacing: '0.5px'
  }
}));

const StyledTab = styled(Tab)({
  textTransform: 'none',
  minWidth: 0,
  padding: '12px 16px',
  color: '#5f6368',
  '&.Mui-selected': {
    color: '#1a73e8'
  }
});

const StyledTabs = styled(Tabs)({
  '& .MuiTabs-indicator': {
    backgroundColor: '#1a73e8',
    height: '3px'
  },
  minHeight: '40px',
  '& .MuiTab-root': {
    minHeight: '40px'
  }
});

// Dummy data structure matching the example
const dummyData = [
  {
    step: 'Typewriter_Intro',
    controlRate: 0.02,
    variant1Rate: 97.67,
    relativeUplift: 410752.71,
    chanceToBeat: 99.00,
    significant: true,
    sampleSizeControl: 8413,
    sampleSizeVariant: 8630,
    credibleInterval: [95.2, 99.8],
    effectSize: 2.35,
    confidenceOverTime: [
      // Historical data
      { date: '2024-03-01', confidence: 15, isProjected: false },
      { date: '2024-03-02', confidence: 28, isProjected: false },
      { date: '2024-03-03', confidence: 45, isProjected: false },
      { date: '2024-03-04', confidence: 52, isProjected: false },
      { date: '2024-03-05', confidence: 68, isProjected: false },
      { date: '2024-03-06', confidence: 72, isProjected: false },
      { date: '2024-03-07', confidence: 78, isProjected: false },
      { date: '2024-03-08', confidence: 82, isProjected: false },
      { date: '2024-03-09', confidence: 85, isProjected: false },
      { date: '2024-03-10', confidence: 87, isProjected: false },
      // Projected data - continues from last historical point
      { date: '2024-03-11', confidence: 88.5, isProjected: true },
      { date: '2024-03-12', confidence: 89.2, isProjected: true },
      { date: '2024-03-13', confidence: 90.1, isProjected: true },
      { date: '2024-03-14', confidence: 91.5, isProjected: true },
      { date: '2024-03-15', confidence: 92.8, isProjected: true }
    ]
  },
  {
    step: 'Goals',
    controlRate: 97.85,
    variant1Rate: 76.57,
    relativeUplift: -21.75,
    chanceToBeat: 0.00,
    significant: true,
    sampleSizeControl: 7500,
    sampleSizeVariant: 7600,
    credibleInterval: [72.5, 78.9],
    effectSize: 1.85,
    confidenceOverTime: [
      { date: '2024-03-01', confidence: 25, isProjected: false },
      { date: '2024-03-02', confidence: 45, isProjected: false },
      { date: '2024-03-03', confidence: 65, isProjected: false },
      { date: '2024-03-04', confidence: 85, isProjected: false },
      { date: '2024-03-05', confidence: 95, isProjected: false }
    ]
  },
  {
    step: 'Protections',
    controlRate: 75.31,
    variant1Rate: 69.56,
    relativeUplift: -7.64,
    chanceToBeat: 21.24,
    significant: false,
    sampleSizeControl: 7000,
    sampleSizeVariant: 7100,
    credibleInterval: [65.5, 73.5],
    effectSize: 0.85,
    confidenceOverTime: [
      // Historical data (Standardized date format YYYY-MM-DD)
      { date: '2024-03-01', confidence: 20, isProjected: false },
      { date: '2024-03-02', confidence: 35, isProjected: false },
      { date: '2024-03-03', confidence: 50, isProjected: false },
      { date: '2024-03-04', confidence: 65, isProjected: false },
      { date: '2024-03-05', confidence: 80, isProjected: false },
      // Projected data - continues from last historical point
      { date: '2024-03-06', confidence: 83, isProjected: true },
      { date: '2024-03-07', confidence: 86, isProjected: true },
      { date: '2024-03-08', confidence: 88, isProjected: true },
      { date: '2024-03-09', confidence: 91, isProjected: true },
      { date: '2024-03-10', confidence: 93, isProjected: true }
    ]
  },
  {
    step: 'HowItWorks',
    controlRate: 74.11,
    variant1Rate: 2.75,
    relativeUplift: -96.29,
    chanceToBeat: 2.00,
    significant: true,
    sampleSizeControl: 6500,
    sampleSizeVariant: 6600,
    credibleInterval: [1.5, 4.0],
    effectSize: 2.15,
    confidenceOverTime: [
      { date: '2024-03-01', confidence: 25, isProjected: false },
      { date: '2024-03-02', confidence: 45, isProjected: false },
      { date: '2024-03-03', confidence: 65, isProjected: false },
      { date: '2024-03-04', confidence: 85, isProjected: false },
      { date: '2024-03-05', confidence: 95, isProjected: false }
    ]
  },
  {
    step: 'Intent',
    controlRate: 72.25,
    variant1Rate: 68.82,
    relativeUplift: -4.74,
    chanceToBeat: 32.86,
    significant: false,
    sampleSizeControl: 6000,
    sampleSizeVariant: 6100,
    credibleInterval: [64.8, 72.8],
    effectSize: 0.45,
    confidenceOverTime: [
      { date: '2024-03-01', confidence: 20, isProjected: false },
      { date: '2024-03-02', confidence: 35, isProjected: false },
      { date: '2024-03-03', confidence: 50, isProjected: false },
      { date: '2024-03-04', confidence: 65, isProjected: false },
      { date: '2024-03-05', confidence: 80, isProjected: false }
    ]
  }
];

interface ExpandableRowProps {
  row: typeof dummyData[0];
  isExpanded: boolean;
}

const ExpandableRow: React.FC<ExpandableRowProps> = ({ row, isExpanded }) => {
  return (
    <TableRow>
      <StyledTableCell colSpan={8} sx={{ p: 0 }}>
        <Collapse in={isExpanded}>
          <Box sx={{ py: 3, px: 4, backgroundColor: '#f7f9fc' }}>
            <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
              <Typography sx={{ color: '#1a73e8', fontSize: '0.795rem', mb: 2 }}>
                Detailed Metrics
              </Typography>
              <Box sx={{ display: 'grid', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography sx={{ color: '#5f6368', fontSize: '0.795rem' }}>Sample Size (Control):</Typography>
                  <Typography sx={{ fontWeight: 500, fontSize: '0.795rem' }}>{row.sampleSizeControl.toLocaleString()}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography sx={{ color: '#5f6368', fontSize: '0.795rem' }}>Sample Size (Variant):</Typography>
                  <Typography sx={{ fontWeight: 500, fontSize: '0.795rem' }}>{row.sampleSizeVariant.toLocaleString()}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography sx={{ color: '#5f6368', fontSize: '0.795rem' }}>95% Credible Interval:</Typography>
                  <Typography sx={{ fontWeight: 500, fontSize: '0.795rem' }}>[{row.credibleInterval[0]}%, {row.credibleInterval[1]}%]</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography sx={{ color: '#5f6368', fontSize: '0.795rem' }}>Effect Size (Cohen's h):</Typography>
                  <Typography sx={{ fontWeight: 500, fontSize: '0.795rem' }}>{row.effectSize} (Very Large)</Typography>
                </Box>
              </Box>
            </Paper>

            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography sx={{ color: '#1a73e8', fontSize: '0.795rem', mb: 2 }}>
                Time to Significance
              </Typography>
              <Box>
                <ConfidenceChart data={row.confidenceOverTime} />
              </Box>
            </Paper>
          </Box>
        </Collapse>
      </StyledTableCell>
    </TableRow>
  );
};

const StatisticalSummary: React.FC = () => {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);

  const handleRowExpand = (step: string) => {
    setExpandedRow(expandedRow === step ? null : step);
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  return (
    <Box sx={{ mt: 4, bgcolor: '#fff', borderRadius: 1, boxShadow: '0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15)' }}>
      <Box sx={{ px: 3, pt: 3 }}>
        <Typography variant="h6" sx={{
          mb: 3,
          fontWeight: 400,
          color: '#202124',
          fontSize: '1.25rem'
        }}>
          Statistical Significance Summary
        </Typography>

        <StyledTabs value={selectedTab} onChange={handleTabChange}>
          <StyledTab label="Control vs Variant 1" />
          <StyledTab label="Control vs Variant 3" />
          <StyledTab label="Variant 1 vs Variant 3" />
          <StyledTab label="All Variants" />
        </StyledTabs>
      </Box>

      <TableContainer sx={{ mt: 2, px: 3, pb: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <StyledTableCell className="header" sx={{ width: 40 }}></StyledTableCell>
              <StyledTableCell className="header">FUNNEL STEP</StyledTableCell>
              <StyledTableCell className="header">CONTROL</StyledTableCell>
              <StyledTableCell className="header">VARIANT 1</StyledTableCell>
              <StyledTableCell className="header">RELATIVE UPLIFT</StyledTableCell>
              <StyledTableCell className="header">CHANCE TO BEAT</StyledTableCell>
              <StyledTableCell className="header">TIME TO SIG. (EST. DATE)</StyledTableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {dummyData.map((row) => (
              <React.Fragment key={row.step}>
                <TableRow
                  onClick={() => handleRowExpand(row.step)}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.02)',
                      cursor: 'pointer'
                    },
                    '&:nth-of-type(even)': {
                      backgroundColor: '#fafafa'
                    }
                  }}
                >
                  <StyledTableCell sx={{ width: 40 }}>
                    {expandedRow === row.step ? (
                      <ExpandMoreIcon sx={{ color: '#5f6368', transition: 'transform 0.2s' }} />
                    ) : (
                      <ChevronRightIcon sx={{ color: '#5f6368', transition: 'transform 0.2s' }} />
                    )}
                  </StyledTableCell>
                  <StyledTableCell sx={{ color: '#5f6368', fontWeight: 500 }}>{row.step}</StyledTableCell>
                  <StyledTableCell>{row.controlRate.toFixed(2)}%</StyledTableCell>
                  <StyledTableCell>{row.variant1Rate.toFixed(2)}%</StyledTableCell>
                  <StyledTableCell
                    sx={{
                      color: row.significant
                        ? (row.relativeUplift >= 0 ? '#34a853' : '#ea4335')
                        : '#5f6368',
                      fontWeight: row.significant ? 700 : 400
                    }}
                  >
                    {row.relativeUplift >= 0 ? '+' : ''}{row.relativeUplift.toFixed(2)}%
                  </StyledTableCell>
                  <StyledTableCell>{row.chanceToBeat.toFixed(2)}%</StyledTableCell>
                  <StyledTableCell>
                    {row.significant ? (
                      <Typography sx={{ color: '#34a853', fontSize: '0.8125rem' }}>Reached</Typography>
                    ) : (
                      <Typography sx={{ color: '#5f6368', fontSize: '0.8125rem' }}>
                        10 days (12/8)
                      </Typography>
                    )}
                  </StyledTableCell>
                </TableRow>
                <ExpandableRow
                  row={row}
                  isExpanded={expandedRow === row.step}
                />
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default StatisticalSummary; 