// Health.js

import React, { useEffect, useState, useRef, useCallback, useContext } from 'react';
import { StateContext } from '../StateContextProvider';
import apiMethods from '../../services/api.methods';
import FloatingChat from './FloatingChat';
import SleepPhasesChart from './charts/SleepPhasesChart';
import SleepStartEndChart from './charts/SleepStartEndChart';
import SleepMetricsChart from './charts/SleepMetricsChart';
import ChatImageModal from '../ChatImageModal';
import TopMenu from '../TopMenu';

import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import './css/Health.css';

const Health = () => {
  const {
    isMobile
  } = useContext(StateContext);

  const [data, setData] = useState([]);
  const [isError, setIsError] = useState(false);
  const [dateRange, setDateRange] = useState([new Date(2024, 6, 1), new Date()]);
  const [startDate, endDate] = dateRange;
  const hasFetchedData = useRef(false);
  const [isFullWidth, setIsFullWidth] = useState(isMobile ? true : false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentChartIndex, setCurrentChartIndex] = useState(0);

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

  const toggleChartSize = () => {
    setIsFullWidth(!isFullWidth);
  };

  const openModal = (index) => {
    setCurrentChartIndex(index);
    setIsModalOpen(true);
  };

  // this is to differentiate if legend was click (so for example Deep sleep in sleep phases)
  // because then we don't want to open modal - we just want to enable/disable this element
  // for any other place in chart - we want to open modal
  const handleChartClick = (clickType, index = 0) => {
    if (clickType !== 'legend') {
      // Chart area or data point was clicked
      openModal(index);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const nextChart = () => {
    setCurrentChartIndex((currentChartIndex + 1) % charts.length);
  };

  const prevChart = () => {
    setCurrentChartIndex((currentChartIndex - 1 + charts.length) % charts.length);
  };

  if (isError) {
    return <div>Error fetching data.</div>;
  }

  const charts = [
    <SleepPhasesChart index={0} data={data} isFullWidth={isFullWidth} key="Daily Sleep Stages" isMobile={isMobile} isModalOpen={isModalOpen} onChartClick={handleChartClick} />,
    <SleepStartEndChart index={1} data={data} isFullWidth={isFullWidth} key="Sleep start / end" isMobile={isMobile} isModalOpen={isModalOpen} onChartClick={handleChartClick} />,
    <SleepMetricsChart index={2} data={data} isFullWidth={isFullWidth} key="Sleep metrics" isMobile={isMobile} isModalOpen={isModalOpen} onChartClick={handleChartClick} />
  ];

  return (
    <div className="layout">
      <TopMenu
        isHealthSection={true}
      />
      <div className="health-container">

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
        {!isMobile && (
          <div className="health-button-container">
            <button className="health-button-toggle" onClick={toggleChartSize}>
              {isFullWidth ? 'Small Graphs' : 'Full screen graphs'}
            </button>
          </div>
        )}
        <div className={`charts-container ${isFullWidth ? 'full-width' : 'small-graphs'}`}>
          {charts.map((chart, index) => (
            <div key={index + "m"}>
              <h4 key={index + "n"} className="chart-title">{chart.key}</h4>
              <div key={index} className="chart-wrapper">
                {chart}
              </div>
            </div>
          ))}
        </div>
        {isModalOpen && (
          <ChatImageModal
            images={charts}
            currentIndex={currentChartIndex}
            onClose={closeModal}
            onNext={nextChart}
            onPrev={prevChart}
            isChart={true}
          />
        )}
        <FloatingChat data={data} />
      </div>
    </div>
  );
};

export default Health;