import openai
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv
from .image_service import ImageService

load_dotenv()

class AIProjectGenerator:
    def __init__(self):
        # Configurar la API key de OpenAI
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")
        
        # Inicializar servicio de imágenes
        self.image_service = ImageService()
    
    def generate_project_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Genera un proyecto Flutter completo basado en un prompt usando OpenAI
        """
        
        system_prompt = """Eres un experto en desarrollo de aplicaciones Flutter y diseño de UI/UX. Tu tarea es generar un JSON válido para crear una aplicación Flutter basada en el prompt del usuario.

RESPONDE ÚNICAMENTE CON EL JSON, SIN TEXTO ADICIONAL, SIN EXPLICACIONES, SIN MARKDOWN.
El json debe tener la siguiente estructura:
{
  "name": "Nombre de la App",
  "description": "Descripción de la app",
  "currentPageId": "page-1",
  "pages": [
    {
      "id": "page-1",
      "name": "Nombre de la página",
      "route": "/",
      "widgets": [
        {
          "id": "unique-id",
          "type": "tipo_widget",
          "name": "Nombre del widget",
          "position": {
            "x": número_o_null,
            "y": número
          },
          "size": {
            "width": "100%" o número,
            "height": número
          },
          "properties": {
            // propiedades específicas del widget
          }
        }
      ]
    }
  ],
  "theme": {
    "primaryColor": "#hexcolor",
    "accentColor": "#hexcolor",
    "backgroundColor": "#FFFFFF"
  }
}


TIPOS DE WIDGETS DISPONIBLES:
- text: Para textos y títulos
- button: Para botones de acción  
- textfield: Para campos de entrada de texto
- image: Para imágenes y logos
- icon: Para íconos decorativos
- checkbox: Para opciones múltiples
- switch: Para activar/desactivar funciones
- slider: Para seleccionar valores en rango
- divider: Para separar secciones
- progress: Para mostrar progreso
- chip: Para etiquetas y filtros
- table: Para mostrar datos tabulares (SIEMPRE usar width: "100%")
- radio: Para selección única entre opciones
- checklist: Para listas de tareas o elementos seleccionables
- appbar: Para barra superior de navegación(SIEMPRE usar width: "100%")
- bottomnavbar: Para navegación inferior entre páginas(SIEMPRE usar width: "100%")

PROPIEDADES ESPECÍFICAS:
- text: { "text": "texto", "fontSize": 16, "color": "#000000", "fontWeight": "normal", "textAlign": "left" }
- button: { "text": "texto", "backgroundColor": "#2196F3", "textColor": "#FFFFFF", "fontSize": 16, "borderRadius": 8 }
- textfield: { "placeholder": "texto", "borderColor": "#D1D1D6", "borderRadius": 8 }
- image: { "src": "placeholder", "fit": "cover", "alt": "descripción de la imagen" }
- container: { "color": "#E3F2FD", "padding": 16, "margin": 8, "borderRadius": 4 }
- icon: { "iconName": "star", "size": 24, "color": "#000000" }
- checkbox: { "label": "Checkbox", "value": false, "activeColor": "#2196F3" }
- switch: { "value": false, "activeColor": "#2196F3" }
- slider: { "value": 50, "min": 0, "max": 100, "activeColor": "#2196F3" }
- divider: { "orientation": "horizontal", "thickness": 1, "color": "#E0E0E0" }
- progress: { "value": 0.5, "backgroundColor": "#E0E0E0", "valueColor": "#2196F3" }
- chip: { "label": "Chip", "textColor": "#000000", "backgroundColor": "#E0E0E0", "fontSize": 14 }
- radio: { "label": "Radio Option", "value": false, "activeColor": "#2196F3", "fontSize": 16 }
- table: { "columns": ["Col1", "Col2", "Col3"], "rows": [["data1", "data2", "data3"]], "headerColor": "#2196F3", "headerTextColor": "#FFFFFF", "textColor": "#000000", "fontSize": 14, "width": "100%" }
- checklist: { "items": ["Item 1", "Item 2"], "checkedItems": [0], "itemColor": "#000000", "checkedColor": "#2196F3", "fontSize": 16 }
- appbar: { "title": "App Title", "backgroundColor": "#2196F3", "titleColor": "#FFFFFF", "elevation": 4, "centerTitle": true, "fontSize": 20 }
- bottomnavbar: { "items": ["Home", "Search", "Profile"], "icons": ["home", "search", "person"], "backgroundColor": "#FFFFFF", "selectedColor": "#2196F3", "unselectedColor": "#757575", "fontSize": 14 }

