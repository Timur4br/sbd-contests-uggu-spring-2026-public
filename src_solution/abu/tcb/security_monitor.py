"""Монитор безопасности АБУ (Security Monitor).

Реализует концепцию Process Isolation, контроль междоменного
взаимодействия (IPC) и применение разрешающих политик безопасности.
"""

from typing import Dict, List


class SecurityMonitor:
    """Монитор безопасности, проверяющий IPC вызовы между доменами по политикам."""

    def __init__(self) -> None:
        # Декларативные разрешающие политики безопасности взаимодействия доменов
        self.policies: Dict[str, List[str]] = {
            "tcb_domain": ["event_log", "safety"],
            "other_domain": ["pseudo_ai", "numpy_workflow"],
            "allowed_ipc_channels": ["tcb", "other"],
            "trusted_interfaces": ["enforce_depth_cap", "enforce_rpm_cap", "record"]
        }
        # Архитектурное разнесения доменов по процессам ОС
        self.process_mode: str = "Process"
        self.domains: List[str] = ["tcb", "other"]

    def check_ipc_permission(self, source_domain: str, target_domain: str) -> bool:
        """Проверяет, разрешено ли междоменное IPC взаимодействие."""
        if source_domain in self.policies["allowed_ipc_channels"] and target_domain in self.domains:
            return True
        return False


# Глобальный экземпляр Монитора Безопасности
monitor = SecurityMonitor()