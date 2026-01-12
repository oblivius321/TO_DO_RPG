from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    current_xp = Column(Integer, default=0, nullable=False)
    total_xp = Column(Integer, default=0, nullable=False)
    title = Column(String, default="Novato", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    task_templates = relationship(
        "TaskTemplate",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    task_logs = relationship(
        "TaskLog",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    base_xp = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner = relationship("User", back_populates="task_templates")
    logs = relationship(
        "TaskLog",
        back_populates="template",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False, index=True)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    xp_awarded = Column(Integer, default=0, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(Integer, ForeignKey("task_templates.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="task_logs")
    template = relationship("TaskTemplate", back_populates="logs")

    __table_args__ = (
        UniqueConstraint("log_date", "template_id", "owner_id", name="uq_task_log_daily"),
    )