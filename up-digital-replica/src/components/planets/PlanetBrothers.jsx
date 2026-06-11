import React from 'react';

// Brothers (Pink/Rose)
export const PlanetBrothers = (props) => {
  return (
    <svg {...props} width="100" height="100" viewBox="0 0 200 200" style={{position: 'absolute', inset: '0', pointerEvents: 'none'}}><defs ><clipPath id="hp-5-clip"><circle cx="100" cy="100" r="100"></circle></clipPath><filter id="hp-5-land" x="0%" y="0%" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="5" seed="31" result="n"></feTurbulence><feColorMatrix in="n" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 5.6 -1.6" result="b"></feColorMatrix><feComposite in="SourceGraphic" in2="b" operator="in"></feComposite></filter><radialGradient id="hp-5-shade" cx="30%" cy="26%" r="80%"><stop offset="0%" stopColor="rgba(255,255,255,0.18)"></stop><stop offset="40%" stopColor="rgba(0,0,0,0)"></stop><stop offset="100%" stopColor="rgba(0,0,0,0.88)"></stop></radialGradient><radialGradient id="hp-5-atmo" cx="32%" cy="28%" r="78%"><stop offset="78%" stopColor="#F472B600"></stop><stop offset="100%" stopColor="#F472B6AA"></stop></radialGradient></defs><g clipPath="url(#hp-5-clip)"><rect width="200" height="200" fill="#831843"></rect><rect width="200" height="200" fill="#F472B6" filter="url(#hp-5-land)"></rect><rect width="200" height="200" fill="#F472B6" filter="url(#hp-5-land)" style={{mixBlendMode: 'screen'}} opacity="0.6"></rect><rect width="200" height="200" fill="#F472B6" filter="url(#hp-5-land)" style={{mixBlendMode: 'screen', filter: 'blur(2px)'}} opacity="0.6"></rect><circle cx="100" cy="100" r="100" fill="url(#hp-5-atmo)"></circle><circle cx="100" cy="100" r="100" fill="url(#hp-5-shade)"></circle><ellipse cx="58" cy="48" rx="22" ry="11" fill="rgba(255,255,255,0.18)" transform="rotate(-28 58 48)"></ellipse><ellipse cx="62" cy="44" rx="9" ry="4" fill="rgba(255,255,255,0.42)" transform="rotate(-28 62 44)"></ellipse></g></svg>
  );
};

export default PlanetBrothers;
