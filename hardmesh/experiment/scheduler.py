"""任务调度器：限并发 + 队列化执行实验步骤。"""
import queue
import threading
import time
import uuid
from typing import Any, Callable, Dict, List


class TaskScheduler:
    """简单的线程池任务调度器。"""

    def __init__(self, workers: int = 4):
        self.workers = workers
        self._q: "queue.Queue" = queue.Queue()
        self._threads: List[threading.Thread] = []
        self._results: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        self._running = True
        for _ in range(self.workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self._threads.append(t)

    def _worker(self) -> None:
        while self._running:
            try:
                task_id, fn, args, kwargs = self._q.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                result = fn(*args, **kwargs)
                with self._lock:
                    self._results[task_id] = {"ok": True, "result": result}
            except Exception as e:
                with self._lock:
                    self._results[task_id] = {"ok": False, "error": str(e)}

    def submit(self, fn: Callable, *args, **kwargs) -> str:
        task_id = uuid.uuid4().hex
        self._q.put((task_id, fn, args, kwargs))
        return task_id

    def wait(self, task_ids: List[str], timeout: float = 60.0) -> Dict[str, Any]:
        deadline = time.time() + timeout
        out = {}
        while task_ids and time.time() < deadline:
            with self._lock:
                for tid in list(task_ids):
                    if tid in self._results:
                        out[tid] = self._results.pop(tid)
                        task_ids.remove(tid)
            if not task_ids:
                break
            time.sleep(0.02)
        return out

    def stop(self) -> None:
        self._running = False
        for t in self._threads:
            t.join(timeout=1.0)
