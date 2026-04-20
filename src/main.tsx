/**
 * TigerEx Frontend - React Application Entry Point
 * @file main.tsx
 * @description Main React application bootstrap
 * @author TigerEx Development Team
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);