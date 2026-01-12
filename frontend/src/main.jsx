import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './styles/main.css';

import TaskInput from './components/TaskInput';
import TaskList from './components/TaskList';
import XPBar from './components/XPBar';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

function App() {
  const [user, setUser] = useState(null);

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  return (
    <Dashboard />
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
