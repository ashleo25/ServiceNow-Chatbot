import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import './ThemeToggle.css';

const ThemeToggle = ({ className = '' }) => {
  const { theme, setTheme } = useTheme();

  const themes = [
    { key: 'light', icon: Sun, label: 'Light' },
    { key: 'dark', icon: Moon, label: 'Dark' },
    { key: 'system', icon: Monitor, label: 'System' }
  ];

  return (
    <div className={`theme-toggle ${className}`}>
      <div className="theme-toggle-container">
        {themes.map(({ key, icon: Icon, label }) => (
          <button
            key={key}
            className={`theme-option ${theme === key ? 'active' : ''}`}
            onClick={() => setTheme(key)}
            title={`Switch to ${label} theme`}
            aria-label={`Switch to ${label} theme`}
          >
            <Icon size={16} />
            <span className="theme-label">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ThemeToggle;