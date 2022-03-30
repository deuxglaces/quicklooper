from typing import Iterator
import collections
import itertools
import time
import unittest

from quicklooper import Looper


class Counter:
    """Simple Counter class has attribute self.count that starts at 0, and is incremented by 1 on each call to
    self.increment"""
    def __init__(self):
        self.count = 0

    def reset(self):
        self.count = 0

    def increment(self):
        self.count += 1


class MessageQueue:
    """Simple MessageQueue class with push and pop methods for str messages
    Raises IndexError if pop is called when MessageQueue is empty
    """
    def __init__(self):
        self._messages = collections.deque()

    def push(self, msg: str) -> None:
        self._messages.append(msg)

    def pop(self) -> str:
        return self._messages.popleft()


class TestLooper(unittest.TestCase):
    def test_interval_with_run_before_first_wait(self):
        counter = Counter()

        class CounterLooper(Looper):
            def main(self):
                counter.increment()

        counter_looper = CounterLooper(interval=0.1)
        # runs loop once immediately, because run_before_first_wait == True (default)
        counter_looper.start()
        # give time to complete 4 additional loops
        time.sleep(0.45)
        counter_looper.stop()
        # loop has completed 5 times
        self.assertEqual(5, counter.count)

    def test_interval_without_run_before_first_wait(self):
        counter = Counter()

        class CounterLooper(Looper):
            _interval = 0.1

            def main(self):
                counter.increment()

        counter.reset()
        counter_looper = CounterLooper(run_before_first_wait=False)
        # does not run loop immediately, because run_before_first_wait == False
        counter_looper.start()
        # give time to complete 4 loops
        time.sleep(0.45)
        counter_looper.stop()
        # loop has completed 4 times
        self.assertEqual(4, counter.count)

    def test_on_startup(self):
        hit_counter = Counter()
        loop_counter = Counter()

        class CounterLooper(Looper):
            def on_start_up(self, *args, **kwargs):
                hit_counter.increment()

            def main(self):
                loop_counter.increment()

        counter_looper = CounterLooper(interval=0.1)
        # calls counter_looper.on_start_up, calls main once immediately, and then enters loop
        counter_looper.start()
        # give time to allow for 4 loops
        time.sleep(0.45)
        counter_looper.stop()
        # hit_counter incremented once on startup
        self.assertEqual(1, hit_counter.count)
        # loop has completed 5 times
        self.assertEqual(5, loop_counter.count)

    def test_on_startup_with_args(self):
        hit_counter = Counter()
        loop_counter = Counter()

        class CounterLooper(Looper):
            def on_start_up(self, increment_by: int):
                for _ in range(increment_by):
                    hit_counter.increment()

            def main(self):
                loop_counter.increment()

        counter_looper = CounterLooper(interval=0.1, start_up_args=[10])
        # calls counter_looper.on_start_up, calls main once immediately, and then enters loop
        counter_looper.start()
        # give time to allow for 4 loops
        time.sleep(0.45)
        counter_looper.stop()
        # hit_counter incremented 10 times on startup
        self.assertEqual(10, hit_counter.count)
        # loop has completed 5 times
        self.assertEqual(5, loop_counter.count)

    def test_on_startup_with_kwargs(self):
        hit_counter = Counter()
        loop_counter = Counter()

        class CounterLooper(Looper):
            def on_start_up(self, increment_by: int, some_counter: Counter):
                for _ in range(increment_by):
                    some_counter.increment()

            def main(self):
                loop_counter.increment()

        counter_looper = CounterLooper(interval=0.1, start_up_args=[10], start_up_kwargs={'some_counter': hit_counter})
        # calls counter_looper.on_start_up, calls main once immediately, and then enters loop
        counter_looper.start()
        # give time to allow for 4 loops
        time.sleep(0.45)
        counter_looper.stop()
        # hit_counter incremented 10 times on startup
        self.assertEqual(10, hit_counter.count)
        # loop has completed 5 times
        self.assertEqual(5, loop_counter.count)

    def test_on_shutdown(self):
        hit_counter = Counter()
        loop_counter = Counter()

        class CounterLooper(Looper):
            def on_start_up(self):
                hit_counter.increment()

            def main(self):
                loop_counter.increment()

            def on_shut_down(self):
                hit_counter.reset()

        counter_looper = CounterLooper(interval=0.1)
        # calls counter_looper.on_start_up, calls main once immediately, and then enters loop
        counter_looper.start()
        # hit_counter incremented on startup
        self.assertEqual(1, hit_counter.count)
        # give time to allow for 4 loops
        time.sleep(0.45)
        # calls on_shut_down
        counter_looper.stop()
        # hit_counter was reset on shutdown
        self.assertEqual(0, hit_counter.count)
        self.assertEqual(5, loop_counter.count)

    def test_on_shutdown_with_args(self):
        loop_counter = Counter()
        msg_queue = MessageQueue()

        class CounterLooper(Looper):
            def main(self):
                loop_counter.increment()

            def on_shut_down(self, msg: str):
                msg_queue.push(msg)

        counter_looper = CounterLooper(interval=0.2, shut_down_args=['Finished!'])
        # calls counter_looper.on_start_up, calls main once immediately, and then enters loop
        counter_looper.start()
        # assert the message queue is empty
        self.assertRaises(IndexError, msg_queue.pop)
        # give time to allow for 4 loops
        time.sleep(0.85)
        # calls on_shut_down
        counter_looper.stop()
        self.assertEqual(5, loop_counter.count)
        # msg was added to queue on shutdown
        self.assertEqual('Finished!', msg_queue.pop())

    def test_on_shutdown_with_kwargs(self):
        loop_counter = Counter()
        msg_queue = MessageQueue()

        class CounterLooper(Looper):
            def main(self):
                loop_counter.increment()

            def on_shut_down(self, queue: MessageQueue, msg: str):
                queue.push(msg)

        kw = {'msg': 'All done!', 'queue': msg_queue}
        counter_looper = CounterLooper(interval=0.1, shut_down_kwargs=kw)
        # calls counter_looper.on_start_up, calls main once immediately, and then enters loop
        counter_looper.start()
        # assert the message queue is empty
        self.assertRaises(IndexError, msg_queue.pop)
        # give time to allow for 4 loops
        time.sleep(0.45)
        # calls on_shut_down
        counter_looper.stop()
        self.assertEqual(5, loop_counter.count)
        # msg was added to queue on shutdown
        self.assertEqual('All done!', msg_queue.pop())

    def test_with_main_args(self):

        def message_generator():
            msg_count = itertools.count(1)
            while True:
                yield f'Message {next(msg_count)}'

        class MessageLooper(Looper):
            _interval = 0.2

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.message_queue = MessageQueue()

            def main(self, get_msg: Iterator):
                self.message_queue.push(next(get_msg))

        message_looper = MessageLooper(message_generator())
        message_looper.start()
        time.sleep(0.9)
        message_looper.stop()
        # msg was added to queue each loop
        self.assertEqual('Message 1', message_looper.message_queue.pop())
        self.assertEqual('Message 2', message_looper.message_queue.pop())
        self.assertEqual('Message 3', message_looper.message_queue.pop())
        self.assertEqual('Message 4', message_looper.message_queue.pop())
        self.assertEqual('Message 5', message_looper.message_queue.pop())
        self.assertRaises(IndexError, message_looper.message_queue.pop)

    def test_with_main_kwargs(self):

        def message_generator():
            msg_count = itertools.count(1)
            while True:
                yield f'Message {next(msg_count)}'

        class MessageLooper(Looper):
            _interval = 0.2

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.message_queue = MessageQueue()

            def main(self, get_msg: Iterator):
                self.message_queue.push(next(get_msg))

        message_looper = MessageLooper(get_msg=message_generator())
        message_looper.start()
        time.sleep(0.9)
        message_looper.stop()
        # msg was added to queue each loop
        self.assertEqual('Message 1', message_looper.message_queue.pop())
        self.assertEqual('Message 2', message_looper.message_queue.pop())
        self.assertEqual('Message 3', message_looper.message_queue.pop())
        self.assertEqual('Message 4', message_looper.message_queue.pop())
        self.assertEqual('Message 5', message_looper.message_queue.pop())
        self.assertRaises(IndexError, message_looper.message_queue.pop)
