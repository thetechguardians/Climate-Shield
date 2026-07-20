"""
Unit tests for backend.subscriptions — covers the SQLite store, payload
validation, risk summariser, and end-to-end REST endpoints. All HTTP tests
go through Flask's test client — no live network or SMTP.
"""
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

import pytest

# Make `backend.*` importable. Test runner is invoked from repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alertsystem import app as flask_app
from backend import subscriptions as subs


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_db(tmp_path):
    """A throwaway SQLite path. Cleaned up automatically when tmp_path is blown away."""
    return str(tmp_path / "climate_shield_test.db")


@pytest.fixture
def store(temp_db):
    return subs.SubscriberStore(db_path=temp_db)


@pytest.fixture
def client(temp_db, monkeypatch):
    """Flask test client pointing at a temp DB. Sweeper thread NOT auto-started."""
    monkeypatch.setenv("CLIMATE_SHIELD_DB_PATH", temp_db)

    # Module-level singletons — we reset between tests.
    subs._store = None
    subs._sweeper = None

    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as client:
        yield client

    # Stop any threads that may have started
    if subs._sweeper:
        subs._sweeper.stop()
    subs._store = None
    subs._sweeper = None


# ===========================================================================
# SubscriberStore
# ===========================================================================

class TestSubscriberStore:

    def test_init_creates_schema_idempotent(self, temp_db):
        store1 = subs.SubscriberStore(temp_db)
        # Second call shouldn't blow up; schema already exists.
        store2 = subs.SubscriberStore(temp_db)
        # Both should be able to read the same empty list.
        assert store1.list_active() == []
        assert store2.list_active() == []

    def test_insert_and_retrieve(self, store, temp_db):
        record = store.insert(
            email="alice@x.com",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            token="t-1",
        )
        assert record["email"] == "alice@x.com"
        assert record["is_active"] == 1
        assert record["subscribed_at"]

        got = store.get_by_token("t-1")
        assert got is not None
        assert got["id"] == record["id"]

    def test_get_by_token_unknown_returns_none(self, store):
        assert store.get_by_token("does-not-exist") is None

    def test_list_active_only_returns_is_active_1(self, store):
        store.insert(email="a@x.com", city="A", state=None, country="X", token="t1")
        store.insert(email="b@x.com", city="B", state=None, country="Y", token="t2")
        # Deactivate t1
        assert store.deactivate("t1") is True
        active = store.list_active()
        assert len(active) == 1
        assert active[0]["email"] == "b@x.com"

    def test_deactivate_unknown_returns_false(self, store):
        assert store.deactivate("nope") is False

    def test_record_alert_increments_counter_and_stores_summary(self, store):
        store.insert(email="a@x.com", city="A", state=None, country="X", token="t1")
        store.record_alert("t1", "Heat Detected", {"heat_risk": 0.9})
        record = store.get_by_token("t1")
        assert record["alerts_sent"] == 1
        assert "Heat Detected" == record["last_alert_summary"]
        assert json.loads(record["last_alert_risks"])["heat_risk"] == 0.9
        assert record["last_alert_sent_at"] is not None

        # Second alert should increment
        store.record_alert("t1", "Flood Alert", {"flood_risk": 0.7})
        record = store.get_by_token("t1")
        assert record["alerts_sent"] == 2
        assert record["last_alert_summary"] == "Flood Alert"


# ===========================================================================
# Email backends
# ===========================================================================

