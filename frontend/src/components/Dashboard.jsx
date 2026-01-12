import React from 'react';

function Dashboard() {
  return (
    <div style={{ maxWidth: 500, margin: '0 auto', fontFamily: 'sans-serif' }}>
      {/* HERO STATUS */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontWeight: 'bold', fontSize: 18 }}>
          HERO STATUS: <span style={{ color: '#bfa23a' }}>Level 05</span>
        </div>
        <div style={{ marginTop: 8, marginBottom: 4, fontSize: 14 }}>85|100 XP</div>
        <div style={{ background: '#ddd', borderRadius: 8, height: 16, width: '100%' }}>
          <div style={{ background: '#f7c948', width: '85%', height: '100%', borderRadius: 8 }} />
        </div>
      </div>

      {/* MISSÕES ATIVAS */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontWeight: 'bold', fontSize: 16, marginBottom: 12 }}>
          SUAS MISSÕES ATIVAS
        </div>
        {/* Missão 1 */}
        <div style={{ display: 'flex', alignItems: 'center', background: '#f5f5f5', borderRadius: 8, padding: 12, marginBottom: 10 }}>
          <input type="checkbox" style={{ marginRight: 12 }} />
          <span style={{ flex: 1 }}>Estudar React Avançado</span>
          <span style={{ background: '#f8d7da', color: '#a94442', borderRadius: 6, padding: '2px 8px', fontSize: 12, marginRight: 8 }}>
            Hard (+50XP)
          </span>
          <button style={{ border: 'none', background: '#eee', borderRadius: 6, padding: '4px 12px', cursor: 'pointer' }}>Estudar</button>
        </div>
        {/* Missão 2 */}
        <div style={{ display: 'flex', alignItems: 'center', background: '#f5f5f5', borderRadius: 8, padding: 12 }}>
          <input type="checkbox" style={{ marginRight: 12 }} />
          <span style={{ flex: 1 }}>Beber 2L de Água</span>
          <span style={{ background: '#d1ecf1', color: '#31708f', borderRadius: 6, padding: '2px 8px', fontSize: 12, marginRight: 8 }}>
            Easy (+15XP)
          </span>
        </div>
      </div>

      {/* MISSÕES CONCLUÍDAS */}
      <div>
        <div style={{ fontWeight: 'bold', fontSize: 16, marginBottom: 12 }}>
          MISSÕES CONCLUÍDAS
        </div>
        <div style={{ display: 'flex', alignItems: 'center', background: '#f5f5f5', borderRadius: 8, padding: 12 }}>
          <span style={{ color: '#d9534f', fontSize: 18, marginRight: 10 }}>✗</span>
          <span style={{ textDecoration: 'line-through', color: '#888', flex: 1 }}>Ler documentação</span>
          <span style={{ color: '#5cb85c', fontSize: 18, marginLeft: 10 }}>✓</span>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
