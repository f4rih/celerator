from textual.screen import ModalScreen
from textual.widgets import Input, Button
from textual.containers import Grid

class CustomRetryModalScreen(ModalScreen[list]):
    def compose(self):
        yield Grid(
            Input(placeholder="Args: arg1, arg2", id="args"),
            Input(placeholder="Kwargs: a=1, b=2", id="kwargs"),
            Button("Apply", variant="success", id="apply"),
            Button("Cancel", variant="error", id="cancel"),
            id="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply":
            self.dismiss([True, 
                          self.query_one("#args", Input).value,
                          self.query_one("#kwargs", Input).value])
        elif event.button.id == "cancel":
            self.dismiss([False, "", ""])

    def on_key(self, event):
        if event.key == 'escape':
            self.dismiss([False, "", ""])
