from pawpal_system import Owner, Pet, Scheduler, Task

owner = Owner("Sam")
rex = Pet("Rex", "Labrador")
mia = Pet("Mia", "Siamese")
owner.add_pet(rex)
owner.add_pet(mia)

walk = Task("Walk", "08:00", frequency="daily")
rex.add_task(walk)
rex.add_task(Task("Vet visit", "14:30"))
mia.add_task(Task("Feed", "08:00"))  # conflicts with Rex's walk
mia.add_task(Task("Brush", "07:15", frequency="weekly"))

scheduler = Scheduler(owner)

print("Today's schedule:")
for t in scheduler.get_todays_schedule():
    print(f"  {t.time}  {t.description}")

print("\nConflicts:")
for warning in scheduler.detect_conflicts():
    print(f"  {warning}")

nxt = scheduler.mark_task_complete(rex, walk)
print(f"\nCompleted 'Walk'; next due {nxt.due_date}")
print("Rex's pending tasks:", [t.description for t in scheduler.filter_tasks("Rex", completed=False)])
