// SleepMetricsChart.js

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { getColor } from '../../../utils/colorHelper';

ChartJS.register(TimeScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const SleepMetricsChart = ({ data, isFullWidth, isMobile }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });

  const chartRef = useRef(null);

  const processData = useCallback(() => {
    const dates = data.map(entry => entry.calendar_date);
    const averageRespiration = data.map(entry => entry.average_respiration_value);
    const avgSleepStress = data.map(entry => entry.avg_sleep_stress);
    const avgOvernightHrv = data.map(entry => entry.avg_overnight_hrv);
    const restingHeartRate = data.map(entry => entry.resting_heart_rate);
    const bodyBatteryChange = data.map(entry => entry.body_battery_change);

    setChartData({
      labels: dates,
      datasets: [
        {
          label: 'Avg Sleep Stress',
          data: avgSleepStress,
          backgroundColor: getColor("red"),
          borderColor: getColor("red", 1),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
        },
        {
          label: 'Avg Overnight HRV',
          data: avgOvernightHrv,
          backgroundColor: getColor("violet"),
          borderColor: getColor("violet", 1),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
        },
        {
          label: 'Resting Heart Rate',
          data: restingHeartRate,
          backgroundColor: getColor("orange"),
          borderColor: getColor("orange", 1),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
        },
        {
          label: 'Body Battery Change',
          data: bodyBatteryChange,
          backgroundColor: getColor("green_light"),
          borderColor: getColor("green_light", 1),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
        },
        {
          label: 'Average Respiration',
          data: averageRespiration,
          backgroundColor: getColor("blue_dark"),
          borderColor: getColor("blue_dark", 1),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
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
        display: isMobile ? false : true,
        title: {
          display: true,
          text: 'Date'
        },
        type: 'category'
      },
      'y-left': {
        type: 'linear',
        position: 'left',
        title: {
          display: isMobile ? false : true,
          text: 'Metrics'
        },
        ticks: {
          font: {
            size: isMobile ? 8 : 12,
          },
          padding: isMobile ? 0 : 5,
        },
        beginAtZero: true
      }
    },
    plugins: {
      legend: {
        position: isMobile ? 'bottom' : 'top',
        labels: {
          boxWidth: 12,
          padding: 10
        }
      },
      title: {
        display: false,
        text: 'Sleep metrics',
      },
    }
  }

  return <Line ref={chartRef} data={chartData} options={options} />;
};

export default SleepMetricsChart;
