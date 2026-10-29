import streamlit as st
import json
import os
from datetime import date, datetime

# --- Configuración de la página ---
st.set_page_config(page_title="Simple TODO App", page_icon="✅", layout="centered")

DATA_FILE = "/app-data/todos.json"

# Asegura que exista la carpeta de datos
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


def load_todos():
    """Carga los TODOs desde el JSON y migra el formato antiguo (lista de strings)."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    todos = []
    for item in raw:
        if isinstance(item, str):
            # Formato antiguo: solo texto, sin fechas
            todos.append({
                "id": datetime.now().timestamp(),
                "text": item,
                "created": date.today().isoformat(),
                "due": None,
            })
        else:
            todos.append(item)
    return todos


def save_todos(todos):
    """Guarda los TODOs en el JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def due_status(due_str):
    """Devuelve (etiqueta, icono) según la fecha límite."""
    if not due_str:
        return "Sin fecha límite", "⚪"
    days = (date.fromisoformat(due_str) - date.today()).days
    if days < 0:
        return f"Vencida hace {-days} día(s)", "🔴"
    if days == 0:
        return "Vence hoy", "🟠"
    if days <= 3:
        return f"Vence en {days} día(s)", "🟡"
    return f"Vence en {days} día(s)", "🟢"


todos = load_todos()

# --- Cabecera ---
st.title("✅ Simple TODO App")
st.caption("Organiza tus tareas con fecha de creación y fecha límite.")

# --- Formulario para añadir tareas ---
with st.form("add_form", clear_on_submit=True):
    new_todo = st.text_input("Nueva tarea", placeholder="¿Qué tienes que hacer?")
    col1, col2 = st.columns([2, 1])
    with col1:
        has_due = st.checkbox("Establecer fecha límite", value=True)
    with col2:
        due_date = st.date_input("Fecha límite", value=date.today(), min_value=date.today())
    submitted = st.form_submit_button("➕ Añadir", use_container_width=True)

if submitted:
    if new_todo.strip():
        todos.append({
            "id": datetime.now().timestamp(),
            "text": new_todo.strip(),
            "created": date.today().isoformat(),
            "due": due_date.isoformat() if has_due else None,
        })
        save_todos(todos)
        st.toast("Tarea añadida", icon="✅")
        st.rerun()
    else:
        st.warning("Escribe una descripción para la tarea.")

st.divider()

# --- Lista de tareas ---
if not todos:
    st.info("No tienes tareas pendientes. ¡Añade la primera! 🎉")
else:
    # Ordenar: primero las que tienen fecha límite más cercana; sin fecha al final
    todos_sorted = sorted(todos, key=lambda t: (t["due"] is None, t["due"] or ""))

    # Métricas rápidas
    overdue = sum(
        1 for t in todos if t["due"] and date.fromisoformat(t["due"]) < date.today()
    )
    m1, m2 = st.columns(2)
    m1.metric("Total de tareas", len(todos))
    m2.metric("Vencidas", overdue)

    st.subheader("Tus TODOs")
    for t in todos_sorted:
        label, icon = due_status(t["due"])
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"**{t['text']}**")
                st.caption(
                    f"📅 Creada: {t['created']}  |  "
                    f"⏰ Límite: {t['due'] or '—'}  |  {icon} {label}"
                )
            with c2:
                if st.button("🗑️", key=f"del_{t['id']}", help="Eliminar tarea"):
                    todos = [x for x in todos if x["id"] != t["id"]]
                    save_todos(todos)
                    st.toast("Tarea eliminada", icon="🗑️")
                    st.rerun()