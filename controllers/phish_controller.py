# controllers/phish_controller.py
"""
Phishing-campaign controller – totalmente funcional
--------------------------------------------------
• Não usa Flask-Login; confia no e-mail salvo em session
• Gera, lista, exporta e rastreia campanhas
"""
from flask import current_app
from datetime import datetime, timedelta
import hashlib, secrets, logging
from io import StringIO
import csv

from flask import (
    Blueprint, request, jsonify, session,
    redirect, url_for
)
from sqlalchemy.exc import SQLAlchemyError

from extensions                import db
from models.phish_event        import PhishEvent, PhishCampaign
from utils.user_agent_parser   import parse_user_agent
from utils.ip_utils            import get_real_ip, get_geolocation
from utils.auth_decorators     import login_required
from utils.email_sender         import send_email  

logger            = logging.getLogger(__name__)
phish_controller  = Blueprint("phish_controller", __name__)


# ───────────────────────── helpers ──────────────────────────
def _user_email() -> str | None:
    return session.get("email")

def _host() -> str:
    return request.host_url.rstrip("/")


# ─────────────────────── rastrear clique ────────────────────
@phish_controller.route("/p/<string:link_hash>")
def track_click(link_hash: str):
    if len(link_hash) != 64:
        return redirect(url_for("login_page"))

    email       = request.args.get("e", "unknown")[:255]
    campaign_id = request.args.get("c")
    target_url  = request.args.get("target") or url_for("login_page")

    try:
        ip        = get_real_ip(request)
        ua        = request.headers.get("User-Agent", "Unknown")[:1000]
        referer   = request.headers.get("Referer")
        ua_info   = parse_user_agent(ua)
        geo_info  = get_geolocation(ip) if ip else {}

        db.session.add(
            PhishEvent(
                sent_by    = email,
                email      = email,
                ip_address = ip or "0.0.0.0",
                user_agent = ua,
                link_hash  = link_hash,
                campaign_id= campaign_id,
                referer    = referer,
                device_type= ua_info["device_type"],
                browser    = ua_info["browser"],
                os         = ua_info["os"],
                country    = geo_info.get("country"),
                city       = geo_info.get("city"),
            )
        )
        db.session.commit()
    except SQLAlchemyError as db_err:
        db.session.rollback()
        logger.error("DB error tracking click: %s", db_err, exc_info=True)
    except Exception as exc:
        logger.error("Error tracking click: %s", exc, exc_info=True)

    return redirect(target_url)


# ───────────────────── gerar links ──────────────────────────
@phish_controller.route("/api/phish/generate", methods=["POST"])
@login_required
def generate_links():
    data = request.get_json() or {}
    emails        = [e.strip() for e in data.get("emails", []) if e.strip()]
    name          = data.get("campaign_name") or "Default campaign"
    descr         = data.get("description", "")
    target        = data.get("target_url") or url_for("login_page", _external=True)

    if not emails:
        return jsonify(error="At least one e-mail is required."), 400
    if len(emails) > 100:
        return jsonify(error="Max 100 e-mails."), 400

    author = _user_email()
    if not author:
        return jsonify(error="Session without user e-mail"), 401

    camp_id = hashlib.sha256(f"{name}:{author}".encode()).hexdigest()[:64]

    camp = PhishCampaign.query.get(camp_id)
    if camp is None:
        camp = PhishCampaign(
            id=camp_id, name=name, description=descr, target_url=target,
            created_by=author, expires_at=datetime.utcnow()+timedelta(days=30)
        )
        db.session.add(camp)


    cfg = current_app.config
    public_url = cfg["PUBLIC_URL"]


    links = []
    base  = public_url
    for addr in emails:
        hsh  = hashlib.sha256(f"{camp_id}:{addr}:{secrets.token_hex(8)}".encode()).hexdigest()
        url  = f"{base}/p/{hsh}?e={addr}&c={camp_id}&target={target}"
        links.append({"email": addr, "link": url, "hash": hsh})

        # ------------- ENVIO DO E-MAIL -------------
        html = f"""
        <p>Olá,</p>
        <p>Clique no link abaixo para testar nosso novo sistema:</p>
        <p><a href="{url}">{url}</a></p>
        <p>Obrigado.</p>
        """
        send_email(subject=name, recipients=[addr], html_body=html)

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error("DB error: %s", e, exc_info=True)
        return jsonify(error="Database error"), 500

    return jsonify(
        campaign_id = camp_id,
        links       = links,
        expires_at  = camp.expires_at.isoformat()
    ), 201


# ───────────────────── estatísticas ─────────────────────────
@phish_controller.route("/api/phish/stats")
@login_required
def stats():
    email = _user_email()
    if not email:
        return jsonify(error="Unauthorized"), 401

    camp_id = request.args.get("campaign_id")
    if camp_id:                                          # estatística de 1 campanha
        camp = PhishCampaign.query.filter_by(id=camp_id, created_by=email).first()
        if not camp:
            return jsonify(error="Campaign not found"), 404

        s   = PhishEvent.get_stats_by_campaign(camp_id)
        tl  = PhishEvent.get_clicks_by_date()

        return jsonify(
            campaign = {
                "id": camp.id, "name": camp.name,
                "since": camp.created_at.isoformat(),
                "until": camp.expires_at.isoformat() if camp.expires_at else None,
            },
            stats = {
                "total_clicks": s.total_clicks if s else 0,
                "unique_users": s.unique_users if s else 0,
                "unique_ips"  : s.unique_ips   if s else 0,
            },
            timeline = [dict(date=str(r.date), clicks=r.clicks) for r in tl],
        )

    # agregado – todas as campanhas do usuário
    camps = PhishCampaign.query.filter_by(created_by=email).all()
    total_clicks, victims = 0, set()
    for c in camps:
        evs = PhishEvent.query.filter_by(campaign_id=c.id).all()
        total_clicks += len(evs)
        victims.update(e.email for e in evs)

    return jsonify(
        total_campaigns=len(camps), total_clicks=total_clicks,
        unique_victims=len(victims),
        campaigns=[
            {
                "id": c.id, "name": c.name,
                "created_at": c.created_at.isoformat(),
                "clicks": PhishEvent.query.filter_by(campaign_id=c.id).count(),
            } for c in camps
        ]
    )


# ───────────────────── exportar CSV ─────────────────────────
@phish_controller.route("/api/phish/export/<string:campaign_id>")
@login_required
def export_csv(campaign_id):
    email = _user_email()
    c     = PhishCampaign.query.filter_by(id=campaign_id, created_by=email).first()
    if not c:
        return jsonify(error="Campaign not found"), 404

    rows = PhishEvent.query.filter_by(campaign_id=campaign_id).all()
    buf  = StringIO()
    w    = csv.writer(buf)
    w.writerow([
        "Email", "IP", "Browser", "OS", "Device",
        "Country", "City", "Clicked At", "User-Agent"
    ])
    for r in rows:
        w.writerow([
            r.email, r.ip_address, r.browser, r.os, r.device_type,
            r.country, r.city, r.clicked_at.strftime("%Y-%m-%d %H:%M:%S"), r.user_agent
        ])

    from flask import Response
    buf.seek(0)
    return Response(
        buf.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=campaign_{campaign_id}.csv"}
    )
