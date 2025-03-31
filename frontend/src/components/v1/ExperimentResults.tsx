import { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Skeleton,
  Alert,
  Chip,
  Tooltip,
  ChipProps
} from '@mui/material';
import axios from 'axios';

interface ExperimentResultsProps {
  experimentId: string | null;
}

interface StepResultData {
  user_count: number;
  converted_count: number;
  conversion_rate: number;
  posterior_mean: number | null;
  ci_95: [number | null, number | null];
  prob_vs_control: number | null;
}

interface StepData {
  step_name: string;
  results: {
    [variantName: string]: StepResultData | null;
  };
}

interface ExperimentData {
  experiment_id: number;
  experiment_name: string;
  variant_names: string[];
  steps_data: StepData[];
}

const ExperimentResults = ({ experimentId }: ExperimentResultsProps) => {
  const [results, setResults] = useState<ExperimentData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      if (!experimentId) return;

      setLoading(true);
      setError(null);

      try {
        const response = await axios.get(`/api/experiments/${experimentId}/`);
        console.log('Experiment results (new structure):', response.data);
        setResults(response.data);
      } catch (err: any) {
        console.error('Error fetching results:', err);
        setError(err.response?.data?.message || 'Failed to fetch experiment results');
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [experimentId]);

  if (!experimentId) {
    return null;
  }

  if (loading) {
    return (
      <Paper
        elevation={2}
        sx={{
          p: 4,
          mt: 4,
          bgcolor: 'background.paper',
          borderRadius: 2,
          boxShadow: '0 3px 10px rgba(0,0,0,0.08)',
        }}
      >
        <Typography variant="h6" gutterBottom>
          <Skeleton width="60%" />
        </Typography>
        <Skeleton variant="rectangular" height={200} />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper
        elevation={2}
        sx={{
          p: 4,
          mt: 4,
          bgcolor: 'background.paper',
          borderRadius: 2,
          boxShadow: '0 3px 10px rgba(0,0,0,0.08)',
        }}
      >
        <Alert severity="error">{error}</Alert>
      </Paper>
    );
  }

  if (!results || !results.steps_data) {
    return null;
  }

  const formatPercent = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  const getChipColor = (chance: number | null | undefined): ChipProps['color'] => {
    if (chance === null || chance === undefined) return 'default';
    if (chance >= 0.95) return 'success';
    if (chance >= 0.8) return 'warning';
    return 'default';
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 4,
        mt: 4,
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
        Results for: {results.experiment_name}
      </Typography>

      <Box sx={{ overflowX: 'auto' }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Funnel Step</TableCell>
                {results.variant_names.map((variantName) => (
                  <TableCell key={variantName} align="center" sx={{ fontWeight: 'bold' }}>
                    {variantName}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {results.steps_data.map((stepItem) => (
                <TableRow key={stepItem.step_name} hover>
                  <TableCell component="th" scope="row" sx={{ fontWeight: 'medium' }}>
                    {stepItem.step_name}
                  </TableCell>
                  {results.variant_names.map((variantName) => {
                    const data = stepItem.results[variantName] ?? null;
                    return (
                      <TableCell key={`${stepItem.step_name}-${variantName}`} align="center">
                        {data ? (
                          <Box sx={{ lineHeight: 1.5 }}>
                            <Typography variant="body2">
                              {formatPercent(data.conversion_rate)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              ({data.converted_count} / {data.user_count})
                            </Typography>
                            {data.prob_vs_control !== null && (
                              <Tooltip title={`Prob. vs Control: ${formatPercent(data.prob_vs_control)}\nCI95: [${formatPercent(data.ci_95[0])}, ${formatPercent(data.ci_95[1])}]\nPost. Mean: ${formatPercent(data.posterior_mean)}`}>
                                <Chip
                                  label={formatPercent(data.prob_vs_control)}
                                  color={getChipColor(data.prob_vs_control)}
                                  size="small"
                                  sx={{ mt: 0.5 }}
                                />
                              </Tooltip>
                            )}
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">-</Typography>
                        )}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      <Box sx={{ mt: 4 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Explanation (per cell):
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Top: Conversion Rate (%)
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Middle: (Converted Count / Total Variant Users)
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Bottom (Chip): Win Probability vs Control (hover for more details)
        </Typography>
      </Box>
    </Paper>
  );
};

export default ExperimentResults;

