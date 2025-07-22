from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user import User, Project
from models.schemas import UserCreate, ProjectCreate
from services.auth_service import get_password_hash, verify_password
from typing import Optional
import uuid


class UserService:
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> Optional[User]:
        """Create a new user with hashed password"""
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                username=user.username,
                email=user.email,
                password=hashed_password,
                color=user.color
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            return None  # User already exists
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user


class ProjectService:
    
    @staticmethod
    def create_project(db: Session, project: ProjectCreate, owner_id: uuid.UUID) -> Project:
        """Create a new project"""
        db_project = Project(
            name=project.name,
            owner_id=owner_id,
            data=project.data
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def get_user_projects(db: Session, owner_id: uuid.UUID):
        """Get all projects for a user"""
        return db.query(Project).filter(Project.owner_id == owner_id).all()
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: uuid.UUID) -> Optional[Project]:
        """Get project by ID"""
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def update_project(db: Session, project_id: uuid.UUID, name: str = None, data: dict = None) -> Optional[Project]:
        """Update project"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            if name:
                project.name = name
            if data is not None:
                project.data = data
            db.commit()
            db.refresh(project)
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: uuid.UUID) -> bool:
        """Delete project"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            db.delete(project)
            db.commit()
            return True
        return False