class TestEmailBackends:

    def test_logging_backend_returns_ok_with_transport_field(self):
        captured = []
        backend = subs.LoggingEmailBackend(logger=captured.append)
        result = backend.send("a@b.com", "subj", "body")
        assert result == {"ok": True, "transport": "log"}
        assert captured and "a@b.com" in captured[0]

    def test_smtp_backend_without_creds_returns_error(self, monkeypatch):
        monkeypatch.delenv("SENDGRID_SMTP_USER", raising=False)
        monkeypatch.delenv("SENDGRID_SMTP_PASS", raising=False)
        backend = subs.SMTPEmailBackend()
        result = backend.send("a@b.com", "subj", "body")
        assert result["ok"] is False
        assert result["transport"] == "smtp"
        assert "SENDGRID" in result["error"]

    def test_get_email_backend_prefers_smtp_when_creds_present(self, monkeypatch):
        monkeypatch.setenv("SENDGRID_SMTP_USER", "apikey")
        monkeypatch.setenv("SENDGRID_SMTP_PASS", "sg.secret")
        backend = subs.get_email_backend()
        assert isinstance(backend, subs.SMTPEmailBackend)

    def test_get_email_backend_falls_back_to_logging_without_creds(self, monkeypatch):
        monkeypatch.delenv("SENDGRID_SMTP_USER", raising=False)
        monkeypatch.delenv("SENDGRID_SMTP_PASS", raising=False)
        backend = subs.get_email_backend()
        assert isinstance(backend, subs.LoggingEmailBackend)


# ===========================================================================
# Risk summariser (pure function — fast)
# ===========================================================================

class TestSummariseRisks:

    def setUp_thresholds(self):
        return {"FLOOD": 0.65, "HEAT": 0.75, "WILDFIRE": 0.65, "CYCLONE": 0.60, "DROUGHT": 0.70}

    def test_no_high_risks_returns_empty_alerts(self):
        risks = {
            "flood_risk":    0.4,
            "heat_risk":     0.6,
            "wildfire_risk": 0.5,
            "cyclone_risk":  0.3,
            "drought_risk":   0.5,
        }
        alerts, high = subs.summarise_risks(risks, self.setUp_thresholds())
        assert alerts == []
        assert high == []

    def test_multiple_high_risks(self):
        risks = {
            "flood_risk":    0.8,
            "heat_risk":     0.9,
            "wildfire_risk": 0.5,
            "cyclone_risk":  0.3,
            "drought_risk":  0.5,
        }
        alerts, high = subs.summarise_risks(risks, self.setUp_thresholds())
        assert "High Flood Risk Detected" in alerts
        assert "Heatwave Conditions Possible" in alerts
        assert "flood" in high
        assert "heat" in high
        assert len(alerts) == 2

    def test_threshold_edge_exactly_equal_is_high(self):
        risks = {"flood_risk": 0.65, "heat_risk": 0.75,
                 "wildfire_risk": 0.65, "cyclone_risk": 0.60, "drought_risk": 0.70}
        alerts, high = subs.summarise_risks(risks, self.setUp_thresholds())
        # All five at-or-above threshold → 5 alerts
        assert len(alerts) == 5

    def test_missing_risk_fields_treated_as_zero(self):
        risks = {}
        alerts, high = subs.summarise_risks(risks, self.setUp_thresholds())
        assert alerts == []

    def test_negative_or_garbage_values_dont_crash(self):
        risks = {"heat_risk": "not-a-number", "flood_risk": None}
        with pytest.raises((TypeError, ValueError)):
            subs.summarise_risks(risks, self.setUp_thresholds())


# ===========================================================================
# Payload validation
# ===========================================================================

