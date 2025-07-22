from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from models.database import get_db
from models.schemas import ProjectCreate, Project, User
from services.user_service import ProjectService
from services.dependencies import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    return ProjectService.create_project(db, project, current_user.id)


@router.get("/", response_model=List[Project])
async def get_my_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects for the current user (owned + collaborative)"""
    from models.user_project_access import UserProjectAccess
    from models.user import Project as ProjectModel
    
    # Proyectos propios
    owned_projects = ProjectService.get_user_projects(db, current_user.id)
    
    # Proyectos colaborativos
    collaborative_projects = db.query(ProjectModel).join(
        UserProjectAccess,
        ProjectModel.id == UserProjectAccess.project_id
    ).filter(
        UserProjectAccess.user_id == current_user.id
    ).all()
    
    # Combinar y eliminar duplicados
    all_projects = {}
    
    for project in owned_projects:
        all_projects[str(project.id)] = project
    
    for project in collaborative_projects:
        all_projects[str(project.id)] = project
    
    return list(all_projects.values())


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user owns the project OR has access through UserProjectAccess
    from models.user_project_access import UserProjectAccess
    
    is_owner = project.owner_id == current_user.id
    has_access = db.query(UserProjectAccess).filter(
        UserProjectAccess.user_id == current_user.id,
        UserProjectAccess.project_id == project_id
    ).first() is not None
    
    if not is_owner and not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: uuid.UUID,
    project_update: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project"""
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user owns the project OR has access through UserProjectAccess
    from models.user_project_access import UserProjectAccess
    
    is_owner = project.owner_id == current_user.id
    has_access = db.query(UserProjectAccess).filter(
        UserProjectAccess.user_id == current_user.id,
        UserProjectAccess.project_id == project_id
    ).first() is not None
    
    if not is_owner and not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project"
        )
    
    updated_project = ProjectService.update_project(
        db, project_id, project_update.name, project_update.data
    )
    return updated_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user owns the project
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )
    
    ProjectService.delete_project(db, project_id)