POSICIONAMIENTO INTELIGENTE:
- x: null para widgets que ocupan todo el ancho, número para posicionamiento específico (ej: botones pequeños lado a lado)
- y: número en píxeles desde arriba, incrementa gradualmente (50, 120, 200, etc.)
- width: "100%" para elementos de ancho completo (appbar, bottomnavbar, tablas de datos), número específico para elementos pequeños
- height: número apropiado para el tipo de widget (text: 30-50, button: 50-60, textfield: 50-60, image: 150-200)
- posiciona los widgets de manera que tengan sentido visual 


REGLAS IMPORTANTES:
1. USA TODOS LOS WIDGETS NECESARIOS para hacer la app completa y funcional
2. Para apps complejas: crea múltiples páginas con bottomnavbar
3. SIEMPRE usa appbar en la primera página
4. El text color o color no debe ser #FFFFFF ya que es un color de fondo por defecto blanco que no se va a ver
5. SOLO LOS WIDGETS QUE NECESITAN 100% DEBEN TENER width: "100%" (appbar, bottomnavbar, tablas de datos)
6. Usa colores coherentes con el tema
7. Para imágenes, usa "src": "placeholder" y añade "alt" con descripción detallada del producto/contenido
8. Incluye imágenes relevantes: logos, productos, ilustraciones según el tipo de app
9. Necesito que la interfaz sea atractiva y lo mas profesional posible , que tenga sentido todo lo que se muestra
10. Usa los widgets disponibles y no uses los mismos para todo , podes usar iconos, botones, textos, etc.
11. Ten en cuenta que no debe pasar el alto o ancho de la pantalla , digamos que es un pixel 9 pro o celular asi , cuestion no hace scroll.
12. RESPONDE SOLO CON JSON VÁLIDO, SIN MARKDOWN, SIN EXPLICACIONES"""

        user_prompt = f"""Genera una aplicación Flutter para: {prompt}

Crea una aplicación completa y funcional con:
1. Páginas necesarias para la funcionalidad
2. Widgets apropiados y bien posicionados
3. Colores y diseño atractivo
4. Navegación si es necesaria

Responde SOLO con el JSON válido, sin explicaciones adicionales."""

        try:
            response = self.client.chat.completions.create(
                model="o1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            
            # Extraer el contenido de la respuesta
            content = response.choices[0].message.content.strip()
            
            # Limpiar la respuesta para obtener solo el JSON
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            # Parsear el JSON para validarlo
            try:
                project_json = json.loads(content)
                
                # Procesar imágenes y generar URLs reales
                project_json = self.process_images_in_project(project_json)
                
                return project_json
            except json.JSONDecodeError as e:
                raise ValueError(f"La respuesta de OpenAI no es un JSON válido: {e}")
                
        except Exception as e:
            raise Exception(f"Error al generar proyecto con OpenAI: {str(e)}")
    
    
    def generate_dart_code_from_project(self, base_project: Dict[str, Any], description: str) -> str:
        """
        Genera código Dart funcional completo basado en un proyecto JSON y una descripción usando AI
        """
        
        system_prompt = """Eres un experto desarrollador Flutter. Tu tarea es generar código Dart COMPLETAMENTE FUNCIONAL basado en un proyecto JSON y una descripción adicional.

RESPONDE ÚNICAMENTE CON EL CÓDIGO DART COMPLETO, SIN EXPLICACIONES, SIN MARKDOWN.

