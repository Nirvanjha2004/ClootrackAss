import React, { useState, useEffect, useCallback } from 'react';
import axios from '../api/axios';
import './TicketForm.css';

const TicketForm = ({ onTicketCreated }) => {
  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('general');
  const [priority, setPriority] = useState('medium');
  
  // UI state
  const [isClassifying, setIsClassifying] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  // Valid choices from backend
  const categories = [
    { value: 'billing', label: 'Billing' },
    { value: 'technical', label: 'Technical' },
    { value: 'account', label: 'Account' },
    { value: 'general', label: 'General' }
  ];
  
  const priorities = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' }
  ];
  
  const classifyTicket = useCallback(async () => {
    setIsClassifying(true);
    try {
      const response = await axios.post('/api/tickets/classify/', {
        description: description
      });
      
      if (response.data.suggested_category) {
        setCategory(response.data.suggested_category);
      }
      if (response.data.suggested_priority) {
        setPriority(response.data.suggested_priority);
      }
    } catch (err) {
      // Silently fail - user can still manually select category and priority
    } finally {
      setIsClassifying(false);
    }
  }, [description]);
  
  // LLM classification with debounce
  useEffect(() => {
    if (!description.trim()) {
      return;
    }
    
    const timer = setTimeout(() => {
      classifyTicket();
    }, 1000); // 1 second debounce
    
    return () => clearTimeout(timer);
  }, [description, classifyTicket]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    try {
      const response = await axios.post('/api/tickets/', {
        title,
        description,
        category,
        priority
      });
      
      // Clear form on success
      setTitle('');
      setDescription('');
      setCategory('general');
      setPriority('medium');
      
      // Notify parent component
      if (onTicketCreated) {
        onTicketCreated(response.data);
      }
    } catch (err) {
      if (err.response && err.response.data) {
        // Display validation errors
        const errors = err.response.data;
        const errorMessages = Object.entries(errors)
          .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
          .join('; ');
        setError(errorMessages);
      } else {
        setError('Failed to create ticket. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="ticket-form-container">
      <h2>Create New Ticket</h2>
      <form onSubmit={handleSubmit} className="ticket-form">
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
            required
            placeholder="Brief description of your issue"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            rows={5}
            placeholder="Detailed description of your issue"
          />
          {isClassifying && (
            <span className="classifying-indicator">
              🤖 Analyzing description...
            </span>
          )}
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="category">Category *</label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              required
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="priority">Priority *</label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              required
            >
              {priorities.map(pri => (
                <option key={pri.value} value={pri.value}>
                  {pri.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <button 
          type="submit" 
          className="submit-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating...' : 'Create Ticket'}
        </button>
      </form>
    </div>
  );
};

export default TicketForm;
