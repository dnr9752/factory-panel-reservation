from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db, SessionLocal
from .models import Panel, Reservation
from .schemas import PanelOut, ReservationCreate, ReservationOut

STATIC = Path(__file__).parent / "static"

def init_db():
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
        conn.execute(text("""
        DO $$ BEGIN
          ALTER TABLE reservations ADD CONSTRAINT no_panel_date_overlap
          EXCLUDE USING gist (
            panel_id WITH =,
            daterange(start_date, end_date + 1, '[)') WITH &&
          );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
        """))
    with SessionLocal() as db:
        if not db.scalar(select(Panel.id).limit(1)):
            coords=[(10,16),(25,16),(40,16),(55,16),(70,16),(85,16),(10,55),(25,55),(40,55),(55,55),(70,55),(85,55)]
            for i,(x,y) in enumerate(coords,1):
                db.add(Panel(code=f"P{i:02d}", name=f"Panel {i:02d}", x=x, y=y, width=8, height=16))
            db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app=FastAPI(title=settings.app_title, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

@app.get("/", include_in_schema=False)
def index(): return FileResponse(STATIC / "index.html")

@app.get("/api/panels", response_model=list[PanelOut])
def panels(db: Session=Depends(get_db)):
    return db.scalars(select(Panel).order_by(Panel.code)).all()

@app.get("/api/reservations", response_model=list[ReservationOut])
def reservations(
    from_date: date | None=None, to_date: date | None=None,
    project: str | None=Query(default=None, max_length=150),
    db: Session=Depends(get_db)):
    q=select(Reservation, Panel.code).join(Panel)
    if from_date: q=q.where(Reservation.end_date >= from_date)
    if to_date: q=q.where(Reservation.start_date <= to_date)
    if project: q=q.where(Reservation.project_name.ilike(f"%{project}%"))
    rows=db.execute(q.order_by(Reservation.start_date, Panel.code)).all()
    return [ReservationOut(id=r.id,panel_id=r.panel_id,panel_code=code,project_name=r.project_name,
        purchase_order=r.purchase_order,requester=r.requester,start_date=r.start_date,end_date=r.end_date,
        note=r.note,created_at=r.created_at) for r,code in rows]

@app.post("/api/reservations", response_model=ReservationOut, status_code=201)
def create_reservation(payload: ReservationCreate, db: Session=Depends(get_db)):
    panel=db.get(Panel,payload.panel_id)
    if not panel: raise HTTPException(404,"Panel을 찾을 수 없습니다.")
    item=Reservation(**payload.model_dump())
    db.add(item)
    try:
        db.commit(); db.refresh(item)
    except IntegrityError as e:
        db.rollback()
        if "no_panel_date_overlap" in str(e.orig):
            raise HTTPException(409,"해당 Panel은 선택한 기간에 이미 예약되어 있습니다.")
        raise HTTPException(400,"예약을 저장할 수 없습니다.")
    return ReservationOut(id=item.id,panel_id=item.panel_id,panel_code=panel.code,project_name=item.project_name,
        purchase_order=item.purchase_order,requester=item.requester,start_date=item.start_date,end_date=item.end_date,
        note=item.note,created_at=item.created_at)

@app.delete("/api/reservations/{reservation_id}", status_code=204)
def delete_reservation(reservation_id:int, x_admin_key:str=Header(default=""), db:Session=Depends(get_db)):
    if x_admin_key != settings.admin_key: raise HTTPException(403,"관리자 키가 올바르지 않습니다.")
    item=db.get(Reservation,reservation_id)
    if not item: raise HTTPException(404,"예약을 찾을 수 없습니다.")
    db.delete(item); db.commit()
