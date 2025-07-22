from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from models.database import SessionLocal
from models.user_project_access import UserProjectAccess
from services.auth_service import decode_token

router = APIRouter(prefix="/collaboration", tags=["Realtime"])
_rooms = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/{project_id}/ws")
async def project_ws(ws: WebSocket, project_id: UUID):
    # 1️⃣  — leer sub-protocolo que mandó el cliente —
    proto_hdr = ws.headers.get("sec-websocket-protocol", "")
    client_proto = proto_hdr.split(",")[0].strip()  # ej. "jwt.eyJhbGciOiJI..."

    if not client_proto.startswith("jwt."):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = client_proto[4:]                        # quita "jwt."
    payload = decode_token(token)
    if payload is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    user_id = UUID(payload["sub"])

    # 2️⃣  — insertar acceso si falta —
    session = SessionLocal()
    try:
        exists = (
            session.query(UserProjectAccess)
            .filter_by(user_id=user_id, project_id=project_id)
            .first()
        )
        if not exists:
            session.add(UserProjectAccess(
                user_id=user_id,
                project_id=project_id,
                granted_at=datetime.utcnow(),
            ))
            session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()

    # 3️⃣  — completar handshake devolviendo EL MISMO protocolo —
    await ws.accept(subprotocol=client_proto)

    # 4️⃣ — broadcast —
    _rooms.setdefault(project_id, []).append(ws)
    try:
        while True:
            msg = await ws.receive_text()
            for peer in _rooms[project_id]:
                if peer is not ws:
                    await peer.send_text(msg)
    except WebSocketDisconnect:
        _rooms[project_id].remove(ws)
        if not _rooms[project_id]:
            _rooms.pop(project_id, None)
