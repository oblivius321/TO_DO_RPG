import React from 'react';

export default function XPBar() {
  // Exemplo estático, substitua por lógica real depois
  const xp = 30;
  const maxXp = 100;

  return (
    <div className="xp-bar-container" style={{ margin: '1rem 0' }}>
      <div style={{ color: '#fff', marginBottom: 4 }}>XP: {xp} / {maxXp}</div>
      <div style={{ background: '#333', borderRadius: 8, height: 18, width: 300 }}>
        <div
          style={{
            width: `${(xp / maxXp) * 100}%`,
            background: 'linear-gradient(90deg, #4f8cff, #7fffd4)',
            height: '100%',
            borderRadius: 8,
            transition: 'width 0.3s',
          }}
        />
      </div>
    </div>
  );
}
