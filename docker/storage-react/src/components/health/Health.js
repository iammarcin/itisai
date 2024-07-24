// Health.js

import React, { useEffect, useState, useRef, useCallback } from 'react';
import apiMethods from '../../services/api.methods';
import FloatingChat from './FloatingChat';
import SleepPhasesChart from './charts/SleepPhasesChart';
import SleepStartEndChart from './charts/SleepStartEndChart';
import SleepMetricsChart from './charts/SleepMetricsChart';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import './css/Health.css';

const Health = () => {
  const [data, setData] = useState([]);
  const [isError, setIsError] = useState(false);
  const [dateRange, setDateRange] = useState([new Date(2024, 0, 1), new Date()]);
  const [startDate, endDate] = dateRange;
  const hasFetchedData = useRef(false);

  const fetchData = useCallback(async (start, end) => {
    try {
      const userInput = {
        "start_date": start.toISOString().split('T')[0],
        "end_date": end.toISOString().split('T')[0],
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

      setData(data);
    } catch (error) {
      console.error('Error fetching data: ', error);
      setIsError(true);
    }
  }, []);

  useEffect(() => {
    if (!hasFetchedData.current && startDate && endDate) {
      fetchData(startDate, endDate);
      hasFetchedData.current = true;
    }
  }, [fetchData, startDate, endDate]);

  const handleDateChange = (update) => {
    setDateRange(update);
    if (update[0] && update[1]) {
      fetchData(update[0], update[1]);
    }
  };

  const setPresetRange = (type) => {
    const end = new Date();
    let start = new Date();

    switch (type) {
      case 'YTD':
        start.setMonth(0);
        start.setDate(1);
        break;
      case 'currentWeek':
        start.setDate(end.getDate() - 7);
        break;
      case 'previousWeek':
        start.setDate(end.getDate() - 14);
        end.setDate(end.getDate() - 7);
        break;
      case 'currentMonth':
        start.setMonth(end.getMonth() - 1);
        break;
      case 'previousMonth':
        end.setMonth(end.getMonth() - 1);
        start.setMonth(end.getMonth() - 1);
        break;
      default:
        break;
    }

    setDateRange([start, end]);
    fetchData(start, end);
  };

  if (isError) {
    return <div>Error fetching data.</div>;
  }

  return (
    <div>
      <h2>Your Health stats</h2>
      <div className="date-picker-container">
        <DatePicker
          selectsRange={true}
          startDate={startDate}
          endDate={endDate}
          onChange={handleDateChange}
          dateFormat="yyyy-MM-dd"
          className="custom-datepicker"
        />
      </div>
      <div className="health-button-container">
        <button className="health-button-preset-date" onClick={() => setPresetRange('YTD')}>YTD</button>
        <button className="health-button-preset-date" onClick={() => setPresetRange('currentWeek')}>Current Week</button>
        <button className="health-button-preset-date" onClick={() => setPresetRange('previousWeek')}>Previous Week</button>
        <button className="health-button-preset-date" onClick={() => setPresetRange('currentMonth')}>Current Month</button>
        <button className="health-button-preset-date" onClick={() => setPresetRange('previousMonth')}>Previous Month</button>
      </div>
      <h4>Sleep timing</h4>
      <SleepStartEndChart data={data} />
      <h4>Sleep metrics</h4>
      <SleepMetricsChart data={data} />
      <h4>Sleep phases</h4>
      <SleepPhasesChart data={data} />
      <FloatingChat />
    </div>
  );
};

export default Health;