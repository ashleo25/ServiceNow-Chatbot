import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './MessageList.css';

const MessageList = ({ messages, isLoading = false, isEnhanced = false }) => {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessageContent = (content, messageType = null) => {
    if (isEnhanced && messageType) {
      return renderEnhancedContent(content, messageType);
    }
    return (
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={dark}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  const renderEnhancedContent = (content, messageType, message = null) => {
    // Special handling for welcome messages
    if (messageType === 'welcome') {
      return (
        <div className="welcome-message">
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="welcome-title">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="welcome-subtitle">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="welcome-section-title">{children}</h3>
              ),
              p: ({ children }) => (
                <p className="welcome-text">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="welcome-list">{children}</ul>
              ),
              li: ({ children }) => (
                <li className="welcome-list-item">{children}</li>
              ),
              strong: ({ children }) => (
                <strong className="welcome-strong">{children}</strong>
              ),
              hr: () => <hr className="welcome-divider" />,
              code: ({ children }) => (
                <code className="welcome-code">{children}</code>
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      );
    }

    // Special handling for ticket creation messages
    if (messageType === 'ticket_creation_result' && message?.ticketResult) {
      return (
        <div className="ticket-creation-result">
          <ReactMarkdown>{content}</ReactMarkdown>
          {message.ticketResult.success && (
            <div className="ticket-success-details">
              <div className="ticket-info">
                <p><strong>Ticket Number:</strong> {message.ticketResult.ticket_number}</p>
                <p><strong>Ticket ID:</strong> {message.ticketResult.ticket_id}</p>
                {message.ticketResult.priority && (
                  <p><strong>Priority:</strong> {message.ticketResult.priority} ({message.ticketResult.priority_name})</p>
                )}
                {message.ticketResult.sla_response_time && (
                  <p><strong>SLA Response:</strong> {message.ticketResult.sla_response_time}</p>
                )}
                {message.ticketResult.sla_resolution_time && (
                  <p><strong>SLA Resolution:</strong> {message.ticketResult.sla_resolution_time}</p>
                )}
                {message.ticketResult.ticket_url && (
                  <p>
                    <a 
                      href={message.ticketResult.ticket_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="ticket-link"
                    >
                      🔗 View Ticket in ServiceNow
                    </a>
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      );
    }

    // Special handling for duplicate detection messages
    if (messageType === 'present_duplicates' && message?.duplicates) {
      return (
        <div className="duplicate-detection">
          <ReactMarkdown>{content}</ReactMarkdown>
          <div className="duplicate-tickets">
            {message.duplicates.slice(0, 3).map((duplicate, index) => (
              <div key={index} className="duplicate-ticket">
                <div className="duplicate-ticket-header">
                  <strong>{duplicate.ticket?.number || 'N/A'}</strong>
                  <span className="similarity-score">
                    {Math.round(duplicate.similarity_score * 100)}% similar
                  </span>
                </div>
                <div className="duplicate-ticket-description">
                  {duplicate.ticket?.short_description || 'No description'}
                </div>
                <div className="duplicate-ticket-reasons">
                  {duplicate.similarity_reasons?.join(', ')}
                </div>
              </div>
            ))}
          </div>
          {message.requiresUserDecision && (
            <div className="duplicate-decision-prompt">
              <p>Please choose what you'd like to do:</p>
            </div>
          )}
        </div>
      );
    }

    // For all other bot messages, use standard markdown with enhanced styling
    return (
      <div className="bot-response-content">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="bot-heading">{children}</h1>
            ),
            h2: ({ children }) => (
              <h2 className="bot-heading">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="bot-heading">{children}</h3>
            ),
            h4: ({ children }) => (
              <h4 className="bot-heading">{children}</h4>
            ),
            h5: ({ children }) => (
              <h5 className="bot-heading">{children}</h5>
            ),
            h6: ({ children }) => (
              <h6 className="bot-heading">{children}</h6>
            ),
            p: ({ children }) => (
              <p className="bot-text">{children}</p>
            ),
            ul: ({ children }) => (
              <ul className="bot-list">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="bot-list">{children}</ol>
            ),
            li: ({ children }) => (
              <li className="bot-list-item">{children}</li>
            ),
            strong: ({ children }) => (
              <strong className="bot-strong">{children}</strong>
            ),
            code: ({ children }) => (
              <code className="bot-code">{children}</code>
            ),
            pre: ({ children }) => (
              <pre className="bot-pre">{children}</pre>
            ),
            blockquote: ({ children }) => (
              <blockquote className="bot-blockquote">{children}</blockquote>
            ),
            table: ({ children }) => (
              <table className="bot-table">{children}</table>
            ),
            a: ({ children, href }) => (
              <a href={href} className="bot-link">{children}</a>
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  };

  const renderSection = (title, content) => {
    const contentStr = content.join('\n').trim();
    
    if (title.includes('Summary') || title.includes('Request Summary')) {
      return (
        <div key={title} className="data-collection">
          <h4>{title}</h4>
          <ReactMarkdown>{contentStr}</ReactMarkdown>
        </div>
      );
    }
    
    if (title.includes('Search Results') || title.includes('Found')) {
      return (
        <div key={title} className="search-results">
          <h4>{title}</h4>
          <ReactMarkdown>{contentStr}</ReactMarkdown>
          <div className="search-results-actions">
            <p className="ticket-creation-prompt">
              <strong>Need more help?</strong> If these results don't solve your issue, you can create a formal ticket.
            </p>
            <div className="action-buttons">
              <button 
                className="action-button primary"
                onClick={() => {
                  // Trigger ticket creation by sending a message
                  const event = new CustomEvent('createTicket');
                  window.dispatchEvent(event);
                }}
              >
                Create Ticket
              </button>
              <button 
                className="action-button secondary"
                onClick={() => {
                  // Trigger new search
                  const event = new CustomEvent('newSearch');
                  window.dispatchEvent(event);
                }}
              >
                New Search
              </button>
            </div>
          </div>
        </div>
      );
    }
    
    if (title.includes('Intent') || title.includes('Detected')) {
      return (
        <div key={title} className="intent-detection">
          <h4>{title}</h4>
          <p>{contentStr}</p>
        </div>
      );
    }
    
    return (
      <div key={title} className="message-section">
        <h4>{title}</h4>
        <ReactMarkdown>{contentStr}</ReactMarkdown>
      </div>
    );
  };

  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="message-list">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message ${message.sender}${isEnhanced ? ' enhanced' : ''} ${message.messageType === 'welcome' ? 'welcome' : ''}`}
        >
          <div className="message-avatar">
            {message.sender === 'user' ? (
              'U'
            ) : message.sender === 'system' ? (
              '!'
            ) : (
              'AI'
            )}
          </div>
          
          <div className="message-content">
            <div className="message-header">
              <span className="message-sender">
                {message.sender === 'user' 
                  ? 'You' 
                  : message.sender === 'system'
                  ? 'System'
                  : isEnhanced
                  ? 'IT Support Assistant'
                  : message.agentType === 'search'
                  ? 'Search Agent'
                  : 'Ticket Agent'
                }
              </span>
              <span className="message-time">
                {formatTimestamp(message.timestamp)}
              </span>
            </div>
            
            <div className="message-body">
              {renderMessageContent(message.content, message.messageType, message)}
            </div>
          </div>
        </div>
      ))}
      
      {isLoading && (
        <div className="message bot enhanced">
          <div className="message-avatar">
            AI
          </div>
          <div className="message-content">
            <div className="message-header">
              <span className="message-sender">IT Support Assistant</span>
            </div>
            <div className="message-body">
              <div className="loading-dots">Thinking</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageList;