import React, { useState, useEffect, useCallback } from 'react';
import axios from '../api/axios';
import TicketCard from './TicketCard';
import './TicketList.css';

const TicketList = ({ refreshTrigger }) => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filter state
  const [filters, setFilters] = useState({
    category: '',
    priority: '',
    status: '',
    search: ''
  });

  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'billing', label: 'Billing' },
    { value: 'technical', label: 'Technical' },
    { value: 'account', label: 'Account' },
    { value: 'general', label: 'General' }
  ];

  const priorities = [
    { value: '', label: 'All Priorities' },
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' }
  ];

  const statuses = [
    { value: '', label: 'All Statuses' },
    { value: 'open', label: 'Open' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' }
  ];

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      // Build query parameters
      const params = {};
      if (filters.category) params.category = filters.category;
      if (filters.priority) params.priority = filters.priority;
      if (filters.status) params.status = filters.status;
      if (filters.search) params.search = filters.search;

      const response = await axios.get('/api/tickets/', { params });
      setTickets(response.data);
    } catch (err) {
      setError('Failed to load tickets. Please try again.');
      console.error('Fetch tickets error:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Fetch tickets on mount and when filters change
  useEffect(() => {
    fetchTickets();
  }, [filters, fetchTickets]);

  // Fetch tickets when refreshTrigger changes (new ticket created)
  useEffect(() => {
    if (refreshTrigger) {
      fetchTickets();
    }
  }, [refreshTrigger, fetchTickets]);

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const [searchInput, setSearchInput] = useState('');

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters(prev => ({
        ...prev,
        search: searchInput
      }));
    }, 500);

    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleSearchChange = (e) => {
    setSearchInput(e.target.value);
  };

  const handleTicketUpdate = () => {
    // Refresh the list when a ticket is updated
    fetchTickets();
  };

  return (
    <div className="ticket-list-container">
      <div className="ticket-list-header">
        <h2>Support Tickets</h2>
        <div className="ticket-count">
          {!loading && `${tickets.length} ticket${tickets.length !== 1 ? 's' : ''}`}
        </div>
      </div>

      <div className="filters-container">
        <div className="filter-group">
          <label htmlFor="search">Search</label>
          <input
            type="text"
            id="search"
            placeholder="Search in title or description..."
            value={searchInput}
            onChange={handleSearchChange}
            className="search-input"
          />
        </div>

        <div className="filter-row">
          <div className="filter-group">
            <label htmlFor="category-filter">Category</label>
            <select
              id="category-filter"
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="filter-select"
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="priority-filter">Priority</label>
            <select
              id="priority-filter"
              value={filters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
              className="filter-select"
            >
              {priorities.map(pri => (
                <option key={pri.value} value={pri.value}>
                  {pri.label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="status-filter">Status</label>
            <select
              id="status-filter"
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="filter-select"
            >
              {statuses.map(stat => (
                <option key={stat.value} value={stat.value}>
                  {stat.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading-message">
          Loading tickets...
        </div>
      ) : tickets.length === 0 ? (
        <div className="empty-message">
          No tickets found. {filters.category || filters.priority || filters.status || filters.search ? 'Try adjusting your filters.' : 'Create your first ticket above!'}
        </div>
      ) : (
        <div className="tickets-grid">
          {tickets.map(ticket => (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
              onUpdate={handleTicketUpdate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TicketList;
