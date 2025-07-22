from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from models.project import FlutterProject
from generators.project_generator import ProjectGenerator
from services.ai_generator import AIProjectGenerator
from services.image_service import ImageService
from models.database import engine, Base
from routers import auth, projects
import os
import base64
import io

# Create database tables
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Flutter Code Generator", description="Generate Flutter apps from JSON configuration")

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize project generator
project_generator = ProjectGenerator()
ai_generator = AIProjectGenerator()
image_service = ImageService()

# Modelo para el prompt
class AIPromptRequest(BaseModel):
    prompt: str

# Modelo para generar imagen
class ImageGenerationRequest(BaseModel):
    prompt: str
    image_type: str = "product"

# Modelo para mejorar proyecto con AI y generar app Flutter
class EnhanceProjectRequest(BaseModel):
    project: Dict[str, Any]
    description: str

@app.post("/generate-flutter-app")
async def generate_flutter_app(project: FlutterProject, background_tasks: BackgroundTasks):
    """Generate Flutter app from JSON configuration"""
    try:
        zip_path = project_generator.generate_flutter_project(project)
        
        # Add cleanup task to background tasks
        background_tasks.add_task(project_generator.cleanup_temp_files, zip_path)
        
        return FileResponse(
            path=zip_path,
            filename=f"{project.name.lower().replace(' ', '_')}_flutter_app.zip",
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename={project.name.lower().replace(' ', '_')}_flutter_app.zip"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Flutter app: {str(e)}")

@app.post("/generate-json-from-prompt")
async def generate_json_from_prompt(request: AIPromptRequest):
    """Generate JSON configuration from AI prompt for preview"""
    try:
        # Generar proyecto usando AI
        project_data = ai_generator.generate_project_from_prompt(request.prompt)
        
        # Validar la estructura del proyecto
        if not ai_generator.validate_project_structure(project_data):
            raise HTTPException(status_code=500, detail="El proyecto generado por AI no tiene una estructura válida")
        
        # Devolver directamente el JSON del proyecto
        return project_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating JSON from prompt: {str(e)}")

@app.post("/generate-image")
async def generate_image(request: ImageGenerationRequest):
    """Generate and upload image to S3 using DALL-E"""
    try:
        image_url = image_service.generate_and_upload_image(request.prompt, request.image_type)
        return {
            "success": True,
            "message": "Imagen generada y subida exitosamente",
            "image_url": image_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")

@app.post("/generate-json-from-image")
async def generate_json_from_image(image: UploadFile = File(...)):
    """Generate JSON configuration from UI image"""
    try:
        # Leer y convertir la imagen a base64
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode("utf-8")
        
        # Generar proyecto usando AI a partir de la imagen (sin descripción)
        project_data = ai_generator.generate_project_from_image(image_base64)
        
        # Validar la estructura del proyecto
        if not ai_generator.validate_project_structure(project_data):
            raise HTTPException(status_code=500, detail="El proyecto generado desde la imagen no tiene una estructura válida")
        
        # Devolver el JSON del proyecto directamente
        return project_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating JSON from image: {str(e)}")

@app.post("/generate-from-image")
async def generate_from_image(background_tasks: BackgroundTasks, image: UploadFile = File(...)):
    """Generate complete Flutter app from UI image"""
    try:
        # Leer y convertir la imagen a base64
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode("utf-8")
        
        # Generar proyecto usando AI a partir de la imagen (sin descripción)
        project_data = ai_generator.generate_project_from_image(image_base64)
        
        # Validar la estructura del proyecto
        if not ai_generator.validate_project_structure(project_data):
            raise HTTPException(status_code=500, detail="El proyecto generado desde la imagen no tiene una estructura válida")
        
        # Crear un proyecto Flutter a partir del JSON
        project = FlutterProject(**project_data)
        zip_path = project_generator.generate_flutter_project(project)
        
        # Add cleanup task to background tasks
        background_tasks.add_task(project_generator.cleanup_temp_files, zip_path)
        
        return FileResponse(
            path=zip_path,
            filename=f"{project.name.lower().replace(' ', '_')}_flutter_app.zip",
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename={project.name.lower().replace(' ', '_')}_flutter_app.zip"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Flutter app from image: {str(e)}")

@app.post("/generate-json-from-audio")
async def generate_json_from_audio(audio: UploadFile = File(...)):
    """Generate JSON configuration from audio description"""
    try:
        # Validar que sea un archivo de audio
        allowed_audio_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/m4a", "audio/ogg", "audio/flac"]
        if audio.content_type not in allowed_audio_types and not audio.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de audio no soportado. Usa MP3, WAV, M4A, OGG o FLAC"
            )
        
        # Leer el contenido del audio
        audio_content = await audio.read()
        
        # Generar proyecto usando AI a partir del audio
        project_data = ai_generator.generate_project_from_audio(audio_content, audio.filename)
        
        # Validar la estructura del proyecto
        if not ai_generator.validate_project_structure(project_data):
            raise HTTPException(status_code=500, detail="El proyecto generado desde el audio no tiene una estructura válida")
        
        # Devolver el JSON del proyecto directamente
        return project_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating JSON from audio: {str(e)}")

