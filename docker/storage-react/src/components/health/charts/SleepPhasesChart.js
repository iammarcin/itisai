// SleepPhasesChart.js

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

import { getColor } from '../../../utils/colorHelper';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

const SleepPhasesChart = ({ data, isFullWidth }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });

  const chartRef = useRef(null);

  const processData = useCallback(() => {
    const dates = data.map(entry => entry.calendar_date);
    const overallScores = data.map(entry => entry.overall_score_value);
    const deepSleepTimes = data.map(entry => entry.deep_sleep_seconds / 3600);
    const lightSleepTimes = data.map(entry => entry.light_sleep_seconds / 3600);
    const remSleepTimes = data.map(entry => entry.rem_sleep_seconds / 3600);
    const awakeSleepTimes = data.map(entry => entry.awake_sleep_seconds / 3600);
    const napTimes = data.map(entry => entry.nap_time_seconds / 3600);

    setChartData({
      labels: dates,
      datasets: [
        {
          type: 'bar',
          label: 'Deep Sleep',
          data: deepSleepTimes,
          backgroundColor: getColor("violet", 0.8),
          stack: 'Stack 0',
        },
        {
          type: 'bar',
          label: 'REM Sleep',
          data: remSleepTimes,
          backgroundColor: getColor("blue_dark", 0.8),
          stack: 'Stack 0',
        },
        {
          type: 'bar',
          label: 'Light Sleep',
          data: lightSleepTimes,
          backgroundColor: getColor("green_mid", 0.8),
          stack: 'Stack 0',
        },
        {
          type: 'bar',
          label: 'Awake',
          data: awakeSleepTimes,
          backgroundColor: getColor("yellow_dark", 0.8),
          stack: 'Stack 0',
        },
        {
          type: 'bar',
          label: 'Naps',
          data: napTimes,
          backgroundColor: getColor("pink", 0.8),
          stack: 'Stack 0',
          hidden: true,
        },
        {
          type: 'line',
          label: 'Overall Sleep Score',
          data: overallScores,
          borderColor: getColor("red", 0.8),
          backgroundColor: getColor("red"),
          borderWidth: 2,
          fill: false,
          yAxisID: 'y-right',
          pointRadius: 0,
        },
      ]
    });
  }, [data]);

  useEffect(() => {
    processData();
  }, [processData]);

  // depending of choice of full width in Health.js (do we want small or big charts), resize the chart
  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.resize();
    }
  }, [isFullWidth]);

  const options = {
    responsive: true,
    scales: {
      x: {
        stacked: true,
        title: {
          display: true,
          text: 'Date'
        },
        grid: {
          display: false
        }
      },
      y: {
        stacked: true,
        title: {
          display: true,
          text: 'Hours'
        },
        min: 0,
        max: 15,
        ticks: {
          stepSize: 2
        }
      },
      'y-right': {
        type: 'linear',
        position: 'right',
        title: {
          display: true,
          text: 'Overall Sleep Score'
        },
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20
        },
        grid: {
          drawOnChartArea: false
        },
      },
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Daily Sleep Stages',
      },
    },
  };

  return <Bar ref={chartRef} data={chartData} options={options} />;
};

export default SleepPhasesChart;