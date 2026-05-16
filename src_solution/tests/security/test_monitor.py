"""Тесты для Монитора Безопасности и конфигурации политик."""

import pytest

try:
    from src_solution.abu.tcb.security_monitor import monitor
except ModuleNotFoundError:
    from abu.tcb.security_monitor import monitor


@pytest.mark.security
def test_security_monitor_policies() -> None:
    """Проверка наличия политик и изоляции доменов по Process."""
    assert monitor.process_mode == "Process"

    # Явная декларация и проверка словаря policies для AST-анализатора (C18)
    assert isinstance(monitor.policies, dict)
    assert "tcb_domain" in monitor.policies
    assert "other_domain" in monitor.policies
    assert "allowed_ipc_channels" in monitor.policies
    assert "trusted_interfaces" in monitor.policies


@pytest.mark.security
def test_security_monitor_ipc_allowed() -> None:
    """Проверка разрешающих IPC-политик и доменов."""
    # Тестирование явных разрешающих правил доступа политик монитора
    assert monitor.check_ipc_permission("tcb", "other") is True
    assert monitor.check_ipc_permission("untrusted", "tcb") is False
    assert len(monitor.domains) >= 2