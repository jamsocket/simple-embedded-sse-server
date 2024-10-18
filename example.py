def send_timestamp_every_second():
    import time
    from jamsocket_embedded_stream_server import EmbeddedEventStreamDB

    db = EmbeddedEventStreamDB()
    while True:
        timestamp = time.time()
        event = {'timestamp': timestamp}
        db.event(event)
        time.sleep(1)

if __name__ == "__main__":
    send_timestamp_every_second()
