/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import { useEffect, useRef, useState } from 'react';

interface HoverProps {
  /** Maximum distance in pixels that the element will move up and down from its initial position. */
  amplitude?: number;
  /** Number of complete hover cycles per second. Lower values create slower, gentler movement. */
  frequency?: number;
}

export default function useHover({
  amplitude = 10,
  frequency = 0.5,
}: HoverProps = {}) {
  const [offset, setOffset] = useState(0);
  const startTimeRef = useRef(Date.now());
  const animationFrameRef = useRef<number>(0);

  useEffect(() => {
    const animate = () => {
      // Calculate time elapsed in seconds since the animation started
      const elapsed = (Date.now() - startTimeRef.current) / 1000;
      // Create smooth sinusoidal motion
      const newOffset = Math.sin(elapsed * frequency * Math.PI) * amplitude;

      setOffset(newOffset);
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    // Start the animation loop
    animationFrameRef.current = requestAnimationFrame(animate);

    // Cancel animation frame when component unmounts or when amplitude/frequency changes
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [amplitude, frequency]);

  return offset;
}
