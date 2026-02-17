import React, { useState } from 'react';
import './App.css';
import TicketForm from './components/TicketForm';
import TicketList from './components/TicketList';
import StatsPanel from './components/StatsPanel';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTicketCreated = (ticket) => {
    console.log('Ticket created:', ticket);
    // Trigger refresh of ticket list and stats
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Support Ticket System</h1>
      </header>
      <main className="App-main">
        <StatsPanel refreshTrigger={refreshTrigger} />
        <TicketForm onTicketCreated={handleTicketCreated} />
        <TicketList refreshTrigger={refreshTrigger} />
      </main>
    </div>
  );
}

export default App;
