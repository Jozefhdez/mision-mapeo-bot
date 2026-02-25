"""
Modelos Pydantic para validación de datos de iniciativas.
Basado en DATA_MODEL.md
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Initiative(BaseModel):
    """Modelo principal de una iniciativa socioambiental."""
    
    # Información General
    nombre: str = Field(..., min_length=3, max_length=200)
    descripcion: str = Field(..., min_length=50)
    categoria: str = Field(...)
    etiquetas: List[str] = Field(..., min_length=3, max_length=5)
    
    # Clasificación del Proyecto
    tipo_proyecto: str = Field(...)
    tipo_enfoque: str = Field(...)
    descripcion_enfoque: str = Field(..., min_length=200)
    ods: str = Field(...)
    
    # Características Operativas
    fuente_recursos: str = Field(...)
    sector_economico: str = Field(...)
    cobertura: str = Field(...)
    estatus: str = Field(...)
    tamano: str = Field(...)
    
    # Ubicación Geográfica
    ubicacion: str = Field(...)
    pais: str = Field(...)
    region: str = Field(...)
    ciudad: str = Field(...)
    codigo_postal: Optional[str] = None
    
    # Información de Contacto
    telefono: Optional[str] = None
    email: Optional[str] = None
    sitio_web: Optional[str] = None
    
    # Redes Sociales
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    
    # Medios y Metadata
    imagenes: Optional[List[str]] = None
    institucion: Optional[str] = None
    
    # Metadata del sistema
    source_url: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None
    
    @field_validator('etiquetas')
    @classmethod
    def validate_etiquetas(cls, v):
        """Valida que las etiquetas estén en minúsculas."""
        return [tag.lower().strip() for tag in v]
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validación básica de email."""
        if v and '@' not in v:
            raise ValueError('Email inválido')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Reforestación Urbana CDMX",
                "descripcion": "Iniciativa de reforestación en áreas urbanas...",
                "categoria": "Acción en área natural",
                "etiquetas": ["reforestacion", "urbano", "ambiental"],
                "tipo_proyecto": "Sin Fines de Lucro",
                "tipo_enfoque": "Ambiental",
                "descripcion_enfoque": "Proyecto enfocado en...",
                "ods": "15: Vida en tierra",
                "fuente_recursos": "Privada",
                "sector_economico": "Agropecuario",
                "cobertura": "Local",
                "estatus": "Consolidado",
                "tamano": "De 11 a 50 colaboradores",
                "ubicacion": "Calle Reforma 123",
                "pais": "Mexico",
                "region": "CDMX",
                "ciudad": "Ciudad de México",
            }
        }


class Source(BaseModel):
    """Modelo para fuentes de información."""
    url: str
    domain: Optional[str] = None
    status: str = "pending"
    first_scraped_at: Optional[datetime] = None
    last_scraped_at: Optional[datetime] = None
    scrape_count: int = 0
    error_message: Optional[str] = None
    initiative_id: Optional[int] = None


class ExtractionLog(BaseModel):
    """Modelo para logs de extracción con LLM."""
    source_id: Optional[int] = None
    initiative_id: Optional[int] = None
    provider: str = "local"  # local, openai
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    success: bool = False
    error_message: Optional[str] = None
    raw_response: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
