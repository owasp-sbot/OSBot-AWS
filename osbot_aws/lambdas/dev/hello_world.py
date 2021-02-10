def run(event, context=None):
    return f"From lambda code, hello {event.get('name')}"