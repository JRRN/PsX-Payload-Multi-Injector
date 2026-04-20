import threading


def start_daemon_thread(target):
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread
