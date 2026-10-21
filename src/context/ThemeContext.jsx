import React, { createContext, useContext, useEffect } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  useEffect(() => {
    // Enforce pure light mode across the application
    document.documentElement.classList.remove('dark');
    localStorage.setItem('auracart_theme', 'light');
  }, []);

  return (
    <ThemeContext.Provider value={{ theme: 'light', isDark: false, toggleTheme: () => {} }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;
