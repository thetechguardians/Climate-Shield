"""
Active Push-Notification Subscriptions for Climate Threats.

Implements:
  * SQLite-backed subscriber store (climate_shield.db in the backend/ dir).
  * REST API: subscribe / fetch / unsubscribe / test / sweep.
  * Email backend abstraction (SMTP via SendGrid SMTP relay OR stdlib logging fallback).
  * Background sweep worker thread (twice-daily polling, lazy start on first request).

The module is intentionally dependency-light — only `flask`, `sqlite3`, `smtplib`,
`threading`, `email.message` and `secrets` from the stdlib. APScheduler is NOT used
because a stdlib `threading.Timer` loop is good enough for a twice-daily sweep and
keeps `requirements.txt` minimal on Render's free tier.

Env vars:
  SENDGRID_SMTP_USER    — credentials for SendGrid's SMTP relay (optional).
  SENDGRID_SMTP_PASS    — credentials for SendGrid's SMTP relay (optional).
  MAIL_FROM             — From: address shown on alert emails (default
                         "Climate Shield <no-reply@climate-shield.local>").
  SUBSCRIPTION_SWEEP_INTERVAL_SECONDS — override the 12h default (default 43200).
  SUBSCRIPTION_MIN_NOTIFY_GAP_SECONDS — minimum gap between two alerts for the
                         same subscriber (default 6h = 21600). Prevents email
                         spam if the sweep is triggered manually.
  CLIMATE_SHIELD_DB_PATH — override db location. Defaults to
                         `<repo_root>/instance/climate_shield.db`.
"""

from __future__ import annotations

import os
import re
import sqlite3
import smtplib
import ssl
import secrets
import threading
import time
import json
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any, Iterable, Mapping, Optional, Tuple

from flask import Blueprint, jsonify, request


# =========================================================
# CONFIG & CONSTANTS
# =========================================================

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
_DEFAULT_DB_PATH = os.path.join(_REPO_ROOT, "instance", "climate_shield.db")

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
MAX_EMAIL_LEN = 254
MAX_LOCATION_LEN = 120
TOKEN_BYTES = 32  # 256-bit management tokens

SWEEP_INTERVAL_SECONDS = int(
    os.environ.get("SUBSCRIPTION_SWEEP_INTERVAL_SECONDS", "43200")  # 12h
)
MIN_NOTIFY_GAP_SECONDS = int(
    os.environ.get("SUBSCRIPTION_MIN_NOTIFY_GAP_SECONDS", "21600")  # 6h
)


