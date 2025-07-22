from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional, Union

class Position(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None

class Size(BaseModel):
    width: Union[float, str]
    height: Union[float, str]
    
    @field_validator('width', 'height')
    @classmethod
    def convert_percentage(cls, v):
        if isinstance(v, str) and v.endswith('%'):
            # Convert percentage to a large number for full width/height
            return 1000.0 if v == "100%" else float(v.replace('%', ''))
        return float(v) if v is not None else 0.0

class FlutterWidget(BaseModel):
    id: str
    type: str
    name: str
    position: Position
    size: Size
    properties: Dict[str, Any]
    children: Optional[List['FlutterWidget']] = None
    parentId: Optional[str] = None

class Page(BaseModel):
    id: str
    name: str
    widgets: List[FlutterWidget]
    route: str
    screen_width: Optional[float] = 390
    screen_height: Optional[float] = 844
    background_color: Optional[str] = "#FFFFFF"

class Theme(BaseModel):
    primaryColor: str
    accentColor: str
    backgroundColor: str

class FlutterProject(BaseModel):
    name: str
    description: Optional[str] = None
    pages: List[Page]
    currentPageId: str
    theme: Theme
    version: Optional[str] = "1.0.0+1"

# Update forward references
FlutterWidget.model_rebuild()
