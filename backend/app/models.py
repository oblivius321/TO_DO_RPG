# backend/app/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# Importação ABSOLUTA
from database import Base

# ------------------------
# Modelo de Usuário (User)
# ------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    title = Column(String, default="Novato")

    # relação com tarefas
    tasks = relationship("Task", back_populates="owner")

# ------------------------
# Modelo de Tarefa (Task)
# ------------------------
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")