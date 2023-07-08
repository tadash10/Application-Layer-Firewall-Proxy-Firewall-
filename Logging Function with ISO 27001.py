import datetime

def log_event(event):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp}: {event}"
    with open("firewall.log", "a") as log_file:
        log_file.write(log_entry + "\n")