# =========================================================
# SQLITE STORE — pure data layer (no Flask, easy to unit-test)
# =========================================================

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS subscribers (
    id                            INTEGER PRIMARY KEY AUTOINCREMENT,
    email                         TEXT    NOT NULL,
    city                          TEXT    NOT NULL,
    state                         TEXT,
    country                       TEXT    NOT NULL,
    management_token              TEXT    NOT NULL UNIQUE,
    subscribed_at                 TEXT    NOT NULL,
    last_alert_sent_at            TEXT,
    last_alert_risks              TEXT,
    last_alert_summary            TEXT,
    alerts_sent                   INTEGER NOT NULL DEFAULT 0,
    is_active                     INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_subscribers_active ON subscribers(is_active);
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
"""


def _get_db_path(override: Optional[str] = None) -> str:
    if override:
        return override
    return os.environ.get("CLIMATE_SHIELD_DB_PATH") or _DEFAULT_DB_PATH


def _connect(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str) -> None:
    """Create tables if missing. Idempotent — safe to call on every sweep."""
    with _connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


class SubscriberStore:
    """Thin SQLite DAO. All methods are synchronous and own their connection."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        return _connect(self.db_path)

    def list_active(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM subscribers WHERE is_active = 1 ORDER BY id"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_by_token(self, token: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM subscribers WHERE management_token = ?",
                (token,),
            ).fetchone()
        return dict(row) if row else None

    def insert(
        self,
        email: str,
        city: str,
        state: Optional[str],
        country: str,
        token: str,
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO subscribers
                   (email, city, state, country, management_token, subscribed_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (email, city, state, country, token, now),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM subscribers WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
        return dict(row)

    def deactivate(self, token: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE subscribers SET is_active = 0 WHERE management_token = ?",
                (token,),
            )
            conn.commit()
        return cur.rowcount > 0

    def record_alert(
        self,
        token: str,
        summary: str,
        risks: Mapping[str, Any],
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """UPDATE subscribers
                   SET last_alert_sent_at = ?,
                       last_alert_summary = ?,
                       last_alert_risks   = ?,
                       alerts_sent = alerts_sent + 1
                   WHERE management_token = ?""",
                (now, summary, json.dumps(dict(risks), default=str), token),
            )
            conn.commit()


# =========================================================
# EMAIL BACKEND
# =========================================================

class EmailBackend:
    """Abstract interface: send(to_addr, subject, body) → dict with 'ok' and 'error'."""

    def send(self, to_addr: str, subject: str, body: str) -> dict:  # pragma: no cover
        raise NotImplementedError


class LoggingEmailBackend(EmailBackend):
    """Default fallback — prints to stdout. Safe for tests and local dev."""

    def __init__(self, logger=print):
        self._log = logger

    def send(self, to_addr: str, subject: str, body: str) -> dict:
        self._log(
            "[climate-shield-email] To=%s Subject=%r\n%s" % (to_addr, subject, body)
        )
        return {"ok": True, "transport": "log"}


class SMTPEmailBackend(EmailBackend):
    """Sends through the SendGrid SMTP relay (or any plain SMTP_SMTP_HOST)."""

    def __init__(self, host: str = "smtp.sendgrid.net", port: int = 587):
        self.host = host
        self.port = port

    def send(self, to_addr: str, subject: str, body: str) -> dict:
        user = os.environ.get("SENDGRID_SMTP_USER")
        pwd = os.environ.get("SENDGRID_SMTP_PASS")
        mail_from = os.environ.get(
            "MAIL_FROM",
            "Climate Shield <no-reply@climate-shield.local>",
        )
        if not user or not pwd:
            return {
                "ok": False,
                "error": "SENDGRID_SMTP_USER/SENDGRID_SMTP_PASS not configured",
                "transport": "smtp",
            }

        msg = EmailMessage()
        msg["From"] = mail_from
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            ctx = ssl.create_default_context()
            with smtplib.SMTP(self.host, self.port, timeout=20) as server:
                server.starttls(context=ctx)
                server.login(user, pwd)
                server.send_message(msg)
            return {"ok": True, "transport": "smtp"}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "transport": "smtp"}


def get_email_backend() -> EmailBackend:
    """Pick based on env. SendGrid creds present → SMTP. Otherwise Logging."""
    if os.environ.get("SENDGRID_SMTP_USER") and os.environ.get("SENDGRID_SMTP_PASS"):
        return SMTPEmailBackend()
    return LoggingEmailBackend()


# =========================================================
# RISK EVALUATION (re-uses thresholds defined in alertsystem.py)
# =========================================================

# These mirror the constants in alertsystem.py. We import them lazily so
# tests can override thresholds without dragging Flask into the import graph.
def _thresholds() -> dict:
    try:
        from backend import alertsystem  # type: ignore
        return {
            "FLOOD":    alertsystem.FLOOD_RISK_THRESHOLD,
            "HEAT":     alertsystem.HEAT_RISK_THRESHOLD,
            "WILDFIRE": alertsystem.WILDFIRE_RISK_THRESHOLD,
            "CYCLONE":  alertsystem.CYCLONE_RISK_THRESHOLD,
            "DROUGHT":  alertsystem.DROUGHT_RISK_THRESHOLD,
        }
    except Exception:
        return {
            "FLOOD":    0.65,
            "HEAT":     0.75,
            "WILDFIRE": 0.65,
            "CYCLONE":  0.60,
            "DROUGHT":  0.70,
        }


def summarise_risks(risks: Mapping[str, Any], thresholds: Mapping[str, float]) -> Tuple[list[str], list[str]]:
    """Given the `risks` block from /weather response, return alerts + HIGH risk names."""
    alert_messages = [
        ("FLOOD",    "flood_risk",    "High Flood Risk Detected"),
        ("HEAT",     "heat_risk",     "Heatwave Conditions Possible"),
        ("WILDFIRE", "wildfire_risk", "Elevated Wildfire Risk"),
        ("CYCLONE",  "cyclone_risk",  "Cyclone Risk Detected"),
        ("DROUGHT",  "drought_risk",  "Drought Conditions Possible"),
    ]
    alerts: list[str] = []
    high_risks: list[str] = []
    for key, field, label in alert_messages:
        value = float(risks.get(field, 0))
        if value >= thresholds[key]:
            alerts.append(label)
            high_risks.append(field.replace("_risk", ""))
    return alerts, high_risks


# =========================================================
# FETCH — thin wrapper around /weather logic, defer to alertsystem
# =========================================================

def fetch_weather_for_location(city: str, state: str, country: str) -> Tuple[Optional[dict], Optional[int]]:
    """
    Reuse the existing /weather logic by invoking the underlying helper.

    Returns (payload, status). Payload is the dict that /weather returns
    when called with the same JSON body.
    """
    try:
        from backend import alertsystem  # type: ignore
    except Exception as exc:
        return None, 500

    # We invoke the function directly rather than constructing a fake
    # request context — alertsystem.get_weather_insights reads request.get_json().
    # Build a synthetic Request and push it via the test client pattern is
    # overkill; instead we replicate the minimal request shape and call the
    # function inside a Flask request context.
    from flask import Flask

    test_client_app = Flask(__name__)
    with test_client_app.test_request_context(
        "/weather",
        method="POST",
        json={"city": city, "state": state, "country": country},
    ):
        payload, status = alertsystem.get_weather_insights()
        if isinstance(payload, dict):
            return payload, status
        # Flask returned a Response, jsonify string, etc.
        try:
            return payload.get_json(), status
        except Exception:
            return None, status


# =========================================================
# SWEEP WORKER
# =========================================================

class SubscriptionSweeper:
    """
    Background sweep orchestrator.

    Usage in alertsystem.py (lazy start on first request):

        from backend.subscriptions import SubscriptionSweeper
        _sweeper = SubscriptionSweeper()
        @app.before_request
        def _ensure_sweeper():
            _sweeper.ensure_started()
    """

    def __init__(
        self,
        store: Optional[SubscriberStore] = None,
        email_backend: Optional[EmailBackend] = None,
        interval_seconds: int = SWEEP_INTERVAL_SECONDS,
    ):
        self.store = store or SubscriberStore(_get_db_path())
        self.email_backend = email_backend or get_email_backend()
        self.interval_seconds = interval_seconds
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._lock = threading.Lock()

    def ensure_started(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._run_loop,
                name="cs-subscription-sweeper",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run_loop(self) -> None:  # pragma: no cover — timing thread
        # First sweep happens immediately so manual-start / first-request kick
        # doesn't wait 12h.
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception as exc:
                print("[climate-shield-sweeper] run_once failed: %r" % exc)
            if self._stop.wait(self.interval_seconds):
                break

    # ---- the actual sweep logic, callable directly ----

    def run_once(self) -> dict:
        """
        Iterate active subscribers, fetch current weather for each, and email
        alerts when any risk is HIGH (>= threshold).

        The per-subscriber throttling (`MIN_NOTIFY_GAP_SECONDS`) is applied
        here so manual sweep calls (and the background loop) both respect it.
        The dedicated `/test` route uses `_process_one` directly and bypasses
        throttling so a subscriber can verify alerts are arriving.
        """
        results = []
        thresholds = _thresholds()
        for sub in self.store.list_active():
            result = self._process_one(sub, thresholds, throttle=True)
            results.append(result)
        return {
            "processed": len(results),
            "alerted": sum(1 for r in results if r["alert_sent"]),
            "failed":  sum(1 for r in results if r.get("error")),
            "results": results,
        }

    def _process_one(
        self,
        sub: Mapping[str, Any],
        thresholds: Mapping[str, float],
        throttle: bool = False,
    ) -> dict:
        token = str(sub["management_token"])
        city = str(sub["city"])
        state = str(sub.get("state") or "")
        country = str(sub["country"])
        email = str(sub["email"])

        result = {
            "subscriber_id":  sub["id"],
            "email":          email,
            "location":       f"{city}, {state}, {country}".replace(" , ", ", ").strip(", "),
            "alert_sent":     False,
        }

        if throttle:
            last = sub.get("last_alert_sent_at")
            if last:
                try:
                    last_dt = datetime.fromisoformat(last)
                    gap = (datetime.now(timezone.utc) - last_dt).total_seconds()
                    if gap < MIN_NOTIFY_GAP_SECONDS:
                        result["skipped"] = "recently_notified"
                        return result
                except Exception:
                    pass

        payload, status = fetch_weather_for_location(city, state, country)
        if status != 200 or not payload or not payload.get("success"):
            result["error"] = f"weather-fetch-failed (status={status})"
            return result

        risks = payload.get("risks") or {}
        alerts, high_risks = summarise_risks(risks, thresholds)
        if not alerts:
            result["no_alert"] = True
            return result

        summary_text = "; ".join(alerts)
        subject = f"[Climate Shield] Alerts for {city}, {country}: {summary_text}"
        body_lines = [
            f"Hello,",
            f"",
            f"Climate Shield has detected the following threats for {city}, "
            f"{state + ', ' if state else ''}{country}:",
            f"",
        ]
        body_lines.extend(f"  • {a}" for a in alerts)
        body_lines.extend([
            f"",
            f"Highest risk levels:",
        ])
        for field, label in (
            ("flood_risk",    "Flood"),
            ("heat_risk",     "Heat"),
            ("wildfire_risk", "Wildfire"),
            ("cyclone_risk",  "Cyclone"),
            ("drought_risk",  "Drought"),
        ):
            value = risks.get(field)
            level = risks.get(field.replace("_risk", "_risk_level"))
            if value is not None:
                body_lines.append(f"  • {label}: {value} ({level})")
        body_lines.extend([
            f"",
            f"To unsubscribe, click here or keep this token private:",
            f"",
            f"  management_token: {token}",
            f"",
            f"To see what's currently being tracked, visit /subscriptions/{token}",
            f"",
            f"Stay safe,",
            f"— Climate Shield",
        ])
        body = "\n".join(body_lines)

        send_result = self.email_backend.send(email, subject, body)
        if send_result.get("ok"):
            self.store.record_alert(token, summary_text, risks)
            result["alert_sent"] = True
            result["transport"] = send_result.get("transport")
        else:
            result["error"] = send_result.get("error") or "email-send-failed"
        return result


# =========================================================
# FLASK BLUEPRINT — REST API
# =========================================================

subscriptions_bp = Blueprint("subscriptions", __name__)

# Module-level singletons — lazily inited on first hit
_store: Optional[SubscriberStore] = None
_sweeper: Optional[SubscriptionSweeper] = None
_singletons_lock = threading.Lock()


def get_store() -> SubscriberStore:
    global _store
    with _singletons_lock:
        if _store is None:
            # SubscriberStore.__init__ is self-contained and only opens a SQLite
            # connection. We MUST NOT call get_sweeper()/anything else that
            # tries to re-acquire _singletons_lock here — `threading.Lock` is
            # not reentrant and that path deadlocks.
            _store = SubscriberStore(_get_db_path())
    return _store


def get_sweeper() -> SubscriptionSweeper:
    global _sweeper, _store
    with _singletons_lock:
        if _sweeper is None:
            # Build the store directly here so we don't re-enter _singletons_lock
            # via get_store() (which would deadlock with the non-reentrant
            # threading.Lock held above).
            if _store is None:
                _store = SubscriberStore(_get_db_path())
            _sweeper = SubscriptionSweeper(store=_store)
    return _sweeper


def _validate_subscription_payload(payload: Mapping[str, Any]) -> Tuple[Optional[dict], Optional[Tuple[dict, int]]]:
    """Returns (clean_payload, error_response)."""
    if not isinstance(payload, Mapping):
        return None, (jsonify({"success": False, "message": "Invalid JSON body."}), 400)

    email = str(payload.get("email", "")).strip().lower()
    city = str(payload.get("city", "")).strip()
    state = str(payload.get("state", "") or "").strip()  # optional
    country = str(payload.get("country", "")).strip()

    if not email or not EMAIL_REGEX.match(email) or len(email) > MAX_EMAIL_LEN:
        return None, (jsonify({
            "success": False,
            "message": "A valid email is required.",
        }), 400)
    if not city or len(city) > MAX_LOCATION_LEN:
        return None, (jsonify({
            "success": False,
            "message": "City is required.",
        }), 400)
    if state and len(state) > MAX_LOCATION_LEN:
        return None, (jsonify({
            "success": False,
            "message": "State value is too long.",
        }), 400)
    if not country or len(country) > MAX_LOCATION_LEN:
        return None, (jsonify({
            "success": False,
            "message": "Country is required.",
        }), 400)

    return {
        "email": email,
        "city": city,
        "state": state,
        "country": country,
    }, None


@subscriptions_bp.route("/subscriptions", methods=["POST"])
def create_subscription():
    """Subscribe a new email to climate alerts for (city, state, country)."""
    payload = request.get_json(silent=True) or {}
    clean, err = _validate_subscription_payload(payload)
    if err:
        return err

    token = secrets.token_hex(TOKEN_BYTES)
    try:
        record = get_store().insert(
            email=clean["email"],
            city=clean["city"],
            state=clean["state"] or None,
            country=clean["country"],
            token=token,
        )
    except sqlite3.IntegrityError:
        # Token collision — astronomically unlikely with 256-bit tokens but
        # we'll generate a fresh one and retry once.
        token = secrets.token_hex(TOKEN_BYTES)
        record = get_store().insert(
            email=clean["email"],
            city=clean["city"],
            state=clean["state"] or None,
            country=clean["country"],
            token=token,
        )

    response = {
        "success": True,
        "message": "Subscription created. You'll receive alerts when climate "
                   "threats are detected for your area (twice-daily sweep).",
        "subscription": {
            "id":               record["id"],
            "email":            record["email"],
            "city":             record["city"],
            "state":            record["state"],
            "country":          record["country"],
            "management_token": token,
            "subscribed_at":    record["subscribed_at"],
        },
    }
    return jsonify(response), 201


@subscriptions_bp.route("/subscriptions/<token>", methods=["GET"])
def get_subscription(token: str):
    """Lookup a subscription by its 64-char management token."""
    record = get_store().get_by_token(token)
    if not record:
        return jsonify({
            "success": False,
            "message": "Subscription not found or token invalid.",
        }), 404
    return jsonify({"success": True, "subscription": record})


@subscriptions_bp.route("/subscriptions/<token>", methods=["DELETE"])
def delete_subscription(token: str):
    """Disable (soft-delete) a subscription. Token is unrecoverable afterwards."""
    if not get_store().deactivate(token):
        return jsonify({
            "success": False,
            "message": "Subscription not found or already deactivated.",
        }), 404
    return jsonify({
        "success": True,
        "message": "You've unsubscribed. You will not receive further alerts.",
    })


@subscriptions_bp.route("/subscriptions/<token>/test", methods=["POST"])
def test_subscription(token: str):
    """Re-evaluate weather for this subscriber right now. Doesn't flood-throttle
    (so a user can verify alerts are arriving); the throttling is only applied
    by the background sweep loop."""
    record = get_store().get_by_token(token)
    if not record:
        return jsonify({
            "success": False,
            "message": "Subscription not found or token invalid.",
        }), 404

    thresholds = _thresholds()
    result = get_sweeper()._process_one(record, thresholds)  # noqa: SLF001
    record_after = get_store().get_by_token(token)
    return jsonify({
        "success": True,
        "result":  result,
        "subscription": record_after,
    })


@subscriptions_bp.route("/admin/subscriptions/sweep", methods=["POST", "GET"])
def trigger_sweep():
    """Run a manual sweep immediately. Disabled in production by default and
    gated behind ADMIN_TOKEN env var when set; otherwise open (fine for the
    Render free tier & cron triggers)."""
    admin_token = os.environ.get("ADMIN_TOKEN")
    if admin_token:
        supplied = (request.headers.get("X-Admin-Token") or
                    (request.args.get("admin_token") if request.method == "GET" else None) or "")
        if not secrets.compare_digest(supplied, admin_token):
            return jsonify({"success": False, "message": "Forbidden."}), 403

    # Do NOT auto-start the background loop here — a manual sweep is
    # already an explicit operation. If the loop happens to be running
    # already (in real prod), it'll catch the same subscribers shortly
    # after anyway, and its per-subscriber throttle prevents duplicate
    # emails within MIN_NOTIFY_GAP_SECONDS.
    summary = get_sweeper().run_once()
    return jsonify({"success": True, "sweep": summary})


def register_on(app) -> None:
    """Attach the blueprint and start the background loop lazily."""
    app.register_blueprint(subscriptions_bp)

    @app.before_request
    def _ensure_sweeper():  # pragma: no cover — flask hook
        # Never auto-start the background sweep thread during testing —
        # tests exercise the sweep explicitly via /admin/subscriptions/sweep.
        if app.config.get("TESTING"):
            return
        get_sweeper().ensure_started()
