import React, { useState } from 'react';
import axios from '../api/axios';
import './TicketCard.css';

const TicketCard = ({ ticket, onUpdate }) => {
  const [status, setStatus] = useState(ticket.status);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState('');

  const statusOptions = [
    { value: 'open', label: 'Open' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' }
  ];

  const handleStatusChange = async (e) => {
    const newStatus = e.target.value;
    setStatus(newStatus);
    setIsUpdating(true);
    setError('');

    try {
      await axios.patch(`/api/tickets/${ticket.id}/`, {
        status: newStatus
      });

      // Notify parent component to refresh the list
      if (onUpdate) {
        onUpdate();
      }
    } catch (err) {
      // Revert status on error
      setStatus(ticket.status);
      setError('Failed to update status');
      console.error('Status update error:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateDescription = (text, maxLength = 150) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const getPriorityClass = (priority) => {
    return `priority-${priority}`;
  };

  const getCategoryClass = (category) => {
    return `category-${category}`;
  };

  return (
    <div className="ticket-card">
      <div className="ticket-header">
        <h3 className="ticket-title">{ticket.title}</h3>
        <div className="ticket-status-control">
          <select
            value={status}
            onChange={handleStatusChange}
            disabled={isUpdating}
            className={`status-dropdown status-${status}`}
          >
            {statusOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <p className="ticket-description">
        {truncateDescription(ticket.description)}
      </p>

      <div className="ticket-meta">
        <span className={`ticket-badge ${getCategoryClass(ticket.category)}`}>
          {ticket.category}
        </span>
        <span className={`ticket-badge ${getPriorityClass(ticket.priority)}`}>
          {ticket.priority}
        </span>
        <span className="ticket-timestamp">
          {formatDate(ticket.created_at)}
        </span>
      </div>

      {error && (
        <div className="ticket-error">
          {error}
        </div>
      )}
    </div>
  );
};

export default TicketCard;