INSTRUCCIONES:
1. Analiza el JSON del proyecto base
2. Lee la descripción adicional para entender la funcionalidad requerida
3. Genera código Dart completo y funcional
4. El código debe incluir TODA la lógica de negocio necesaria
5. Implementa state management correcto (StatefulWidget donde sea necesario)
6. Crea métodos funcionales reales (calculadora que calcule, ecommerce que maneje carrito, etc.)

ESTRUCTURA DEL CÓDIGO:
- Importa todas las librerías necesarias
- Crea main() con runApp()
- Implementa MyApp class
- Crea todas las páginas como StatefulWidget o StatelessWidget según necesidad
- Implementa toda la lógica funcional

FUNCIONALIDADES A IMPLEMENTAR SEGÚN EL TIPO:
- CALCULADORA: Operaciones matemáticas reales, manejo de estado, botones funcionales
- ECOMMERCE: Carrito de compras, agregar/quitar productos, total de precios, navegación
- TODO/TAREAS: Agregar/eliminar tareas, marcar como completado, persistencia local
- SOCIAL: Posts, likes, comentarios, navegación entre pantallas
- CUALQUIER APP: Funcionalidad completa según la descripción

REQUISITOS DEL CÓDIGO:
1. Debe compilar sin errores
2. Toda la funcionalidad debe trabajar
3. State management apropiado
4. Navegación entre páginas si es necesario
5. Formularios que validen y procesen datos
6. Botones que ejecuten acciones reales
7. Interfaz responsive y bien diseñada
8. No quiero nada deprecado
EJEMPLOS DE FUNCIONALIDAD:
- Botón "+" en calculadora: suma los números realmente
- Botón "Agregar al carrito": añade producto a lista y actualiza total
- Campo de texto para nueva tarea: agrega tarea a la lista al presionar botón
- Checkbox: cambia estado y actualiza UI

NO USES PLACEHOLDER NI CÓDIGO DUMMY. TODO DEBE SER FUNCIONAL.
NECESITO CÓDIGO DART VÁLIDO Y FUNCIONAL, NADA DEPRECADO NI EXPERIMENTAL.
RESPONDE SOLO CON CÓDIGO DART VÁLIDO Y FUNCIONAL."""

        user_prompt = f"""PROYECTO JSON BASE:
{json.dumps(base_project, indent=2, ensure_ascii=False)}

DESCRIPCIÓN FUNCIONAL:
{description}

