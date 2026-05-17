"""Тесты FastAPI приложения."""

import os
import pytest
from fastapi.testclient import TestClient

try:
    import src_solution.abu.app as app_mod
    from src_solution.abu.app import app
    from src_solution.abu.tcb.event_log import default_log
except ModuleNotFoundError:
    import abu.app as app_mod
    from abu.app import app
    from abu.tcb.event_log import default_log


@pytest.fixture()
def client() -> TestClient:
    """HTTP-клиент для приложения."""
    return TestClient(app)


@pytest.mark.security
def test_health(client: TestClient) -> None:
    """Health endpoint."""
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.security
def test_mission_flow(client: TestClient) -> None:
    """Создание миссии и тик до завершения."""
    r = client.post(
        "/api/v1/missions",
        json={"target_depth_m": 2.0, "max_rpm": 250.0},
    )
    assert r.status_code == 200
    mid = r.json()["mission_id"]
    for _ in range(20):
        t = client.post("/api/v1/missions/tick")
        assert t.status_code == 200
        m_status = t.json().get("mission", {}).get("mission_status")
        if m_status == "completed":
            break
    st = client.get("/api/v1/status")
    assert st.json()["mission_id"] == mid


@pytest.mark.security
def test_ai_suggest(client: TestClient) -> None:
    """Эндпоинт псевдо-ИИ."""
    r = client.post(
        "/api/v1/ai/suggest",
        json={"depth_m": 5.0, "torque_nm": 3000.0},
    )
    assert r.status_code == 200
    assert "suggested_rpm" in r.json()


@pytest.mark.security
def test_tick_without_mission(client: TestClient) -> None:
    """Тик без миссии — ошибка."""
    import sys

    app_mod._mission = None
    for module_name in ("abu.app", "src_solution.abu.app"):
        if module_name in sys.modules:
            setattr(sys.modules[module_name], "_mission", None)
    r = client.post("/api/v1/missions/tick")
    assert r.status_code == 400


@pytest.mark.security
def test_rpm_env_cap(client: TestClient) -> None:
    """Переменная окружения ограничивает обороты."""
    os.environ["ABU_MAX_RPM"] = "100"
    try:
        client.post("/api/v1/missions", json={"target_depth_m": 5.0})
        t = client.post("/api/v1/missions/tick")
        assert t.json()["mission"]["rpm"] <= 100
    finally:
        del os.environ["ABU_MAX_RPM"]


@pytest.mark.security
def test_log_integration() -> None:
    """Проверка интеграции журнала."""
    assert default_log is not None
