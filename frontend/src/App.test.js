import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

test('renders Support Ticket System header', () => {
  render(<App />);
  const headerElement = screen.getByText(/Support Ticket System/i);
  expect(headerElement).toBeInTheDocument();
});

test('renders Create New Ticket form', () => {
  render(<App />);
  const formHeader = screen.getByText(/Create New Ticket/i);
  expect(formHeader).toBeInTheDocument();
});

test('renders Support Tickets list', () => {
  render(<App />);
  const listHeader = screen.getByText(/Support Tickets/i);
  expect(listHeader).toBeInTheDocument();
});
