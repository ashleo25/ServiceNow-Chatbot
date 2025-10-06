import { useState, useEffect, useCallback, createContext, useContext } from 'react';

// Theme Context
const ThemeContext = createContext({
  theme: 'light',
  toggleTheme: () => {},
  setTheme: () => {},
});

// Theme Provider Component
export const ThemeProvider = ({ children, defaultTheme = 'light' }) => {
  const [theme, setThemeState] = useState(defaultTheme);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('smartek21-theme');
    if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
      setThemeState(savedTheme);
    }
  }, []);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    
    // Also set class for compatibility
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme);
  }, [theme]);

  // Set theme and persist to localStorage
  const setTheme = useCallback((newTheme) => {
    if (['light', 'dark'].includes(newTheme)) {
      setThemeState(newTheme);
      localStorage.setItem('smartek21-theme', newTheme);
    }
  }, []);

  // Toggle between light and dark
  const toggleTheme = useCallback(() => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  }, [theme, setTheme]);

  const value = {
    theme,
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// Hook to use theme
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Hook for system preference detection
export const useSystemTheme = () => {
  const [systemTheme, setSystemTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e) => {
      setSystemTheme(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return systemTheme;
};

// Hook for auto theme (follows system preference)
export const useAutoTheme = () => {
  const systemTheme = useSystemTheme();
  const { theme, setTheme } = useTheme();
  const [isAuto, setIsAuto] = useState(false);

  // Enable auto theme
  const enableAutoTheme = useCallback(() => {
    setIsAuto(true);
    setTheme(systemTheme);
    localStorage.setItem('smartek21-theme-auto', 'true');
  }, [systemTheme, setTheme]);

  // Disable auto theme
  const disableAutoTheme = useCallback(() => {
    setIsAuto(false);
    localStorage.removeItem('smartek21-theme-auto');
  }, []);

  // Check if auto theme is enabled on mount
  useEffect(() => {
    const autoEnabled = localStorage.getItem('smartek21-theme-auto') === 'true';
    setIsAuto(autoEnabled);
  }, []);

  // Follow system theme when auto is enabled
  useEffect(() => {
    if (isAuto) {
      setTheme(systemTheme);
    }
  }, [isAuto, systemTheme, setTheme]);

  return {
    isAuto,
    systemTheme,
    enableAutoTheme,
    disableAutoTheme,
  };
};

// CSS-in-JS theme hook (for dynamic styling)
export const useThemeStyles = () => {
  const { theme } = useTheme();
  
  return {
    theme,
    // Get CSS custom property value
    getCSSVar: useCallback((property) => {
      if (typeof window !== 'undefined') {
        return getComputedStyle(document.documentElement)
          .getPropertyValue(property)
          .trim();
      }
      return '';
    }, []),
    
    // Theme-aware styles
    styles: {
      // Common interactive styles
      button: {
        primary: `
          background-color: var(--color-accent);
          color: white;
          border: none;
          border-radius: var(--radius-lg);
          padding: var(--spacing-sm) var(--spacing-lg);
          font-weight: var(--font-weight-medium);
          transition: var(--transition-colors);
          cursor: pointer;
        `,
        secondary: `
          background-color: transparent;
          color: var(--color-text-secondary);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--spacing-sm) var(--spacing-lg);
          font-weight: var(--font-weight-medium);
          transition: var(--transition-colors);
          cursor: pointer;
        `,
      },
      
      // Message styles
      message: {
        user: `
          background-color: var(--color-message-user-bg);
          border-radius: var(--radius-2xl);
          padding: var(--spacing-md) var(--spacing-lg);
          margin: var(--spacing-sm) 0;
        `,
        assistant: `
          background-color: var(--color-message-assistant-bg);
          border-radius: var(--radius-2xl);
          padding: var(--spacing-md) var(--spacing-lg);
          margin: var(--spacing-sm) 0;
          box-shadow: var(--shadow-sm);
        `,
      },
    },
  };
};

export default useTheme;