import React, { useState } from 'react';

export default function TaskInput() {
  const [task, setTask] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!task.trim()) return;
    // Aqui você pode adicionar lógica para enviar a task para o backend ou atualizar o estado global
    setTask('');
  };

  return (
    <form className="task-input" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Nova tarefa..."
        value={task}
        onChange={e => setTask(e.target.value)}
      />
      <button type="submit">Adicionar</button>
    </form>
  );
}