Genera el código Dart completo y funcional para esta aplicación Flutter. El código debe implementar TODA la funcionalidad descrita y ser completamente operativo."""

        try:
            response = self.client.chat.completions.create(
                model="o1",
                messages=[
                    {"role": "user", "content": system_prompt + "\n\n" + user_prompt}
                ],
            )
            
            # Extraer el contenido de la respuesta
            dart_code = response.choices[0].message.content.strip()
            
            # Limpiar el código si viene con markdown
            if dart_code.startswith("```dart"):
                dart_code = dart_code.replace("```dart", "").replace("```", "").strip()
            elif dart_code.startswith("```"):
                dart_code = dart_code.replace("```", "").strip()
            
            return dart_code
                
        except Exception as e:
            raise Exception(f"Error al generar código Dart con OpenAI: {str(e)}")
    
    def process_images_in_project(self, project: Dict[str, Any], app_type: str = "default") -> Dict[str, Any]:
        """
        Procesa el proyecto generado y reemplaza las URLs de imágenes placeholder 
        con imágenes reales generadas por DALL-E y subidas a S3
        """
        try:
            # Detectar tipo de app basado en el nombre y descripción
            app_name = project.get('name', '').lower()
            app_description = project.get('description', '').lower()
            
            if any(word in app_name + app_description for word in ['ecommerce', 'shop', 'store', 'product', 'tienda']):
                app_type = 'ecommerce'
            elif any(word in app_name + app_description for word in ['task', 'todo', 'productivity', 'tareas']):
                app_type = 'tasks'
            elif any(word in app_name + app_description for word in ['social', 'chat', 'community']):
                app_type = 'social'
            elif any(word in app_name + app_description for word in ['fitness', 'gym', 'workout', 'exercise']):
                app_type = 'fitness'
            elif any(word in app_name + app_description for word in ['food', 'recipe', 'restaurant', 'delivery', 'comida']):
                app_type = 'food'
            
            # Procesar cada página
            for page in project.get('pages', []):
                for widget in page.get('widgets', []):
                    if widget.get('type') == 'image':
                        # Generar imagen contextual basada en alt o name
                        context = widget.get('properties', {}).get('alt', widget.get('name', 'imagen'))
                        
                        # Determinar tipo de imagen basado en contexto
                        if any(word in context.lower() for word in ['producto', 'product', 'item']):
                            image_type = 'product'
                        elif any(word in context.lower() for word in ['logo', 'brand']):
                            image_type = 'logo'
                        elif any(word in context.lower() for word in ['banner', 'header']):
                            image_type = 'banner'
                        else:
                            image_type = 'image'
                        
                        # Generar imagen
                        image_url = self.image_service.get_image_for_context(
                            app_type, image_type, context
                        )
                        # Actualizar la URL de la imagen
                        widget['properties']['src'] = image_url
                    
                    elif widget.get('type') == 'table':
                        # Solo procesar imágenes en tablas de datos reales, no catálogos
                        columns = widget.get('properties', {}).get('columns', [])
                        if 'image' in str(columns).lower() or 'imagen' in str(columns).lower():
                            rows = widget.get('properties', {}).get('rows', [])
                            for row in rows:
                                # Buscar columnas que podrían contener URLs de imagen
                                for i, cell in enumerate(row):
                                    if isinstance(cell, str) and ('placeholder' in cell or 'http' in cell):
                                        # Generar imagen basada en el contexto de la fila
                                        context = ' '.join(str(c) for c in row if c != cell)
                                        image_url = self.image_service.get_image_for_context(
                                            app_type, 'product', context
                                        )
                                        row[i] = image_url
            
            return project
            
        except Exception as e:
            print(f"Error procesando imágenes: {str(e)}")
            return project  # Retornar proyecto original si falla
    
    def validate_project_structure(self, project: Dict[str, Any]) -> bool:
        """
        Valida que el proyecto generado tenga la estructura correcta
        """
        required_fields = ["name", "description", "currentPageId", "pages", "theme"]
        
        for field in required_fields:
            if field not in project:
                return False
        
        if not isinstance(project["pages"], list) or len(project["pages"]) == 0:
            return False
        
        for page in project["pages"]:
            page_required = ["id", "name", "route", "widgets"]
            for field in page_required:
                if field not in page:
                    return False
        
        return True
        
    def generate_project_from_image(self, image_base64: str, description: str = "") -> Dict[str, Any]:
        """
        Genera un proyecto Flutter basado en una imagen de interfaz de usuario
        
        Args:
            image_base64: Imagen en formato base64
            description: Descripción opcional para dar contexto (no es necesaria)
        
        Returns:
            Dict con la estructura del proyecto Flutter
        """
        # No necesitamos usar la descripción, generaremos el JSON directamente de la imagen
            
        system_prompt = """Eres un experto en desarrollo de aplicaciones Flutter y diseño de UI/UX. Tu tarea es analizar la imagen de una interfaz de usuario y convertirla en un JSON válido para crear una aplicación Flutter.

RESPONDE ÚNICAMENTE CON EL JSON, SIN TEXTO ADICIONAL, SIN EXPLICACIONES, SIN MARKDOWN.
El json debe tener la siguiente estructura:
{
  "name": "Nombre de la App",
  "description": "Descripción de la app",
  "currentPageId": "page-1",
  "pages": [
    {
      "id": "page-1",
      "name": "Nombre de la página",
      "route": "/",
      "widgets": [
        {
          "id": "unique-id",
          "type": "tipo_widget",
          "name": "Nombre del widget",
          "position": {
            "x": número_o_null,
            "y": número
          },
          "size": {
            "width": "100%" o número,
            "height": número
          },
          "properties": {
            // propiedades específicas del widget
          }
        }
      ]
    }
  ],
  "theme": {
    "primaryColor": "#hexcolor",
    "accentColor": "#hexcolor",
    "backgroundColor": "#FFFFFF"
  }
}

