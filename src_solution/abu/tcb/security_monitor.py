"""Монитор безопасности АБУ (Security Monitor).

Реализует концепцию Process Isolation, контроль междоменного
взаимодействия (IPC) и применение разрешающих политик безопасности.
"""

import multiprocessing
from typing import Any, Dict, List


class SecurityMonitor:
    """Монитор безопасности, проверяющий IPC вызовы между доменами."""

    def __init__(self) -> None:
        # Декларативные разрешающие политики для междоменных взаимодействий
        self.policies: Dict[str, List[str]] = {
            "tcb_domain": ["event_log", "safety"],
            "other_domain": ["pseudo_ai", "numpy_workflow"],
            "allowed_ipc_channels": {
                "tcb": ["other"],
                "other": [],
            },
            "trusted_interfaces": [
                "enforce_depth_cap",
                "enforce_rpm_cap",
                "record",
            ],
        }
        # Архитектурное разнесения доменов по процессам ОС
        self.process_mode: str = "Process"
        self.domains: List[str] = ["tcb", "other"]

    def check_ipc_permission(
        self,
        source_domain: str,
        target_domain: str,
    ) -> bool:
        """Проверяет, разрешено ли междоменное IPC взаимодействие."""
        allowed_targets = self.policies["allowed_ipc_channels"].get(
            source_domain,
            [],
        )
        return target_domain in allowed_targets

    def request_response_allowed(
        self,
        source_domain: str,
        target_domain: str,
        request_name: str,
        response_name: str,
    ) -> bool:
        """Проверяет request/response boundary между доменами."""
        if not request_name or not response_name:
            return False
        return self.check_ipc_permission(source_domain, target_domain)

    def spawn_domain_process(self, target: Any, *args: object) -> int | None:
        """Запускает домен в отдельном процессе для Process boundary."""
        proc = multiprocessing.Process(target=target, args=args)
        proc.start()
        proc.join(timeout=0.2)
        if proc.is_alive():
            proc.terminate()
        return proc.exitcode


# Глобальный экземпляр Монитора Безопасности
monitor = SecurityMonitor()
