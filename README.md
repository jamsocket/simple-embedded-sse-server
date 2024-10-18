# Jamsocket Embedded Stream Server

This library packages a simple embedded stream server.

Clients can connect and receive messages over Server-Sent Events (SSE).

The Server-Sent Events client will handle reconnects, and messages missed during the disconnect will be replayed.

Messages are any valid JSON objects.

## Usage

See `example.py` for a simple example.

```python
from jamsocket_embedded_stream_server import EmbeddedEventStreamDB

db = EmbeddedEventStreamDB()

db.event({"hello": "world"})
```

## Subscribing to the stream

The browser has a built-in `EventSource` client that can connect to the stream. It automatically handles
reconnects.

```javascript
let st = new EventSource("http://localhost:8080/events?since=50"); // show events after event #50
st.onmessage = (e) => console.log(e); // log events to console
```

## Persistence

This does not yet persist data beyond the life of the server process.

If this API is otherwise good, I can add persistence to S3 without changing the API.
