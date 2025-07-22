import boto3
import openai
import requests
import uuid
from io import BytesIO
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class ImageService:
    def __init__(self):
        # Configurar OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")
            
        self.openai_client = openai.OpenAI(api_key=openai_key)
        
        # Configurar S3 con variables de entorno
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if not aws_access_key or not aws_secret_key:
            raise ValueError("AWS credentials no están configuradas en las variables de entorno")
        
        self.s3_client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "sa-east-1"),
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "mycoachbucket")
    
    def generate_and_upload_image(self, prompt: str, image_type: str = "product") -> str:
        """
        Genera una imagen usando DALL-E y la sube a S3 (optimizada para velocidad)
        
        Args:
            prompt: Descripción de la imagen a generar
            image_type: Tipo de imagen (product, logo, background, etc.)
            
        Returns:
            URL de la imagen en S3
        """
        try:
            # Simplificar prompt para mayor velocidad
            simple_prompt = prompt.split(',')[0].strip()  # Solo la primera parte
            if len(simple_prompt) > 40:
                simple_prompt = simple_prompt[:40]
            
            # Generar imagen con DALL-E 2 (más rápido que DALL-E 3)
            response = self.openai_client.images.generate(
                model="dall-e-2",  # Más rápido que dall-e-3
                prompt=simple_prompt,  # Prompt más corto = más rápido
                size="256x256",  # Tamaño pequeño para máxima velocidad
                n=1,
            )
            
            # Obtener URL de la imagen generada
            image_url = response.data[0].url
            
            # Descargar la imagen con timeout muy corto
            image_response = requests.get(image_url, timeout=5)  # Timeout reducido para velocidad
            if image_response.status_code != 200:
                raise Exception("Error al descargar la imagen generada")
            
            # Generar nombre único para el archivo (más corto)
            file_name = f"flutter_app_images/{image_type}_{uuid.uuid4().hex[:8]}.png"
            
            # Subir a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=image_response.content,
                ContentType="image/png",
            )
            
            # Retornar URL pública de S3
            s3_url = f"https://{self.bucket_name}.s3.sa-east-1.amazonaws.com/{file_name}"
            
            return s3_url
            
        except Exception as e:
            print(f"Error generando/subiendo imagen: {str(e)}")
            # Retornar URL de imagen por defecto
            return "https://via.placeholder.com/256x256/E0E0E0/666666?text=Image"
    
    def get_image_for_context(self, app_type: str, widget_type: str, context: str = "") -> str:
        """
        Genera una imagen específica basada en el contexto de la app
        
        Args:
            app_type: Tipo de aplicación (ecommerce, tasks, social, etc.)
            widget_type: Tipo de widget (product, logo, background, etc.)
            context: Contexto adicional específico
            
        Returns:
            URL de la imagen en S3
        """
        
        # Prompts simplificados para mayor velocidad
        prompts = {
            "ecommerce": {
                "product": f"product {context}",
                "logo": f"logo {context}",
                "background": "ecommerce background"
            },
            "tasks": {
                "icon": f"task icon {context}",
                "background": "productivity background"
            },
            "social": {
                "profile": f"profile {context}",
                "background": "social background"
            },
            "fitness": {
                "exercise": f"fitness {context}",
                "equipment": f"gym equipment {context}"
            },
            "food": {
                "dish": f"food {context}",
                "restaurant": f"restaurant {context}"
            },
            "default": {
                "image": f"app image {context}",
                "icon": f"icon {context}"
            }
        }
        
        # Obtener prompt específico o usar default
        app_prompts = prompts.get(app_type, prompts["default"])
        prompt = app_prompts.get(widget_type, app_prompts.get("image", f"Modern {widget_type} image, {context}"))
        
        return self.generate_and_upload_image(prompt, f"{app_type}_{widget_type}")
