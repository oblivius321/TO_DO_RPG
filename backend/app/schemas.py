from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    level: int
    current_xp: int
    total_xp: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class TaskTemplateBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    base_xp: int = Field(default=10, ge=0, le=500)
    is_active: bool = True


class TaskTemplateCreate(TaskTemplateBase):
    pass


class TaskTemplateUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    base_xp: Optional[int] = Field(default=None, ge=0, le=500)
    is_active: Optional[bool] = None


class TaskTemplateRead(TaskTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class TaskLogRead(BaseModel):
    id: int
    log_date: date
    completed: bool
    completed_at: Optional[datetime]
    xp_awarded: int
    template: TaskTemplateRead

    model_config = {
        "from_attributes": True,
    }


class DailyProgressResponse(BaseModel):
    logs: list[TaskLogRead]
    level: int
    current_xp: int
    title: str


class TaskCompletionResponse(BaseModel):
    message: str
    xp_awarded: int
    level: int
    current_xp: int
    title: str
    level_ups: int
    bonus_awarded: bool


class Message(BaseModel):
    message: str