import { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Skeleton,
  Alert,
  Chip
} from '@mui/material';
import axios from 'axios';

interface ExperimentResultsProps {
  experimentId: string | null;
}

interface FunnelStep {
  step_name: string;
  overall_conversion: number;
}

interface Variant {
  variant_name: string;
  user_count: number;
  funnel_steps: FunnelStep[];
  relative_uplift: number | null;
}

interface BayesianResult {
  chance_to_beat_control: number;
  relative_uplift: number;
  credible_interval: [number, number];
}

interface VariantResults {
  experiment_name: string;
  control: Variant;
  variants: Variant[];
  bayesian_results: Record<string, BayesianResult>;
}

const ExperimentResults = ({ experimentId }: ExperimentResultsProps) => {
  const [results, setResults] = useState<VariantResults | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      if (!experimentId) return;

      setLoading(true);
      setError(null);

      try {
        const response = await axios.get(`/api/experiments/${experimentId}/`);
        console.log('Experiment results:', response.data);
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

  if (!results) {
    return null;
  }

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const getChipColor = (chance: number) => {
    if (chance >= 0.95) return 'success';
    if (chance >= 0.8) return 'warning';
    return 'default';
  };

  const renderVariantRows = () => {
    return results.variants.map((variant) => {
      const bayesianResult = results.bayesian_results[variant.variant_name];
      return (
        <TableRow key={variant.variant_name}>
          <TableCell>{variant.variant_name}</TableCell>
          <TableCell align="right">{variant.user_count}</TableCell>
          {variant.funnel_steps.map((step) => (
            <TableCell key={step.step_name} align="right">
              {formatPercent(step.overall_conversion)}
            </TableCell>
          ))}
          <TableCell align="right">
            {bayesianResult ? (
              <Chip
                label={formatPercent(bayesianResult.chance_to_beat_control)}
                color={getChipColor(bayesianResult.chance_to_beat_control)}
                size="small"
              />
            ) : 'N/A'}
          </TableCell>
          <TableCell align="right">
            {bayesianResult ? formatPercent(bayesianResult.relative_uplift) : 'N/A'}
          </TableCell>
          <TableCell align="right">
            {bayesianResult
              ? `${formatPercent(bayesianResult.credible_interval[0])} to ${formatPercent(bayesianResult.credible_interval[1])}`
              : 'N/A'}
          </TableCell>
        </TableRow>
      );
    });
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
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Variant</TableCell>
                <TableCell align="right">Users</TableCell>
                {results.control.funnel_steps.map((step) => (
                  <TableCell key={step.step_name} align="right">
                    {step.step_name}
                  </TableCell>
                ))}
                <TableCell align="right">Win Probability</TableCell>
                <TableCell align="right">Relative Uplift</TableCell>
                <TableCell align="right">95% Credible Interval</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow sx={{ backgroundColor: 'rgba(0, 0, 0, 0.04)' }}>
                <TableCell>{results.control.variant_name} (control)</TableCell>
                <TableCell align="right">{results.control.user_count}</TableCell>
                {results.control.funnel_steps.map((step) => (
                  <TableCell key={step.step_name} align="right">
                    {formatPercent(step.overall_conversion)}
                  </TableCell>
                ))}
                <TableCell align="right">—</TableCell>
                <TableCell align="right">—</TableCell>
                <TableCell align="right">—</TableCell>
              </TableRow>
              {renderVariantRows()}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      <Box sx={{ mt: 4 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Explanation:
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • <strong>Win Probability</strong>: The probability that this variant is better than the control.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • <strong>Relative Uplift</strong>: The estimated percentage improvement over the control group.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • <strong>95% Credible Interval</strong>: There's a 95% chance the true uplift falls within this range.
        </Typography>
      </Box>
    </Paper>
  );
};

export default ExperimentResults;

