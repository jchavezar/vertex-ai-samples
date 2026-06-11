import React from 'react';

const CLIENTS = [
  "Supermicro",
  "Avant Gallery",
  "Bayer",
  "Mauboussin",
  "Villeroy & Boch",
  "Dorchester",
  "Four Seasons",
  "Sephora",
  "Ritz-Carlton"
];

export const Clients = () => {
  // Duplicate the list multiple times to ensure it fills the width and scrolls seamlessly
  const doubledClients = [...CLIENTS, ...CLIENTS, ...CLIENTS, ...CLIENTS];

  return (
    <section className="relative overflow-hidden py-16 bg-brand-light-alt border-y border-brand-dark-alt/5">
      <div className="w-full flex overflow-hidden select-none">
        <div className="flex shrink-0 gap-16 items-center animate-client-scroll min-w-full justify-around pr-16">
          {doubledClients.map((client, idx) => (
            <span 
              key={idx} 
              className="text-brand-dark-alt/40 font-black text-xl md:text-2xl tracking-widest uppercase flex items-center gap-4 whitespace-nowrap"
            >
              {client}
              <span className="text-brand-lime text-lg">✦</span>
            </span>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Clients;
