<p align="center">
  <img src="https://raw.githubusercontent.com/f4rih/celerator/refs/heads/main/celerator_logo.png" alt="Celerator Logo" width="240"/>
</p>

<h1 align="center">Celerator</h1>
<p align="center">
  🔧 Real-time terminal-based Celery task monitor and retry dashboard built with <a href="https://github.com/Textualize/textual">Textual</a>.
</p>

---

## 🚀 What is Celerator?

**Celerator** is a TUI (Text User Interface) application for debugging and monitoring Celery tasks in real time. It connects to your Celery broker (Redis, RabbitMQ, etc.), listens to task lifecycle events, and presents them in an interactive terminal interface — complete with retry capabilities, traceback viewing, and more.

It uses Celery's built-in **event system**, meaning no code changes are required in your app — just run your workers with `--events` enabled.

---

## ✨ Features

- 📡 **Live Event Monitoring**: Captures real-time task data using the Celery event stream
- 🔁 **Retry Failed Tasks**: One-key retry of failed tasks with original or custom arguments
- 🧠 **Detailed Debug Panels**: View args, kwargs, exceptions, and tracebacks
- ⌨️ **Full Keyboard Support**: Efficient, mouse-free task inspection
- 📋 **In-Memory Task Store**: View and scroll through all received tasks
- 🎨 **Styled UI**: Powered by Textual and customizable stylesheets
- ✅ Works with **any Celery-based app**, including Django, Flask, FastAPI, etc.

---

## 📸 Screenshot

> _Replace this with a terminal screenshot of the app_

---

## 📦 Installation

```bash
pip install celerator
```

To use Celerator, you need to start your Celery worker with the `--events` flag enabled to emit task event data:

```bash
celery -A your_project worker --loglevel=info --events
```

Then, in another terminal, launch Celerator with the same broker URI:

```bash
celerator --broker=redis://localhost:6379/0
```


---

## ⌨️ Keyboard Shortcuts

| Key        | Action                        |
|------------|-------------------------------|
| `r`        | Retry selected task           |
| `ctrl+r`   | Retry with custom args        |
| `c`        | Clear task table              |
| `q`        | Quit the app                  |
| `↑` / `↓`  | Navigate task list            |
| `Enter`    | Show traceback / task details |