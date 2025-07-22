from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from starlette.websockets import WebSocketState

from models.database import SessionLocal
from models.user_project_access import UserProjectAccess
from services.auth_service import decode_token

router = APIRouter(prefix="/collaboration", tags=["Realtime"])
_rooms = {}  # project_id -> list of websockets
_user_connections = {}  # project_id -> user_id -> websocket

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
    
    # El payload["sub"] puede ser un email, necesitamos obtener el user_id
    user_email = payload.get("sub")
    if not user_email:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Buscar el usuario por email para obtener su UUID
    session = SessionLocal()
    try:
        from models.user import User
        user = session.query(User).filter(User.email == user_email).first()
        if not user:
            session.close()
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_id = user.id

        # 2️⃣  — insertar acceso si falta —
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
    except Exception as e:
        session.rollback()
        session.close()
        await ws.close(code=status.WS_1011_INTERNAL_ERROR)
        return
    finally:
        session.close()

    # 3️⃣  — completar handshake devolviendo EL MISMO protocolo —
    await ws.accept(subprotocol=client_proto)

    # 4️⃣ — gestión de conexiones por usuario —
    _rooms.setdefault(project_id, [])
    _user_connections.setdefault(project_id, {})
    
    # Si el usuario ya tiene una conexión, cerrar la anterior
    if user_id in _user_connections[project_id]:
        old_ws = _user_connections[project_id][user_id]
        try:
            if old_ws.client_state == WebSocketState.CONNECTED:
                await old_ws.close(code=status.WS_1000_NORMAL_CLOSURE)
        except:
            pass
        # Remover de rooms si existe
        if old_ws in _rooms[project_id]:
            _rooms[project_id].remove(old_ws)
    
    # Agregar nueva conexión
    _rooms[project_id].append(ws)
    _user_connections[project_id][user_id] = ws
    
    print(f"User {user_id} connected to project {project_id}. Total connections: {len(_rooms[project_id])}")
    
    try:
        while True:
            msg = await ws.receive_text()
            # Lista de conexiones a remover si están cerradas
            closed_connections = []
            
            for peer in _rooms[project_id]:
                if peer is not ws:
                    try:
                        # Verificar si el WebSocket está abierto antes de enviar
                        if peer.client_state == WebSocketState.CONNECTED:
                            await peer.send_text(msg)
                        else:
                            closed_connections.append(peer)
                    except Exception:
                        # Si hay error al enviar, marcar para remover
                        closed_connections.append(peer)
            
            # Remover conexiones cerradas
            for closed_peer in closed_connections:
                if closed_peer in _rooms[project_id]:
                    _rooms[project_id].remove(closed_peer)
                    # Remover también de user_connections
                    for uid, uws in list(_user_connections[project_id].items()):
                        if uws == closed_peer:
                            del _user_connections[project_id][uid]
                            break
                    
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected from project {project_id}")
        if ws in _rooms[project_id]:
            _rooms[project_id].remove(ws)
        if user_id in _user_connections[project_id]:
            del _user_connections[project_id][user_id]
        if not _rooms[project_id]:
            _rooms.pop(project_id, None)
            _user_connections.pop(project_id, None)
