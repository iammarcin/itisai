import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import apiMethods from '../services/api.methods';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Health = () => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });
  const [isError, setIsError] = useState(false);
  const hasFetchedData = useRef(false);

  const fetchData = useCallback(async () => {
    try {
      console.log("EXEC")
      const userInput = {
        "start_date": "2024-01-01",
        "end_date": "2024-07-01",
        "table": "get_sleep_data"
      };
      const response = await apiMethods.triggerAPIRequest(
        "api/db",
        "provider.db",
        "get_garmin_data",
        userInput
      );

      console.log('response: ', response);

      const data = response.message?.result;

      if (!data) {
        throw new Error('No data received');
      }

      const dates = data.map(entry => entry.calendar_date);
      //const overallScores = data.map(entry => entry.overall_score_value);
      const sleepTimes = data.map(entry => entry.sleep_time_seconds / 3600);
      const deepSleepTimes = data.map(entry => entry.deep_sleep_seconds / 3600);
      const lightSleepTimes = data.map(entry => entry.light_sleep_seconds / 3600);
      const remSleepTimes = data.map(entry => entry.rem_sleep_seconds / 3600);
      const awakeSleepTimes = data.map(entry => entry.awake_sleep_seconds / 3600);

      setChartData({
        labels: dates,
        datasets: [
          /*{
            label: 'Overall Sleep Score',
            data: overallScores,
            backgroundColor: 'rgba(75,192,192,0.2)',
            borderColor: 'rgba(75,192,192,1)',
            borderWidth: 1,
            fill: true,
          },*/
          {
            label: 'Total Sleep Time (hours)',
            data: sleepTimes,
            backgroundColor: 'rgba(153,102,255,0.2)',
            borderColor: 'rgba(153,102,255,1)',
            borderWidth: 1,
            fill: true,
          },
          {
            label: 'Deep Sleep Time (hours)',
            data: deepSleepTimes,
            backgroundColor: 'rgba(255,159,64,0.2)',
            borderColor: 'rgba(255,159,64,1)',
            borderWidth: 1,
            fill: true,
          },
          {
            label: 'Light Sleep Time (hours)',
            data: lightSleepTimes,
            backgroundColor: 'rgba(54,162,235,0.2)',
            borderColor: 'rgba(54,162,235,1)',
            borderWidth: 1,
            fill: true,
          },
          {
            label: 'REM Sleep Time (hours)',
            data: remSleepTimes,
            backgroundColor: 'rgba(255,206,86,0.2)',
            borderColor: 'rgba(255,206,86,1)',
            borderWidth: 1,
            fill: true,
          },
          {
            label: 'Awake Time (hours)',
            data: awakeSleepTimes,
            backgroundColor: 'rgba(255,99,132,0.2)',
            borderColor: 'rgba(255,99,132,1)',
            borderWidth: 1,
            fill: true,
          },
        ]
      });
    } catch (error) {
      console.error('Error fetching data: ', error);
      setIsError(true);
    }
  }, []);

  useEffect(() => {
    console.log('useEffect');
    console.log("hasFetchedData.current: ", hasFetchedData.current)
    if (!hasFetchedData.current) {
      fetchData();
      hasFetchedData.current = true;
    }
  }, [fetchData]);

  if (isError) {
    return <div>Error fetching data.</div>;
  }

  return (
    <div>
      <h2>Sleep Metrics Over Time</h2>
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
              type: 'category' // Specify the type explicitly
            },
            y: {
              title: {
                display: true,
                text: 'Value'
              },
              beginAtZero: true
            }
          }
        }}
      />
    </div>
  );
};

export default Health;
