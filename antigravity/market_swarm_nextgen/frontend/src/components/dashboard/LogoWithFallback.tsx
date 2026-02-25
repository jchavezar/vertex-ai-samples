import React from 'react';

interface LogoWithFallbackProps {
  ticker: string;
  className?: string;
}

const LogoWithFallback: React.FC<LogoWithFallbackProps> = ({ ticker, className }) => {
  const [error, setError] = React.useState(false);

  if (error) {
    return (
      <div className={`${className} flex items-center justify-center rounded-xl bg-gradient-to-br from-gray-800 to-gray-950 border border-white/10 shadow-inner overflow-hidden relative`}>
        <div className="absolute inset-0 bg-blue-500/5" />
        <span className="text-[14px] font-black text-white/40 tracking-tighter uppercase select-none">
          {ticker.slice(0, 2)}
        </span>
      </div>
    );
  }

  return (
    <img
      src={`/assets/${ticker.toLowerCase()}_3d_icon.png`}
      onError={() => setError(true)}
      className={className}
      alt={ticker}
    />
  );
};

export default React.memo(LogoWithFallback);
