from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    description: str
    time: str  # "HH:MM"
    frequency: str = "once"  # "once", "daily", or "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    priority: str = "medium"  # "low", "medium", or "high"

    def mark_complete(self) -> None:
        self.completed = True


@dataclass
class Pet:
    name: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_todays_schedule(self) -> list[Task]:
        today = date.today()
        tasks = [
            t
            for t in self.owner.get_all_tasks()
            if t.due_date == today and not t.completed
        ]
        return self.sort_by_time(tasks)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> list[Task]:
        if pet_name is None:
            tasks = self.owner.get_all_tasks()
        else:
            tasks = [t for p in self.owner.pets if p.name == pet_name for t in p.tasks]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> list[str]:
        slots: dict[tuple[date, str], list[str]] = {}
        for t in self.owner.get_all_tasks():
            slots.setdefault((t.due_date, t.time), []).append(t.description)
        return [
            f"Conflict at {time} on {due}: {', '.join(names)}"
            for (due, time), names in slots.items()
            if len(names) > 1
        ]

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        task.mark_complete()
        days = {"daily": 1, "weekly": 7}.get(task.frequency)
        if days is None:
            return None
        next_task = replace(
            task, due_date=task.due_date + timedelta(days=days), completed=False
        )
        pet.add_task(next_task)
        return next_task
