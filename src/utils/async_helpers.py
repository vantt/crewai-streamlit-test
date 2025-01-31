# src/utils/async_helpers.py
import asyncio
import functools
import threading
from typing import Any, Callable, Coroutine, TypeVar, cast
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')

def run_async(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """
    Decorator to run async functions in synchronous context.
    Useful for bridging async and sync code in Streamlit.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            try:
                # Clean up any remaining tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
            except Exception:
                pass

    return wrapper

class AsyncToSync:
    """
    Context manager to run async code in a synchronous context.
    Handles proper setup and teardown of event loop.
    """
    def __init__(self):
        self.loop = None
        self._thread_id = None
        self._old_loop = None

    def __enter__(self):
        self._thread_id = threading.get_ident()
        try:
            self._old_loop = asyncio.get_event_loop()
        except RuntimeError:
            self._old_loop = None
            
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        return self.loop

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.loop and threading.get_ident() == self._thread_id:
            try:
                # Clean up any remaining tasks
                pending = asyncio.all_tasks(self.loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    
                if not self.loop.is_closed():
                    self.loop.close()
            except Exception:
                pass
            
        if self._old_loop is not None:
            try:
                asyncio.set_event_loop(self._old_loop)
            except Exception:
                pass

def run_coroutine_in_thread(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run a coroutine in a separate thread.
    Useful for running async code without blocking the main thread.
    """
    result = None
    exception = None
    
    def run_coro():
        nonlocal result, exception
        with AsyncToSync() as loop:
            try:
                result = loop.run_until_complete(coro)
            except Exception as e:
                exception = e

    # Use ThreadPoolExecutor for better thread management
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_coro)
        future.result()  # Wait for completion
    
    if exception:
        raise exception
    return cast(T, result)