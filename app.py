import streamlit as st
import json
import os

DATA_FILE = "/app-data/todos.json"

# Ensure data folder exists
os.makedirs("/app-data", exist_ok=True)

# Load todos
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        todos = json.load(f)
else:
    todos = []

st.title("Simple TODO App")

new_todo = st.text_input("Add a new TODO")
if st.button("Add"):
    if new_todo:
        todos.append(new_todo)
        with open(DATA_FILE, "w") as f:
            json.dump(todos, f)
        st.rerun()

st.write("Your TODOs:")
for t in todos:
    st.write("-", t)