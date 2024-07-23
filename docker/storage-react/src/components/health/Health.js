import React, { useEffect, useState, useRef, useCallback } from 'react';
import apiMethods from '../../services/api.methods';
import FloatingChat from './FloatingChat';
import SleepPhasesChart from './charts/SleepPhasesChart';
import SleepStartEndChart from './charts/SleepStartEndChart';
import SleepMetricsChart from './charts/SleepMetricsChart';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

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

  const setPresetRange = (days) => {
    const end = new Date();
    const start = new Date(end.getTime() - days * 24 * 60 * 60 * 1000);
    setDateRange([start, end]);
    fetchData(start, end);
  };

  if (isError) {
    return <div>Error fetching data.</div>;
  }

  return (
    <div>
      <h2>Your Health stats</h2>
      <div style={{ marginBottom: '20px' }}>
        <DatePicker
          selectsRange={true}
          startDate={startDate}
          endDate={endDate}
          onChange={handleDateChange}
          dateFormat="yyyy-MM-dd"
        />
        <button onClick={() => setPresetRange(7)}>Current Week</button>
        <button onClick={() => setPresetRange(14)}>Previous Week</button>
        <button onClick={() => setPresetRange(30)}>Current Month</button>
        <button onClick={() => setPresetRange(60)}>Previous Month</button>
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