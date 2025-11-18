
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session


import services
import models
import database

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TaskCreate(BaseModel):
    title: str
    completed: bool = False

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool

    class Config:
        from_attributes = True

# Modelo para resposta do usuário
class UserResponse(BaseModel):
    id: int
    name: str
    level: int
    xp: int
    title: str

    class Config:
        from_attributes = True

# ID do usuário padrão (por enquanto)
DEFAULT_USER_ID = 1

@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).filter(models.Task.owner_id == DEFAULT_USER_ID).all()
    return tasks

@router.post("/tasks")
def add_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    # Cria nova task
    new_task = models.Task(
        title=task_data.title,
        completed=task_data.completed,
        owner_id=DEFAULT_USER_ID
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {
        "message": "Task adicionada!",
        "task": new_task
    }

@router.put("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    # 1. Encontrar a task
    task = db.query(models.Task).filter(
        models.Task.id == task_id, 
        models.Task.owner_id == DEFAULT_USER_ID
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    if task.completed:
        return {"message": "Task já estava completa!"}
    
    # 2. Marcar como completa
    task.completed = True
    
    # 3. Buscar usuário
    user = db.query(models.User).filter(models.User.id == DEFAULT_USER_ID).first()
    if not user:
        # Criar usuário padrão se não existir
        user = models.User(id=DEFAULT_USER_ID, name="Jogador", level=1, xp=0, title="Novato")
        db.add(user)
    
    # 4. Verificar se TODAS as tasks estão completas
    todas_tasks = db.query(models.Task).filter(models.Task.owner_id == DEFAULT_USER_ID).all()
    todas_completas = all(task.completed for task in todas_tasks)
    
    # 5. Aplicar sistema de XP - SEU SERVICES.PY 🎮
    xp_ganho = 10
    mensagem_xp = services.add_xp(user, xp_ganho, todas_completas)
    
    # 6. SALVAR AS ALTERAÇÕES NO BANCO
    db.commit()
    db.refresh(user)  # Atualiza os dados do usuário
    
    # 7. Preparar resposta
    response = {
        "message": f"✅ Task '{task.title}' completada!",
        "xp_ganho": xp_ganho,
        "xp_total": user.xp,
        "level": user.level,
        "title": user.title,
        "system_message": mensagem_xp
    }
    
    # 8. Adicionar bônus se todas completas
    if todas_completas:
        response["bonus_diario"] = "🎉 TODAS TASKS COMPLETAS! Bônus aplicado!"
    
    return response

@router.get("/user/stats", response_model=UserResponse)
def get_user_stats(db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == DEFAULT_USER_ID).first()
    if not user:
        # Criar usuário padrão se não existir
        user = models.User(id=DEFAULT_USER_ID, name="Jogador", level=1, xp=0, title="Novato")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(
        models.Task.id == task_id, 
        models.Task.owner_id == DEFAULT_USER_ID
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    db.delete(task)
    db.commit()
    
    return {"message": f"Task '{task.title}' deletada!"}

@router.post("/reset")
def reset_system(db: Session = Depends(get_db)):
    """Endpoint para resetar o sistema (apenas para testes)"""
    # Deletar todas as tasks
    db.query(models.Task).filter(models.Task.owner_id == DEFAULT_USER_ID).delete()
    
    # Resetar usuário
    user = db.query(models.User).filter(models.User.id == DEFAULT_USER_ID).first()
    if user:
        user.level = 1
        user.xp = 0
        user.title = "Novato"
    
    db.commit()
    
    return {"message": "Sistema resetado! 🎮"}