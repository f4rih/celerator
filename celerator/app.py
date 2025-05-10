import ast
import asyncio

from textual.app import App
from textual.binding import Binding
from textual.widgets import DataTable, Header, Footer, Log
from textual.widgets._data_table import RowDoesNotExist
from celerator.broker import retry_task
from celerator.widgets import CustomRetryModalScreen
from celerator.models import TaskRepository
from celerator.utils import convert_args_safely


class CeleryMonitor(App):
    CSS_PATH = "styles/styles.tcss"

    BINDINGS = [
        Binding(key="r", action="", description="Retry Selected Task"),
        Binding(key="ctrl+r", action="custom_task_retry", description="Retry with custom args"),
        Binding(key='c', action='clear_table', description="Clear table data"),
        Binding(key="q", action="quit", description="Quit the app"),
    ]

    def __init__(self, task_queue, broker_uri=None, **kwargs):
        super().__init__(**kwargs)
        self.task_queue = task_queue
        self.broker_uri = broker_uri
        self.added_tasks = set()
        self.title = "Celerator - Debug and Monitor your celery tasks"
        self.task_repo = TaskRepository()

    def compose(self):
        yield Header(show_clock=True)
        self.table = DataTable(classes="table-outline")
        self.table.add_columns("UUID", "Name", "Args", "Kwargs", "State", "Datetime", "ETA")
        self.table.add_column("Exception", width=20)
        self.table.add_column("Traceback", width=20)
        self.table.cursor_type = 'row'
        self.table.zebra_stripes = True
        yield self.table

        self.traceback_panel = Log(highlight=True, classes="outline")
        self.traceback_panel.styles.height = 15
        self.traceback_panel.styles.dock = "bottom"
        self.traceback_panel.styles.margin = (0, 0, 1, 0)
        self.traceback_panel.styles.padding = 1
        self.traceback_panel.write("No traceback available")
        yield self.traceback_panel 

        yield Footer()

    async def on_mount(self):
        self.theme = "dracula"
        self.tracebacks = {}
        asyncio.create_task(self.update_table())

    async def create_retry_task_with_custom_args(self, action, r, k) -> None:
        if action:
            r, k = convert_args_safely(r, k)
            row_key = self.table.cursor_row
            if row_key is not None:
                try:
                    row = self.table.get_row_at(row_key)
                    uuid = row[0]
                    task = self.task_repo.get_retriable_task(uuid)
                    await self.retry_selected_task(
                        task_name=task.name,
                        r=r,
                        k=k,
                        uuid=uuid
                    )
                    self.traceback_panel.write(k)
                    self.traceback_panel.write(r)
                except RowDoesNotExist:
                    self.notify(f"No task is selected.", severity="error")

    async def action_custom_task_retry(self) -> None:
        def apply_retry(data: list):
            action, r, k = data
            asyncio.create_task(self.create_retry_task_with_custom_args(action, r, k)) 
        self.push_screen(CustomRetryModalScreen(), apply_retry)

    async def action_clear_table(self) -> None:
        self.table.clear()
        self.traceback_panel.clear()
        self.traceback_panel.write("No traceback available")
        self.notify("Clearing table done.")

    async def retry_selected_task(self, task_name, r, k, uuid):
        retry_task(
            task_name,
            args=r,
            kwargs=k,
            broker_uri=self.broker_uri
            )
        self.notify(f"Retrying task {uuid}")

    async def on_key(self, event):
        if event.key == "r":
            row_key = self.table.cursor_row
            if row_key is not None:
                try:
                    row = self.table.get_row_at(row_key)
                    uuid = row[0]
                    task = self.task_repo.get_retriable_task(uuid)
                    await self.retry_selected_task(
                        task_name=task.name,
                        r=ast.literal_eval(task.args),
                        k=ast.literal_eval(task.kwargs),
                        uuid=uuid
                    )

                except RowDoesNotExist:
                    self.notify(f"No task is selected.", severity="error")

        elif event.key == "ctrl+q":
            self.exit()


    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        row = self.table.get_row(event.row_key)
        uuid = row[0]
        state_ = row[4]
        traceback_key = f"{uuid}.{state_}"
        traceback = self.task_repo.get_traceback(traceback_key)
        self.traceback_panel.clear()
        self.traceback_panel.write(traceback or "No traceback available")

    async def update_table(self):
        while True:
            while not self.task_queue.empty():
                new_task = self.task_queue.get()
                if new_task.get('uuid'):
                    task = self.task_repo.serialize(new_task)
                    self.task_repo.add(task)

                    # Store tracebacks
                    traceback_key = f"{task.uuid}.{task.state}"
                    self.task_repo.add_traceback(traceback_key, task.traceback)

                    self.table.add_row(
                        task.uuid,
                        task.name,
                        task.args,
                        task.kwargs,
                        task.styled_state,
                        task.timestamp,
                        task.eta,
                        task.styled_exception,
                        task.styled_traceback
                    )
                    if task.state == "RECEIVED":
                        self.task_repo.add_retriable_task(task=task)

            await asyncio.sleep(0.5)
