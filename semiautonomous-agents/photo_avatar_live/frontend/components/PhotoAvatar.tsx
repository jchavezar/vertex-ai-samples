/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { useLiveAPIContext } from '../contexts/LiveAPIContext';

interface Face {
  mouthX: number;
  mouthY: number;
  mouthW: number;
  leftEyeX: number;
  leftEyeY: number;
  rightEyeX: number;
  rightEyeY: number;
}

type Mode = 'idle' | 'capture' | 'photo';

const BTN_BASE: React.CSSProperties = {
  border: 'none',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontFamily: 'inherit',
};

export default function PhotoAvatar() {
  const { volume, connected } = useLiveAPIContext();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const faceRef = useRef<Face | null>(null);
  const volRef = useRef(0);
  const streamRef = useRef<MediaStream | null>(null);
  const [mode, setMode] = useState<Mode>('idle');
  const animRef = useRef({ time: 0, jaw: 0, blink: 0, blinking: false, nextBlink: 2500 });

  useEffect(() => { volRef.current = volume; }, [volume]);
  useEffect(() => () => { streamRef.current?.getTracks().forEach(t => t.stop()); }, []);

  // ── Face detection via Chrome FaceDetector API ──────────────────────────
  const detectFace = useCallback(async (img: HTMLImageElement): Promise<Face> => {
    const iw = img.naturalWidth;
    const ih = img.naturalHeight;
    // Proportional defaults that work well for centered selfies
    let face: Face = {
      mouthX: 0.5,  mouthY: 0.675, mouthW: 0.235,
      leftEyeX: 0.365, leftEyeY: 0.405,
      rightEyeX: 0.635, rightEyeY: 0.405,
    };
    if ('FaceDetector' in window) {
      try {
        const fd = new (window as any).FaceDetector({ fastMode: false });
        const faces: any[] = await fd.detect(img);
        if (faces.length > 0) {
          const { boundingBox: bb, landmarks: lm } = faces[0];
          const mouth = lm?.find((l: any) => l.type === 'mouth');
          const le    = lm?.find((l: any) => l.type === 'left-eye');
          const re    = lm?.find((l: any) => l.type === 'right-eye');
          face = {
            mouthX:    (mouth?.location.x ?? bb.x + bb.width * 0.5) / iw,
            mouthY:    (mouth?.location.y ?? bb.y + bb.height * 0.73) / ih,
            mouthW:    (bb.width * 0.44) / iw,
            leftEyeX:  (le?.location.x ?? bb.x + bb.width * 0.28) / iw,
            leftEyeY:  (le?.location.y ?? bb.y + bb.height * 0.36) / ih,
            rightEyeX: (re?.location.x ?? bb.x + bb.width * 0.72) / iw,
            rightEyeY: (re?.location.y ?? bb.y + bb.height * 0.36) / ih,
          };
        }
      } catch (e) {
        console.warn('FaceDetector unavailable, using proportional fallback:', e);
      }
    }
    return face;
  }, []);

  // ── Open webcam ───────────────────────────────────────────────────────────
  const startCapture = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 640 } },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setMode('capture');
    } catch {
      alert('Camera access required. Please allow camera access in your browser.');
    }
  }, []);

  // ── Capture snapshot ──────────────────────────────────────────────────────
  const takePhoto = useCallback(async () => {
    const video = videoRef.current;
    if (!video) return;
    const tc = document.createElement('canvas');
    tc.width  = video.videoWidth  || 640;
    tc.height = video.videoHeight || 640;
    const tctx = tc.getContext('2d')!;
    tctx.translate(tc.width, 0);
    tctx.scale(-1, 1); // mirror for natural selfie orientation
    tctx.drawImage(video, 0, 0);
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;

    const img = new Image();
    img.onload = async () => {
      imgRef.current = img;
      const face = await detectFace(img);
      faceRef.current = face;
      animRef.current = { time: 0, jaw: 0, blink: 0, blinking: false, nextBlink: 2500 };
      setMode('photo');
    };
    img.src = tc.toDataURL('image/jpeg', 0.93);
  }, [detectFace]);

  // ── Animation loop ────────────────────────────────────────────────────────
  useEffect(() => {
    if (mode !== 'photo') return;
    const canvas = canvasRef.current;
    const img    = imgRef.current;
    if (!canvas || !img) return;
    const ctx = canvas.getContext('2d')!;
    let raf: number;
    let last = performance.now();

    const frame = (now: number) => {
      const dt = Math.min(now - last, 50);
      last = now;
      const a = animRef.current;
      a.time += dt;

      // Resize canvas to parent when needed
      const par = canvas.parentElement!;
      const cw = par.clientWidth;
      const ch = par.clientHeight;
      if (canvas.width !== cw)  canvas.width  = cw;
      if (canvas.height !== ch) canvas.height = ch;

      // Blink state machine
      if (!a.blinking && now > a.nextBlink) { a.blinking = true; a.blink = 0; }
      if (a.blinking) {
        a.blink += dt / 68;
        if (a.blink >= 2) {
          a.blinking = false;
          a.nextBlink = now + 2000 + Math.random() * 2500;
        }
      }
      const blinkF = a.blinking ? (a.blink <= 1 ? a.blink : 2 - a.blink) : 0;

      // Jaw driven by Gemini Live output volume
      a.jaw += (Math.min(volRef.current * 3.2, 1) - a.jaw) * 0.22;

      // Gentle float
      const fy = Math.sin(a.time * 0.0016) * 5;

      // Cover-fit image layout
      const iw = img.naturalWidth;
      const ih = img.naturalHeight;
      const sc = Math.max(cw / iw, ch / ih);
      const dw = iw * sc;
      const dh = ih * sc;
      const dx = (cw - dw) / 2;
      const dy = (ch - dh) / 2;

      ctx.clearRect(0, 0, cw, ch);
      ctx.save();
      ctx.translate(0, fy);

      // ── 1. Full photo ────────────────────────────────────────────────────
      ctx.drawImage(img, dx, dy, dw, dh);

      const f = faceRef.current;

      // ── 2. Mouth animation ───────────────────────────────────────────────
      if (f && a.jaw > 0.03) {
        const mx = f.mouthX * dw + dx;
        const my = f.mouthY * dh + dy;
        const mw = f.mouthW * dw;
        const ow = mw * 0.9  * a.jaw;
        const oh = mw * 0.44 * a.jaw;

        // Erase the closed lips by compositing the skin above them
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(mx, my, mw * 0.5, mw * 0.15, 0, 0, Math.PI * 2);
        ctx.clip();
        const coverSrcY = Math.max(0, (my - mw * 0.38 - dy) / sc);
        ctx.drawImage(
          img,
          (mx - mw * 0.5 - dx) / sc, coverSrcY,
          mw / sc, (mw * 0.3) / sc,
          mx - mw * 0.5, my - mw * 0.15,
          mw, mw * 0.3,
        );
        ctx.restore();

        // Dark mouth cavity with radial depth gradient
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(mx, my + oh * 0.09, ow * 0.5, oh * 0.53, 0, 0, Math.PI * 2);
        const mg = ctx.createRadialGradient(mx, my, 0, mx, my + oh * 0.3, ow * 0.55);
        mg.addColorStop(0, '#3e0000');
        mg.addColorStop(0.6, '#220000');
        mg.addColorStop(1, '#130000');
        ctx.fillStyle = mg;
        ctx.fill();

        // Upper teeth appear once the mouth opens past ~20 %
        if (a.jaw > 0.2) {
          const tw = ow * 0.84;
          const th = Math.min(oh * 0.36, 17);
          ctx.save();
          ctx.beginPath();
          ctx.ellipse(mx, my + oh * 0.09, ow * 0.5, oh * 0.53, 0, 0, Math.PI * 2);
          ctx.clip();

          ctx.fillStyle = '#f6f2ee';
          ctx.beginPath();
          (ctx as any).roundRect(mx - tw / 2, my - oh * 0.44, tw, th, [0, 0, 3, 3]);
          ctx.fill();

          ctx.strokeStyle = 'rgba(190,183,176,0.5)';
          ctx.lineWidth = 1;
          for (let i = 1; i < 6; i++) {
            const tx = mx - tw / 2 + (tw / 6) * i;
            ctx.beginPath();
            ctx.moveTo(tx, my - oh * 0.44);
            ctx.lineTo(tx, my - oh * 0.44 + th);
            ctx.stroke();
          }

          // Lower teeth hint for wide-open mouth
          if (a.jaw > 0.5) {
            const ltw = ow * 0.68;
            const lth = Math.min(oh * 0.22, 11);
            ctx.fillStyle = '#ede9e5';
            ctx.beginPath();
            (ctx as any).roundRect(mx - ltw / 2, my + oh * 0.32, ltw, lth, [3, 3, 0, 0]);
            ctx.fill();
          }
          ctx.restore();
        }
        ctx.restore();
      }

      // ── 3. Eye blink ─────────────────────────────────────────────────────
      if (f && blinkF > 0.02) {
        ([[f.leftEyeX, f.leftEyeY], [f.rightEyeX, f.rightEyeY]] as [number, number][])
          .forEach(([ex, ey]) => {
            const epx = ex * dw + dx;
            const epy = ey * dh + dy;
            const ew  = (f.mouthW * dw) * 0.46;
            const eh  = ew * 0.37;
            ctx.save();
            ctx.beginPath();
            ctx.ellipse(epx, epy, ew * 0.5, eh * blinkF + 1, 0, 0, Math.PI * 2);
            ctx.clip();
            // Composite skin texture from above the brow — looks like real eyelid closure
            const srcY = Math.max(0, (epy - eh * 2.2 - dy) / sc);
            ctx.drawImage(
              img,
              (epx - ew * 0.5 - dx) / sc, srcY,
              ew / sc, (eh * 3.5) / sc,
              epx - ew * 0.5, epy - eh,
              ew, eh * 2.5,
            );
            ctx.restore();
          });
      }

      // ── 4. Vignette ───────────────────────────────────────────────────────
      const vg = ctx.createRadialGradient(cw / 2, ch / 2, cw * 0.26, cw / 2, ch / 2, cw * 0.78);
      vg.addColorStop(0, 'rgba(0,0,0,0)');
      vg.addColorStop(1, 'rgba(0,0,0,0.42)');
      ctx.fillStyle = vg;
      ctx.fillRect(0, 0, cw, ch);

      ctx.restore();
      raf = requestAnimationFrame(frame);
    };

    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, [mode]);

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', background: '#080808' }}>

      {/* ── Idle: prompt user to take a selfie ── */}
      {mode === 'idle' && (
        <div style={{
          width: '100%', height: '100%',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center', gap: 24,
        }}>
          <div style={{ textAlign: 'center', color: 'rgba(255,255,255,0.55)', lineHeight: 1.6 }}>
            <div style={{ fontSize: 56, marginBottom: 12 }}>🪞</div>
            <p style={{ fontSize: 18, marginBottom: 6, color: 'rgba(255,255,255,0.8)' }}>
              Create your photorealistic avatar
            </p>
            <p style={{ fontSize: 13 }}>
              Take a selfie — your face becomes the avatar
            </p>
          </div>
          <button
            onClick={startCapture}
            style={{
              ...BTN_BASE,
              padding: '13px 32px',
              background: '#4a90e2',
              borderRadius: 24,
              color: '#fff',
              fontSize: 15,
              fontWeight: 600,
              gap: 8,
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>photo_camera</span>
            Take Selfie
          </button>
        </div>
      )}

      {/* ── Capture: webcam preview ── */}
      {mode === 'capture' && (
        <div style={{
          width: '100%', height: '100%',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
        }}>
          <div style={{ position: 'relative', marginBottom: 24 }}>
            <video
              ref={videoRef}
              style={{
                width: 300, height: 300,
                borderRadius: '50%',
                objectFit: 'cover',
                transform: 'scaleX(-1)',
                border: '2px solid rgba(255,255,255,0.16)',
                boxShadow: '0 0 60px rgba(74,144,226,0.25)',
                display: 'block',
              }}
              muted playsInline autoPlay
            />
            <div style={{
              position: 'absolute', inset: -5,
              borderRadius: '50%',
              border: '2px solid rgba(74,144,226,0.4)',
              pointerEvents: 'none',
            }} />
          </div>
          <p style={{ color: 'rgba(255,255,255,0.45)', margin: '0 0 18px', fontSize: 13 }}>
            Center your face, then capture
          </p>
          <div style={{ display: 'flex', gap: 10 }}>
            <button
              onClick={takePhoto}
              style={{ ...BTN_BASE, padding: '12px 28px', background: '#4a90e2', borderRadius: 22, color: '#fff', fontSize: 14, fontWeight: 600 }}
            >
              Capture
            </button>
            <button
              onClick={() => { streamRef.current?.getTracks().forEach(t => t.stop()); setMode('idle'); }}
              style={{ ...BTN_BASE, padding: '12px 18px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.11)', borderRadius: 22, color: '#fff', fontSize: 14 }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* ── Photo: animated canvas ── */}
      <canvas
        ref={canvasRef}
        style={{ width: '100%', height: '100%', display: mode === 'photo' ? 'block' : 'none' }}
      />

      {/* ── Waiting overlay when not connected ── */}
      {mode === 'photo' && !connected && (
        <div style={{
          position: 'absolute', bottom: '15%', left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)',
          padding: '10px 22px', borderRadius: 20, color: 'white',
          fontSize: 13, fontWeight: 500, border: '1px solid rgba(255,255,255,0.15)',
          pointerEvents: 'none', whiteSpace: 'nowrap',
        }}>
          Press ▶ to start talking
        </div>
      )}

      {/* ── Camera toggle (bottom-left) ── */}
      {mode !== 'capture' && (
        <button
          onClick={mode === 'idle' ? startCapture : () => setMode('idle')}
          title={mode === 'idle' ? 'Take a selfie to create your avatar' : 'Retake photo'}
          style={{
            ...BTN_BASE,
            position: 'absolute', bottom: 20, left: 20,
            width: 44, height: 44,
            background: 'rgba(0,0,0,0.52)',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255,255,255,0.13)',
            borderRadius: '50%',
            color: '#fff',
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
            {mode === 'idle' ? 'photo_camera' : 'cameraswitch'}
          </span>
        </button>
      )}
    </div>
  );
}
