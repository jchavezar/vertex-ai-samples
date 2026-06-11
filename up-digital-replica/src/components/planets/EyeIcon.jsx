import React from 'react';

// Eye Icon
export const EyeIcon = (props) => {
  return (
    <svg {...props} viewBox="0 0 200 200" style={{position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '88%', height: '88%', pointerEvents: 'none', zIndex: '2', opacity: '0.92'}}><defs ><radialGradient id="cv-eye-iris" cx="50%" cy="50%" r="55%"><stop offset="0%" stopColor="#E5FFB8"></stop><stop offset="55%" stopColor="#BFFF00"></stop><stop offset="100%" stopColor="#5E7C00"></stop></radialGradient><clipPath id="cv-eye-shape"><path d="M 20 100 Q 100 28 180 100 Q 100 172 20 100 Z"></path></clipPath></defs><path d="M 20 100 Q 100 28 180 100 Q 100 172 20 100 Z" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.45)" strokeWidth="1.2"></path><path d="M 20 100 Q 100 28 180 100" fill="none" stroke="rgba(255,255,255,0.65)" strokeWidth="1.5" strokeLinecap="round"></path><path d="M 20 100 Q 100 172 180 100" fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth="1.2" strokeLinecap="round"></path><g className="cv-eye-pupil" clipPath="url(#cv-eye-shape)" style={props.pupilStyle}><circle cx="100" cy="100" r="28" fill="url(#cv-eye-iris)"></circle><circle cx="100" cy="100" r="28" fill="none" stroke="rgba(0,0,0,0.4)" strokeWidth="0.8"></circle><circle cx="100" cy="100" r="13" fill="#050507"></circle><ellipse cx="92" cy="92" rx="4.5" ry="3" fill="rgba(255,255,255,0.9)"></ellipse><circle cx="106" cy="106" r="1.5" fill="rgba(255,255,255,0.55)"></circle></g><path className="cv-eye-lid" d="M 20 100 Q 100 28 180 100 Q 100 172 20 100 Z" fill="#050507" opacity="0"></path></svg>
  );
};

export default EyeIcon;
