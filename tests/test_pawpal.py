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
