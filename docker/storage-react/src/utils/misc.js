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

export { formatDate, convertFileAndImageLocationsToAttached };