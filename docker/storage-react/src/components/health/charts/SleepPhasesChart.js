import React, { useEffect, useState, useCallback } from 'react';
import { Line } from 'react-chartjs-2';
import { getColor } from '../../../utils/colorHelper'; // Assuming you move getColor to a helper file

const SleepPhasesChart = ({ data }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });

  const processData = useCallback(() => {
    const dates = data.map(entry => entry.calendar_date);
    const overallScores = data.map(entry => entry.overall_score_value);
    const sleepTimes = data.map(entry => entry.sleep_time_seconds / 3600);
    const deepSleepTimes = data.map(entry => entry.deep_sleep_seconds / 3600);
    const lightSleepTimes = data.map(entry => entry.light_sleep_seconds / 3600);
    const remSleepTimes = data.map(entry => entry.rem_sleep_seconds / 3600);
    const awakeSleepTimes = data.map(entry => entry.awake_sleep_seconds / 3600);
    const napTimes = data.map(entry => entry.nap_time_seconds / 3600);

    setChartData({
      labels: dates,
      datasets: [
        {
          label: 'Overall Sleep Score',
          data: overallScores,
          backgroundColor: getColor("red"),
          borderColor: getColor("red", "border"),
          borderWidth: 1,
          yAxisID: 'y-right',
          fill: true,
        },
        {
          label: 'Total Sleep Time (hours)',
          data: sleepTimes,
          backgroundColor: getColor("violet"),
          borderColor: getColor("violet", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
        },
        {
          label: 'Deep Sleep Time (hours)',
          data: deepSleepTimes,
          backgroundColor: getColor("orange"),
          borderColor: getColor("orange", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
        },
        {
          label: 'Light Sleep Time (hours)',
          data: lightSleepTimes,
          backgroundColor: getColor("green_light"),
          borderColor: getColor("green_light", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
        },
        {
          label: 'REM Sleep Time (hours)',
          data: remSleepTimes,
          backgroundColor: getColor("blue_dark"),
          borderColor: getColor("blue_dark", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
        },
        {
          label: 'Awake Time (hours)',
          data: awakeSleepTimes,
          backgroundColor: getColor("green_dark"),
          borderColor: getColor("green_dark", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
        },
        {
          label: 'Nap time (hours)',
          data: napTimes,
          backgroundColor: getColor("yellow_dark"),
          borderColor: getColor("yellow_dark", "border"),
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

  return (
    <Line
      data={chartData}
      options={{
        responsive: true,
        scales: {
          x: {
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
              display: true,
              text: 'Sleep hours'
            },
            beginAtZero: true
          },
          'y-right': {
            type: 'linear',
            position: 'right',
            title: {
              display: true,
              text: 'Overall Sleep Score'
            },
            beginAtZero: true,
            min: 0,
            max: 100,
            grid: {
              drawOnChartArea: false // only want the grid lines for one axis to show up
            }
          }
        }
      }}
    />
  );
};

export default SleepPhasesChart;
