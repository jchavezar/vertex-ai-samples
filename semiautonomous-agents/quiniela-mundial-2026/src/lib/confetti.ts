"use client";

// Reusable lightweight canvas confetti burst utility (zero-dependency).
export function fireConfetti(options?: { count?: number; originY?: number }) {
  if (typeof window === "undefined") return;

  const count = options?.count ?? 40;
  const originY = options?.originY ?? 0.6;

  const canvas = document.createElement("canvas");
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  canvas.style.position = "fixed";
  canvas.style.top = "0";
  canvas.style.left = "0";
  canvas.style.pointerEvents = "none";
  canvas.style.zIndex = "9999";
  document.body.appendChild(canvas);

  const ctx = canvas.getContext("2d");
  if (!ctx) {
    document.body.removeChild(canvas);
    return;
  }

  const colors = ["#006847", "#CE1126", "#FFD54F", "#00897B", "#5E5BFF", "#FFFFFF"];
  const particles: Array<{
    x: number;
    y: number;
    vx: number;
    vy: number;
    size: number;
    color: string;
    rotation: number;
    vRot: number;
    alpha: number;
  }> = [];

  for (let i = 0; i < count; i++) {
    particles.push({
      x: window.innerWidth * 0.5 + (Math.random() * 80 - 40),
      y: window.innerHeight * originY,
      vx: (Math.random() - 0.5) * 12,
      vy: -(Math.random() * 10 + 6),
      size: Math.random() * 8 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      rotation: Math.random() * 360,
      vRot: (Math.random() - 0.5) * 15,
      alpha: 1,
    });
  }

  let startTime: number | null = null;
  const duration = 2200; // ms

  function animate(now: number) {
    if (!startTime) startTime = now;
    const elapsed = now - startTime;
    const progress = elapsed / duration;

    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let active = false;
    for (const p of particles) {
      if (p.alpha <= 0) continue;
      active = true;

      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.35; // gravity
      p.vx *= 0.98;
      p.rotation += p.vRot;
      p.alpha = Math.max(0, 1 - progress * 1.2);

      ctx.save();
      ctx.globalAlpha = p.alpha;
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.5);
      ctx.restore();
    }

    if (progress < 1 && active) {
      requestAnimationFrame(animate);
    } else {
      if (document.body.contains(canvas)) {
        document.body.removeChild(canvas);
      }
    }
  }

  requestAnimationFrame(animate);
}
