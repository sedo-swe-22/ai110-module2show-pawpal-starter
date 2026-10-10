from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    preferred_time: Optional[str] = None
    frequency: Optional[str] = None
    pet: Optional[Pet] = None
    scheduled_time: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class Pet:
    name: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, title: str, updates: dict) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass


class Scheduler:
    def generate_schedule(self, owner: Owner) -> list[Task]:
        pass

    def display_schedule(self, tasks: list[Task]) -> None:
        pass
