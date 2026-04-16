import { useState, useCallback } from 'react';

// Simple context-based store for global state
export const useStore = () => {
  const [results, setResults] = useState({});
  const [history, setHistory] = useState([]);
  const [settings, setSettings] = useState({
    autoEnhance: true,
    confThreshold: 0.5,
    theme: 'dark',
  });

  const addResult = useCallback((key, data) => {
    setResults((prev) => ({ ...prev, [key]: data }));
    setHistory((prev) => [{ timestamp: new Date(), key, data }, ...prev.slice(0, 99)]);
  }, []);

  const clearResults = useCallback(() => {
    setResults({});
  }, []);

  const updateSettings = useCallback((newSettings) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  }, []);

  return {
    results,
    history,
    settings,
    addResult,
    clearResults,
    updateSettings,
  };
};
