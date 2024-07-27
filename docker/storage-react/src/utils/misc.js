// misc.js

const formatDate = (dateString) => {
  if (dateString === null) {
    return '';
  }
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};

// used in ChatMessage - when we execute handleEdit 
// to convert list of attached image to proper format so it can be used later to submit to API
const convertFileAndImageLocationsToAttached = (imageLocations) => {
  return imageLocations.map(url => ({
    file: null, // Since we don't have the file, this can be null
    url: url,
    placeholder: false
  }));
};

// this is used in FloatingChat - we get data from DB and we optimize it before sending to API
// by optimize i mean: formatting it like CSV file (putting columns in first line and then only values)
// and getting rid of some data
const optimizeHealthDataForAPICall = (data) => {
  // Define columns to keep
  const columnsToKeep = [
    'calendar_date', 'sleep_time_seconds', 'sleep_start', 'sleep_end',
    'deep_sleep_seconds', 'light_sleep_seconds', 'rem_sleep_seconds',
    'awake_sleep_seconds', 'average_respiration_value', 'avg_sleep_stress',
    'overall_score_value', 'overall_score_qualifier', 'rem_percentage_value',
    'light_percentage_value', 'deep_percentage_value', 'avg_overnight_hrv',
    'resting_heart_rate', 'body_battery_change'
  ];

  // Sort data by date (descending) and take last 7 days
  //const sortedData = data.sort((a, b) => new Date(b.calendar_date) - new Date(a.calendar_date)).slice(0, 7);

  // Create CSV-like structure
  let csvData = columnsToKeep.join(',') + '\n';

  data.forEach(day => {
    csvData += columnsToKeep.map(col => day[col]).join(',') + '\n';
  });

  return csvData.trim();
};




export { formatDate, convertFileAndImageLocationsToAttached, optimizeHealthDataForAPICall };