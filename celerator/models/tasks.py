from dataclasses import dataclass
from datetime import datetime

from rich.text import Text

@dataclass
class Task:
    uuid: str
    name: str
    args: str
    kwargs: str
    state: str
    styled_state: str
    exception: str
    styled_exception: str 
    traceback: str
    styled_traceback: str
    eta: str
    timestamp: str

@dataclass
class RetriableTask:
    uuid: str
    name: str
    args: str
    kwargs: str



class TaskRepository:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._tracebacks: dict[str, str] = {}
        self._retriable_tasks: dict[str, RetriableTask] = {}

    def add(self, task: Task):
        self._tasks[task.uuid] = task

    def add_traceback(self, key: str, traceback: str) -> None:
        self._tracebacks[key] = traceback

    def get_traceback(self, key: str) -> str | None:
        traceback = self._tracebacks.get(key)
        return traceback
    
    def add_retriable_task(self, task: Task) -> None:
        self._retriable_tasks[task.uuid] = RetriableTask(
            uuid=task.uuid,
            name=task.name,
            args=task.args,
            kwargs=task.kwargs
        )

    def get_retriable_task(self, uuid: str) -> RetriableTask | None:
        return self._retriable_tasks.get(uuid)

    def find_by_uuid(self, uuid: str) -> Task | None:
        return self._tasks.get(uuid)

    def all(self) -> list[Task]:
        return list(self._tasks.values())

    def clear(self):
        self._tasks.clear()

    def serialize(self, task: dict) -> Task | None:
        uuid = task['uuid']
        if uuid:
            # Get the current timestamp as formatted string
            # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamp = task['timestamp']
            ts_to_dt = datetime.fromtimestamp(timestamp)
            formatted_dt = ts_to_dt.strftime("%Y-%m-%d %H:%M:%S")

            # Determine color based on state
            state = task['state'] or ""
            color = {
                "RECEIVED": "black on yellow",
                "STARTED": "black on cyan",
                "SUCCESS": "black on green",
                "FAILURE": "black on red"
            }.get(state.upper(), "white")


            # Create styled Text object for state
            state_text = Text(state, style=color)
            exception = task.get('exception') or ""
            exception_text = Text(exception, style="red" if exception else "white")

            traceback = task.get('traceback') or ""
            traceback_preview = (traceback[:15] + "...") if len(traceback) > 20 else traceback

            eta = task.get('eta')
            if eta is not None:
                dt = datetime.fromisoformat(eta)
                eta = dt.strftime("%Y-%m-%d %H:%M:%S")

            return Task(
                    uuid=uuid,
                    name=task['name'] or "",
                    args=str(task['args']) or "",
                    kwargs=str(task['kwargs']) or "",
                    state=state,
                    styled_state=state_text,
                    exception=exception_text,
                    styled_exception=exception_text,
                    traceback=task.get('traceback') or "",
                    styled_traceback=traceback_preview,
                    eta=eta,
                    timestamp=formatted_dt,
            )

        return None