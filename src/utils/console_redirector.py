"""
Console Redirector
Redirects stdout/stderr to a queue for display in the console widget
"""

class ConsoleRedirector:
    """Class to redirect stdout/stderr to a queue for display in the console widget"""
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass
