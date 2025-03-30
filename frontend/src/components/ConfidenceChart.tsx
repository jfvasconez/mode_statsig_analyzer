// frontend/src/components/ConfidenceChart.tsx
// Component that displays the confidence over time chart for A/B test results

import React from 'react';
import { Box, Typography } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  ReferenceLine,
  Tooltip,
  CartesianGrid
} from 'recharts';

interface ConfidenceDataPoint {
  date: string;
  confidence: number;
  isProjected: boolean;
}

interface ConfidenceChartProps {
  data: ConfidenceDataPoint[];
}

const ConfidenceChart: React.FC<ConfidenceChartProps> = ({ data }) => {
  // Find the point where projection starts
  const lastHistoricalIndex = data.findIndex(point => point.isProjected);
  const historicalData = data.slice(0, lastHistoricalIndex);
  const projectedData = data.slice(lastHistoricalIndex - 1); // Include overlap point

  // Check if we've reached confidence threshold
  const hasReachedConfidence = historicalData.some(point => point.confidence >= 90);

  return (
    <Box>
      <Box sx={{ height: 300, mt: 2 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 20, right: 30, left: 10, bottom: 30 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey="date"
              stroke="#5f6368"
              tickLine={true}
              axisLine={true}
              angle={-45}
              textAnchor="end"
              height={50}
              tick={{ fontSize: 12 }}
              label={{
                value: 'Date',
                position: 'bottom',
                offset: 20,
                style: { fill: '#5f6368' }
              }}
            />
            <YAxis
              domain={[0, 100]}
              ticks={[0, 25, 50, 75, 90, 100]}
              stroke="#5f6368"
              tickLine={true}
              axisLine={true}
              tick={{ fontSize: 12 }}
              label={{
                value: 'Confidence (%)',
                angle: -90,
                position: 'insideLeft',
                offset: 0,
                style: { fill: '#5f6368' }
              }}
            />
            <Tooltip
              labelFormatter={(value) => `Date: ${value}`}
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'Confidence']}
            />
            {/* Historical data line */}
            <Line
              data={historicalData}
              type="monotone"
              dataKey="confidence"
              stroke="#1a73e8"
              strokeWidth={2}
              dot={{ r: 4, fill: '#1a73e8' }}
              name="Historical"
              connectNulls
            />
            {/* Projected data line - only show if not reached confidence */}
            {!hasReachedConfidence && projectedData.length > 0 && (
              <Line
                data={projectedData}
                type="monotone"
                dataKey="confidence"
                stroke="#1a73e8"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ r: 3, fill: '#1a73e8', strokeDasharray: '2 2' }}
                name="Projected"
                connectNulls
              />
            )}
            <ReferenceLine
              y={90}
              stroke="#34a853"
              strokeDasharray="3 3"
              strokeWidth={1}
              label={{
                value: '90% Confidence Threshold',
                position: 'right',
                fontSize: 12
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
      {!hasReachedConfidence && (
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 2, bgcolor: '#1a73e8' }} />
            <Typography sx={{ fontSize: '0.75rem', color: '#5f6368' }}>
              Historical Data
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 2, bgcolor: '#1a73e8', borderStyle: 'dashed', borderWidth: '2px' }} />
            <Typography sx={{ fontSize: '0.75rem', color: '#5f6368' }}>
              Projected Data
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ConfidenceChart; 