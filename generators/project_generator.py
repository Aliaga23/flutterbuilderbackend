from jinja2 import Environment, FileSystemLoader
from models.project import FlutterProject, Page
from generators.widget_generator import WidgetGenerator
from utils.converters import hex_to_dart_color
import os
import zipfile
import tempfile
import shutil

class ProjectGenerator:
    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.widget_generator = WidgetGenerator(template_dir)
    
    def generate_flutter_project(self, project: FlutterProject) -> str:
        """Generate complete Flutter project and return ZIP file path"""
        # Create temporary directory for the project
        temp_dir = tempfile.mkdtemp()
        project_name = project.name.lower().replace(' ', '_')
        project_dir = os.path.join(temp_dir, project_name)
        
        try:
            # Copy base template instead of using flutter create
            self._copy_base_template(project_dir)
            
            # Override generated files with our custom content
            self._generate_main_dart(project, project_dir)
            self._generate_pages(project, project_dir)
            self._update_pubspec(project, project_dir)
            
            # Create ZIP file
            zip_path = self._create_zip(project_dir, project.name)
            
            return zip_path
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise e
    
    def _copy_base_template(self, project_dir: str):
        """Copy the base Flutter template to project directory"""
        base_template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flutter_base_template')
        
        if not os.path.exists(base_template_path):
            raise Exception(f"Base template not found at {base_template_path}")
        
        # Copy the entire base template
        shutil.copytree(base_template_path, project_dir)
    
    
    def _update_pubspec(self, project: FlutterProject, project_dir: str):
        """Update pubspec.yaml with project-specific information"""
        template = self.env.get_template('pubspec.yaml.j2')
        
        # Check if project has images to determine if we need cached_network_image
        has_images = False
        if project.pages:
            for page in project.pages:
                if page.widgets:
                    for widget in page.widgets:
                        if widget.type == 'image':
                            has_images = True
                            break
                if has_images:
                    break
        
        content = template.render(
            project_name=project.name.lower().replace(' ', '_'),
            description=project.description or f"A new Flutter project: {project.name}",
            version=project.version or "1.0.0+1",
            has_images=has_images
        )
        
        pubspec_path = os.path.join(project_dir, 'pubspec.yaml')
        with open(pubspec_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
    
    def _generate_main_dart(self, project: FlutterProject, project_dir: str):
        """Generate main.dart file"""
        # Make sure the lib directory exists even if it's missing from the base template
        os.makedirs(os.path.join(project_dir, 'lib'), exist_ok=True)
        
        template = self.env.get_template('main.dart.j2')
        
        # Get the first page as the initial route
        initial_page = project.pages[0] if project.pages else None
        initial_route = f"/{initial_page.name}" if initial_page else "/"
        
        # Generate imports for all pages
        page_imports = []
        routes = {}
        
        for page in project.pages:
            page_class_name = f"{page.name.title().replace(' ', '')}Page"
            page_imports.append(f"import 'pages/{page.name.lower().replace(' ', '_')}_page.dart';")
            routes[f"/{page.name}"] = page_class_name
        
        content = template.render(
            app_name=project.name,
            page_imports=page_imports,
            initial_route=initial_route,
            routes=routes,
            theme_primary_color=project.theme.primaryColor if project.theme else "#2196F3"
        )
        
        with open(os.path.join(project_dir, 'lib', 'main.dart'), 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_pages(self, project: FlutterProject, project_dir: str):
        """Generate all page files"""
        # Create pages directory if it doesn't exist
        pages_dir = os.path.join(project_dir, 'lib', 'pages')
        os.makedirs(pages_dir, exist_ok=True)
        
        for page in project.pages:
            self._generate_page(page, project, project_dir)
    
    def _generate_page(self, page: Page, project: FlutterProject, project_dir: str):
        """Generate individual page file"""
        template = self.env.get_template('page.dart.j2')
        
        # Separate widgets by type
        regular_widgets = []
        appbar_widget = None
        bottomnav_widget = None
        
        for widget in page.widgets:
            if widget.type == 'appbar':
                appbar_widget = widget
            elif widget.type == 'bottomnavbar':
                bottomnav_widget = widget
            else:
                widget_code = self.widget_generator.generate_widget(
                    widget, 
                    page.screen_width or 390, 
                    page.screen_height or 844
                )
                regular_widgets.append(widget_code)
        
        # Generate appbar and bottomnav code
        appbar_code = None
        bottomnav_code = None
        page_routes = []
        
        if appbar_widget:
            appbar_code = self.widget_generator.generate_widget(appbar_widget)
        
        if bottomnav_widget:
            bottomnav_code = self.widget_generator.generate_widget(bottomnav_widget)
            # Extract routes from project pages for bottomnav navigation
            page_routes = [f"/{p.name}" for p in project.pages]
        
        # Calculate current nav index for this page
        current_nav_index = 0
        if bottomnav_widget and page_routes:
            current_route = f"/{page.name}"
            if current_route in page_routes:
                current_nav_index = page_routes.index(current_route)
        
        page_class_name = f"{page.name.title().replace(' ', '')}Page"
        file_name = f"{page.name.lower().replace(' ', '_')}_page.dart"
        
        content = template.render(
            page_class_name=page_class_name,
            page_title=page.name,
            background_color=hex_to_dart_color(page.background_color or "#FFFFFF"),
            widgets=regular_widgets,
            appbar=appbar_code,
            bottomnav=bottomnav_code,
            page_routes=page_routes,
            current_nav_index=current_nav_index,
            screen_width=page.screen_width or 390,
            screen_height=page.screen_height or 844
        )
        
        
        page_path = os.path.join(project_dir, 'lib', 'pages', file_name)
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_zip(self, project_dir: str, project_name: str) -> str:
        """Create ZIP file from project directory"""
        zip_path = os.path.join(tempfile.gettempdir(), f"{project_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate relative path for the zip
                    relative_path = os.path.relpath(file_path, project_dir)
                    zipf.write(file_path, relative_path)
        
        return zip_path
    
    def cleanup_temp_files(self, zip_path: str):
        """Clean up temporary files after sending ZIP"""
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            # Also clean up the temp directory if it still exists
            temp_dir = os.path.dirname(os.path.dirname(zip_path))
            if os.path.exists(temp_dir) and 'tmp' in temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not clean up temporary files: {e}")
