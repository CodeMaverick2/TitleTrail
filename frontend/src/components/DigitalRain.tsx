import React, { useEffect, useRef } from 'react';

const DigitalRain: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;

    const createRainDrop = () => {
      const drop = document.createElement('span');
      const number = Math.floor(Math.random() * 2); // Binary numbers
      drop.textContent = number.toString();
      
      // Random starting position
      const startX = Math.random() * containerWidth;
      drop.style.left = `${startX}px`;
      
      // Random animation duration
      const duration = 3 + Math.random() * 5;
      drop.style.animationDuration = `${duration}s`;
      
      container.appendChild(drop);

      setTimeout(() => {
        drop.remove();
      }, duration * 1000);
    };

    for (let i = 0; i < 50; i++) {
      setTimeout(createRainDrop, Math.random() * 3000);
    }
    const interval = setInterval(createRainDrop, 100);

    return () => {
      clearInterval(interval);
      container.innerHTML = '';
    };
  }, []);

  return <div ref={containerRef} className="digital-rain" />;
};
export default DigitalRain;