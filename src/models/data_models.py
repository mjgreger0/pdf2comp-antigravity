from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict

class Datasheet(BaseModel):
    id: Optional[int] = None
    filename: str
    file_hash: str
    title: Optional[str] = None
    revision: Optional[str] = None
    document_date: Optional[date] = None
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class Component(BaseModel):
    id: Optional[int] = None
    datasheet_id: int
    part_number: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class Package(BaseModel):
    id: Optional[int] = None
    component_id: int
    name: str
    package_type: Optional[str] = None
    dimensions: Optional[Dict[str, float]] = Field(default_factory=dict, description="IPC-7351 dimensions")
    model_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="CadQuery params")
    
    model_config = ConfigDict(from_attributes=True)

class Pin(BaseModel):
    id: Optional[int] = None
    package_id: int
    number: str
    name: Optional[str] = None
    electrical_type: Optional[str] = None
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class CorrectionLog(BaseModel):
    id: Optional[int] = None
    task_type: str
    input_context: str
    llm_output: Optional[Dict[str, Any]] = None
    user_corrected_output: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
