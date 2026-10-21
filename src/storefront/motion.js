import { useEffect } from 'react';

export const reduceMotion = () => typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
export const finePointer = () => typeof window !== 'undefined' && !!window.matchMedia?.('(hover: hover) and (pointer: fine)').matches;

/**
 * 3D tilt that follows the pointer. Sets --rx / --ry (degrees) and --gx / --gy (glare position) on the element;
 * the .ac-tilt CSS turns them into perspective rotation and a soft light reflection.
 * Does nothing on touch screens or when the person prefers reduced motion.
 */
export function useTilt(ref, max = 9) {
  useEffect(() => {
    const el = ref.current;
    if (!el || reduceMotion() || !finePointer()) return undefined;
    let raf = 0;
    const move = (e) => {
      const r = el.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width;
      const py = (e.clientY - r.top) / r.height;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        el.style.setProperty('--ry', `${((px - 0.5) * 2 * max).toFixed(2)}deg`);
        el.style.setProperty('--rx', `${((0.5 - py) * 2 * max).toFixed(2)}deg`);
        el.style.setProperty('--gx', `${(px * 100).toFixed(1)}%`);
        el.style.setProperty('--gy', `${(py * 100).toFixed(1)}%`);
        el.dataset.tilt = 'on';
      });
    };
    const leave = () => {
      cancelAnimationFrame(raf);
      el.style.setProperty('--rx', '0deg');
      el.style.setProperty('--ry', '0deg');
      el.dataset.tilt = 'off';
    };
    el.addEventListener('pointermove', move);
    el.addEventListener('pointerleave', leave);
    return () => {
      cancelAnimationFrame(raf);
      el.removeEventListener('pointermove', move);
      el.removeEventListener('pointerleave', leave);
    };
  }, [ref, max]);
}
