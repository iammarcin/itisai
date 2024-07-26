// SleepPhasesChart.js

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

import { getColor } from '../../../utils/colorHelper';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

const SleepPhasesChart = ({ index, data, isFullWidth, isMobile, isModalOpen, onChartClick }) => {
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
          tension: 0.1,
          pointRadius: 1,
          fill: true,
          yAxisID: 'y-right',
          pointStyle: 'circle',
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
    maintainAspectRatio: isMobile ? false : true,
    scales: {
      x: {
        // display the x axis only on mobile if modal is open
        display: isMobile ? isModalOpen ? true : false : true,
        stacked: true,
        title: {
          display: true,
          text: 'Date'
        },
        grid: {
          display: false
        },
        type: 'category'
      },
      y: {
        stacked: true,
        title: {
          display: isMobile ? false : true,
          text: 'Hours'
        },
        min: 0,
        max: 15,
        ticks: {
          stepSize: 2,
          font: {
            size: isMobile ? 8 : 12,
          },
          padding: isMobile ? 0 : 5,
        }
      },
      'y-right': {
        type: 'linear',
        position: 'right',
        title: {
          display: isMobile ? false : true,
          text: 'Overall Sleep Score'
        },
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20,
          font: {
            size: isMobile ? 8 : 12,
          },
          padding: isMobile ? 0 : 5,
        },
        grid: {
          drawOnChartArea: false
        },
      },
    },
    onClick: () => { // important to differentiate if legend was clicked or not
      onChartClick('chart', index);
    },
    plugins: {
      legend: {
        position: isMobile ? 'bottom' : 'top',
        labels: {
          boxWidth: 12,
          padding: 10
        },
        onClick: (event, legendItem, legend) => { // important to differentiate if legend was clicked or not
          // Custom legend click handler
          ChartJS.defaults.plugins.legend.onClick(event, legendItem, legend);
          onChartClick('legend', index);
        },
      },
      title: {
        display: false,
        text: 'Daily Sleep Stages',
      },
    },
  };

  return <Bar ref={chartRef} data={chartData} options={options} />;
};

export default SleepPhasesChart;