from fastapi.testclient import TestClient

from main import app, require_user

client = TestClient(app)


def authenticated_user():
    return {"id": "test-user", "claims": {"sub": "test-user"}}


def setup_function():
    app.dependency_overrides[require_user] = authenticated_user


def teardown_function():
    app.dependency_overrides.clear()


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_regions_are_marked_as_planned():
    response = client.get("/api/regions")
    assert response.status_code == 200
    regions = response.json()["regions"]
    assert regions
    assert all(region["status"] == "planned" for region in regions)


def test_wireguard_provisioning_fails_closed_until_servers_exist():
    response = client.post(
        "/api/wireguard/config",
        json={
            "region_id": "us-east",
            "device_name": "Meu dispositivo",
            "ip_type": "shared",
            "public_key": "A" * 43 + "=",
        },
    )
    assert response.status_code == 503
    assert "ainda não conectados" in response.json()["detail"]


def test_unknown_region_is_rejected():
    response = client.post(
        "/api/wireguard/config",
        json={
            "region_id": "unknown",
            "device_name": "Meu dispositivo",
            "ip_type": "shared",
            "public_key": "A" * 43 + "=",
        },
    )
    assert response.status_code == 404


def test_proxy_remains_disabled():
    response = client.post(
        "/api/proxy/session",
        json={"url": "https://example.com"},
    )
    assert response.status_code == 503
    assert "desativado" in response.json()["detail"]
