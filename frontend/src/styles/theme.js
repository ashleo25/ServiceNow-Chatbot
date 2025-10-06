/**
 * SmarTek21 Brand Theme System
 * ChatGPT-inspired design with SmarTek21 brand colors
 */

// SmarTek21 Brand Colors (from Brandfetch)
export const brandColors = {
  shark: '#23272b',        // Primary text color
  wildSand: '#f5f5f5',     // Primary background
  silverChalice: '#9f9f9f', // Muted text/borders
};

// Theme Tokens
export const tokens = {
  colors: {
    // Brand neutrals
    fg: brandColors.shark,
    bg: brandColors.wildSand,
    muted: brandColors.silverChalice,
    
    // Accent colors (deep indigo for WCAG AA compliance)
    accent: {
      light: '#4338ca', // indigo-800
      dark: '#6366f1',  // indigo-400
    },
    
    // Light theme
    light: {
      bg: '#f5f5f5',      // Wild Sand
      surface: '#ffffff',  // Pure white surfaces
      text: '#23272b',     // Shark
      textSecondary: '#6b7280', // Gray-500
      textMuted: '#9f9f9f', // Silver Chalice
      border: '#e7e7e7',   // Light borders
      accent: '#4338ca',   // Indigo-800
      accentHover: '#3730a3', // Indigo-900
      
      // Message specific
      messageBg: '#ffffff',
      messageUserBg: '#f8fafc',
      messageAssistantBg: '#fafbfc',
      
      // Status colors
      success: '#059669',
      warning: '#d97706',
      error: '#dc2626',
      info: '#0284c7',
    },
    
    // Dark theme
    dark: {
      bg: '#0f1115',       // Very dark background
      surface: '#151822',   // Dark surfaces
      text: '#e6e8ee',     // Light text
      textSecondary: '#9ca3af', // Gray-400
      textMuted: '#6b7280', // Gray-500
      border: '#2a2e3a',   // Dark borders
      accent: '#6366f1',   // Indigo-400
      accentHover: '#8b5cf6', // Violet-500
      
      // Message specific
      messageBg: '#1f2937',
      messageUserBg: '#374151',
      messageAssistantBg: '#1e293b',
      
      // Status colors
      success: '#10b981',
      warning: '#f59e0b',
      error: '#f87171',
      info: '#3b82f6',
    },
  },
  
  // Typography scale (system UI stack)
  typography: {
    fontFamily: {
      system: [
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
      ].join(', '),
      mono: [
        'ui-monospace',
        'SFMono-Regular',
        '"SF Mono"',
        'Consolas',
        '"Liberation Mono"',
        'Menlo',
        'monospace',
      ].join(', '),
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '0.9375rem', // 15px (slightly larger body)
      lg: '1rem',       // 16px
      xl: '1.125rem',   // 18px
      '2xl': '1.25rem', // 20px
      '3xl': '1.5rem',  // 24px
    },
    lineHeight: {
      tight: '1.25',    // For message bubbles
      normal: '1.5',    // For markdown content
      relaxed: '1.625', // For generous spacing
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
  },
  
  // Spacing scale (8px base)
  spacing: {
    xs: '0.5rem',   // 8px
    sm: '0.75rem',  // 12px
    md: '1rem',     // 16px
    lg: '1.25rem',  // 20px
    xl: '1.5rem',   // 24px
    '2xl': '2rem',  // 32px
    '3xl': '3rem',  // 48px
  },
  
  // Border radius
  radius: {
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '1rem',      // 16px
    xl: '1.25rem',   // 20px
    '2xl': '1.5rem', // 24px
    full: '9999px',  // Full round
  },
  
  // Shadows (soft, low elevation)
  shadows: {
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  
  // Transitions (smooth 150-200ms)
  transitions: {
    fast: '150ms ease',
    normal: '200ms ease',
    slow: '300ms ease',
    
    // Specific properties
    colors: '150ms ease',
    shadow: '200ms ease',
    transform: '200ms ease',
  },
  
  // Layout constants
  layout: {
    sidebarWidth: '280px',
    maxContentWidth: '780px',
    headerHeight: '64px',
    composerMaxHeight: '200px', // ~6 lines
  },
};

// Theme context creation helper
export const createTheme = (mode = 'light') => ({
  mode,
  colors: tokens.colors[mode],
  ...tokens,
});

// CSS custom properties generator
export const generateCSSVariables = (theme) => {
  const cssVars = {};
  
  // Colors
  Object.entries(theme.colors).forEach(([key, value]) => {
    if (typeof value === 'string') {
      cssVars[`--color-${key}`] = value;
    }
  });
  
  // Typography
  cssVars['--font-family-system'] = theme.typography.fontFamily.system;
  cssVars['--font-family-mono'] = theme.typography.fontFamily.mono;
  
  // Spacing
  Object.entries(theme.spacing).forEach(([key, value]) => {
    cssVars[`--spacing-${key}`] = value;
  });
  
  // Radius
  Object.entries(theme.radius).forEach(([key, value]) => {
    cssVars[`--radius-${key}`] = value;
  });
  
  // Layout
  Object.entries(theme.layout).forEach(([key, value]) => {
    cssVars[`--layout-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`] = value;
  });
  
  return cssVars;
};

// Default themes
export const lightTheme = createTheme('light');
export const darkTheme = createTheme('dark');

export default {
  tokens,
  lightTheme,
  darkTheme,
  createTheme,
  generateCSSVariables,
};