import { useState, useEffect } from 'react';

// Simplified hook to fetch stock data (simulated with real-world logic for demo)
// In a real production app, you'd use a backend proxy for Yahoo Finance or Alpha Vantage
export const useStockData = (ticker) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Simulating a fetch from a financial API
        // In reality, we'd call something like:
        // const response = await fetch(`https://api.example.com/stocks/${ticker}`);

        // Let's create a realistic mock that "fetches" based on the ticker
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulate network lag

        const basePrice = ticker === 'FDS-US' ? 288.48 : 150.00;
        const change = (Math.random() * 10 - 5).toFixed(2);
        const changePercent = ((change / basePrice) * 100).toFixed(2);

        setData({
          ticker,
          price: (basePrice + parseFloat(change)).toFixed(2),
          change: change > 0 ? `+${change}` : change,
          changePercent: change > 0 ? `+${changePercent}%` : `${changePercent}%`,
          isUp: change > 0,
          lastUpdated: new Date().toLocaleTimeString(),
          marketCap: "11,102.43M"
        });
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, [ticker]);

  return { data, loading, error };
};
