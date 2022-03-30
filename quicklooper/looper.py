from typing import Optional, List, Any, Dict
import threading


class Looper:
    """
    Implements a simple "polling" style loop, run in a separate thread.

    Extend this class, and override the main method with code to be run every self._interval seconds,
    on_start_up and on_shut_down methods may also be overridden with code to be run once before/after the main loop

    e.g. a simple polling app which monitors a local directory for files to print:
    class PrintMonitor(Looper):
        def __init__(self, directory: str):
            super().__init__(10.0)
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
    """
    _interval = 5.0  # seconds
    _run_before_first_wait = True  # True to run main immediately after start_up, False to wait _interval secs first

    def __init__(self,
                 *args: Any,
                 interval: Optional[float] = None,
                 run_before_first_wait: Optional[bool] = None,
                 start_up_args: Optional[List[Any]] = None,
                 start_up_kwargs: Optional[Dict[str, Any]] = None,
                 shut_down_args: Optional[List[Any]] = None,
                 shut_down_kwargs: Optional[Dict[str, Any]] = None,
                 **kwargs: Any,
                 ):
        if interval is not None:
            self._interval = interval
        if run_before_first_wait is not None:
            self._run_before_first_wait = run_before_first_wait
        self._thread: Optional[threading.Thread] = None
        self._exit_event: Optional[threading.Event] = None
        self._start_up_args = start_up_args or []
        self._start_up_kwargs = start_up_kwargs or {}
        self._shut_down_args = shut_down_args or []
        self._shut_down_kwargs = shut_down_kwargs or {}
        self._main_args = args
        self._main_kwargs = kwargs

    def on_start_up(self, *args, **kwargs):
        """Method called by self.start before starting the main loop.

        Override this method with startup tasks to be completed before main is called for the first time.
        """
        pass

    def on_shut_down(self, *args, **kwargs):
        """Method called by self.stop after the main loop exits

        Override this method with shutdown tasks to be completed to clean up
        """
        pass

    def main(self, *args, **kwargs):
        """Main method called every self._interval seconds by self._tick

        Override this method with code to be run every self._interval seconds
        """
        pass

    def _tick(self) -> None:
        """Runs in the main thread, and calls self.main eery self._interval seconds until self.stop is called

        Do not override this method
        """
        if self._run_before_first_wait:
            self.main(*self._main_args, **self._main_kwargs)
        while True:
            if self._exit_event.wait(timeout=self._interval):
                break
            else:
                self.main(*self._main_args, **self._main_kwargs)

    def start(self) -> None:
        """Call this method to run start up tasks in self.start_up and then begin the main loop
        """
        if self._thread is None:  # avoid starting while already started
            self._exit_event = threading.Event()
            self.on_start_up(*self._start_up_args, **self._start_up_kwargs)
            self._thread = threading.Thread(target=self._tick)
            self._thread.start()

    def stop(self) -> None:
        """Call this method to exit the main loop immediately and run shut down tasks
        """
        if self._exit_event is not None:
            self._exit_event.set()
        self._thread.join()
        self.on_shut_down(*self._shut_down_args, **self._shut_down_kwargs)
        self._exit_event = None
        self._thread = None
