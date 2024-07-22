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
import apiMethods from '../../services/api.methods';
import FloatingChat from './FloatingChat';

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

const getColor = (color, type = "background") => {
  var colorTransparency = 0;
  if (type === "border") {
    colorTransparency = 1;
  } else {
    colorTransparency = 0; // 0.2
  }

  //rgba(75,192,192,1)',

  const colors = {
    "red": "rgba(255,0,0," + colorTransparency + ")",
    "green_dark": "rgba(0,102,51," + colorTransparency + ")",
    "green_light": "rgba(0,255,0," + colorTransparency + ")",
    "blue_dark": "rgba(0,102,204," + colorTransparency + ")",
    "blue_light": "rgba(153,255,255," + colorTransparency + ")",
    "violet": "rgba(102,0,204," + colorTransparency + ")",
    "orange": "rgba(255,128,0," + colorTransparency + ")",
    "yellow_dark": "rgba(255,255,0," + colorTransparency + ")",
    "yellow_light": "rgba(255,255,204," + colorTransparency + ")",
    "purple": "rgba(255,51,255," + colorTransparency + ")",
    "white": "rgba(255,255,255," + colorTransparency + ")",
    "gray_dark": "rgba(96,96,96," + colorTransparency + ")",
    "gray_light": "rgba(192,192,192," + colorTransparency + ")",
  }

  return colors[color];
}



const Health = () => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });
  const [isError, setIsError] = useState(false);
  const hasFetchedData = useRef(false);

  const fetchData = useCallback(async () => {
    try {
      const userInput = {
        "start_date": "2024-01-01",
        "end_date": "2024-07-22",
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
      const overallScores = data.map(entry => entry.overall_score_value);
      const sleepTimes = data.map(entry => entry.sleep_time_seconds / 3600);
      const deepSleepTimes = data.map(entry => entry.deep_sleep_seconds / 3600);
      const lightSleepTimes = data.map(entry => entry.light_sleep_seconds / 3600);
      const remSleepTimes = data.map(entry => entry.rem_sleep_seconds / 3600);
      const awakeSleepTimes = data.map(entry => entry.awake_sleep_seconds / 3600);
      const napTimes = data.map(entry => entry.nap_time_seconds / 3600);

      const sleepStart = data.map(entry => entry.sleep_start);
      const sleepEnd = data.map(entry => entry.sleep_end);
      const averageRespiration = data.map(entry => entry.average_respiration_value);
      const avgSleepStress = data.map(entry => entry.avg_sleep_stress);
      const avgOvernightHrv = data.map(entry => entry.avg_overnight_hrv);
      const restingHeartRate = data.map(entry => entry.resting_heart_rate);
      const bodyBatteryChange = data.map(entry => entry.body_battery_change);

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
      <h2>Your Health stats</h2>
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
      <FloatingChat />
    </div>
  );
};

export default Health;
