# Quick Looper

A simple polling style loop, run in a separate thread.

## Installation

Install from PyPI:

    pip install quicklooper

## How to use

Make a class that inherits from the Looper class, and override the `main` method with code to be run each loop.  The loop period may be set by assigning a float value to the class variable `_interval` or by passing the `interval` keyword arg to the `Looper.__init__` method.

Override the `on_start_up` and `on_shut_down` methods to add any code to be run before the first loop, and after the final loop when `stop` is called.

Example of a basic app which polls the `/printfiles` directory for new files to print:

    from quicklooper import Looper


    class PrintMonitor(Looper):
        _interval = 10.0

        def __init__(self, directory: str):
            self.directory: str = directory
            self._printed_files: Set[str] = set()
    
        def on_start_up():
            self._printed_files = {file for file in os.listdir(self.directory)}
    
        def main():
            for file in os.listdir(self.directory):
                send_to_printer(file)  # implementation not shown
                self._printed_files.add(file)


    if __name__ == '__main__':
        print_monitor = PrintMonitor('/printfiles')
        print_monitor.start()


When `print_montitor.start()` is called, the app runs `on_start_up` method, and then calls `main` every 
ten seconds to scan for new files to print.

Call `stop` to exit the loop immediately.