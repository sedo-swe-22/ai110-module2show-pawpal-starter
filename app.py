from datetime import datetime

import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Add pets and tasks below, then generate today's schedule.

The UI is wired to the classes in `pawpal_system.py`: `Owner`, `Pet`, `Task` and `Scheduler`.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Streamlit reruns this script on every interaction, so keep the Owner in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner

st.subheader("Owner & Pets")
owner.name = st.text_input("Owner name", value=owner.name)

with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    breed = st.text_input("Breed", value="Shiba Inu")
    if st.form_submit_button("Add pet") and pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), breed.strip()))

if owner.pets:
    st.write(f"{owner.name}'s pets: " + ", ".join(f"{p.name} ({p.breed})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    selected = st.selectbox("Pet", [p.name for p in owner.pets])
    pet = next(p for p in owner.pets if p.name == selected)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        description = st.text_input("Task", value="Morning walk")
    with col2:
        time = st.text_input("Time (HH:MM)", value="08:00")
    with col3:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            st.error("Time must be in HH:MM format, e.g. 08:00.")
        else:
            pet.add_task(Task(description, time, frequency=frequency, priority=priority))

    rows = [
        {
            "pet": p.name,
            "task": t.description,
            "time": t.time,
            "frequency": t.frequency,
            "priority": t.priority,
            "due": t.due_date,
            "done": t.completed,
        }
        for p in owner.pets
        for t in p.tasks
    ]
    if rows:
        st.write("Current tasks:")
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    todays = scheduler.get_todays_schedule()
    if todays:
        st.table(
            [{"time": t.time, "task": t.description, "priority": t.priority} for t in todays]
        )
    else:
        st.info("Nothing scheduled for today.")
    for warning in scheduler.detect_conflicts():
        st.warning(warning)
