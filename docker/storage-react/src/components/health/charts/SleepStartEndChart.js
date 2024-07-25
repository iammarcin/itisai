// SleepStartEndChart.js

import React, { useEffect, useState, useCallback } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';

import { getColor } from '../../../utils/colorHelper';

ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const SleepStartEndChart = ({ data }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });

  const processData = useCallback(() => {
    const dates = data.map(entry => entry.calendar_date);
    const sleepStart = data.map(entry => {
      let [hours, minutes] = entry.sleep_start.split(':').map(Number);
      if (hours < 19) hours += 24; // Adjust for next day if before 7 PM
      return hours + minutes / 60;
    });
    const sleepEnd = data.map(entry => {
      let [hours, minutes] = entry.sleep_end.split(':').map(Number);
      hours += 24; // Always add 24 to ensure it's on the next day
      return hours + minutes / 60;
    });

    setChartData({
      labels: dates,
      datasets: [
        {
          label: 'Sleep Start',
          data: sleepStart,
          borderColor: getColor("green_dark", 1),
          tension: 0.1,
          pointRadius: 3,
        },
        {
          label: 'Sleep End',
          data: sleepEnd,
          borderColor: getColor("red", 1),
          tension: 0.1,
          pointRadius: 3,
        }
      ]
    });
  }, [data]);

  useEffect(() => {
    processData();
  }, [processData]);

  const options = {
    responsive: true,
    scales: {
      x: {
        type: 'category',
        title: {
          display: true,
          text: 'Date'
        }
      },
      y: {
        type: 'linear',
        min: 19,
        max: 34, // 10 AM next day
        ticks: {
          stepSize: 1,
          callback: function (value) {
            value = value % 24;
            return value.toString().padStart(2, '0') + ':00';
          }
        },
        title: {
          display: true,
          text: 'Time of Day'
        }
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function (context) {
            let value = context.parsed.y;
            let hours = Math.floor(value) % 24;
            let minutes = Math.round((value - Math.floor(value)) * 60);
            return `${context.dataset.label}: ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
          }
        }
      }
    }
  };

  return <Line data={chartData} options={options} />;
};

export default SleepStartEndChart;