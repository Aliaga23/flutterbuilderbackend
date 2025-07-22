from jinja2 import Environment, FileSystemLoader
from models.project import FlutterWidget
from utils.converters import (
    hex_to_dart_color, 
    convert_position_to_flutter,
    get_icon_mapping,
    get_font_weight_mapping,
    get_text_align_mapping,
    get_box_fit_mapping
)
import os

class WidgetGenerator:
    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.icon_map = get_icon_mapping()
        self.font_weight_map = get_font_weight_mapping()
        self.text_align_map = get_text_align_mapping()
        self.box_fit_map = get_box_fit_mapping()
    
    def generate_widget(self, widget: FlutterWidget, screen_width: float = 390, screen_height: float = 844) -> str:
        """Generate Flutter widget code using templates"""
        props = widget.properties
        responsive_pos = convert_position_to_flutter(widget.position, widget.size, screen_width, screen_height)
        
        widget_content = self._generate_widget_content(widget, responsive_pos, screen_width, screen_height)
        
        # Special widgets that shouldn't be wrapped in Positioned
        if widget.type in ['appbar', 'bottomnavbar']:
            return widget_content
        
        # Wrap in positioned widget for regular widgets
        wrapper_template = self.env.get_template('widget_wrapper.dart.j2')
        return wrapper_template.render(
            left=responsive_pos['left'],
            top=responsive_pos['top'],
            widget_content=widget_content
        )
    
    def _generate_widget_content(self, widget: FlutterWidget, responsive_pos: dict, screen_width: float = 390, screen_height: float = 844) -> str:
        """Generate the actual widget content based on type"""
        props = widget.properties
        widget_id = widget.id
        
        if widget.type == 'text':
            return self._generate_text_widget(props)
        elif widget.type == 'button':
            return self._generate_button_widget(props, responsive_pos)
        elif widget.type == 'textfield':
            return self._generate_textfield_widget(props, responsive_pos, widget_id)
        elif widget.type == 'image':
            return self._generate_image_widget(props, responsive_pos)
        elif widget.type == 'container':
            return self._generate_container_widget(props, responsive_pos)
        elif widget.type == 'icon':
            return self._generate_icon_widget(props)
        elif widget.type == 'checkbox':
            return self._generate_checkbox_widget(props, responsive_pos)
        elif widget.type == 'switch':
            return self._generate_switch_widget(props, responsive_pos, widget_id)
        elif widget.type == 'slider':
            return self._generate_slider_widget(props, responsive_pos, widget_id)
        elif widget.type == 'divider':
            return self._generate_divider_widget(props, responsive_pos)
        elif widget.type == 'progress':
            return self._generate_progress_widget(props, responsive_pos)
        elif widget.type == 'chip':
            return self._generate_chip_widget(props)
        elif widget.type == 'table':
            # Use special converter for tables to ensure full width
            from utils.converters import convert_table_position_to_flutter
            table_responsive_pos = convert_table_position_to_flutter(widget.position, widget.size, screen_width, screen_height)
            return self._generate_table_widget(props, table_responsive_pos)
        elif widget.type == 'radio':
            return self._generate_radio_widget(props, responsive_pos, widget_id)
        elif widget.type == 'checklist':
            return self._generate_checklist_widget(props, responsive_pos, widget_id)
        elif widget.type == 'dropdown':
            return self._generate_dropdown_widget(props, responsive_pos)
        elif widget.type == 'appbar':
            return self._generate_appbar_widget(props)
        elif widget.type == 'bottomnavbar':
            return self._generate_bottomnav_widget(props)
        else:
            return self._generate_default_widget(widget, responsive_pos)
    
    def _generate_text_widget(self, props: dict) -> str:
        template = self.env.get_template('widgets/text.dart.j2')
        # Convert font size to responsive ratio (font_size / screen_width)
        font_size_ratio = props.get('fontSize', 16) / 390  # 390 is reference width
        return template.render(
            text=props.get('text', 'Text'),
            font_size_ratio=f"{props.get('fontSize', 16) / 390:.6f}",
            color=hex_to_dart_color(props.get('color', '#000000')),
            font_weight=self.font_weight_map.get(props.get('fontWeight', 'normal'), 'FontWeight.normal'),
            text_align=self.text_align_map.get(props.get('textAlign', 'left'), 'TextAlign.left')
        )
    
    def _generate_button_widget(self, props: dict, responsive_pos: dict) -> str:
        template = self.env.get_template('widgets/button.dart.j2')
        return template.render(
            text=props.get('text', 'Button'),
            bg_color=hex_to_dart_color(props.get('backgroundColor', '#2196F3')),
            text_color=hex_to_dart_color(props.get('textColor', '#FFFFFF')),
            font_size_px=props.get('fontSize', 16),
            border_radius_px=props.get('borderRadius', 8),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_textfield_widget(self, props: dict, responsive_pos: dict, widget_id: str) -> str:
        template = self.env.get_template('widgets/textfield.dart.j2')
        return template.render(
            widget_id=widget_id,
            placeholder=props.get('placeholder', 'Enter text...'),
            border_color=hex_to_dart_color(props.get('borderColor', '#D1D1D6')),
            border_radius_px=props.get('borderRadius', 8),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_image_widget(self, props: dict, responsive_pos: dict) -> str:
        template = self.env.get_template('widgets/image.dart.j2')
        return template.render(
            src=props.get('src', 'https://via.placeholder.com/150'),
            fit=self.box_fit_map.get(props.get('fit', 'cover'), 'BoxFit.cover'),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_container_widget(self, props: dict, responsive_pos: dict) -> str:
        template = self.env.get_template('widgets/container.dart.j2')
        return template.render(
            color=hex_to_dart_color(props.get('color', '#E3F2FD')),
            padding_px=props.get('padding', 16),
            margin_px=props.get('margin', 8),
            border_radius_px=props.get('borderRadius', 4),
            width=responsive_pos['width'],
            height=responsive_pos['height'],
            has_child=False,
            child_content=""
        )
    
    def _generate_icon_widget(self, props: dict) -> str:
        template = self.env.get_template('widgets/icon.dart.j2')
        icon_name = props.get('iconName', 'star')
        return template.render(
            icon=self.icon_map.get(icon_name.lower(), 'Icons.star'),
            size_px=props.get('size', 24),
            color=hex_to_dart_color(props.get('color', '#000000'))
        )
    
    def _generate_checkbox_widget(self, props: dict, responsive_pos: dict) -> str:
        template = self.env.get_template('widgets/checkbox.dart.j2')
        return template.render(
            label=props.get('label', 'Checkbox'),
            value=str(props.get('value', False)).lower(),
            active_color=hex_to_dart_color(props.get('activeColor', '#2196F3')),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_switch_widget(self, props: dict, responsive_pos: dict, widget_id: str) -> str:
        template = self.env.get_template('widgets/switch.dart.j2')
        return template.render(
            widget_id=widget_id,
            value=str(props.get('value', False)).lower(),
            active_color=hex_to_dart_color(props.get('activeColor', '#2196F3')),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_slider_widget(self, props: dict, responsive_pos: dict, widget_id: str) -> str:
        template = self.env.get_template('widgets/slider.dart.j2')
        return template.render(
            widget_id=widget_id,
            value=props.get('value', 50),
            min=props.get('min', 0),
            max=props.get('max', 100),
            active_color=hex_to_dart_color(props.get('activeColor', '#2196F3')),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_divider_widget(self, props: dict, responsive_pos: dict) -> str:
        template = self.env.get_template('widgets/divider.dart.j2')
        return template.render(
            orientation=props.get('orientation', 'horizontal'),
            thickness_px=props.get('thickness', 1),
            color=hex_to_dart_color(props.get('color', '#E0E0E0')),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_progress_widget(self, props: dict, responsive_pos: dict) -> str:
        template = self.env.get_template('widgets/progress.dart.j2')
        return template.render(
            value=props.get('value', 0.5),
            background_color=hex_to_dart_color(props.get('backgroundColor', '#E0E0E0')),
            value_color=hex_to_dart_color(props.get('valueColor', '#2196F3')),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_chip_widget(self, props: dict) -> str:
        template = self.env.get_template('widgets/chip.dart.j2')
        return template.render(
            label=props.get('label', 'Chip'),
            text_color=hex_to_dart_color(props.get('textColor', '#000000')),
            background_color=hex_to_dart_color(props.get('backgroundColor', '#E0E0E0')),
            font_size_px=props.get('fontSize', 14)
        )
    
    def _generate_table_widget(self, props: dict, responsive_pos: dict) -> str:
        template = self.env.get_template('widgets/table.dart.j2')
        
        return template.render(
            columns=props.get('columns', ['Column 1', 'Column 2']),
            rows=props.get('rows', [['Data 1', 'Data 2']]),
            header_color=hex_to_dart_color(props.get('headerColor', '#2196F3')),
            header_text_color=hex_to_dart_color(props.get('headerTextColor', '#FFFFFF')),
            text_color=hex_to_dart_color(props.get('textColor', '#000000')),
            row_color=hex_to_dart_color(props.get('rowColor', '#FFFFFF')),
            alternate_row_color=hex_to_dart_color(props.get('alternateRowColor', '#F5F5F5')),
            border_color=hex_to_dart_color(props.get('borderColor', '#E0E0E0')),
            font_size_px=props.get('fontSize', 14),
            padding_px=props.get('padding', 8),
            show_borders=props.get('showBorders', True),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_radio_widget(self, props: dict, responsive_pos: dict, widget_id: str) -> str:
        template = self.env.get_template('widgets/radio.dart.j2')
        return template.render(
            widget_id=widget_id,
            label=props.get('label', 'Radio Option'),
            value=str(props.get('value', False)).lower(),
            active_color=hex_to_dart_color(props.get('activeColor', '#2196F3')),
            font_size_px=props.get('fontSize', 16),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_checklist_widget(self, props: dict, responsive_pos: dict, widget_id: str) -> str:
        template = self.env.get_template('widgets/checklist.dart.j2')
        items = props.get('items', ['Task 1', 'Task 2', 'Task 3'])
        checked_items = props.get('checkedItems', [0])
        item_color = hex_to_dart_color(props.get('itemColor', '#000000'))
        checked_color = hex_to_dart_color(props.get('checkedColor', '#2196F3'))
        
        # Prepare items with checked status
        template_items = []
        for i, item in enumerate(items):
            is_checked = i in checked_items
            template_items.append({
                'text': item,
                'checked': str(is_checked).lower()
            })
        
        return template.render(
            widget_id=widget_id,
            items=template_items,
            item_color=item_color,
            checked_color=checked_color,
            font_size_px=props.get('fontSize', 16),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_appbar_widget(self, props: dict) -> str:
        template = self.env.get_template('widgets/appbar.dart.j2')
        return template.render(
            title=props.get('title', 'App Title'),
            background_color=hex_to_dart_color(props.get('backgroundColor', '#2196F3')),
            title_color=hex_to_dart_color(props.get('titleColor', '#FFFFFF')),
            elevation=props.get('elevation', 4),
            center_title=str(props.get('centerTitle', True)).lower(),
            font_size_px=props.get('fontSize', 20)
        )
    
    def _generate_bottomnav_widget(self, props: dict) -> str:
        template = self.env.get_template('widgets/bottomnav.dart.j2')
        items = props.get('items', ['Home'])
        icons = props.get('icons', ['home'])
        
        # Prepare items with icons
        template_items = []
        for item, icon in zip(items, icons):
            icon_name = self.icon_map.get(icon.lower(), 'Icons.home')
            template_items.append({
                'icon': icon_name,
                'label': item
            })
        
        return template.render(
            items=template_items,
            background_color=hex_to_dart_color(props.get('backgroundColor', '#FFFFFF')),
            selected_color=hex_to_dart_color(props.get('selectedColor', '#2196F3')),
            unselected_color=hex_to_dart_color(props.get('unselectedColor', '#757575')),
            font_size_px=props.get('fontSize', 14)
        )
        
    def _generate_dropdown_widget(self, props: dict, responsive_pos: dict) -> str:
        template = self.env.get_template('widgets/dropdown.dart.j2')
        return template.render(
            items=props.get('items', ['Option 1', 'Option 2', 'Option 3']),
            placeholder=props.get('placeholder', 'Select an option'),
            background_color=hex_to_dart_color(props.get('backgroundColor', '#FFFFFF')),
            border_color=hex_to_dart_color(props.get('borderColor', '#CCCCCC')),
            text_color=hex_to_dart_color(props.get('textColor', '#000000')),
            arrow_color=hex_to_dart_color(props.get('arrowColor', '#757575')),
            font_size_px=props.get('fontSize', 14),
            border_radius=props.get('borderRadius', 4),
            border_width=props.get('borderWidth', 1),
            width=responsive_pos['width'],
            height=responsive_pos['height']
        )
    
    def _generate_default_widget(self, widget: FlutterWidget, responsive_pos: dict) -> str:
        return f"""Container(
            width: {responsive_pos['width']},
            height: {responsive_pos['height']},
            color: Colors.grey[300],
            child: Center(
              child: Text(
                '{widget.type}',
                style: TextStyle(color: Colors.grey[600]),
              ),
            ),
          )"""