TIPOS DE WIDGETS DISPONIBLES:
- text: Para textos y títulos
- button: Para botones de acción  
- textfield: Para campos de entrada de texto
- icon: Para íconos decorativos
- checkbox: Para opciones múltiples
- switch: Para activar/desactivar funciones
- slider: Para seleccionar valores en rango
- divider: Para separar secciones
- progress: Para mostrar progreso
- chip: Para etiquetas y filtros
- table: Para mostrar datos tabulares (SIEMPRE usar width: "100%")
- radio: Para selección única entre opciones
- checklist: Para listas de tareas o elementos seleccionables
- appbar: Para barra superior de navegación(SIEMPRE usar width: "100%")
- bottomnavbar: Para navegación inferior entre páginas(SIEMPRE usar width: "100%")
- dropdown: Para listas desplegables de opciones

PROPIEDADES ESPECÍFICAS:
- text: { "text": "texto", "fontSize": 16, "color": "#000000", "fontWeight": "normal", "textAlign": "left" }
- button: { "text": "texto", "backgroundColor": "#2196F3", "textColor": "#FFFFFF", "fontSize": 16, "borderRadius": 8 }
- textfield: { "placeholder": "texto", "borderColor": "#D1D1D6", "borderRadius": 8 }
- container: { "color": "#E3F2FD", "padding": 16, "margin": 8, "borderRadius": 4 }
- icon: { "iconName": "star", "size": 24, "color": "#000000" }
- checkbox: { "label": "Checkbox", "value": false, "activeColor": "#2196F3" }
- switch: { "value": false, "activeColor": "#2196F3" }
- slider: { "value": 50, "min": 0, "max": 100, "activeColor": "#2196F3" }
- divider: { "orientation": "horizontal", "thickness": 1, "color": "#E0E0E0" }
- progress: { "value": 0.5, "backgroundColor": "#E0E0E0", "valueColor": "#2196F3" }
- chip: { "label": "Chip", "textColor": "#000000", "backgroundColor": "#E0E0E0", "fontSize": 14 }
- radio: { "label": "Radio Option", "value": false, "activeColor": "#2196F3", "fontSize": 16 }
- table: { "columns": ["Col1", "Col2", "Col3"], "rows": [["data1", "data2", "data3"]], "headerColor": "#2196F3", "headerTextColor": "#FFFFFF", "textColor": "#000000", "fontSize": 14, "width": "100%" }
- checklist: { "items": ["Item 1", "Item 2"], "checkedItems": [0], "itemColor": "#000000", "checkedColor": "#2196F3", "fontSize": 16 }
- appbar: { "title": "App Title", "backgroundColor": "#2196F3", "titleColor": "#FFFFFF", "elevation": 4, "centerTitle": true, "fontSize": 20 }
- bottomnavbar: { "items": ["Home", "Search", "Profile"], "icons": ["home", "search", "person"], "backgroundColor": "#FFFFFF", "selectedColor": "#2196F3", "unselectedColor": "#757575", "fontSize": 14 }
- dropdown: { "items": ["Option 1", "Option 2"], "placeholder": "Select option", "backgroundColor": "#FFFFFF", "borderColor": "#CCCCCC", "textColor": "#000000", "fontSize": 14 }

POSICIONAMIENTO INTELIGENTE (VALORES OBLIGATORIOS):
- x: null SOLO para widgets de ancho completo (appbar, bottomnavbar, table), números específicos como 20, 50, 100 para otros
- y: OBLIGATORIO número en píxeles desde arriba (ej: 50, 120, 200, 280) - JAMÁS usar null
- width: "100%" para elementos de ancho completo O números específicos como 200, 300, 150 - JAMÁS usar null  
- height: OBLIGATORIO números específicos según widget (text: 30-40, button: 48-56, textfield: 48-56, image: 120-200, icon: 24-48) - JAMÁS usar null

