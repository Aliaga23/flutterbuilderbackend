from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from starlette.websockets import WebSocketState

from models.database import SessionLocal
from models.user_project_access import UserProjectAccess
from models.user import User
from services.auth_service import decode_token

router = APIRouter(prefix="/collaboration", tags=["Realtime"])
_rooms = {}

def db():
    d = SessionLocal()
    try:
        yield d
    finally:
        d.close()

@router.websocket("/{project_id}/ws")
async def project_ws(ws: WebSocket, project_id: UUID):
    print(f"WebSocket connection attempt for project: {project_id}")
    print(f"Headers: {dict(ws.headers)}")
    
    proto_hdr = ws.headers.get("sec-websocket-protocol", "")
    print(f"Protocol header: {proto_hdr}")
    
    client_proto = proto_hdr.split(",")[0].strip()  # ej. "jwt.eyJhbGciOiJI..."
    print(f"Client protocol: {client_proto}")

    if not client_proto.startswith("jwt."):
        print("Protocol validation failed: doesn't start with jwt.")
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = client_proto[4:]                        # quita "jwt."
    print(f"Extracted token: {token[:20]}...")  # Only show first 20 chars for security
    
    payload = decode_token(token)
    print(f"Token payload: {payload}")
    
    if payload is None:
        print("Token validation failed: payload is None")
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Extraer email del token y buscar el user_id en la base de datos
    try:
        user_email = payload["sub"]  # Asumiendo que "sub" contiene el email
        print(f"User email: {user_email}")
    except (KeyError, TypeError) as e:
        print(f"Email extraction failed: {e}")
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    session = SessionLocal()
    try:
        # Buscar el usuario por email para obtener su ID
        user = session.query(User).filter(User.email == user_email).first()
        if not user:
            print(f"User not found with email: {user_email}")
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        user_id = user.id
        print(f"User ID: {user_id}")
        
        # Verificar acceso al proyecto y otorgarlo si no existe
        exists = (
            session.query(UserProjectAccess)
            .filter_by(user_id=user_id, project_id=project_id)
            .first()
        )
        if not exists:
            print(f"User {user_email} doesn't have access to project {project_id}, granting access...")
            session.add(UserProjectAccess(
                user_id=user_id,
                project_id=project_id,
                granted_at=datetime.utcnow(),
            ))
            session.commit()
            print("Access granted successfully!")
        else:
            print(f"User {user_email} already has access to project {project_id}")
    except IntegrityError as e:
        print(f"Error granting access: {e}")
        session.rollback()
    finally:
        session.close()

    print("Accepting WebSocket connection...")
    await ws.accept(subprotocol=client_proto)
    print("WebSocket connection accepted!")

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