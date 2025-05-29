
import React from 'react';
import { AlertType } from '../types';
import { useAlert } from '../contexts/AlertContext'; // Assuming AlertContext might provide onClose

interface AlertProps {
  id: string; // Added id for keying and removal
  message: string;
  type: AlertType;
  onClose?: (id: string) => void; // Pass id to onClose
}

export const Alert: React.FC<AlertProps> = ({ id, message, type, onClose }) => {
  let baseClasses = 'border-l-4 p-4 rounded-md shadow-lg text-sm w-full max-w-md mx-auto my-2';
  let typeClasses = '';
  let iconPath = "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"; // Info
  let iconFillClass = 'fill-current h-5 w-5 mr-3';

  switch (type) {
    case AlertType.SUCCESS:
      typeClasses = 'bg-dj-blue/10 border-dj-blue text-dj-blue';
      iconPath = "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"; // Success
      iconFillClass += ' text-dj-blue';
      break;
    case AlertType.ERROR:
      typeClasses = 'bg-red-600/10 border-red-600 text-red-700 dark:bg-red-700/20 dark:text-red-300 dark:border-red-500';
      iconPath = "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"; // Error
      iconFillClass += ' text-red-600 dark:text-red-400';
      break;
    case AlertType.INFO:
    default:
      typeClasses = 'bg-dj-secondary-blue/10 border-dj-secondary-blue text-dj-secondary-blue'; // Using secondary blue for info
      iconPath = "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"; // Info
      iconFillClass += ' text-dj-secondary-blue';
      break;
  }

  return (
    <div className={`${baseClasses} ${typeClasses} bg-dj-nav-bg`} role="alert">
      <div className="flex">
        <div className="py-1">
          <svg className={iconFillClass} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path d={iconPath}/>
          </svg>
        </div>
        <div className="flex-grow">
          <p className="font-medium">{type.charAt(0).toUpperCase() + type.slice(1)}</p>
          <p>{message}</p>
        </div>
        {onClose && (
          <button 
            onClick={() => onClose(id)} 
            className="ml-auto -mx-1.5 -my-1.5 p-1.5 rounded-lg focus:ring-2 focus:ring-current inline-flex h-8 w-8 items-center justify-center hover:bg-opacity-20 hover:bg-current transition-colors" 
            aria-label="Dismiss"
          >
            <span className="sr-only">Dismiss</span>
            <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

// New AlertContainer component
interface AlertContainerProps {
  alerts: Array<{ id: string; message: string; type: AlertType }>;
  removeAlert: (id: string) => void;
}

export const AlertContainer: React.FC<AlertContainerProps> = ({ alerts, removeAlert }) => {
  if (!alerts.length) return null;

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-[100] w-full max-w-md px-4 space-y-2">
      {alerts.map((alert) => (
        <Alert
          key={alert.id}
          id={alert.id}
          message={alert.message}
          type={alert.type}
          onClose={removeAlert}
        />
      ))}
    </div>
  );
};