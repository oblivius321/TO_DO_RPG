from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

from sqlalchemy.orm import Session

import models


LEVELS = [
    {"min": 1, "max": 15, "xp": 100, "title": "Novato"},
    {"min": 16, "max": 20, "xp": 150, "title": "Aprendiz"},
    {"min": 21, "max": 30, "xp": 200, "title": "Guerreiro"},
    {"min": 31, "max": 50, "xp": 250, "title": "Mestre"},
    {"min": 51, "max": 70, "xp": 300, "title": "Grão Mestre"},
    {"min": 71, "max": 100, "xp": 500, "title": "Deus"},
]

MAX_LEVEL = 100
DAILY_COMPLETION_BONUS = 50


def get_xp_for_level(level: int) -> int:
    for lvl in LEVELS:
        if lvl["min"] <= level <= lvl["max"]:
            return lvl["xp"]
    return LEVELS[-1]["xp"]


def get_title_for_level(level: int) -> str:
    for lvl in LEVELS:
        if lvl["min"] <= level <= lvl["max"]:
            return lvl["title"]
    return LEVELS[-1]["title"]


def apply_xp(user: models.User, xp_amount: int) -> dict:
    if xp_amount <= 0:
        return {
            "level": user.level,
            "current_xp": user.current_xp,
            "title": user.title,
            "level_ups": 0,
            "xp_awarded": 0,
        }

    user.total_xp += xp_amount
    user.current_xp += xp_amount
    level_ups = 0

    while user.level < MAX_LEVEL and user.current_xp >= get_xp_for_level(user.level):
        threshold = get_xp_for_level(user.level)
        user.current_xp -= threshold
        user.level += 1
        level_ups += 1

    if user.level >= MAX_LEVEL:
        user.level = MAX_LEVEL
        user.current_xp = 0

    user.title = get_title_for_level(user.level)

    return {
        "level": user.level,
        "current_xp": user.current_xp,
        "title": user.title,
        "level_ups": level_ups,
        "xp_awarded": xp_amount,
    }


def ensure_daily_logs(
    db: Session,
    user: models.User,
    target_date: date | None = None,
) -> list[models.TaskLog]:
    target_date = target_date or date.today()

    templates: list[models.TaskTemplate] = (
        db.query(models.TaskTemplate)
        .filter(
            models.TaskTemplate.owner_id == user.id,
            models.TaskTemplate.is_active.is_(True),
        )
        .all()
    )

    if not templates:
        return []

    existing_logs: list[models.TaskLog] = (
        db.query(models.TaskLog)
        .filter(
            models.TaskLog.owner_id == user.id,
            models.TaskLog.log_date == target_date,
        )
        .all()
    )

    logs_by_template = {log.template_id: log for log in existing_logs}
    created_logs: list[models.TaskLog] = []

    for template in templates:
        if template.id not in logs_by_template:
            log = models.TaskLog(
                owner_id=user.id,
                template_id=template.id,
                log_date=target_date,
            )
            db.add(log)
            created_logs.append(log)

    if created_logs:
        db.flush()
        existing_logs.extend(created_logs)

    return existing_logs


def _all_completed(logs: Iterable[models.TaskLog]) -> bool:
    return all(log.completed for log in logs)


def complete_task_log(
    db: Session,
    log: models.TaskLog,
    user: models.User,
) -> dict:
    if log.completed:
        return {"already_completed": True, "xp_awarded": log.xp_awarded}

    log.completed = True
    log.completed_at = datetime.utcnow()

    base_xp = log.template.base_xp if log.template else 0
    result = apply_xp(user, base_xp)
    log.xp_awarded = base_xp

    daily_logs: list[models.TaskLog] = (
        db.query(models.TaskLog)
        .filter(
            models.TaskLog.owner_id == user.id,
            models.TaskLog.log_date == log.log_date,
        )
        .all()
    )

    bonus_awarded = False
    if daily_logs and _all_completed(daily_logs):
        bonus_already_given = any(
            dl.xp_awarded
            > (dl.template.base_xp if dl.template and dl.template.base_xp else 0)
            for dl in daily_logs
        )
        if not bonus_already_given:
            bonus = DAILY_COMPLETION_BONUS
            bonus_result = apply_xp(user, bonus)
            log.xp_awarded += bonus
            result["xp_awarded"] += bonus
            result["level_ups"] += bonus_result["level_ups"]
            result["current_xp"] = bonus_result["current_xp"]
            result["level"] = bonus_result["level"]
            result["title"] = bonus_result["title"]
            bonus_awarded = True

    result["bonus_awarded"] = bonus_awarded
    return result
