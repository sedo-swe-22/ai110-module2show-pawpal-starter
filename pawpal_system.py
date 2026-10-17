from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import Optional


@dataclass
class Task:
    description: str
    time: str  # "HH:MM"
    frequency: str = "once"  # "once", "daily", or "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    priority: str = "medium"  # "low", "medium", or "high"

    def __post_init__(self) -> None:
        """Normalize time to zero-padded HH:MM and reject invalid times."""
        self.time = datetime.strptime(self.time, "%H:%M").strftime("%H:%M")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner."""
        self.owner = owner

    def get_todays_schedule(self) -> list[Task]:
        """Return today's incomplete tasks, ordered by time then priority."""
        today = date.today()
        tasks = [
            t
            for t in self.owner.get_all_tasks()
            if t.due_date == today and not t.completed
        ]
        return self.sort_by_time(tasks)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks sorted by time, with higher priority first on ties."""
        rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: (t.time, rank.get(t.priority, 1)))

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status.

        pet_name is matched case-insensitively; either filter may be None to skip
        it. Tasks of every due date are included.
        """
        if pet_name is None:
            tasks = self.owner.get_all_tasks()
        else:
            wanted = pet_name.casefold()
            tasks = [
                t
                for p in self.owner.pets
                if p.name.casefold() == wanted
                for t in p.tasks
            ]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> list[str]:
        """Return a warning for each date/time slot holding more than one task.

        Lightweight strategy: group tasks by (due_date, time) in one pass and warn
        about any group larger than one. It covers tasks for the same pet or for
        different pets, never raises, and only matches exact start times (task
        durations are not modelled, so overlapping ranges are not detected).
        """
        slots: defaultdict[tuple[date, str], list[str]] = defaultdict(list)
        for pet in self.owner.pets:
            for t in pet.tasks:
                slots[(t.due_date, t.time)].append(f"{pet.name}: {t.description}")
        return [
            f"Conflict at {time} on {due}: {', '.join(entries)}"
            for (due, time), entries in slots.items()
            if len(entries) > 1
        ]

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """Complete a task and, if recurring, add and return the next occurrence.

        The next due date is max(due_date, today) plus the interval, so a late task
        never spawns an occurrence in the past and an early one keeps its schedule.
        Completing an already-completed task is a no-op, so it never spawns duplicates.
        """
        if task.completed:
            return None
        task.mark_complete()
        days = {"daily": 1, "weekly": 7}.get(task.frequency)
        if days is None:
            return None
        base = max(task.due_date, date.today())
        next_task = replace(
            task, due_date=base + timedelta(days=days), completed=False
        )
        pet.add_task(next_task)
        return next_task
