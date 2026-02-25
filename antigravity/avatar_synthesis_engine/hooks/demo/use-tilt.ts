/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import { useEffect, useRef, useState } from 'react';

export type UseTiltProps = {
  /** Maximum tilt angle (degrees) in either direction. */
  maxAngle: number;
  /** How quickly the tilt occurs. Lower values create slower, gentler movement. */
  speed?: number;
  /** Whether tilt mode is currently active. */
  isActive: boolean;
};

/**
 * Map a value from one domain of numbers to another,
 * e.g., scalemap(0.5, 0, 2, 10, 20) = 12.5
 */
export function scalemap(
  value: number,
  start1: number,
  stop1: number,
  start2: number,
  stop2: number
): number {
  return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1));
}

export default function useTilt({
  maxAngle = 5,
  speed = 0.1,
  isActive = false,
}: UseTiltProps) {
  const [angle, setAngle] = useState<number>(0);
  const [targetAngle, setTargetAngle] = useState<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout>(undefined);
  const animationFrameRef = useRef<number>(0);

  // Reset to center when not active
  useEffect(() => {
    if (!isActive) {
      setTargetAngle(0);
    }
  }, [isActive]);

  // Schedule next random tilt (only when active)
  useEffect(() => {
    if (!isActive) return;

    const scheduleNextTilt = () => {
      const delay = 1000 + Math.random() * 2000; // Random delay between 1-3 seconds
      timeoutRef.current = setTimeout(() => {
        // First, return to center if we're not there
        if (Math.abs(targetAngle) > 0.1) {
          setTargetAngle(0);
          scheduleNextTilt();
        } else {
          // Then, pick a new random angle
          const newAngle =
            (Math.random() > 0.5 ? 1 : -1) *
            (maxAngle * 0.3 + Math.random() * maxAngle * 0.7);
          setTargetAngle(newAngle);
          scheduleNextTilt();
        }
      }, delay);
    };

    scheduleNextTilt();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [maxAngle, isActive]);

  // Animate current angle towards target angle
  useEffect(() => {
    const animate = () => {
      setAngle(currentAngle => {
        const diff = targetAngle - currentAngle;
        // Ease towards target angle
        const delta = diff * speed;
        return currentAngle + delta;
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [targetAngle, speed]);

  return angle;
}
