// options/General.js

import React from 'react';

const General = () => {
 const isProduction = process.env.NODE_ENV === 'production';

 return (
  <div className="general-options">
   {!isProduction && (
    <div className="option-item">
     <label>Production Mode</label>
     <input type="checkbox" />
    </div>
   )}
   <div className="option-item">
    <label>Test Data</label>
    <input type="checkbox" />
   </div>
   <div className="option-item">
    <label>Use Watson for nonprod</label>
    <input type="checkbox" />
   </div>
   <div className="option-item">
    <label>API auth Token</label>
    <input type="password" />
   </div>
  </div>
 );
};

export default General;