@app.post("/generate-from-audio")
async def generate_from_audio(background_tasks: BackgroundTasks, audio: UploadFile = File(...)):
    """Generate complete Flutter app from audio description"""
    try:
        # Validar que sea un archivo de audio
        allowed_audio_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/m4a", "audio/ogg", "audio/flac"]
        if audio.content_type not in allowed_audio_types and not audio.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de audio no soportado. Usa MP3, WAV, M4A, OGG o FLAC"
            )
        
        # Leer el contenido del audio
        audio_content = await audio.read()
        
        # Generar proyecto usando AI a partir del audio
        project_data = ai_generator.generate_project_from_audio(audio_content, audio.filename)
        
        # Validar la estructura del proyecto
        if not ai_generator.validate_project_structure(project_data):
            raise HTTPException(status_code=500, detail="El proyecto generado desde el audio no tiene una estructura válida")
        
        # Crear un proyecto Flutter a partir del JSON
        project = FlutterProject(**project_data)
        zip_path = project_generator.generate_flutter_project(project)
        
        # Add cleanup task to background tasks
        background_tasks.add_task(project_generator.cleanup_temp_files, zip_path)
        
        return FileResponse(
            path=zip_path,
            filename=f"{project.name.lower().replace(' ', '_')}_flutter_app.zip",
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename={project.name.lower().replace(' ', '_')}_flutter_app.zip"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Flutter app from audio: {str(e)}")

@app.post("/generate-functional-app-from-json")
async def generate_functional_app_from_json(request: EnhanceProjectRequest, background_tasks: BackgroundTasks):
    """Generate completely functional Flutter app from JSON project + AI description"""
    try:
        # Generar código Dart funcional usando AI
        dart_code = ai_generator.generate_dart_code_from_project(request.project, request.description)
        
        # Crear directorio temporal para el proyecto
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        # Obtener nombre del proyecto
        project_name = request.project.get('name', 'flutter_app').lower().replace(' ', '_')
        project_dir = os.path.join(temp_dir, project_name)
        
        # Crear estructura base del proyecto Flutter
        project_generator._copy_base_template(project_dir)
        
        # Escribir el código Dart funcional generado por AI
        main_dart_path = os.path.join(project_dir, "lib", "main.dart")
        with open(main_dart_path, 'w', encoding='utf-8') as f:
            f.write(dart_code)
        
        # Crear archivo ZIP
        zip_path = project_generator._create_zip(project_dir, project_name)
        
        # Add cleanup task to background tasks
        background_tasks.add_task(project_generator.cleanup_temp_files, zip_path)
        
        return FileResponse(
            path=zip_path,
            filename=f"{project_name}_ai_functional_flutter_app.zip",
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename={project_name}_ai_functional_flutter_app.zip"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating functional Flutter app from JSON: {str(e)}")

