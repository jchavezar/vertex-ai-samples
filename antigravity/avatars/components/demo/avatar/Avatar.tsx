/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */
import { useEffect, useRef, useState } from 'react';
import { useLiveAPIContext } from '../../../contexts/LiveAPIContext';
import { useAgent } from '@/lib/state';

// Simple Config Modal Component
function ConfigModal({ onClose, initialInstruction, onSave }: { onClose: () => void, initialInstruction: string, onSave: (val: string) => void }) {
  const [val, setVal] = useState(initialInstruction);
  return (
    <div style={{
      position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.8)', zIndex: 100,
      display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <div style={{ background: '#1e1e1e', padding: '24px', borderRadius: '12px', width: '500px', maxWidth: '90%', color: '#fff' }}>
        <h3 style={{ margin: '0 0 12px 0' }}>Avatar Behavior</h3>
        <p style={{ fontSize: '14px', color: '#ccc', marginBottom: '16px' }}>
          Describe the avatar's mood, personality, and how it should talk (characterization).
        </p>
        <textarea 
          value={val}
          onChange={e => setVal(e.target.value)}
          style={{ 
            width: '100%', height: '200px', background: '#333', 
            color: '#fff', border: '1px solid #444', borderRadius: '4px',
            padding: '12px', marginBottom: '16px', fontSize: '16px', lineHeight: '1.5', resize: 'vertical'
          }}
          placeholder="e.g. You are a cheerful pirate who loves telling jokes..."
        />
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button 
            onClick={onClose}
            style={{ padding: '6px 12px', background: 'transparent', border: '1px solid #555', color: '#fff', borderRadius: '4px', cursor: 'pointer' }}
          >
            Cancel
          </button>
          <button 
             onClick={() => { onSave(val); onClose(); }}
             style={{ padding: '6px 12px', background: '#4a90e2', border: 'none', color: '#fff', borderRadius: '4px', cursor: 'pointer' }}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Avatar() {
  const { volume, connected, setConfig, config } = useLiveAPIContext();
  const { current: currentAgent } = useAgent();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [showConfig, setShowConfig] = useState(false);
  
  const currentInstruction = config?.systemInstruction?.parts?.[0]?.text || '';

  const handleSaveConfig = (newInstruction: string) => {
    setConfig({
      ...config,
      systemInstruction: {
        parts: [{ text: newInstruction }]
      }
    });
  };

  // Agent Visuals (with fallbacks)
  const visuals = currentAgent.visuals || {
    skinColor: ['#ffdfc4', '#e0b795', '#a67c52'],
    hairColor: '#1a1a1a',
    hairStyle: 'spiky',
    clothingColor: '#546e7a',
    clothingColor2: '#263238',
    eyeColor: '#59443b',
    headShape: 'angular'
  };

  const visualsRef = useRef(visuals);
  useEffect(() => {
    visualsRef.current = visuals; // Sync ref for animation loop
  }, [currentAgent]);

  // Animation State Refs
  const stateRef = useRef({
    time: 0,
    isBlinking: false,
    blinkProgress: 0,
    nextBlinkTime: 2000,
    eyeTargetX: 0,
    eyeTargetY: 0,
    eyeCurrentX: 0,
    eyeCurrentY: 0,
    nextEyeMoveTime: 1000,
    floatY: 0,
    currentMouthHeight: 0,
  });

  const volumeRef = useRef(0);
  const agentRef = useRef(currentAgent);
  useEffect(() => {
    agentRef.current = currentAgent;
  }, [currentAgent]);

  useEffect(() => {
    volumeRef.current = volume;
  }, [volume]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let lastTime = performance.now();

    const render = (now: number) => {
      if (!ctx || !canvas) return;
      const width = canvas.width;
      const height = canvas.height;
      
      const centerX = width / 2;
      const centerY = height / 2;
      const minDim = Math.min(width, height);
      const headScale = minDim * 0.28; 
      const r = headScale;

      // --- HELPERS ---
      const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
      
      const dimColor = (color: string, amount: number) => {
        if (!color.startsWith('#')) return color;
        const r = parseInt(color.slice(1,3), 16);
        const g = parseInt(color.slice(3,5), 16);
        const b = parseInt(color.slice(5,7), 16);
        return `rgba(${Math.floor(r*amount)}, ${Math.floor(g*amount)}, ${Math.floor(b*amount)}, 1)`;
      };

      const project = (x: number, y: number, z: number) => {
        const lookYaw = stateRef.current.eyeCurrentX * 0.25;
        const lookPitch = stateRef.current.eyeCurrentY * 0.2;
        const rx = x * Math.cos(lookYaw) - z * Math.sin(lookYaw);
        const rz = x * Math.sin(lookYaw) + z * Math.cos(lookYaw);
        const ry = y * Math.cos(lookPitch) - rz * Math.sin(lookPitch);
        const perspective = 800;
        const scale = perspective / (perspective + rz);
        return { 
          x: centerX + rx * scale, 
          y: centerY + stateRef.current.floatY + ry * scale,
          scale
        };
      };

      // --- ANIMATION UPDATE ---
      const dt = Math.min((now - lastTime), 100); 
      lastTime = now;
      stateRef.current.time += dt;
      const viz = visualsRef.current;

      // Blinking
      if (!stateRef.current.isBlinking) {
        if (performance.now() > stateRef.current.nextBlinkTime) {
          stateRef.current.isBlinking = true;
          stateRef.current.blinkProgress = 0;
        }
      } else {
        stateRef.current.blinkProgress += 0.15; // Speed
        if (stateRef.current.blinkProgress >= 2) {
          stateRef.current.isBlinking = false;
          stateRef.current.nextBlinkTime = performance.now() + Math.random() * 3000 + 1000;
        }
      }
      const lidFactor = stateRef.current.isBlinking 
        ? (stateRef.current.blinkProgress <= 1 ? stateRef.current.blinkProgress : 2 - stateRef.current.blinkProgress)
        : 0;

      // Mouse Look
      stateRef.current.eyeCurrentX = lerp(stateRef.current.eyeCurrentX, stateRef.current.eyeTargetX, 0.08);
      stateRef.current.eyeCurrentY = lerp(stateRef.current.eyeCurrentY, stateRef.current.eyeTargetY, 0.08);
      stateRef.current.floatY = Math.sin(performance.now() * 0.002) * (headScale * 0.05);

      const targetMouthHeight = Math.min(volumeRef.current * 3.5, 1.4); 
      stateRef.current.currentMouthHeight = lerp(stateRef.current.currentMouthHeight, targetMouthHeight, 0.3);

      // --- DRAWING ---
      if (agentRef.current.id === 'jew-jitsu') {
          // Special background for Jew Jitsu? Optional, but keeping it thematic
          ctx.clearRect(0, 0, width, height); 
      } else if (agentRef.current.id === 'fortnite-ace') {
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(0, 0, width, height);
      } else {
          ctx.clearRect(0, 0, width, height);
      }

      // 1. SHOULDERS (Behind)
      ctx.save();
      const neckW = headScale * 0.4;
      const neckTopY = centerY + headScale * 0.8 + stateRef.current.floatY;
      const shoulderY = centerY + headScale * 1.3 + stateRef.current.floatY * 0.5;
      
      if (viz.clothingStyle === 'suit') {
          // Suit Jacket
          ctx.fillStyle = viz.clothingColor;
          ctx.beginPath();
          ctx.moveTo(centerX - width * 0.45, height);
          ctx.quadraticCurveTo(centerX - width * 0.4, shoulderY + 20, centerX, shoulderY);
          ctx.quadraticCurveTo(centerX + width * 0.4, shoulderY + 20, centerX + width * 0.45, height);
          ctx.fill();

          // Shirt V
          ctx.fillStyle = '#ffffff';
          ctx.beginPath();
          ctx.moveTo(centerX - headScale * 0.3, shoulderY + 10);
          ctx.lineTo(centerX, shoulderY + headScale * 0.8);
          ctx.lineTo(centerX + headScale * 0.3, shoulderY + 10);
          ctx.closePath();
          ctx.fill();

          // Tie
          ctx.fillStyle = '#d32f2f'; // Red tie default
          ctx.beginPath();
          ctx.moveTo(centerX - headScale * 0.1, shoulderY + headScale * 0.2);
          ctx.lineTo(centerX + headScale * 0.1, shoulderY + headScale * 0.2);
          ctx.lineTo(centerX + headScale * 0.15, shoulderY + headScale * 0.5);
          ctx.lineTo(centerX, shoulderY + headScale * 1.0);
          ctx.lineTo(centerX - headScale * 0.15, shoulderY + headScale * 0.5);
          ctx.closePath();
          ctx.fill();

          // Suit Lapels
          ctx.strokeStyle = dimColor(viz.clothingColor, 0.8);
          ctx.lineWidth = 4;
          ctx.beginPath();
          ctx.moveTo(centerX - headScale * 0.32, shoulderY + 10);
          ctx.lineTo(centerX, shoulderY + headScale * 0.75);
          ctx.lineTo(centerX + headScale * 0.32, shoulderY + 10);
          ctx.stroke();

      } else if (viz.clothingStyle === 'gi') {
        // White Shirt (formerly Gi)
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(centerX - headScale * 1.5, shoulderY + headScale * 1.5);
        ctx.quadraticCurveTo(centerX - headScale, shoulderY + headScale * 0.4, centerX - neckW * 0.5, neckTopY);
        ctx.lineTo(centerX + neckW * 0.5, neckTopY);
        ctx.quadraticCurveTo(centerX + headScale, shoulderY + headScale * 0.4, centerX + headScale * 1.5, shoulderY + headScale * 1.5);
        ctx.fill();

        // Black Belt
        ctx.fillStyle = '#111111';
        ctx.fillRect(centerX - headScale * 0.6, shoulderY + headScale * 0.7, headScale * 1.2, headScale * 0.2);
        
        // Shirt Collar
        ctx.strokeStyle = '#dddddd';
        ctx.lineWidth = 4;
        ctx.beginPath();
        // Left collar
        ctx.moveTo(centerX - neckW * 0.5, neckTopY);
        ctx.lineTo(centerX - neckW * 1.2, neckTopY + headScale * 0.4);
        ctx.lineTo(centerX - neckW * 0.2, neckTopY + headScale * 0.3);
        // Right collar
        ctx.moveTo(centerX + neckW * 0.5, neckTopY);
        ctx.lineTo(centerX + neckW * 1.2, neckTopY + headScale * 0.4);
        ctx.lineTo(centerX + neckW * 0.2, neckTopY + headScale * 0.3);
        ctx.stroke();
      } else if (viz.clothingStyle === 'cardigan') {
        // Cardigan Style
        ctx.fillStyle = viz.clothingColor; // Cardigan color
        ctx.beginPath();
        // Shoulders
        ctx.moveTo(centerX - width * 0.45, height);
        ctx.quadraticCurveTo(centerX - width * 0.4, shoulderY + 20, centerX, shoulderY);
        ctx.quadraticCurveTo(centerX + width * 0.4, shoulderY + 20, centerX + width * 0.45, height);
        ctx.fill();

        // Shirt underneath (V-neck)
        ctx.fillStyle = viz.clothingColor2;
        ctx.beginPath();
        ctx.moveTo(centerX - headScale * 0.25, shoulderY + 10);
        ctx.lineTo(centerX, shoulderY + headScale * 0.7);
        ctx.lineTo(centerX + headScale * 0.25, shoulderY + 10);
        ctx.closePath();
        ctx.fill();

        // Buttons
        ctx.fillStyle = dimColor(viz.clothingColor, 0.6);
        for (let i = 0; i < 3; i++) {
          ctx.beginPath();
          ctx.arc(centerX, shoulderY + headScale * (0.8 + i * 0.25), 4, 0, Math.PI * 2);
          ctx.fill();
        }

        // Collar/Opening trim
        ctx.strokeStyle = dimColor(viz.clothingColor, 0.8);
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(centerX - headScale * 0.25, shoulderY + 10);
        ctx.lineTo(centerX, shoulderY + headScale * 0.8);
        ctx.lineTo(centerX + headScale * 0.25, shoulderY + 10);
        ctx.stroke();

    } else {
        // Casual Jacket/Shirt
          const jacketGrad = ctx.createLinearGradient(centerX, shoulderY, centerX, height);
          jacketGrad.addColorStop(0, viz.clothingColor);
          jacketGrad.addColorStop(1, dimColor(viz.clothingColor, 0.7));
          ctx.fillStyle = jacketGrad;
          ctx.beginPath();
          ctx.moveTo(centerX - width * 0.45, height);
          ctx.quadraticCurveTo(centerX - width * 0.4, shoulderY + 20, centerX, shoulderY);
          ctx.quadraticCurveTo(centerX + width * 0.4, shoulderY + 20, centerX + width * 0.45, height);
          ctx.fill();
      }
      ctx.restore();

      // 2. NECK (Behind Head)
      ctx.save();
      const neckBottomY = shoulderY + 10;
      ctx.beginPath();
      ctx.moveTo(centerX - neckW * 0.4, neckTopY);
      ctx.lineTo(centerX + neckW * 0.4, neckTopY);
      ctx.lineTo(centerX + neckW * 0.6, neckBottomY);
      ctx.lineTo(centerX - neckW * 0.6, neckBottomY);
      ctx.closePath();
      
      const neckGrad = ctx.createLinearGradient(0, neckTopY, 0, neckBottomY);
      const isWii = viz.style === 'wii';
      if (isWii) {
          ctx.fillStyle = viz.skinColor[1]; // Flat for Wii
      } else {
          neckGrad.addColorStop(0, dimColor(viz.skinColor[2], 0.65)); // Strong shadow
          neckGrad.addColorStop(0.4, viz.skinColor[1]);
          neckGrad.addColorStop(1, viz.skinColor[2]);
          ctx.fillStyle = neckGrad;
      }
      ctx.fill();
      ctx.restore();

      // 3. BACK HAIR
      if (viz.hairStyle === 'long') {
          ctx.save();
          ctx.translate(centerX, centerY + stateRef.current.floatY);
          ctx.fillStyle = viz.hairColor;
          ctx.beginPath();
          ctx.arc(0, 0, r * 1.35, Math.PI, 0); 
          ctx.lineTo(r * 1.5, height - centerY);
          ctx.lineTo(-r * 1.5, height - centerY);
          ctx.fill();
          // Texture
          if (!isWii) {
              ctx.strokeStyle = 'rgba(0,0,0,0.15)';
              ctx.lineWidth = 2;
              for(let i=0; i<15; i++) {
                  const tx = (Math.sin(i * 1.5) * r * 1.2);
                  const ty = (Math.cos(i * 0.8) * r * 1.2);
                  ctx.beginPath();
                  ctx.arc(tx, ty + r * 0.5, r * 0.2, 0, Math.PI * 2);
                  ctx.stroke();
              }
          }
          ctx.restore();
      }

      // 4. HEAD GROUP
      
      // --- REPORTER STYLE (Anchor Annie) ---
      if (viz.style === 'reporter') {
          ctx.save();
          const headY = centerY + stateRef.current.floatY;
          ctx.translate(centerX, headY);
          
          // Helper for natural skin shading
          const createSkinGradient = (x: number, y: number, r: number) => {
              const grad = ctx.createRadialGradient(x-r*0.2, y-r*0.2, 0, x, y, r);
              grad.addColorStop(0, viz.skinColor[0]);
              grad.addColorStop(1, viz.skinColor[1]);
              return grad;
          };
          
          // --- BACKGROUND: NYC SKYLINE ---
          // Draw this BEHIND the head (before the rest of the avatar)
          // Since we already translated to (centerX, headY), we need to untranslate or just draw strictly relative
          // But backgrounds should be static relative to screen, not floating head.
          // Let's restore, draw BG, then save/translate again for head.
          ctx.restore(); 
          ctx.save();
          
          // Background Gradient (Night City)
          const bgGrad = ctx.createLinearGradient(0, 0, 0, canvas.height);
          bgGrad.addColorStop(0, '#0d1b2a'); // Dark Blue Night
          bgGrad.addColorStop(1, '#1b263b');
          ctx.globalCompositeOperation = 'destination-over'; // Draw behind existing content if any (though we are early in stack)
          // Actually, we are in the render loop. "ctx" is cleared every frame.
          // Avatars are drawn on top of transparent BG usually. 
          // We can just draw full screen rect here behind everything.
          
          // Draw Skyline
          const drawSkyline = () => {
              const baseH = canvas.height;
              const width = canvas.width;
              
              // Helper to draw a single building
              const drawBuilding = (x: number, w: number, h: number, style: 'flat' | 'spire' | 'slanted', windows: boolean[][]) => {
                  ctx.fillRect(x - w/2, baseH - h, w, h);
                  
                  // Windows (Grid pattern)
                  ctx.fillStyle = 'rgba(255, 255, 200, 0.15)'; // Warmer light
                  const cols = Math.floor(w / 15);
                  const rows = Math.floor(h / 20);
                  const padX = (w - (cols * 8)) / 2;
                  
                  for(let r=0; r<rows; r++) {
                      if (r >= windows.length) break;
                      for(let c=0; c<cols; c++) {
                          if (c >= windows[r].length) break;
                          if (windows[r][c]) { // Use pre-calculated window state
                              ctx.fillRect(x - w/2 + padX + c*10, baseH - h + 10 + r*15, 6, 8);
                          }
                      }
                  }
                  
                  // Roof detail
                  ctx.fillStyle = '#08101a'; // Match silhouette for add-ons
                  if (style === 'spire') {
                      ctx.beginPath();
                      ctx.moveTo(x - w*0.1, baseH - h);
                      ctx.lineTo(x, baseH - h - w*0.6); // Spire top
                      ctx.lineTo(x + w*0.1, baseH - h);
                      ctx.fill();
                      // Antenna line
                      ctx.beginPath();
                      ctx.moveTo(x, baseH - h - w*0.6);
                      ctx.lineTo(x, baseH - h - w*1.5);
                      ctx.strokeStyle = 'rgba(255,255,255,0.3)';
                      ctx.lineWidth = 2;
                      ctx.stroke();
                  } else if (style === 'slanted') {
                      ctx.beginPath();
                      ctx.moveTo(x - w/2, baseH - h);
                      ctx.lineTo(x + w/2, baseH - h - 20);
                      ctx.lineTo(x + w/2, baseH - h);
                      ctx.fill();
                  }
              };

              // Layer 1: Far background (silhouette only)
              ctx.fillStyle = '#050a10';
              // We need static backgrounds too. 
              // For simplicity, let's just use fixed deterministic "random" based on index or just simple static blocks for layer 1 
              // to avoid complex memoization for background noise.
              // actually, let's just make layer 1 static blocks.
              [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200].forEach((x, i) => {
                  const h = 100 + (i * 1213 % 150);
                  const w = 60 + (i * 7919 % 60);
                  ctx.fillRect(x, baseH - h, w, h);
              });

              // Layer 2: Main Skyline (Use MEMOIZED stateRef data if we had it, or just deterministic)
              // Better: We should generate this ONCE. 
              // Since we can't easily add a new hook inside this conditional block comfortably without breaking rules of hooks if style changes...
              // We will use a deterministic seed or just stored values. 
              // Actually, we can just use a seeded random or simple hash for stability.
              
              const seed = 12345;
              const random = (i: number) => {
                  const x = Math.sin(seed + i) * 10000;
                  return x - Math.floor(x);
              };

              const numBuildings = 8;
              const spacing = width / numBuildings;
              
              for(let i=0; i<numBuildings + 1; i++) {
                   const r1 = random(i * 10);
                   const r2 = random(i * 10 + 1);
                   const r3 = random(i * 10 + 2);
                   const r4 = random(i * 10 + 3);

                   const x = i * spacing + (r1 - 0.5) * 40;
                   const w = 60 + r2 * 60;
                   
                   const distFromCenter = Math.abs(x - width/2) / (width/2);
                   const baseHeight = 200 + (1 - distFromCenter) * 150; 
                   const h = baseHeight + r3 * 100;
                   
                   // Fixed logic: Check highest threshold first, or use exclusive ranges
                   // r4 is 0..1
                   // > 0.7 -> spire (30%)
                   // > 0.4 -> slanted (30%)
                   // else -> flat (40%)
                   const type = r4 > 0.7 ? 'spire' : r4 > 0.4 ? 'slanted' : 'flat';
                   
                   // Force varied heights on left side too, maybe reduce center-bias slightly or add random variability height
                   // The previous baseHeight calculation made side buildings much shorter. Let's boost them a bit.
                   const boostedH = h * (1 + (r1 * 0.3)); // Add up to 30% more random height

                   // Generate deterministic windows
                   const windowRows = Math.floor(boostedH / 20);
                   const windowCols = Math.floor(w / 15);
                   const windows: boolean[][] = [];
                   for(let wr=0; wr<windowRows; wr++) {
                       const rowArr = [];
                       for(let wc=0; wc<windowCols; wc++) {
                            // Deterministic window light
                            const wrand = random(i * 1000 + wr * 100 + wc);
                            const rowDark = random(i * 1000 + wr * 100) > 0.6; // varies per row
                            const lit = !rowDark && wrand > 0.2;
                            rowArr.push(lit);
                       }
                       windows.push(rowArr);
                   }

                   ctx.fillStyle = '#0d1b2a'; 
                   drawBuilding(x, w, boostedH, type, windows);
              }
          };
          drawSkyline();
          
          ctx.globalCompositeOperation = 'source-over'; // <--- IMPORTANT: Reset to default!

          // Restore to HEAD context
          ctx.translate(centerX, headY);
          
          // 1. HAIR BACK (Bob style)
          if (viz.hairStyle === 'news_bob') {
              ctx.fillStyle = viz.hairColor;
              ctx.beginPath();
              // Voluminous Bob backing
              ctx.ellipse(0, 0, r * 1.3, r * 1.3, 0, Math.PI, 2 * Math.PI); // Top arch
              ctx.quadraticCurveTo(r * 1.4, r * 1.2, r * 1.0, r * 1.5); // Right side flow
              ctx.lineTo(-r * 1.0, r * 1.5); // Bottom
              ctx.quadraticCurveTo(-r * 1.4, r * 1.2, -r * 1.3, 0); // Left side
              ctx.fill();
          }

          // 2. NECK & DRESS (High neck / V-neck professional)
          ctx.fillStyle = viz.skinColor[2]; // Shadow neck
          ctx.fillRect(-r*0.3, r*0.8, r*0.6, r*0.6);
          
          // Dress Body
          if (viz.clothingStyle === 'dress') {
              ctx.fillStyle = viz.clothingColor;
              ctx.beginPath();
              // Shoulders
              ctx.moveTo(-r * 1.2, r * 1.4);
              ctx.quadraticCurveTo(-r * 0.5, r * 1.2, 0, r * 1.4); // Neckline left
              ctx.quadraticCurveTo(r * 0.5, r * 1.2, r * 1.2, r * 1.4); // Neckline right
              ctx.lineTo(r * 1.5, r * 3); // Down right
              ctx.lineTo(-r * 1.5, r * 3); // Down left
              ctx.fill();
              
              // Detail line / V-neck
              ctx.strokeStyle = viz.clothingColor2;
              ctx.lineWidth = 3;
              ctx.beginPath();
              ctx.moveTo(-r*0.5, r*1.25);
              ctx.lineTo(0, r*1.8);
              ctx.lineTo(r*0.5, r*1.25);
              ctx.stroke();
          }

          // 3. FACE SHAPE (Soft/Oval)
          ctx.fillStyle = createSkinGradient(0, 0, r);
          ctx.beginPath();
          // More realistic jawline than 'soft' memoji
          ctx.moveTo(-r*0.9, -r*0.2);
          ctx.quadraticCurveTo(-r*0.95, r*0.6, 0, r*1.05); // Left jaw to chin
          ctx.quadraticCurveTo(r*0.95, r*0.6, r*0.9, -r*0.2); // Right jaw
          ctx.quadraticCurveTo(r*0.9, -r*0.9, 0, -r*0.9); // Top
          ctx.quadraticCurveTo(-r*0.9, -r*0.9, -r*0.9, -r*0.2); // Close
          ctx.fill();

          // 4. FACE FEATURES
          
          // Eyes (Almond shape, styled)
          const drawReporterEye = (side: -1 | 1) => {
              const ex = side * r * 0.35;
              const ey = -r * 0.1;
              const ew = r * 0.25;
              const eh = r * 0.18;
              
              // Sclera
              ctx.fillStyle = '#fff';
              ctx.beginPath();
              ctx.ellipse(ex, ey, ew, eh, 0, 0, Math.PI*2);
              ctx.fill();
              
              // Iris/Pupil
              const lx = ex + stateRef.current.eyeCurrentX * ew * 0.4;
              const ly = ey + stateRef.current.eyeCurrentY * eh * 0.4;
              
              ctx.fillStyle = viz.eyeColor;
              ctx.beginPath();
              ctx.arc(lx, ly, eh * 0.6, 0, Math.PI*2);
              ctx.fill();
              ctx.fillStyle = '#000';
              ctx.beginPath();
              ctx.arc(lx, ly, eh * 0.3, 0, Math.PI*2); // Pupil
              ctx.fill();
              
              // Eyeliner / Lashes
              ctx.strokeStyle = '#1a1a1a';
              ctx.lineWidth = 2.5;
              ctx.beginPath();
              ctx.moveTo(ex - ew * 0.9, ey);
              ctx.quadraticCurveTo(ex, ey - eh * 1.3, ex + ew * 1.1, ey - eh * 0.2); // Winged liner
              ctx.stroke();
              
               // Blink
              if (lidFactor > 0) {
                  ctx.fillStyle = viz.skinColor[1];
                  ctx.beginPath();
                  ctx.rect(ex - ew, ey - eh, ew*2, eh * 2 * lidFactor);
                  ctx.fill();
              }
          };
          drawReporterEye(-1);
          drawReporterEye(1);

          // Nose (Natural)
          ctx.fillStyle = 'rgba(0,0,0,0.1)';
          ctx.beginPath();
          ctx.arc(0, r*0.25, r*0.06, 0, Math.PI*2); // Subtle tip shadow
          ctx.fill();

          // Mouth (Lipstick)
          const mouthY = r * 0.5;
          const mouthW = r * 0.4;
          const volume = stateRef.current.currentMouthHeight; // 0 to ~1
          const mouthOpen = Math.min(volume * r * 0.3, r * 0.4);
          
          ctx.fillStyle = '#d81b60'; // Lipstick color
          ctx.beginPath();
          // Upper lip
          ctx.moveTo(-mouthW * 0.8, mouthY);
          ctx.quadraticCurveTo(0, mouthY - r*0.1, mouthW * 0.8, mouthY); 
          // Lower lip / Opening
          ctx.quadraticCurveTo(0, mouthY + mouthOpen + r*0.15, -mouthW * 0.8, mouthY);
          ctx.fill();
          
          // Inner mouth (if open)
          if (mouthOpen > 2) {
              ctx.fillStyle = '#4a0000';
              ctx.beginPath();
              ctx.ellipse(0, mouthY + mouthOpen*0.4, mouthW * 0.5, mouthOpen * 0.4, 0, 0, Math.PI*2);
              ctx.fill();
          }

          // 5. HAIR FRONT (Bangs / Side sweep)
          if (viz.hairStyle === 'news_bob') {
              ctx.fillStyle = viz.hairColor;
              ctx.beginPath();
              // Side part sweep
              ctx.moveTo(0, -r * 0.9);
              ctx.quadraticCurveTo(r * 0.8, -r * 0.8, r * 1.05, r * 0.2); // Right side
              ctx.quadraticCurveTo(r * 0.5, -r * 0.2, 0, -r * 0.9); // Sweep back
              ctx.fill();
              
              // Left side tuck
              ctx.beginPath();
              ctx.moveTo(0, -r * 0.9);
              ctx.quadraticCurveTo(-r * 0.9, -r * 0.5, -r * 1.05, 0); 
              ctx.lineTo(-r * 1.1, -r * 0.8);
              ctx.fill();
          }

          ctx.restore();
      } else if (viz.style === 'giraffe') {
          // ... (Giraffe block)
          const projectHeadPoint = (lx: number, ly: number, lz: number) => {
              const yaw = stateRef.current.eyeCurrentX * 0.5; // Stronger turn for giraffe
              const pitch = stateRef.current.eyeCurrentY * 0.3;
              
              // Rotate around Y (Yaw)
              let x1 = lx * Math.cos(yaw) - lz * Math.sin(yaw);
              let z1 = lx * Math.sin(yaw) + lz * Math.cos(yaw);
              
              // Rotate around X (Pitch)
              let y1 = ly * Math.cos(pitch) - z1 * Math.sin(pitch);
              let z2 = ly * Math.sin(pitch) + z1 * Math.cos(pitch);
              
              const perspective = 1000;
              const scale = perspective / (perspective + z2);
              
              return {
                  x: centerX + x1 * scale,
                  y: centerY + stateRef.current.floatY + y1 * scale,
                  scale: scale,
                  zIndex: z2
              };
          };

          // 1. BACK OSSICONES & EARS (if looking up/away)
          // Simplified: Draw interactively sorted by Z? 
          // For now, simpler painter's algorithm: Back Ears/Horns -> Head -> Front Ears/Horns? 
          // Actually, giraffe ears/horns are usually on top/side. Let's draw standard for now.

          // HEAD BASE (The skull)
          // Distorted sphere/egg
          const headCenter = projectHeadPoint(0, 0, 0);
          const headScaleX = r * 0.9; 
          const headScaleY = r * 1.1;
          
          ctx.beginPath();
          ctx.ellipse(headCenter.x, headCenter.y, headScaleX * headCenter.scale, headScaleY * headCenter.scale, 0, 0, Math.PI*2);
          
          // Skin Gradient
          const grad = ctx.createRadialGradient(
              headCenter.x - r*0.3, headCenter.y - r*0.3, 0,
              headCenter.x, headCenter.y, r*1.5
          );
          grad.addColorStop(0, viz.skinColor[0]);
          grad.addColorStop(1, viz.skinColor[2]);
          ctx.fillStyle = grad;
          ctx.fill();

          // SPOTS (Projected onto head sphere roughly)
          const spots = [
              {x: -0.6, y: -0.5, s: 0.2}, {x: 0.6, y: -0.4, s: 0.18}, 
              {x: 0, y: -0.8, s: 0.15}, {x: -0.5, y: 0.5, s: 0.12},
              {x: 0.7, y: 0.3, s: 0.14}
          ];
          ctx.fillStyle = 'rgba(139, 69, 19, 0.65)';
          spots.forEach(spot => {
              const p = projectHeadPoint(spot.x * r, spot.y * r, r * 0.9); // Surface
              if (p.zIndex < 0) return; // Cull back spots roughly
              ctx.beginPath();
              ctx.ellipse(p.x, p.y, r * spot.s * p.scale, r * spot.s * 0.8 * p.scale, 0, 0, Math.PI*2);
              ctx.fill();
          });

          // OSSICONES (Horns)
          const draw3DOssicone = (side: -1 | 1) => {
              const root = projectHeadPoint(side * r * 0.5, -r * 0.8, 0);
              const tip = projectHeadPoint(side * r * 0.6, -r * 1.5, 0); // Tilted out
              
              ctx.lineWidth = r * 0.15 * root.scale;
              ctx.lineCap = 'round';
              ctx.strokeStyle = viz.skinColor[1];
              ctx.beginPath();
              ctx.moveTo(root.x, root.y);
              ctx.lineTo(tip.x, tip.y);
              ctx.stroke();
              
              // Tuft
              ctx.fillStyle = '#5c4033'; // Dark brown tuft
              ctx.beginPath();
              ctx.arc(tip.x, tip.y, r * 0.12 * tip.scale, 0, Math.PI*2);
              ctx.fill();
          };
          draw3DOssicone(-1);
          draw3DOssicone(1);

          // EARS
          const draw3DEar = (side: -1 | 1) => {
              const root = projectHeadPoint(side * r * 0.9, -r * 0.2, -r * 0.2);
              const tip = projectHeadPoint(side * r * 1.8, -r * 0.1, -r * 0.4);
              
              ctx.fillStyle = viz.skinColor[0];
              ctx.beginPath();
              ctx.moveTo(root.x, root.y - r*0.1);
              ctx.quadraticCurveTo(
                  projectHeadPoint(side * r * 1.4, -r * 0.6, -r*0.3).x, 
                  projectHeadPoint(side * r * 1.4, -r * 0.6, -r*0.3).y, 
                  tip.x, tip.y
              );
              ctx.quadraticCurveTo(
                  projectHeadPoint(side * r * 1.4, r * 0.2, -r*0.3).x, 
                  projectHeadPoint(side * r * 1.4, r * 0.2, -r*0.3).y, 
                  root.x, root.y + r*0.1
              );
              ctx.fill();
          };
          draw3DEar(-1);
          draw3DEar(1);

          // EYES (Large, side-facing but forward looking)
          const draw3DEye = (side: -1 | 1) => {
              const eyePos = projectHeadPoint(side * r * 0.45, -r * 0.1, r * 0.6);
              const eyeSize = r * 0.22 * eyePos.scale;
              
              // Sclera
              ctx.fillStyle = '#fff';
              ctx.beginPath();
              ctx.ellipse(eyePos.x, eyePos.y, eyeSize, eyeSize * 0.8, 0, 0, Math.PI*2);
              ctx.fill();

              // Pupil/Iris (Tracking)
              const lx = eyePos.x + stateRef.current.eyeCurrentX * eyeSize * 0.4;
              const ly = eyePos.y + stateRef.current.eyeCurrentY * eyeSize * 0.4;
              
              ctx.fillStyle = '#3e2723';
              ctx.beginPath();
              ctx.arc(lx, ly, eyeSize * 0.6, 0, Math.PI*2);
              ctx.fill();
              
              // Shine
              ctx.fillStyle = '#fff';
              ctx.beginPath();
              ctx.arc(lx - eyeSize*0.2, ly - eyeSize*0.2, eyeSize * 0.2, 0, Math.PI*2);
              ctx.fill();
              
              // Eyelid (Blinking)
              if (lidFactor > 0) {
                  ctx.fillStyle = viz.skinColor[1];
                  ctx.beginPath();
                  ctx.rect(eyePos.x - eyeSize, eyePos.y - eyeSize, eyeSize*2, eyeSize * 2 * lidFactor);
                  ctx.fill();
              }
              
              // Lashes
              ctx.strokeStyle = '#222';
              ctx.lineWidth = 2;
              ctx.beginPath();
              ctx.moveTo(eyePos.x - eyeSize, eyePos.y - eyeSize*0.5);
              ctx.quadraticCurveTo(eyePos.x, eyePos.y - eyeSize * 1.2, eyePos.x + eyeSize, eyePos.y - eyeSize*0.5);
              ctx.stroke();
          };
          draw3DEye(-1);
          draw3DEye(1);

          // MUZZLE / SNOUT (The 3D projected part)
          // Project forward based on r
          const snoutZ = r * 0.9;
          const snoutBase = projectHeadPoint(0, r * 0.3, r * 0.4); // Overlaps face slightly
          const snoutTip = projectHeadPoint(0, r * 0.4, snoutZ); // Sticking out
          
          const snoutScale = snoutTip.scale;
          const snoutW = r * 0.55 * snoutScale;
          const snoutH = r * 0.45 * snoutScale;


          // Draw snout connection (bridge)
          // Ideally blending, but simpler overlap works for current style






          // Snout Main Shape
          ctx.fillStyle = '#ffecd2'; // Lighter muzzle color
          ctx.beginPath();
          ctx.ellipse(snoutTip.x, snoutTip.y, snoutW, snoutH, 0, 0, Math.PI*2);
          ctx.fill();
          
          // Nostrils
          const noseY = snoutTip.y - snoutH * 0.2;
          ctx.fillStyle = '#4e342e';
          const drawNostril = (side: -1 | 1) => {
              const nx = snoutTip.x + side * snoutW * 0.4;
              // Expand with breathing?
              const breath = Math.sin(performance.now() * 0.003) * 0.1 + 1;
              ctx.beginPath();
              ctx.ellipse(nx, noseY, snoutW * 0.12 * breath, snoutW * 0.08 * breath, side * 0.2, 0, Math.PI*2);
              ctx.fill();
          };
          drawNostril(-1);
          drawNostril(1);

          // MOUTH (On the snout)
          const mouthY = snoutTip.y + snoutH * 0.3;
          const mouthW = snoutW * 0.6;
          const mouthOpen = stateRef.current.currentMouthHeight * snoutH * 0.4; // Talking magnitude
          
          ctx.fillStyle = '#3e2723';
          ctx.beginPath();
          if (mouthOpen < 2) {
              // Closed smile
              ctx.lineWidth = 3;
              ctx.strokeStyle = '#3e2723';
              ctx.moveTo(snoutTip.x - mouthW * 0.8, mouthY);
              ctx.quadraticCurveTo(snoutTip.x, mouthY + snoutH*0.2, snoutTip.x + mouthW * 0.8, mouthY);
              ctx.stroke();
          } else {
              // Open mouth (Chewing/Talking)
              ctx.ellipse(snoutTip.x, mouthY + mouthOpen*0.3, mouthW * 0.8, mouthOpen * 0.6, 0, 0, Math.PI*2);
              ctx.fill();
              // Teeth/Tongue?
              ctx.fillStyle = '#d32f2f'; // Tongue
              ctx.beginPath();
              ctx.ellipse(snoutTip.x, mouthY + mouthOpen*0.6, mouthW * 0.4, mouthOpen * 0.3, 0, 0, Math.PI*2);
              ctx.fill();
          }

          ctx.restore();

      } else {

      // 4. HEAD (Memoji or Wii Style)
      // ... (Existing implementation) ...
      ctx.save();
      ctx.translate(centerX, centerY + stateRef.current.floatY);
      
      // Ears (All Styles)

      const drawEar = (side: -1 | 1) => {
          ctx.save();
          if (viz.headShape === 'square') {
              // Blocky Ears
              ctx.translate(side * r * 1.05, 0);
              ctx.fillStyle = viz.skinColor[1];
              ctx.fillRect(-r * 0.1, -r * 0.15, r * 0.2, r * 0.3);
          } else {
              ctx.translate(side * r * 0.95, 0);
              ctx.fillStyle = viz.skinColor[1];
              ctx.beginPath();
              ctx.ellipse(0, 0, r * 0.15, r * 0.25, side * 0.1, 0, Math.PI * 2);
              ctx.fill();
              // Inner ear shadow
              ctx.fillStyle = 'rgba(0,0,0,0.1)';
              ctx.beginPath();
              ctx.ellipse(0, 0, r * 0.08, r * 0.15, side * 0.1, 0, Math.PI * 2);
              ctx.fill();
          }
          ctx.restore();
      };
      drawEar(-1);
      drawEar(1);

      // Face Shape
      if (viz.headShape === 'square') {
          // Blocky Minecraft Style - Perfectly centered
          const sqSize = r * 0.95;
          ctx.beginPath();
          ctx.roundRect(-sqSize, -sqSize, sqSize * 2, sqSize * 2, r * 0.05);
      } else {
          ctx.beginPath();
          ctx.arc(0, -r * 0.1, r, Math.PI, 0); // Top
          let chinW = 0.5;
          let chinDrop = 1.35;
          if (viz.headShape === 'angular') { chinW = 0.35; chinDrop = 1.35; }
          else if (viz.headShape === 'round') { chinW = 0.7; chinDrop = 1.25; }
          else if (viz.headShape === 'soft') { chinW = 0.55; chinDrop = 1.35; }
          else if (viz.headShape === 'fortnite') { chinW = 0.32; chinDrop = 1.45; } // Defined V-shape
          
          ctx.bezierCurveTo(r, r * 0.6, r * chinW, r * 1.2, 0, r * chinDrop); // Right
          ctx.bezierCurveTo(-r * chinW, r * 1.2, -r, r * 0.6, -r, -r * 0.1); // Left
          ctx.closePath();
      }
      
      if (isWii) {
          ctx.fillStyle = viz.skinColor[1];
          ctx.fill();
          ctx.strokeStyle = 'rgba(0,0,0,0.1)';
          ctx.lineWidth = 2;
          ctx.stroke();
      } else {
          // Skin Glossy Gradient
          const faceGrad = ctx.createRadialGradient(-r*0.2, -r*0.3, r*0.2, 0, 0, r*1.5);
          faceGrad.addColorStop(0, viz.skinColor[0]);
          faceGrad.addColorStop(0.4, viz.skinColor[1]);
          faceGrad.addColorStop(1, dimColor(viz.skinColor[2], 0.9));
          ctx.fillStyle = faceGrad;
          ctx.fill();

          // Ambient Occlusion / Soft Shadow on edges
          ctx.strokeStyle = 'rgba(0,0,0,0.05)';
          ctx.lineWidth = 2;
          ctx.stroke();

          // Highlights (Memoji Glow)
          const glow = ctx.createRadialGradient(0, -r*0.5, 0, 0, -r*0.5, r*0.7);
          glow.addColorStop(0, 'rgba(255,255,255,0.15)');
          glow.addColorStop(1, 'rgba(255,255,255,0)');
          ctx.fillStyle = glow;
          ctx.fill();
      }

      // Blush (only for Memoji/Fortnite style)
      if (!isWii) {
          const blushGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, r * 0.2);
          blushGrad.addColorStop(0, 'rgba(255, 100, 100, 0.12)');
          blushGrad.addColorStop(1, 'rgba(255, 100, 100, 0)');
          ctx.save();
          ctx.translate(-r * 0.45, r * 0.2);
          ctx.fillStyle = blushGrad; ctx.fillRect(-r*0.2, -r*0.2, r*0.4, r*0.4);
          ctx.restore();
          ctx.save();
          ctx.translate(r * 0.45, r * 0.2);
          ctx.fillStyle = blushGrad; ctx.fillRect(-r*0.2, -r*0.2, r*0.4, r*0.4);
          ctx.restore();
      }

      // 5. EYES
      const drawEye = (side: -1 | 1) => {
          const ep = project(side * r * 0.38, 0, r * 0.5);
          const er = r * 0.18 * ep.scale;
          
          ctx.save();
          ctx.translate(ep.x - centerX, ep.y - (centerY + stateRef.current.floatY));
          
          if (viz.headShape === 'square') {
              // Minecraft Style Square Eyes
              const eyeW = er * 1.2;
              const eyeH = er * 1.0;
              ctx.fillStyle = '#fff'; // Sclera
              ctx.fillRect(-eyeW * 0.5, -eyeH * 0.5, eyeW, eyeH);
              
              const lx = stateRef.current.eyeCurrentX * er * 0.2;
              const ly = stateRef.current.eyeCurrentY * er * 0.2;
              const pupilSize = er * 0.5;
              ctx.fillStyle = viz.eyeColor; // Iris/Pupil combined for blocky look
              ctx.fillRect(lx - pupilSize * 0.5, ly - pupilSize * 0.5, pupilSize, pupilSize);
          } else if (isWii) {
              // Wii style simple eyes (Pill shapes)
              ctx.rotate(side * -0.1);
              ctx.fillStyle = '#111';
              ctx.beginPath();
              ctx.ellipse(0, 0, er * 0.6, er * 0.9, 0, 0, Math.PI * 2);
              ctx.fill();
              // Small highlight
              ctx.fillStyle = '#fff';
              ctx.beginPath();
              ctx.arc(-er * 0.2, -er * 0.3, er * 0.15, 0, Math.PI * 2);
              ctx.fill();
          } else {
              // Memoji High Contrast
              ctx.beginPath();
              ctx.moveTo(-er * 1.25, 0); 
              ctx.quadraticCurveTo(0, -er * 0.9, er * 1.25, 0);
              ctx.quadraticCurveTo(0, er * 0.9, -er * 1.25, 0);
              ctx.clip();
              ctx.fillStyle = '#fff';
              ctx.fill();
              
              const ishad = ctx.createLinearGradient(0, -er, 0, er);
              ishad.addColorStop(0, 'rgba(0,0,0,0.12)');
              ishad.addColorStop(0.3, 'rgba(0,0,0,0)');
              ctx.fillStyle = ishad;
              ctx.fillRect(-er*2, -er, er*4, er*2);

              const lx = stateRef.current.eyeCurrentX * er * 0.4;
              const ly = stateRef.current.eyeCurrentY * er * 0.4;
              const ir = er * 0.7;
              ctx.beginPath();
              ctx.arc(lx, ly, ir, 0, Math.PI * 2);
              const iG = ctx.createRadialGradient(lx, ly, 0, lx, ly, ir);
              iG.addColorStop(0, viz.eyeColor);
              iG.addColorStop(0.8, viz.eyeColor);
              iG.addColorStop(1, '#000');
              ctx.fillStyle = iG;
              ctx.fill();

              ctx.fillStyle = '#111';
              ctx.beginPath();
              ctx.arc(lx, ly, ir * 0.45, 0, Math.PI * 2);
              ctx.fill();

              ctx.fillStyle = '#fff';
              ctx.beginPath();
              ctx.ellipse(lx - ir*0.35, ly - ir*0.35, ir*0.25, ir*0.15, Math.PI/4, 0, Math.PI*2);
              ctx.fill();
          }
          ctx.restore();

          // Lash Crease (Not for Wii or Square)
          if (!isWii && viz.headShape !== 'square') {
              ctx.strokeStyle = '#222';
              ctx.lineWidth = er * 0.12;
              ctx.lineCap = 'round';
              ctx.beginPath();
              ctx.moveTo(ep.x - centerX - er * 1.3, ep.y - (centerY + stateRef.current.floatY));
              ctx.quadraticCurveTo(ep.x - centerX, ep.y - (centerY + stateRef.current.floatY) - er * 1.0, ep.x - centerX + er * 1.3, ep.y - (centerY + stateRef.current.floatY));
              ctx.stroke();

              if (viz.hairStyle === 'long') {
                  ctx.beginPath();
                  const lx = ep.x - centerX;
                  const ly = ep.y - (centerY + stateRef.current.floatY);
                  ctx.moveTo(lx + side * er * 1.25, ly); 
                  ctx.quadraticCurveTo(lx + side * er * 1.6, ly - er * 0.5, lx + side * er * 1.8, ly - er * 0.8);
                  ctx.stroke();
              }

              if (lidFactor > 0) {
                  ctx.fillStyle = viz.skinColor[1];
                  ctx.fillRect(ep.x - centerX - er*1.5, ep.y - (centerY + stateRef.current.floatY) - er*1.5, er*3, er*3 * lidFactor);
              }
          }
      };
      drawEye(-1);
      drawEye(1);

      // 6. NOSE & MOUTH
      // Nose
      if (isWii) {
          // Wii simple nose
          ctx.strokeStyle = 'rgba(0,0,0,0.15)';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.arc(0, r * 0.35, r * 0.08, Math.PI * 1.2, Math.PI * 1.8);
          ctx.stroke();
      } else {
          ctx.fillStyle = 'rgba(120, 50, 40, 0.12)';
          ctx.beginPath();
          ctx.ellipse(0, r * 0.2, r * 0.1, r * 0.05, 0, 0, Math.PI * 2);
          ctx.fill();
      }

      // Mouth
      const mw = r * 0.28;
      const mh = Math.max(3, stateRef.current.currentMouthHeight * r * 0.15);
      ctx.save();
      ctx.translate(0, r * 0.6);
      if (stateRef.current.currentMouthHeight < 0.1) {
          ctx.strokeStyle = (isWii || viz.headShape === 'square') ? '#222' : '#a1887f';
          ctx.lineWidth = (isWii || viz.headShape === 'square') ? 4 : 3;
          ctx.lineCap = 'round';
          ctx.beginPath();
          ctx.moveTo(-mw * 0.6, 0);
          ctx.quadraticCurveTo(0, (isWii || viz.headShape === 'square') ? 8 : r*0.05, mw * 0.6, 0);
          ctx.stroke();
      } else {
          ctx.fillStyle = '#3e2723';
          ctx.beginPath();
          if (viz.headShape === 'square') {
              // Rectangular mouth for Minecraft
              ctx.rect(-mw * 0.5, -mh * 0.5, mw, mh);
          } else if (isWii) {
              ctx.ellipse(0, mh * 0.4, mw * 0.6, mh * 1.2, 0, 0, Math.PI * 2);
          } else {
              ctx.roundRect(-mw * 0.5, -mh * 0.5, mw, mh, 20);
          }
          ctx.fill();
          if (!isWii) {
              ctx.fillStyle = '#fff';
              ctx.beginPath();
              ctx.roundRect(-mw * 0.4, -mh * 0.5, mw * 0.8, mh * 0.3, 2);
              ctx.fill();
          }
      }
      ctx.restore();

      // 7. HAIR (Front)

        // --- GLASSES (If enabled) ---
        if (viz.glasses === 'round') {
          ctx.save();
          // Scale glasses based on 'r' (head radius) which is defined in this block
          // r is available here
          const gScale = r * 0.012; // Adjust scale for this coordinate system (usually 'r' is head radius ~100)
          // actually 'r' is huge here usually? no, 'r = headScale'

          const glSize = r * 0.6; // total width?
          const glY = -r * 0.1;

          ctx.strokeStyle = '#333';
          ctx.lineWidth = r * 0.08;

          const lx = -r * 0.35;
          const rx = r * 0.35;
          const rad = r * 0.28;

          // Lenses
          ctx.beginPath();
          ctx.arc(lx, glY, rad, 0, Math.PI * 2);
          ctx.stroke();
          ctx.beginPath();
          ctx.arc(rx, glY, rad, 0, Math.PI * 2);
          ctx.stroke();

          // Bridge
          ctx.beginPath();
          ctx.moveTo(lx + rad, glY);
          ctx.quadraticCurveTo(0, glY - rad * 0.5, rx - rad, glY);
          ctx.stroke();

          // Reflections
          ctx.fillStyle = 'rgba(255,255,255,0.2)';
          ctx.beginPath();
          ctx.arc(lx, glY, rad * 0.9, 0, Math.PI * 2);
          ctx.fill();
          ctx.beginPath();
          ctx.arc(rx, glY, rad * 0.9, 0, Math.PI * 2);
          ctx.fill();

          ctx.restore();
        }

      // 7. HAIR (Front)
      if (viz.headShape === 'square') {
          // Minecraft Style Blocky hair - Refined for "Normal" proportions
          const sqSize = r * 1.1;
          const pixelSize = sqSize * 0.25; 
          ctx.fillStyle = viz.hairColor;
          
          // Thicker cap - Now relative to centered head (top is -r*0.95)
          const headTop = -r * 0.95;
          ctx.fillRect(-sqSize, headTop - pixelSize * 2, sqSize * 2, pixelSize * 2);
          
          // Sideburns / Back wrap
          ctx.fillRect(-sqSize, headTop, pixelSize * 2.5, pixelSize * 6);
          ctx.fillRect(sqSize - pixelSize * 2.5, headTop, pixelSize * 2.5, pixelSize * 6);
          
          // Small fringe
          ctx.fillRect(-sqSize * 0.6, headTop, sqSize * 1.2, pixelSize * 0.8);

      } else if (viz.hairStyle === 'chef_hat') {
          // Chef Hat - LIFTED
          ctx.fillStyle = '#ffffff';
          // Top Floof
          ctx.beginPath();
          ctx.ellipse(0, -r * 2.0, r * 1.2, r * 0.8, 0, 0, Math.PI * 2);
          ctx.fill();
          // Band
          ctx.beginPath();
          ctx.roundRect(-r * 0.75, -r * 1.7, r * 1.5, r * 0.5, 6);
          ctx.fill();
          // Shadow/Details
          ctx.strokeStyle = '#e8e8e8';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(-r * 0.35, -r * 2.0);
          ctx.lineTo(-r * 0.35, -r * 1.6);
          ctx.moveTo(r * 0.35, -r * 2.0);
          ctx.lineTo(r * 0.35, -r * 1.6);
          ctx.stroke();
      } else if (viz.hairStyle === 'none' && viz.clothingStyle === 'gi') {
          // Kippah (Yarmulke)
          ctx.fillStyle = '#222'; // Dark Kippah
          ctx.beginPath();
          ctx.ellipse(0, -r * 0.95, r * 0.5, r * 0.2, 0, 0, Math.PI * 2);
          ctx.fill();

          // Payot (Sidelocks)
          ctx.strokeStyle = viz.hairColor || '#1a1a1a';
          ctx.lineWidth = 6;
          ctx.lineCap = 'round';
          
          const drawPayot = (side: -1 | 1) => {
              ctx.beginPath();
              const startX = side * r * 0.82;
              const startY = -r * 0.1;
              ctx.moveTo(startX, startY);
              // Multi-curl path
              ctx.bezierCurveTo(
                  startX + side * r * 0.25, startY + r * 0.4,
                  startX - side * r * 0.15, startY + r * 0.6,
                  startX + side * r * 0.1, startY + r * 0.9
              );
              ctx.stroke();
          };
          drawPayot(-1);
          drawPayot(1);
      } else if (viz.hairStyle === 'spiky') {
          ctx.fillStyle = viz.hairColor;
          ctx.beginPath();
          ctx.ellipse(0, -r * 0.7, r * 1.0, r * 0.4, 0, Math.PI, 0);
          ctx.fill();
          for(let i=0; i<10; i++){
             const tx = (i/9 - 0.5) * r * 1.8;
             const ty = -r * 0.8;
             ctx.beginPath();
             ctx.moveTo(tx - r*0.1, ty);
             ctx.lineTo(tx, ty - r*0.4);
             ctx.lineTo(tx + r*0.1, ty);
             ctx.fill();
          }
      } else if (viz.hairStyle === 'long') {
          // Memoji Long/Curly Hair
          ctx.fillStyle = viz.hairColor;
          // Solid base
          ctx.beginPath();
          ctx.moveTo(-r * 1.2, 0);
          ctx.quadraticCurveTo(-r * 1.0, -r * 1.2, 0, -r * 1.1);
          ctx.quadraticCurveTo(r * 1.0, -r * 1.2, r * 1.2, 0);
          ctx.quadraticCurveTo(0, -r * 0.5, -r * 1.2, 0);
          ctx.fill();
          // Texture strands
          ctx.strokeStyle = 'rgba(255,255,255,0.1)';
          ctx.lineWidth = 1;
          for(let i=0; i<10; i++) {
              const tx = (i/9 - 0.5) * r * 1.5;
              ctx.beginPath();
              ctx.moveTo(tx, -r);
              ctx.bezierCurveTo(tx + r*0.2, -r*0.5, tx - r*0.2, -r*0.1, tx, 0);
              ctx.stroke();
          }
      }

      // ... (Standard eye/mouth/hair rendering) copied implicitly by not deleting it 
      // Closing the else block for STANDARD renderer
      }
      
      // Legacy "Jerry" block removed as it is now handled by the main 'giraffe' block above
       
      ctx.restore(); // Final head group
      animationFrameId = requestAnimationFrame(render);
    };

    const handleResize = () => {
      if (!canvas.parentElement) return;
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    };
    window.addEventListener('resize', handleResize);
    handleResize();

    render(performance.now());

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div className="avatar-canvas-container" style={{ 
      width: '100%', 
      height: '100%', 
      position: 'relative',
      background: currentAgent.id === 'fortnite-ace' ? 'white' : 'transparent'
    }}>
      <canvas
        ref={canvasRef}
        style={{ width: '100%', height: '100%', display: 'block' }}
      />
      {!connected && (
        <div style={{
          position: 'absolute',
          bottom: '15%', left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)',
          padding: '12px 24px', borderRadius: '24px', color: 'white',
          fontWeight: 600, border: '1px solid rgba(255,255,255,0.2)',
          zIndex: 10, pointerEvents: 'none', whiteSpace: 'nowrap',
        }}>
          Waiting for connection...
        </div>
      )}

      {/* Config Button (Gear) */}
      <button
        onClick={() => setShowConfig(true)}
        style={{
          position: 'absolute', bottom: '20px', right: '20px',
          background: 'rgba(0,0,0,0.5)', border: 'none', borderRadius: '50%',
          width: '40px', height: '40px', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'white', zIndex: 20
        }}
      >
        <span className="material-symbols-outlined">settings</span>
      </button>

      {/* Config Modal */}
      {showConfig && (
        <ConfigModal 
          onClose={() => setShowConfig(false)}
          initialInstruction={currentInstruction}
          onSave={handleSaveConfig}
        />
      )}
    </div>
  );
}
