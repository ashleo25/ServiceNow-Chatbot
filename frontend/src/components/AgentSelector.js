import React from 'react';
import { Search, Ticket, Database, Bot } from 'lucide-react';
import './AgentSelector.css';

const AgentSelector = ({ selectedAgent, onAgentChange }) => {
  const agents = [
    {
      id: 'enhanced',
      name: 'Enhanced Assistant',
      description: 'AI-powered intent detection with structured data collection',
      icon: <Bot size={20} />,
      color: '#1976d2'
    },
    {
      id: 'search',
      name: 'Search Agent',
      description: 'Search knowledge base and ServiceNow records',
      icon: <Search size={20} />,
      color: '#4f46e5'
    },
    {
      id: 'ticket',
      name: 'Ticket Agent',
      description: 'Create and manage ServiceNow tickets',
      icon: <Ticket size={20} />,
      color: '#059669'
    }
  ];

  return (
    <div className="agent-selector">
      <div className="agent-selector-header">
        <h3>Choose an Agent</h3>
        <p>Select the type of assistance you need</p>
      </div>
      
      <div className="agent-options">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`agent-option ${selectedAgent === agent.id ? 'selected' : ''}`}
            onClick={() => onAgentChange(agent.id)}
            style={{
              '--agent-color': agent.color,
              borderColor: selectedAgent === agent.id ? agent.color : 'transparent'
            }}
          >
            <div className="agent-icon" style={{ color: agent.color }}>
              {agent.icon}
            </div>
            <div className="agent-info">
              <h4>{agent.name}</h4>
              <p>{agent.description}</p>
            </div>
            <div className="agent-radio">
              <div className={`radio-dot ${selectedAgent === agent.id ? 'active' : ''}`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentSelector;
