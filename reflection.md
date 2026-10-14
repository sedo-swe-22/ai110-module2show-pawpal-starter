# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
- owner
    - name, pet
    + add a pet
- pet
    - name, breed, 
    + add/edit task(s)
- task
    - time, priority, preference, frequencies
- scheduler
    + generate a daily schedule/plan
    + display a daily schedule/plan
    + add owner


+ Add Owner + Pet info
+ Add/Edit a task with duration and proirity
+ Generate a daily schedule/plan based on constraints and priorities cleanly

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**Initial UML design**

The design has four classes in a simple chain. An `Owner` has many `Pet`s, and each `Pet` has many `Task`s. A `Scheduler` reads an owner's pets and tasks and produces a daily plan. The data classes (`Owner`, `Pet`, `Task`) only store information. All the scheduling logic sits in one place, `Scheduler`.

**Classes and responsibilities**

- **Owner** holds the owner's name, their `available_minutes` for the day, and their list of pets. The available time is the main constraint the scheduler works within. Its one method, `add_pet`, covers the requirement to enter owner and pet info.
- **Pet** holds the pet's name, breed, and its list of tasks. It manages those tasks through `add_task`, `edit_task` and `remove_task`, so users can add and edit tasks.
- **Task** is a single care activity. It stores the title, duration, priority, preferred time, frequency, and which pet it belongs to. It also stores the scheduler's results, `scheduled_time` and `reason`, so a plan can explain itself.
- **Scheduler** has no state of its own. `generate_schedule(owner)` picks and orders tasks by priority and the owner's available time, and fills in each task's `scheduled_time` and `reason`. `display_schedule(tasks)` shows the plan clearly.

**Design choice:** I kept the scheduling logic out of the data classes so it can change without touching them. I kept the number of classes at four to stay simple. The cost is that `Task` carries both input and output fields, and tasks that didn't fit have nowhere to record why.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The design changed after I reviewed my skeleton against the project requirements. I simplified it to match what the brief asks for:

- **Added to match the requirements:** `Task.completed` and `Task.mark_complete()`, `Task.due_date` for recurring tasks, `Owner.get_all_tasks()`, and Scheduler methods for sorting, filtering, conflict detection and completing recurring tasks. The Scheduler now holds an `Owner` and reads every pet's tasks through `get_all_tasks()`.
- **Removed:** `Owner.available_minutes`, `Task.preferred_time`, `Task.scheduled_time`, `Task.reason`, `Task.duration_minutes` and `Scheduler.generate_schedule` and `display_schedule`. A time-budget scheduler with explanations was more complex than the project needs, which schedules by exact `"HH:MM"` time.
- **Removed `Task.pet`:** the two-way link between `Task` and `Pet` was hard to keep in sync. The Scheduler can find a task's pet while looping over `owner.pets`.
- **Kept to four classes:** every feature fits in `Task`, `Pet`, `Owner` or `Scheduler`, so extra classes such as a plan or priority class were unnecessary. `priority` stays a plain attribute on `Task`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code across the whole workflow rather than for one step:

- **Design:** turning my UML into class skeletons, then reviewing those skeletons against the project requirements.
- **Implementation:** filling in the `Task`, `Pet`, `Owner` and `Scheduler` logic and a CLI demo (`main.py`).
- **Tests and docs:** drafting two simple unit tests, adding one-line docstrings to every method, and writing the README implementation summary.

The most helpful prompts were small and specific, such as "draft two simple tests: task completion and task addition", or "add 1-line docstrings to the methods". Each one gave a short result I could read in full. Asking the AI to review my skeleton against the requirements was also useful, because it surfaced where my first design had drifted from what the brief asked for.

**b. Judgment and verification**

- **What the AI suggested:** my first UML was a time-budget scheduler. It had `Owner.available_minutes`, `Task.duration_minutes`, `scheduled_time` and `reason` fields, and `generate_schedule` / `display_schedule` methods that would pick tasks by priority and explain the plan. The requirements review pointed out that this was more than the project needs, and that the project schedules by exact `"HH:MM"` time.
- **What I accepted:** removing those fields and methods, and adding `Task.completed`, `Task.due_date`, `Owner.get_all_tasks()` and the Scheduler's sorting, filtering, conflict-detection and recurrence methods.
- **What I rejected:** adding extra classes (a plan class, a priority class). Every feature fits in the four existing classes, so `priority` stays a plain attribute on `Task`. I also dropped the two-way `Task.pet` link because it was hard to keep in sync with `Pet.tasks`.
- **How I verified it:**
  - I ran the CLI demo in `main.py`, which exercises today's schedule, a deliberate 08:00 conflict between two pets, and a daily task being completed and rescheduled.
  - I ran the two unit tests with `python -m pytest tests/ -v` (both pass). They check that `mark_complete()` changes a task's status and that `add_task()` increases a pet's task count.
  - After the docstring pass, I re-ran the tests to confirm nothing changed in behavior.
  - I checked the generated docstrings and README summary against the code, since they should describe what the methods actually do.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
