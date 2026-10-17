# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation summary

The core logic lives in `pawpal_system.py` (no UI dependencies), with `main.py` as a CLI demo and `tests/test_pawpal.py` for unit tests.

- **`Task`**: a dataclass for one care item (description, `"HH:MM"` time, frequency of `once`/`daily`/`weekly`, due date, priority, completed flag). `mark_complete()` sets its status.
- **`Pet`**: a dataclass that owns a list of `Task`s and exposes `add_task()` / `remove_task()`.
- **`Owner`**: a dataclass that owns a list of `Pet`s. `get_all_tasks()` flattens every pet's tasks into one list.
- **`Scheduler`**: takes an `Owner` and works over `owner.get_all_tasks()`. It builds today's schedule (incomplete tasks due today, sorted by time), filters by pet and/or completion, detects conflicts (tasks sharing a date and time), and handles recurrence: `mark_task_complete()` completes a task and, for `daily`/`weekly` tasks, adds a copy due 1 or 7 days later to the pet.

Flow: `Owner` → has many `Pet` → has many `Task`; `Scheduler` reads across that hierarchy and is the only class that makes scheduling decisions.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py` (tasks added out of order, then sorted, checked for conflicts, completed and filtered):

```
As added (unsorted):
  14:30  Vet visit     [todo]
  08:00  Walk          [todo]
  18:00  Evening play  [todo]
  08:00  Feed          [todo]
  07:15  Brush         [todo]
  09:00  Medication    [todo]
  09:00  Play          [todo]

Sorted by time:
  07:15  Brush         [todo]
  08:00  Feed          [todo]
  08:00  Walk          [todo]
  09:00  Medication    [todo]
  09:00  Play          [todo]
  14:30  Vet visit     [todo]
  18:00  Evening play  [todo]

Today's schedule:
  07:15  Brush         [todo]
  08:00  Feed          [todo]
  08:00  Walk          [todo]
  09:00  Medication    [todo]
  09:00  Play          [todo]
  14:30  Vet visit     [todo]
  18:00  Evening play  [todo]

Conflicts:
  Conflict at 08:00 on 2026-10-16: Rex: Walk, Mia: Feed
  Conflict at 09:00 on 2026-10-16: Mia: Medication, Mia: Play

Completed 'Walk'; next due 2026-10-17

Filtered: pet 'rex' (case-insensitive):
  14:30  Vet visit     [todo]
  08:00  Walk          [done]
  18:00  Evening play  [todo]
  08:00  Walk          [todo]

Filtered: completed:
  08:00  Walk          [done]

Filtered: Rex, pending:
  14:30  Vet visit     [todo]
  18:00  Evening play  [todo]
  08:00  Walk          [todo]
```

## 🧪 Testing PawPal+

Run the full suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`, 47 tests):

- **Sorting:** chronological order, zero-padded time normalization, priority tie-breaks, stable order, empty input and `00:00`/`23:59` boundaries.
- **Filtering:** by pet (case-insensitive), by completion status, by both, and for pets or owners with no tasks.
- **Recurring tasks:** daily (+1 day) and weekly (+7 days) next occurrences, late and early completion, chained and repeated completion, and month, year and leap-day rollover.
- **Conflict detection:** same pet, different pets, three-way clashes, separate clashes, different dates, and completed tasks ignored.
- **Today's schedule and validation:** only open tasks due today appear; invalid time, frequency and priority raise `ValueError`.

Sample output of a successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/soh/Documents/personal/learning/codepath/ai110-module2show-pawpal-starter
plugins: platformdirs-4.12.3, anyio-4.15.1
collected 47 items

tests/test_pawpal.py ...............................................     [100%]

============================== 47 passed in 0.04s ==============================
```

**Confidence level: ★★★★☆ (4/5).** All 47 tests pass and cover each scheduling rule, including the date edge cases. I stop at four stars because conflicts only compare exact start times (no durations) and the Streamlit UI has no automated tests.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.get_todays_schedule()` | Sorts by `"HH:MM"` (times are normalized to zero-padded form in `Task.__post_init__`, invalid times raise `ValueError`); ties go to the higher priority. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Filter by pet name (case-insensitive), completion status, or both. |
| Conflict handling | `Scheduler.detect_conflicts()` | One pass groups open (not completed) tasks by date and time and returns a warning string per clash, naming each pet. Works for one pet or several; it never raises. Only exact start times are compared, not durations. |
| Recurring tasks | `Scheduler.mark_task_complete()` | Completing a `daily`/`weekly` task adds a copy due `max(due_date, today)` + 1 or 7 days (`timedelta`). Completing a task twice does not duplicate it. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Run `streamlit run app.py`.
2. Enter the owner name and add one or more pets (name and breed).
3. Pick a pet and add tasks with a description, an `HH:MM` time, a frequency (`once`, `daily`, `weekly`) and a priority. Malformed times are rejected.
4. Review the task table and today's schedule, which is sorted by time (higher priority first on ties).
5. Check the conflict warnings; two tasks at the same date and time are flagged, for the same pet or different pets.
6. Mark a recurring task complete and see its next occurrence appear on its new due date.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
