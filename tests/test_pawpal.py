from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task(description="Walk", time="08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", breed="Corgi")
    before = len(pet.tasks)
    pet.add_task(Task(description="Feed", time="09:00"))
    assert len(pet.tasks) == before + 1


from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Scheduler


def make_scheduler():
    owner = Owner(name="Sam")
    buddy = Pet(name="Buddy", breed="Lab")
    mia = Pet(name="Mia", breed="Tabby")
    owner.add_pet(buddy)
    owner.add_pet(mia)
    return Scheduler(owner), buddy, mia


def test_time_is_normalized_so_sorting_is_correct():
    sched, buddy, _ = make_scheduler()
    late = Task("Dinner", "18:00")
    early = Task("Walk", "9:00")
    assert early.time == "09:00"
    assert [t.description for t in sched.sort_by_time([late, early])] == ["Walk", "Dinner"]


@pytest.mark.parametrize("bad", ["25:00", "12:60", "noon", ""])
def test_invalid_time_is_rejected(bad):
    with pytest.raises(ValueError):
        Task("Walk", bad)


def test_sort_breaks_time_ties_by_priority():
    sched, _, _ = make_scheduler()
    low = Task("Brush", "08:00", priority="low")
    high = Task("Meds", "08:00", priority="high")
    med = Task("Feed", "08:00")
    assert sched.sort_by_time([low, med, high]) == [high, med, low]


def test_filter_by_pet_name_is_case_insensitive():
    sched, buddy, mia = make_scheduler()
    walk = Task("Walk", "08:00")
    buddy.add_task(walk)
    mia.add_task(Task("Feed", "09:00"))
    assert sched.filter_tasks(pet_name="bUDdy") == [walk]
    assert sched.filter_tasks(pet_name="nobody") == []


def test_filter_by_completed_status():
    sched, buddy, _ = make_scheduler()
    done, pending = Task("Walk", "08:00"), Task("Feed", "09:00")
    buddy.add_task(done)
    buddy.add_task(pending)
    done.mark_complete()
    assert sched.filter_tasks(completed=True) == [done]
    assert sched.filter_tasks(pet_name="Buddy", completed=False) == [pending]


def test_daily_task_spawns_next_day():
    sched, buddy, _ = make_scheduler()
    task = Task("Walk", "08:00", frequency="daily")
    buddy.add_task(task)
    nxt = sched.mark_task_complete(buddy, task)
    assert nxt.due_date == task.due_date + timedelta(days=1)
    assert nxt.completed is False


def test_completing_twice_does_not_duplicate_recurring_task():
    sched, buddy, _ = make_scheduler()
    task = Task("Walk", "08:00", frequency="weekly")
    buddy.add_task(task)
    assert sched.mark_task_complete(buddy, task) is not None
    assert sched.mark_task_complete(buddy, task) is None
    assert len(buddy.tasks) == 2


def test_once_task_does_not_recur():
    sched, buddy, _ = make_scheduler()
    task = Task("Vet", "14:00")
    buddy.add_task(task)
    assert sched.mark_task_complete(buddy, task) is None
    assert len(buddy.tasks) == 1


def test_detect_conflicts_across_pets():
    sched, buddy, mia = make_scheduler()
    buddy.add_task(Task("Walk", "08:00"))
    mia.add_task(Task("Feed", "08:00"))
    mia.add_task(Task("Brush", "09:00"))
    conflicts = sched.detect_conflicts()
    assert len(conflicts) == 1 and "Walk" in conflicts[0] and "Feed" in conflicts[0]


def test_no_conflict_on_different_dates():
    sched, buddy, _ = make_scheduler()
    buddy.add_task(Task("Walk", "08:00"))
    buddy.add_task(Task("Walk", "08:00", due_date=date.today() + timedelta(days=1)))
    assert sched.detect_conflicts() == []


def test_daily_due_today_recurs_tomorrow():
    sched, buddy, _ = make_scheduler()
    task = Task("Walk", "08:00", frequency="daily")
    buddy.add_task(task)
    assert sched.mark_task_complete(buddy, task).due_date == date.today() + timedelta(days=1)


def test_weekly_due_today_recurs_in_seven_days():
    sched, buddy, _ = make_scheduler()
    task = Task("Groom", "10:00", frequency="weekly")
    buddy.add_task(task)
    assert sched.mark_task_complete(buddy, task).due_date == date.today() + timedelta(days=7)


def test_late_daily_task_recurs_from_today_not_the_past():
    sched, buddy, _ = make_scheduler()
    task = Task("Walk", "08:00", frequency="daily", due_date=date.today() - timedelta(days=3))
    buddy.add_task(task)
    assert sched.mark_task_complete(buddy, task).due_date == date.today() + timedelta(days=1)


def test_early_completion_keeps_future_schedule():
    sched, buddy, _ = make_scheduler()
    tomorrow = date.today() + timedelta(days=1)
    task = Task("Walk", "08:00", frequency="daily", due_date=tomorrow)
    buddy.add_task(task)
    assert sched.mark_task_complete(buddy, task).due_date == tomorrow + timedelta(days=1)


def test_conflict_for_same_pet_names_the_pet():
    sched, buddy, _ = make_scheduler()
    buddy.add_task(Task("Walk", "08:00"))
    buddy.add_task(Task("Bath", "08:00"))
    (warning,) = sched.detect_conflicts()
    assert "Buddy: Walk" in warning and "Buddy: Bath" in warning
