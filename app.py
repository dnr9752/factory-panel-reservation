import os
from datetime import date, datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL", "sqlite:///reservations.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config.update(
    SQLALCHEMY_DATABASE_URI=database_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY=os.getenv("SECRET_KEY", "prototype-only-change-me"),
)
db = SQLAlchemy(app)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    panel = db.Column(db.String(20), nullable=False, index=True)
    user_name = db.Column(db.String(80), nullable=False)
    project_name = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    note = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id,
            "panel": self.panel,
            "user_name": self.user_name,
            "project_name": self.project_name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "note": self.note or "",
        }

with app.app_context():
    db.create_all()

@app.get("/")
def index():
    return render_template("index.html", panels=[f"P{i}" for i in range(1, 11)], today=date.today().isoformat())

@app.get("/api/reservations")
def list_reservations():
    rows = Reservation.query.order_by(Reservation.start_date, Reservation.panel).all()
    return jsonify([row.as_dict() for row in rows])

@app.post("/api/reservations")
def create_reservation():
    data = request.get_json(silent=True) or {}
    required = ["panel", "user_name", "project_name", "start_date", "end_date"]
    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify(message="필수 항목을 모두 입력해 주세요."), 400

    panel = str(data["panel"]).strip().upper()
    if panel not in {f"P{i}" for i in range(1, 11)}:
        return jsonify(message="올바르지 않은 판넬입니다."), 400

    try:
        start = date.fromisoformat(data["start_date"])
        end = date.fromisoformat(data["end_date"])
    except ValueError:
        return jsonify(message="날짜 형식이 올바르지 않습니다."), 400
    if start > end:
        return jsonify(message="종료일은 시작일보다 빠를 수 없습니다."), 400

    try:
        # PostgreSQL에서는 판넬별 트랜잭션 잠금으로 동시 예약 충돌을 줄입니다.
        if db.engine.dialect.name == "postgresql":
            db.session.execute(text("SELECT pg_advisory_xact_lock(hashtext(:panel))"), {"panel": panel})

        conflict = Reservation.query.filter(
            Reservation.panel == panel,
            Reservation.start_date <= end,
            Reservation.end_date >= start,
        ).first()
        if conflict:
            db.session.rollback()
            return jsonify(message=f"이미 예약된 기간입니다: {conflict.start_date} ~ {conflict.end_date} ({conflict.user_name})"), 409

        row = Reservation(
            panel=panel,
            user_name=str(data["user_name"]).strip()[:80],
            project_name=str(data["project_name"]).strip()[:120],
            start_date=start,
            end_date=end,
            note=str(data.get("note", "")).strip()[:300],
        )
        db.session.add(row)
        db.session.commit()
        return jsonify(message="예약이 등록되었습니다.", reservation=row.as_dict()), 201
    except (IntegrityError, Exception):
        db.session.rollback()
        app.logger.exception("Reservation creation failed")
        return jsonify(message="예약 저장 중 오류가 발생했습니다."), 500

@app.delete("/api/reservations/<int:reservation_id>")
def delete_reservation(reservation_id):
    row = db.session.get(Reservation, reservation_id)
    if not row:
        return jsonify(message="예약을 찾을 수 없습니다."), 404
    db.session.delete(row)
    db.session.commit()
    return jsonify(message="예약이 취소되었습니다.")

@app.get("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
