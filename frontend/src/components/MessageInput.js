import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Mic, MicOff } from 'lucide-react';
import './MessageInput.css';

const MessageInput = ({ 
  value: externalValue,
  onChange: externalOnChange,
  onSend,
  onSendMessage,
  disabled, 
  placeholder 
}) => {
  // Support both controlled and uncontrolled modes
  const isControlled = externalValue !== undefined && externalOnChange !== undefined;
  const [internalValue, setInternalValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef(null);
  
  const value = isControlled ? externalValue : internalValue;
  const setValue = isControlled ? externalOnChange : setInternalValue;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (value.trim() && !disabled) {
      if (onSendMessage) {
        onSendMessage(value.trim());
        if (!isControlled) {
          setValue('');
        }
      } else if (onSend) {
        onSend(value.trim());
        if (!isControlled) {
          setValue('');
        }
      }
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Handle file upload logic here
      console.log('File selected:', file.name);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Handle recording logic here
  };

  return (
    <div className="message-input">
      <div className="input-container">
        <div className="input-actions">
          <button
            className="action-button"
            onClick={() => document.getElementById('file-upload').click()}
            disabled={disabled}
            title="Attach file"
          >
            <Paperclip size={18} />
          </button>
          
          <button
            className={`action-button ${isRecording ? 'recording' : ''}`}
            onClick={toggleRecording}
            disabled={disabled}
            title={isRecording ? 'Stop recording' : 'Start recording'}
          >
            {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
          </button>
        </div>
        
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            className="message-textarea"
            rows={1}
            maxLength={2000}
          />
          
          <div className="input-footer">
            <span className="char-count">
              {value.length}/2000
            </span>
          </div>
        </div>
        
        <button
          className={`send-button ${value.trim() && !disabled ? 'active' : ''}`}
          onClick={handleSend}
          disabled={!value.trim() || disabled}
          title="Send message"
        >
          <Send size={18} />
        </button>
      </div>
      
      <input
        id="file-upload"
        type="file"
        style={{ display: 'none' }}
        onChange={handleFileUpload}
        accept="image/*,.pdf,.doc,.docx,.txt"
      />
    </div>
  );
};

export default MessageInput;