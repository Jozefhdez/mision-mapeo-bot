"""
Configuración maestra de los campos del formulario de Bekaab.
Define tipos de datos, opciones permitidas, descripciones y ejemplos.
"""

FORM_CONFIG = {
    "nombre": {
        "label": "Nombre de la Iniciativa",
        "type": "text",
        "required": True,
        "description": "El nombre público de tu proyecto.",
        "example": "Ejemplo: Huerto Comunitario Tláloc"
    },
    "descripcion": {
        "label": "Descripción",
        "type": "text",
        "required": True,
        "description": "Escribe todo lo que quieras sobre tu iniciativa.",
        "example": "Ejemplo: Este proyecto busca recuperar espacios públicos para convertirlos en zonas de cultivo orgánico..."
    },
    "categoria": {
        "label": "Categoría",
        "type": "choice",
        "required": True,
        "description": "Selecciona una SUBCATEGORIA. NO SELECCIONES CATEGORÍA PRINCIPAL. Puede ser la más representativa.",
        "example": "Ejemplo: Acción en área natural",
        "options": [
            "Acción en área natural", "Acción en Casa", "Acción en el trabajo", 
            "Acción en escuela", "Acción en localidad", "Otra acción",
            "Centro de investigación", "Cursos o talleres", "Educación básica", 
            "Educación media", "Educación superior", "Otra iniciativa educativa",
            "Agricultura o Jardinería", "Alimentos o Bebidas", "Aparatos Electrónicos",
            "Artículos Desechables", "Belleza o Cuidado", "Bolsas", "Certificadoras",
            "Comercio, Finanzas e Inversión", "Consultoría o Servicios", "Decoración de Interiores",
            "Emprendimiento", "Hogar", "Limpieza", "Madera", "Mascotas", "Medios de Comunicación",
            "Mercadotecnia o Publicidad", "Niños y bebés", "Otro producto o servicio",
            "Papelería y oficina", "Reciclaje o desechos", "Ropa y accesorios", "Salud",
            "Servicios y artículos funerarios", "Centro de acopio", "Organizacion gubernamental",
            "Organización internacional", "Organización No Gubernamental", "Otra institución",
            "Agricultura o ganadería", "Apicultura", "Aprovechamiento forestal", "Artesanía",
            "Caza, pesca o recolección", "Otra producción", "Centro comercial", 
            "Otro punto de intercambio", "Tianguis o mercado", "Tienda", "Agua", "Aire",
            "Arquitectura o Construcción", "Energía", "Otra tecnologia", "Suelo", "Transporte",
            "Balneario", "Hotel", "Otro turismo", "Parque", "Restaurante", "Transporte (servicio)"
        ]
    },
    "etiquetas": {
        "label": "Etiquetas",
        "type": "text",
        "required": True,
        "description": "Escribe entre 3 y 5 palabras clave separadas por comas. Si requieres agregar otra, usa solo minúsculas y sepáralas por coma.",
        "example": "Ejemplo: biodegradable, derecho ambiental, consumo consciente"
    },
    "tipo_enfoque": {
        "label": "Tipo de Enfoque",
        "type": "choice",
        "required": True,
        "description": "Selecciona el enfoque que más corresponde a tu iniciativa.",
        "options": ["Social", "Ambiental", "Sustentable", "Regenerativo", "Economía Circular"]
    },
    "descripcion_enfoque": {
        "label": "Descripción del Enfoque",
        "type": "text",
        "required": True,
        "description": "Explica por qué elegiste ese enfoque (mínimo 200 caracteres).",
        "example": "Ejemplo: Nuestra iniciativa es Sustentable porque equilibra el crecimiento económico con el cuidado del agua y..."
    },
    "ods": {
        "label": "ODS",
        "type": "multiselect",
        "required": True,
        "description": "Objetivos de Desarrollo Sostenible que atiende el proyecto.",
        "options": [
            "1: Fin de la pobreza", "2: Hambre cero", "3: Salud y bienestar", 
            "4: Educación de calidad", "5: Igualdad de género", "6: Agua limpia y saneamiento",
            "7: energía asequible y limpia", "8: Trabajo decente y crecimiento económico",
            "9: Industria", "10: Reducción de la desigualdad", "11: Ciudades y comunidades sostenibles",
            "12: Consumo y producción responsables", "13: Acción climática", "14: Vida bajo el agua",
            "15: Vida en tierra", "16: Paz y justicia Instituciones fuertes", "17: Alianzas para lograr los objetivos"
        ]
    },
    "fuente_recursos": {
        "label": "Fuente de los Recursos",
        "type": "choice",
        "required": True,
        "description": "¿De dónde proviene el financiamiento?",
        "options": ["Particular", "Privada", "Pública", "Mixta", "(por definir)"]
    },
    "sector_economico": {
        "label": "Sector Económico",
        "type": "choice",
        "required": True,
        "description": "Sector al que pertenece la iniciativa.",
        "options": [
            "Agropecuario", "Industrial", "De infraestructura pública", 
            "De infraestructura económica", "De servicios", "No aplica", "(por definir)"
        ]
    },
    "cobertura": {
        "label": "Área de Cobertura",
        "type": "choice",
        "required": True,
        "description": "¿Cuál es el alcance territorial actual?",
        "options": ["Local", "Regional", "Nacional", "Multinacional", "Global", "(por definir)"]
    },
    "estatus": {
        "label": "Estatus",
        "type": "choice",
        "required": True,
        "description": "¿Cuál es el nivel de desarrollo de tu iniciativa?",
        "options": [
            "Idea", "En diseño o construcción", "Reciente", 
            "Consolidado", "Completado", "(por definir)"
        ]
    },
    "tamano": {
        "label": "Tamaño",
        "type": "choice",
        "required": True,
        "description": "¿Cuántas personas participan (remuneradas o no)?",
        "options": [
            "De 1 a 2 colaboradores", "De 3 a 10 colaboradores", 
            "De 11 a 50 colaboradores", "De 51 a 100 colaboradores", 
            "De 101 a 500 colaboradores", "Más de 500 colaboradores", "(por definir)"
        ]
    },
    "certificaciones": {
        "label": "Certificaciones",
        "type": "multiselect",
        "required": False,
        "description": "Selecciona las certificaciones con las que cuenta tu iniciativa.",
        "options": [
            "B-corp", "Biodinámico", "Biosphere", "BREAM", "Certificación participativa",
            "Empresa Socialmente Responsible", "Global Compact", "Great Place To Work Mexico",
            "Green Destinations", "Green Key", "HACCP", "ISO 14000 Gestión ambiental",
            "ISO 14064 Huella de carbono", "ISO 26000 Responsabilidad social",
            "ISO 5001 Gestión energética", "ISO 9000 Gestión de la calidad", "LEED",
            "Living Building Challenge", "Orgánico", "Rainforest Alliance",
            "SA 8000 Responsabilidad social", "Travelife", "Otra", "(por definir)"
        ]
    },
    "institucion": {
        "label": "Institución",
        "type": "choice",
        "required": False,
        "description": "Institución de donde emana el proyecto.",
        "options": [
            "(No seleccionar)",
            "Centro Mexicano de Derecho Ambiental", "Conservación Internacional", "FAO",
            "Fondo Mexicano para la Conservacón de la Naturaleza", "Fundación Tláloc",
            "Earth & Life University", "Green Peace", "Instituto Politécnico Nacional",
            "ProNatura", "SAGARPA", "SEMARNAT", "Tecnológico de Monterrey",
            "Universidad Autónoma Chapingo", "Universidad Autónoma del Estado de México",
            "Universidad Autónoma Metropolitana", "Universidad del Medio Ambiente",
            "Universidad Iberoamericana", "WWF México"
        ]
    },
    "otra_institucin": {
        "label": "Otra Institución",
        "type": "text",
        "required": False,
        "description": "Escribe aquí si la institución de donde emana el proyecto no está en la lista anterior."
    },
    "ubicacion": {
        "label": "Ubicación",
        "type": "text",
        "required": True,
        "description": "Dirección completa donde opera la iniciativa. Comienza a escribir y el sistema tratará de ubicar la dirección.",
        "example": "Ejemplo: Calle Eva Briseño 593, Santa Fe, 45168 Zapopan, Jal."
    },
    "pais": {
        "label": "País",
        "type": "text",
        "required": True,
        "description": "País de operación.",
        "example": "Ejemplo: Mexico"
    },
    "region": {
        "label": "Región/Estado",
        "type": "text",
        "required": True,
        "description": "Estado o provincia.",
        "example": "Ejemplo: Jalisco"
    },
    "ciudad": {
        "label": "Ciudad",
        "type": "text",
        "required": True,
        "description": "Ciudad principal.",
        "example": "Ejemplo: Zapopan"
    },
    "codigo_postal": {
        "label": "Código postal",
        "type": "text",
        "required": False,
        "description": "Por favor, introduce el código postal.",
        "example": "Ejemplo: 45168"
    },
    "latitud": {
        "label": "Latitud de la dirección",
        "type": "text",
        "required": True,
        "description": "Coordenada de latitud para mayor precisión en el mapa.",
        "example": "Ejemplo: 39.955823048131286"
    },
    "longitud": {
        "label": "Longitud de la dirección",
        "type": "text",
        "required": True,
        "description": "Coordenada de longitud para mayor precisión en el mapa.",
        "example": "Ejemplo: -75.14408111572266"
    },
    "telefono": {
        "label": "Teléfono",
        "type": "text",
        "required": False,
        "description": "Teléfono de contacto.",
        "example": "Ejemplo: +52 33 1234 5678"
    },
    "sitio_web": {
        "label": "Sitio Web",
        "type": "text",
        "required": False,
        "description": "URL del sitio web.",
        "example": "Ejemplo: https://www.ejemplo.com"
    },
    "facebook": {
        "label": "Facebook",
        "type": "text",
        "required": False,
        "description": "URL de la página de Facebook.",
        "example": "Ejemplo: https://facebook.com/pagina"
    },
    "twitter": {
        "label": "Twitter",
        "type": "text",
        "required": False,
        "description": "URL del perfil de Twitter.",
        "example": "Ejemplo: https://twitter.com/usuario"
    },
    "instagram": {
        "label": "Instagram",
        "type": "text",
        "required": False,
        "description": "URL del perfil de Instagram.",
        "example": "Ejemplo: https://instagram.com/usuario"
    },
    "ofertas_especiales": {
        "label": "Ofertas Especiales",
        "type": "text",
        "required": False,
        "description": "Escribe las ofertas especiales para miembros de Bekaab y de la Red."
    },
    "imagenes": {
        "label": "Imágenes",
        "type": "file",
        "required": True,
        "description": "Sube las imágenes que gustes para mostrar tu iniciativa (mínimo 3)."
    },
    "video": {
        "label": "Vídeo",
        "type": "text",
        "required": False,
        "description": "Agrega la dirección URL de YouTube, Vimeo, etc.",
        "example": "Ejemplo: https://youtube.com/watch?v=..."
    },
    "email_contacto": {
        "label": "Email de contacto",
        "type": "text",
        "required": True,
        "description": "Email al que quieres que los usuarios te escriban.",
        "example": "Ejemplo: info@bekaab.org"
    },
    "registrado_por": {
        "label": "Registrado por",
        "type": "text",
        "required": True,
        "description": "Escribe el correo electrónico de quien registra la iniciativa (este campo no será visible)."
    },
    "recomendado_por": {
        "label": "Recomendado por",
        "type": "text",
        "required": False,
        "description": "Escribe el correo electrónico de quien te haya invitado a registrar tu iniciativa (este campo no será visible)."
    },
    "comentarios_registro": {
        "label": "Comentarios en el Registro",
        "type": "text",
        "required": False,
        "description": "¿Alguna duda o comentario de este registro? (este campo no será visible)."
    },
}
