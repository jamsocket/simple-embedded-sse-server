import threading
import queue
from flask import Flask, Response, stream_with_context, request
from collections import deque
import structlog
from waitress import serve

logger = structlog.get_logger()

app = Flask(__name__)

class EmbeddedEventStreamDB:
    def __init__(self, max_event_history=400):
        self.clients = []
        self.lock = threading.Lock()
        self.event_history = deque(maxlen=max_event_history)
        self.event_id = 0

        # Start the HTTP server in a separate thread
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def run_server(self):
        @app.route('/events')
        def events():
            def gen():
                try:
                    q = queue.Queue()
                    with self.lock:
                        self.clients.append(q)
                    
                    # Retrieve 'since' parameter or 'Last-Event-ID' header
                    since_id = request.args.get('since')
                    if since_id is None:
                        since_id = request.headers.get('Last-Event-ID')

                    if since_id is not None:
                        try:
                            since_id = int(since_id)
                        except ValueError:
                            since_id = None  # Invalid since_id provided
                    
                    # Send past events since 'since_id'
                    with self.lock:
                        if since_id is not None:
                            past_events = [event for event in self.event_history if event['id'] > since_id]
                        else:
                            past_events = list(self.event_history)
                    for event in past_events:
                        yield f"id: {event['id']}\ndata: {event['data']}\n\n"

                    # Send new events as they arrive
                    while True:
                        event = q.get()
                        yield f"id: {event['id']}\ndata: {event['data']}\n\n"
                except GeneratorExit:
                    # Clean up client queue on disconnect
                    with self.lock:
                        self.clients.remove(q)

            return Response(stream_with_context(gen()), mimetype='text/event-stream')

        serve(app, host='0.0.0.0', port=8080)

    def event(self, event_data):
        # Increment event ID and store event in history
        with self.lock:
            self.event_id += 1
            event = {'id': self.event_id, 'data': event_data}
            logger.info("received event", data=event)
            self.event_history.append(event)
            # Send the event to all connected clients
            for client_queue in self.clients:
                client_queue.put(event)
