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

// Helper type for series with potential nulls
// Define the type explicitly to allow null confidence
interface SeriesDataPoint {
  date: string;
  confidence: number | null; // Allow null
  isProjected: boolean;
}

const ConfidenceChart: React.FC<ConfidenceChartProps> = ({ data }) => {
  // Find the index where projection starts
  const lastHistoricalIndex = data.findIndex(point => point.isProjected);

  // Check if we've reached confidence threshold in historical data
  const historicalSegment = lastHistoricalIndex === -1 ? data : data.slice(0, lastHistoricalIndex);
  const hasReachedConfidence = historicalSegment.some(point => point.confidence >= 90);

  // Create data series for historical line (nulls after projection starts)
  const historicalLineData: SeriesDataPoint[] = data.map((point, index) => ({
    ...point,
    // Set confidence to null if it's a projected point
    confidence: (lastHistoricalIndex !== -1 && index >= lastHistoricalIndex) ? null : point.confidence,
  }));

  // Create data series for projected line (nulls before, includes overlap point)
  let projectedLineData: SeriesDataPoint[] | null = null;
  if (lastHistoricalIndex !== -1) {
    projectedLineData = data.map((point, index) => ({
      ...point,
      // Keep confidence only for the overlap point (index - 1) and projected points (index >= lastHistoricalIndex)
      confidence: index >= lastHistoricalIndex - 1 && point.isProjected
        ? point.confidence
        : (index === lastHistoricalIndex - 1 ? point.confidence : null)
    }));
  }

  // Determine if the projected line should be shown
  const showProjectedLine = !hasReachedConfidence && projectedLineData && projectedLineData.some(p => p?.confidence !== null && p.isProjected);

  return (
    <Box>
      <Box sx={{ height: 300, mt: 2 }}>
        <ResponsiveContainer width="100%" height="100%">
          {/* Pass original data for axis calculation */}
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
              formatter={(value: number, name, props) => {
                // Don't show tooltip for null values
                if (value === null || value === undefined) return null;
                // Determine if the point is projected based on the original data point payload
                const originalPoint = props.payload as ConfidenceDataPoint;
                const label = originalPoint?.isProjected ? 'Projected Confidence' : 'Confidence';
                return [`${value.toFixed(1)}%`, label];
              }}
            />

            {/* Historical data line using historicalLineData */}
            <Line
              data={historicalLineData} // Use series with nulls
              type="monotone"
              dataKey="confidence"
              stroke="#1a73e8"
              strokeWidth={2}
              dot={{ r: 3, fill: '#1a73e8' }} // Consistent dot
              name="Historical"
              connectNulls // <-- Connect across nulls
              isAnimationActive={false}
            />

            {/* Projected data line using projectedLineData */}
            {showProjectedLine && projectedLineData && (
              <Line
                data={projectedLineData} // Use series with nulls
                type="monotone"
                dataKey="confidence"
                stroke="#1a73e8"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ r: 3, fill: '#1a73e8' }} // Consistent dot
                name="Projected"
                connectNulls // <-- Connect across nulls
                isAnimationActive={false}
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
      {/* Legend only shown if projection exists and confidence not reached */}
      {showProjectedLine && (
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 2, bgcolor: '#1a73e8' }} />
            <Typography sx={{ fontSize: '0.75rem', color: '#5f6368' }}>
              Historical Data
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 2, bgcolor: '#1a73e8', borderTop: '2px dashed #1a73e8' }} />
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