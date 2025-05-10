from celery import Celery
from celery import signature
from celery.events import EventReceiver
from celery.events.state import State


app_celery = None
state = State()

def set_broker_uri(uri):
    global app_celery
    app_celery = Celery('celerator', broker=uri)

def retry_task(task_name, args=None, kwargs=None, broker_uri=None):
    global app_celery
    if app_celery is None:
        if broker_uri is None:
            raise RuntimeError("Celery app is not initialized and no broker URI was provided.")
        set_broker_uri(broker_uri)
    sig = signature(task_name, args=args, kwargs=kwargs)
    sig.apply_async()

def event_worker(queue, broker_uri):
    set_broker_uri(broker_uri)
    def event_handler(event):
        state.event(event)
        # Push relevant info to queue
        queue.put({
            'uuid': event.get('uuid'),
            'name': event.get('name'),
            'args': event.get('args'),
            'kwargs': event.get('kwargs'),
            'state': event.get('state'),
            'exception': event.get('exception'),
            'traceback': event.get('traceback'),
            'eta': event.get('eta'),
            'timestamp': event.get('timestamp'),
        })

    with app_celery.connection() as connection:
        recv = EventReceiver(connection, handlers={'*': event_handler})
        recv.capture(limit=None, timeout=None, wakeup=True)

