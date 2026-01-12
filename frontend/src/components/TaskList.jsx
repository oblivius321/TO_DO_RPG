import React from 'react';

export default function TaskList() {
  // Exemplo estático, substitua por lógica real depois
  const tasks = [];

  return (
    <div className="task-list">
      {tasks.length === 0 ? (
        <p>Nenhuma tarefa ainda.</p>
      ) : (
        <ul>
          {tasks.map((task, idx) => (
            <li key={idx}>{task}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
