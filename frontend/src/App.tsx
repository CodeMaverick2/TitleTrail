import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import PropertyDetailsPage from './pages/PropertyDetailsPage';
import DigitalRain from './components/DigitalRain';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <DigitalRain />
        <div className="content-wrapper">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/property/:propertyId" element={<PropertyDetailsPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;