EJEMPLOS DE POSICIONAMIENTO CORRECTO:
- Texto título: {"x": null, "y": 60}, {"width": "100%", "height": 40}
- Botón pequeño: {"x": 50, "y": 120}, {"width": 120, "height": 48}
- Campo de texto: {"x": 20, "y": 180}, {"width": 280, "height": 50}
- AppBar: {"x": null, "y": 0}, {"width": "100%", "height": 56}

REGLAS CRÍTICAS:
1. ANALIZA cada elemento visual de la imagen y asigna posiciones Y valores ESPECÍFICOS
2. CALCULA posiciones reales basadas en la disposición visual de la imagen
3. El text color o color no debe ser #FFFFFF ya que es un color de fondo por defecto blanco que no se va a ver
3. USA números concretos, NO null en width/height
4. Si hay texto en la imagen, transcríbelo EXACTAMENTE
5. Respeta colores y estilos visuales de la imagen
6. Posiciona elementos de forma que coincidan con la imagen original
7. CADA widget DEBE tener valores numéricos válidos en size
8. NUNCA uses null en width o height - siempre números o "100%"
9. Distribuye elementos con espaciado visual apropiado (y: 50, 120, 190, 260, etc.)
10. RESPONDE SOLO CON JSON VÁLIDO, SIN MARKDOWN, SIN EXPLICACIONES"""
        
        user_prompt = """Analiza cuidadosamente esta imagen de interfaz de usuario y conviértela en una configuración JSON para Flutter.

Identifica todos los elementos presentes en la imagen:
- Textos y sus estilos
- Botones y sus colores
- Campos de entrada
- Imágenes y íconos
- Elementos de navegación
- Colores y tema general

Mapea cada elemento a un widget de Flutter apropiado, respetando las posiciones y estilos visuales de la imagen original.

Responde SOLO con el JSON válido, sin explicaciones adicionales."""
        
        try:
            # Llamar a la API de OpenAI con la imagen
            response = self.client.chat.completions.create(
                model="o1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
            )
            
            # Extraer el JSON del mensaje de respuesta
            json_content = response.choices[0].message.content.strip()
            
            # Limpiar el contenido JSON si tiene formateo Markdown
            if json_content.startswith("```json"):
                json_content = json_content.split("```json")[1]
            if "```" in json_content:
                json_content = json_content.split("```")[0]
                
            # Parsear el JSON
            project_data = json.loads(json_content)
            
            # Retornar el proyecto directamente sin validaciones complejas
            return project_data
            
        except Exception as e:
            # En caso de error, crear un proyecto mínimo
            raise Exception(f"Error generando proyecto desde imagen: {str(e)}")
    
    def generate_project_from_audio(self, audio_content: bytes, audio_filename: str) -> Dict[str, Any]:
        """
        Genera un proyecto Flutter basado en una descripción de audio usando Whisper
        
        Args:
            audio_content: Contenido del archivo de audio en bytes
            audio_filename: Nombre del archivo de audio
        
        Returns:
            Dict con la estructura del proyecto Flutter
        """
        
        try:
            # Guardar temporalmente el archivo de audio
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_filename)[1]) as temp_audio:
                temp_audio.write(audio_content)
                temp_audio_path = temp_audio.name
            
            try:
                # Transcribir el audio usando Whisper
                with open(temp_audio_path, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="es"  # Configurar para español, cambia si necesitas otro idioma
                    )
                
                transcribed_text = transcript.text
                
                # Usar el texto transcrito para generar el proyecto
                project_data = self.generate_project_from_prompt(transcribed_text)
                
                return project_data
                
            finally:
                # Limpiar el archivo temporal
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                    
        except Exception as e:
            raise Exception(f"Error generando proyecto desde audio: {str(e)}")
