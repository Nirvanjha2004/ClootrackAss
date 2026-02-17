import React, { useState, useEffect } from 'react';
import axios from '../api/axios';
import './StatsPanel.css';

const StatsPanel = ({ refreshTrigger }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchStats = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.get('/api/tickets/stats/');
      setStats(response.data);
    } catch (err) {
      setError('Failed to load statistics. Please try again.');
      console.error('Fetch stats error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch stats on mount
  useEffect(() => {
    fetchStats();
  }, []);

  // Re-fetch stats when refreshTrigger changes
  useEffect(() => {
    if (refreshTrigger) {
      fetchStats();
    }
  }, [refreshTrigger]);

  if (loading) {
    return (
      <div className="stats-panel-container">
        <h2>Statistics</h2>
        <div className="loading-message">Loading statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stats-panel-container">
        <h2>Statistics</h2>
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="stats-panel-container">
      <h2>Statistics</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_tickets}</div>
          <div className="stat-label">Total Tickets</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats.open_tickets}</div>
          <div className="stat-label">Open Tickets</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats.avg_tickets_per_day}</div>
          <div className="stat-label">Avg Tickets/Day</div>
        </div>
      </div>

      <div className="breakdown-section">
        <div className="breakdown-card">
          <h3>Priority Breakdown</h3>
          <ul className="breakdown-list">
            {Object.entries(stats.priority_breakdown || {}).map(([priority, count]) => (
              <li key={priority} className="breakdown-item">
                <span className={`priority-badge priority-${priority}`}>
                  {priority.charAt(0).toUpperCase() + priority.slice(1)}
                </span>
                <span className="breakdown-count">{count}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="breakdown-card">
          <h3>Category Breakdown</h3>
          <ul className="breakdown-list">
            {Object.entries(stats.category_breakdown || {}).map(([category, count]) => (
              <li key={category} className="breakdown-item">
                <span className={`category-badge category-${category}`}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </span>
                <span className="breakdown-count">{count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default StatsPanel;
