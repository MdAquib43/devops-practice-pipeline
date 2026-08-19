from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import itertools

app = FastAPI(title="Task Tracker API")

# In-memory store (swap for Postgres later if you want a DB rep too)
tasks: dict[int, dict] = {}
_id_counter = itertools.count(1)


class Task(BaseModel):
    title: str
    done: bool = False


class TaskOut(Task):
    id: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks():
    return [TaskOut(id=tid, **t) for tid, t in tasks.items()]


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(task: Task):
    tid = next(_id_counter)
    tasks[tid] = task.dict()
    return TaskOut(id=tid, **tasks[tid])


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut(id=task_id, **tasks[task_id])


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: Task):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id] = task.dict()
    return TaskOut(id=task_id, **tasks[task_id])


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
