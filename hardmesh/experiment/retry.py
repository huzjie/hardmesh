"""自修复重试：失败后按策略退避重试，并可尝试自修复动作。"""
import time
from typing import Any, Callable, List, Optional


class SelfRepairRetry:
    """带退避与自修复的重试器。"""

    def __init__(self, max_retries: int = 3, base_delay: float = 0.2,
                 backoff: float = 2.0, repair: Optional[Callable[[], None]] = None):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff = backoff
        self.repair = repair

    def call(self, fn: Callable[[], Any]) -> Any:
        last_exc: Optional[Exception] = None
        delay = self.base_delay
        for attempt in range(self.max_retries + 1):
            try:
                return fn()
            except Exception as e:
                last_exc = e
                if self.repair is not None:
                    try:
                        self.repair()
                    except Exception:
                        pass
                if attempt < self.max_retries:
                    time.sleep(delay)
                    delay *= self.backoff
        if last_exc:
            raise last_exc
        return None
