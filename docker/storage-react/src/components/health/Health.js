import React, { useEffect, useState, useRef, useCallback } from 'react';
import apiMethods from '../../services/api.methods';
import FloatingChat from './FloatingChat';
import SleepPhasesChart from './charts/SleepPhasesChart';
import SleepStartEndChart from './charts/SleepStartEndChart';
import SleepMetricsChart from './charts/SleepMetricsChart';

const Health = () => {
  const [data, setData] = useState([]);
  const [isError, setIsError] = useState(false);
  const hasFetchedData = useRef(false);

  const fetchData = useCallback(async () => {
    try {
      const userInput = {
        "start_date": "2024-07-15",
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

      setData(data);
    } catch (error) {
      console.error('Error fetching data: ', error);
      setIsError(true);
    }
  }, []);

  useEffect(() => {
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
      <h4>Sleep timing</h4>
      <SleepStartEndChart data={data} />
      <h4>Sleep timing</h4>
      <SleepMetricsChart data={data} />
      <h4>Sleep phases</h4>
      <SleepPhasesChart data={data} />
      <FloatingChat />
    </div>
  );
};

export default Health;