class TestValidation:

    @pytest.mark.parametrize("payload,expected_field", [
        ({"city": "Pune", "state": "MH", "country": "IN"}, "email"),
        ({"email": "", "city": "Pune", "country": "IN"}, "email"),
        ({"email": "no-at-sign", "city": "Pune", "country": "IN"}, "email"),
        ({"email": "a@b.com", "city": "", "country": "IN"}, "city"),
        ({"email": "a@b.com", "state": "x" * 200, "country": "IN", "city": "Pune"}, "state"),
        ({"email": "a@b.com", "city": "Pune", "country": ""}, "country"),
    ])
    def test_invalid_payloads_rejected(self, client, payload, expected_field):
        resp = client.post("/subscriptions", json=payload)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False
        # The message mentions the offending field, no PII
        msg = data["message"].lower()
        assert expected_field in msg or "valid" in msg

    def test_valid_payload_with_optional_state_inserts(self, client):
        resp = client.post("/subscriptions", json={
            "email": "alice@example.com",
            "city": "Pune",
            "country": "India",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        sub = data["subscription"]
        assert sub["email"] == "alice@example.com"
        assert sub["city"] == "Pune"
        assert sub["country"] == "India"
        assert sub["state"] in (None, "", )
        assert len(sub["management_token"]) == 64  # 32 hex bytes

    def test_email_is_lowercase_normalised(self, client):
        resp = client.post("/subscriptions", json={
            "email": "ALICE@Example.COM",
            "city": "Pune",
            "country": "India",
        })
        assert resp.status_code == 201
        assert resp.get_json()["subscription"]["email"] == "alice@example.com"

    def test_excessively_long_email_rejected(self, client):
        long_email = ("a" * 300) + "@x.com"
        resp = client.post("/subscriptions", json={
            "email": long_email,
            "city": "Pune",
            "country": "India",
        })
        assert resp.status_code == 400


# ===========================================================================
# REST endpoints — GET/DELETE/Test
# ===========================================================================

class TestRESTEndpoints:

    def _subscribe(self, client, email="bob@example.com", city="Mumbai",
                   state="Maharashtra", country="India"):
        resp = client.post("/subscriptions", json={
            "email": email, "city": city, "state": state, "country": country,
        })
        assert resp.status_code == 201
        return resp.get_json()["subscription"]

    def test_get_subscription_unknown_returns_404(self, client):
        resp = client.get("/subscriptions/missing-token")
        assert resp.status_code == 404

    def test_get_subscription_after_create_returns_record(self, client):
        sub = self._subscribe(client)
        resp = client.get(f"/subscriptions/{sub['management_token']}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["subscription"]["email"] == "bob@example.com"

    def test_delete_subscription_then_get_returns_404_or_inactive(self, client):
        sub = self._subscribe(client)
        del_resp = client.delete(f"/subscriptions/{sub['management_token']}")
        assert del_resp.status_code == 200
        assert del_resp.get_json()["success"] is True

        # GET still finds it — but is_active is now 0. We don't 404 it (so subscribers
        # can verify they're unsubscribed.)
        get_resp = client.get(f"/subscriptions/{sub['management_token']}")
        assert get_resp.status_code == 200
        assert get_resp.get_json()["subscription"]["is_active"] == 0

    def test_delete_unknown_returns_404(self, client):
        resp = client.delete("/subscriptions/non-existent-token")
        assert resp.status_code == 404


# ===========================================================================
# Manual sweep endpoint
# ===========================================================================

class TestSweepEndpoint:

    def test_sweep_with_no_subscribers_returns_empty_summary(self, client):
        resp = client.post("/admin/subscriptions/sweep")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["sweep"]["processed"] == 0
        assert data["sweep"]["alerted"] == 0

    def test_sweep_with_subscribers_no_alerts(self, client, monkeypatch):
        client.post("/subscriptions", json={
            "email": "alice@example.com", "city": "Pune", "country": "India",
        })

        # Patch fetch_weather_for_location to return "no alerts" pattern.
        def fake_fetch(city, state, country):
            return {"success": True, "risks": {"flood_risk": 0.1}}, 200
        monkeypatch.setattr(subs, "fetch_weather_for_location", fake_fetch)

        # Patch email backend so we never touch SMTP
        monkeypatch.setattr(subs, "get_email_backend", lambda: subs.LoggingEmailBackend())

        resp = client.post("/admin/subscriptions/sweep")
        assert resp.status_code == 200
        sweep = resp.get_json()["sweep"]
        assert sweep["processed"] == 1
        assert sweep["alerted"] == 0

    def test_sweep_with_high_risk_triggers_email_and_records_alert(self, client, monkeypatch):
        # Subscribe one user
        client.post("/subscriptions", json={
            "email": "carol@example.com", "city": "Mumbai", "state": "MH", "country": "India",
        })

        sent_messages = []
        class CaptureBackend(subs.EmailBackend):
            def send(self, to_addr, subject, body):
                sent_messages.append({"to": to_addr, "subject": subject, "body": body})
                return {"ok": True, "transport": "capture"}

        # Fake weather shows HIGH heat risk
        def fake_fetch(city, state, country):
            return {
                "success": True,
                "risks": {
                    "heat_risk": 0.9, "heat_risk_level": "HIGH",
                    "flood_risk": 0.1, "flood_risk_level": "LOW",
                    "wildfire_risk": 0.2, "wildfire_risk_level": "LOW",
                    "cyclone_risk": 0.1, "cyclone_risk_level": "LOW",
                    "drought_risk": 0.2, "drought_risk_level": "LOW",
                },
            }, 200
        monkeypatch.setattr(subs, "fetch_weather_for_location", fake_fetch)
        monkeypatch.setattr(subs, "get_email_backend", lambda: CaptureBackend())

        resp = client.post("/admin/subscriptions/sweep")
        assert resp.status_code == 200
        sweep = resp.get_json()["sweep"]
        assert sweep["alerted"] == 1
        assert sweep["failed"] == 0
        assert len(sent_messages) == 1, "expected exactly one email on first sweep"
        assert sent_messages[0]["to"] == "carol@example.com"
        assert "Heatwave Conditions Possible" in sent_messages[0]["subject"]

        # Reset the in-test config so the second sweep ALSO touches
        # `fetch_weather_for_location` and the email backend — otherwise we'd
        # just be verifying pure cache/short-circuit.
        sent_messages.clear()

        # Second sweep should be throttled by MIN_NOTIFY_GAP_SECONDS — the
        # run_once check in the route applies the same per-subscriber throttle.
        sweep2 = client.post("/admin/subscriptions/sweep").get_json()["sweep"]
        assert sweep2["alerted"] == 0
        results = sweep2["results"]
        assert results[0].get("skipped") == "recently_notified"
        # No new email should have been sent on the second sweep
        assert len(sent_messages) == 0

    def test_sweep_propagates_weather_fetch_failure_in_result(self, client, monkeypatch):
        client.post("/subscriptions", json={
            "email": "d@x.com", "city": "X", "country": "Y",
        })
        def fake_fetch(city, state, country):
            return None, 500
        monkeypatch.setattr(subs, "fetch_weather_for_location", fake_fetch)
        monkeypatch.setattr(subs, "get_email_backend", lambda: subs.LoggingEmailBackend())

        resp = client.post("/admin/subscriptions/sweep")
        data = resp.get_json()["sweep"]
        assert data["processed"] == 1
        assert data["alerted"] == 0
        assert data["failed"] == 1
        assert "weather-fetch-failed" in data["results"][0]["error"]

    def test_sweep_admin_token_required_when_set(self, client, monkeypatch):
        monkeypatch.setenv("ADMIN_TOKEN", "super-secret")
        # Need to reload module-level singletons so the env pick-up happens,
        # but actually ADMIN_TOKEN is read inside the route handler — so setenv
        # mid-test is enough.

        resp = client.post("/admin/subscriptions/sweep")
        assert resp.status_code == 403

        # With token header:
        resp_ok = client.post(
            "/admin/subscriptions/sweep",
            headers={"X-Admin-Token": "super-secret"},
        )
        assert resp_ok.status_code == 200

    def test_test_endpoint_404_for_unknown_token(self, client):
        resp = client.post("/subscriptions/no-such-token/test")
        assert resp.status_code == 404

    def test_test_endpoint_evaluates_current_weather(self, client, monkeypatch):
        sub = client.post("/subscriptions", json={
            "email": "e@x.com", "city": "E", "state": "St", "country": "Y",
        }).get_json()["subscription"]
        token = sub["management_token"]

        captured = []
        class Capture(subs.EmailBackend):
            def send(self, to_addr, subject, body):
                captured.append((to_addr, subject, body))
                return {"ok": True, "transport": "capture"}

        def fake_fetch(city, state, country):
            return {"success": True, "risks": {
                "flood_risk": 0.8, "flood_risk_level": "HIGH",
                "heat_risk": 0.1, "heat_risk_level": "LOW",
                "wildfire_risk": 0.1, "wildfire_risk_level": "LOW",
                "cyclone_risk": 0.1, "cyclone_risk_level": "LOW",
                "drought_risk": 0.1, "drought_risk_level": "LOW",
            }}, 200

        monkeypatch.setattr(subs, "fetch_weather_for_location", fake_fetch)
        monkeypatch.setattr(subs, "get_email_backend", lambda: Capture())

        resp = client.post(f"/subscriptions/{token}/test")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["result"]["alert_sent"] is True
        assert len(captured) == 1
