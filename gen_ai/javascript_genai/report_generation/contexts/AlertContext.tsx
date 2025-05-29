
import React, { createContext, useState, useCallback, useContext, ReactNode } from 'react';
import { AlertType } from '../types';
import { AlertContainer } from '../components/Alert';

interface AlertMessage {
  id: string;
  message: string;
  type: AlertType;
}

interface AlertContextType {
  alerts: AlertMessage[];
  addAlert: (message: string, type: AlertType, duration?: number) => void;
  removeAlert: (id: string) => void;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export const AlertProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  const [alerts, setAlerts] = useState<AlertMessage[]>([]);

  const removeAlert = useCallback((id: string) => {
    setAlerts((prevAlerts) => prevAlerts.filter((alert) => alert.id !== id));
  }, []);

  const addAlert = useCallback((message: string, type: AlertType, duration: number = 5000) => {
    const id = Math.random().toString(36).substr(2, 9);
    setAlerts((prevAlerts) => [...prevAlerts, { id, message, type }]);
    if (duration > 0) {
        setTimeout(() => {
        removeAlert(id);
        }, duration);
    }
  }, [removeAlert]);

  return (
    <AlertContext.Provider value={{ alerts, addAlert, removeAlert }}>
      {children}
      <AlertContainer alerts={alerts} removeAlert={removeAlert} />
    </AlertContext.Provider>
  );
};

export const useAlert = (): AlertContextType => {
  const context = useContext(AlertContext);
  if (context === undefined) {
    throw new Error('useAlert must be used within an AlertProvider');
  }
  return context;
};