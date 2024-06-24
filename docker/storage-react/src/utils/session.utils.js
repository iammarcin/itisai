// session.utils.js

var currentSessionId = "";

const setCurrentSessionId = (session_id) => {
 if (session_id) {
  currentSessionId = session_id;
 }
};

const getCurrentSessionId = () => {
 return currentSessionId;
}

export { setCurrentSessionId, getCurrentSessionId };