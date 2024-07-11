import React, { useEffect, useState, useRef, useCallback } from 'react';

import apiMethods from '../services/api.methods';


const Garmin = () => {
  const [isError, setIsError] = useState(false);
  const hasFetchedData = useRef(false);

  const fetchData = useCallback(async () => {
    try {
      console.log("EXEC")
      const userInput = {
        "activity_id": "15367619474",
        "table": "get_activity_gps_data"
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
      <h2>Garmin map</h2>

    </div>
  );
};

export default Garmin;
