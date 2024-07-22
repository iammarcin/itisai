import React, { useEffect, useState, useCallback } from 'react';
import { Line } from 'react-chartjs-2';
import { getColor } from '../../../utils/colorHelper'; // Assuming you move getColor to a helper file

const SleepMetricsChart = ({ data }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });

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
          borderColor: getColor("red", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
        },
        {
          label: 'Avg Overnight HRV',
          data: avgOvernightHrv,
          backgroundColor: getColor("violet"),
          borderColor: getColor("violet", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
        },
        {
          label: 'Resting Heart Rate',
          data: restingHeartRate,
          backgroundColor: getColor("orange"),
          borderColor: getColor("orange", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
        },
        {
          label: 'Body Battery Change',
          data: bodyBatteryChange,
          backgroundColor: getColor("green_light"),
          borderColor: getColor("green_light", "border"),
          borderWidth: 1,
          yAxisID: 'y-left',
          fill: true,
          hidden: true,
        },
        {
          label: 'Average Respiration',
          data: averageRespiration,
          backgroundColor: getColor("blue_dark"),
          borderColor: getColor("blue_dark", "border"),
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
              text: 'Metrics'
            },
            beginAtZero: true
          }
        }
      }}
    />
  );
};

export default SleepMetricsChart;
