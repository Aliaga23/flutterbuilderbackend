from models.project import Position, Size

def hex_to_dart_color(hex_color: str) -> str:
    """Convert hex color to Dart Color"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    return f"Color(0xFF{hex_color.upper()})"

def convert_position_to_flutter(position: Position, size: Size, screen_width: float, screen_height: float) -> dict:
    """Convert position to responsive coordinates based on current screen"""
    
    # Handle null positions (for full-width widgets like appbar, bottomnav)
    if position.x is None:
        left = "0.0"
    else:
        # Convert to percentage of current screen width
        left_percent = position.x / screen_width if screen_width > 0 else 0
        left = f"MediaQuery.of(context).size.width * {left_percent:.6f}"
    
    if position.y is None:
        top = "0.0"
    else:
        # Convert to percentage of current screen height  
        top_percent = position.y / screen_height if screen_height > 0 else 0
        top = f"MediaQuery.of(context).size.height * {top_percent:.6f}"
    
    # Convert sizes to responsive percentages
    if isinstance(size.width, str) and size.width.endswith('%'):
        if size.width == "100%":
            width = "MediaQuery.of(context).size.width"
        else:
            percent = float(size.width.replace('%', '')) / 100
            width = f"MediaQuery.of(context).size.width * {percent:.6f}"
    else:
        # Convert pixel width to percentage of current screen
        width_percent = float(size.width) / screen_width if screen_width > 0 else 0.2
        width = f"MediaQuery.of(context).size.width * {width_percent:.6f}"
    
    if isinstance(size.height, str) and size.height.endswith('%'):
        if size.height == "100%":
            height = "MediaQuery.of(context).size.height"
        else:
            percent = float(size.height.replace('%', '')) / 100
            height = f"MediaQuery.of(context).size.height * {percent:.6f}"
    else:
        # Convert pixel height to percentage of current screen
        height_percent = float(size.height) / screen_height if screen_height > 0 else 0.1
        height = f"MediaQuery.of(context).size.height * {height_percent:.6f}"
    
    return {
        'left': left,
        'top': top,
        'width': width,
        'height': height
    }

def get_icon_mapping() -> dict:
    """Get mapping of icon names to Material Icons"""
    return {
        'star': 'Icons.star',
        'home': 'Icons.home',
        'search': 'Icons.search',
        'user': 'Icons.person',
        'settings': 'Icons.settings',
        'heart': 'Icons.favorite',
        'plus': 'Icons.add',
        'minus': 'Icons.remove',
        'check': 'Icons.check',
        'close': 'Icons.close',
        'menu': 'Icons.menu',
        'edit': 'Icons.edit',
        'delete': 'Icons.delete',
        'camera': 'Icons.camera_alt',
        'phone': 'Icons.phone',
        'mail': 'Icons.email',
        'lock': 'Icons.lock',
        'calendar': 'Icons.calendar_today',
        'location': 'Icons.location_on'
    }

def get_font_weight_mapping() -> dict:
    """Get mapping of font weights"""
    return {
        'normal': 'FontWeight.normal',
        'bold': 'FontWeight.bold',
        '300': 'FontWeight.w300',
        '500': 'FontWeight.w500',
        '600': 'FontWeight.w600',
        '700': 'FontWeight.w700'
    }

def get_text_align_mapping() -> dict:
    """Get mapping of text alignment"""
    return {
        'left': 'TextAlign.left',
        'center': 'TextAlign.center',
        'right': 'TextAlign.right',
        'justify': 'TextAlign.justify'
    }

def get_box_fit_mapping() -> dict:
    """Get mapping of box fit values"""
    return {
        'cover': 'BoxFit.cover',
        'contain': 'BoxFit.contain',
        'fill': 'BoxFit.fill',
        'fitWidth': 'BoxFit.fitWidth',
        'fitHeight': 'BoxFit.fitHeight'
    }

def convert_table_position_to_flutter(position: Position, size: Size, screen_width: float, screen_height: float) -> dict:
    """Convert position to responsive coordinates for tables - always full width"""
    
    # Tables should always start from left edge
    left = "0.0"
    
    if position.y is None:
        top = "0.0"
    else:
        # Convert to percentage of current screen height  
        top_percent = position.y / screen_height if screen_height > 0 else 0
        top = f"MediaQuery.of(context).size.height * {top_percent:.6f}"
    
    # Tables always occupy full width
    width = "MediaQuery.of(context).size.width"
    
    # Handle height conversion
    if isinstance(size.height, str) and size.height.endswith('%'):
        if size.height == "100%":
            height = "MediaQuery.of(context).size.height"
        else:
            percent = float(size.height.replace('%', '')) / 100
            height = f"MediaQuery.of(context).size.height * {percent:.6f}"
    else:
        # Convert pixel height to percentage of current screen
        height_percent = float(size.height) / screen_height if screen_height > 0 else 0.3
        height = f"MediaQuery.of(context).size.height * {height_percent:.6f}"
    
    return {
        'left': left,
        'top': top,
        'width': width,
        'height': height
    }
