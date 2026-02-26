"""
Módulo de base de datos SQLite para almacenar iniciativas.
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Wrapper simple para SQLite con operaciones CRUD."""
    
    def __init__(self, db_path: str = "./data/initiatives.db"):
        """Inicializa la conexión a la base de datos."""
        self.db_path = db_path
        
        # Crear directorio si no existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar tablas
        self._init_tables()
        logger.info(f"Database initialized at {db_path}")
    
    def _get_connection(self):
        """Obtiene una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Crea las tablas si no existen."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabla initiatives
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS initiatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla sources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                domain TEXT,
                status TEXT DEFAULT 'pending',
                first_scraped_at TIMESTAMP,
                last_scraped_at TIMESTAMP,
                scrape_count INTEGER DEFAULT 0,
                error_message TEXT,
                initiative_id INTEGER,
                FOREIGN KEY (initiative_id) REFERENCES initiatives (id)
            )
        """)
        
        # Tabla logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extraction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                initiative_id INTEGER,
                provider TEXT,
                model_name TEXT,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                duration_ms INTEGER DEFAULT 0,
                success BOOLEAN DEFAULT 0,
                error_message TEXT,
                raw_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES sources (id),
                FOREIGN KEY (initiative_id) REFERENCES initiatives (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # === INITIATIVES ===
    
    def create_initiative(self, data: dict, source_url: Optional[str] = None) -> int:
        """Crea una nueva iniciativa."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO initiatives (data_json, status, source_url)
            VALUES (?, ?, ?)
        """, (json.dumps(data, ensure_ascii=False), data.get('status', 'pending'), source_url))
        
        initiative_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created initiative ID: {initiative_id}")
        return initiative_id
    
    def get_initiative(self, initiative_id: int) -> Optional[Dict]:
        """Obtiene una iniciativa por ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM initiatives WHERE id = ?", (initiative_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'data': json.loads(row['data_json']),
                'status': row['status'],
                'source_url': row['source_url'],
                'created_at': row['created_at']
            }
        return None
    
    def update_initiative_status(self, initiative_id: int, status: str):
        """Actualiza el estado de una iniciativa."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE initiatives 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, initiative_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated initiative {initiative_id} to status: {status}")
    
    def update_initiative_data(self, initiative_id: int, data: Dict):
        """Actualiza los datos completos de una iniciativa."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE initiatives 
            SET data_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(data, ensure_ascii=False), initiative_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated initiative {initiative_id} data")
    
    def search_duplicates(self, name: str, city: str) -> List[Dict]:
        """Busca iniciativas similares por nombre y ciudad."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, data_json 
            FROM initiatives 
            WHERE data_json LIKE ? OR data_json LIKE ?
        """, (f'%{name}%', f'%{city}%'))
        
        results = []
        for row in cursor.fetchall():
            data = json.loads(row['data_json'])
            results.append({
                'id': row['id'],
                'nombre': data.get('nombre'),
                'ciudad': data.get('ciudad')
            })
        
        conn.close()
        return results
    
    # === SOURCES ===
    
    def create_source(self, url: str, domain: Optional[str] = None) -> int:
        """Crea o actualiza una fuente."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO sources (url, domain, first_scraped_at, last_scraped_at, scrape_count)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
            """, (url, domain))
            source_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # URL ya existe, actualizar
            cursor.execute("""
                UPDATE sources 
                SET last_scraped_at = CURRENT_TIMESTAMP,
                    scrape_count = scrape_count + 1
                WHERE url = ?
            """, (url,))
            cursor.execute("SELECT id FROM sources WHERE url = ?", (url,))
            source_id = cursor.fetchone()['id']
        
        conn.commit()
        conn.close()
        return source_id
    
    def update_source_status(self, source_id: int, status: str, error_message: Optional[str] = None):
        """Actualiza el estado de una fuente."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sources 
            SET status = ?, error_message = ?
            WHERE id = ?
        """, (status, error_message, source_id))
        
        conn.commit()
        conn.close()
    
    # === LOGS ===
    
    def create_extraction_log(self, log_data: dict) -> int:
        """Crea un log de extracción."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO extraction_logs (
                source_id, initiative_id, provider, model_name,
                prompt_tokens, completion_tokens, total_tokens,
                cost_usd, duration_ms, success, error_message, raw_response
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_data.get('source_id'),
            log_data.get('initiative_id'),
            log_data.get('provider', 'local'),
            log_data.get('model_name'),
            log_data.get('prompt_tokens', 0),
            log_data.get('completion_tokens', 0),
            log_data.get('total_tokens', 0),
            log_data.get('cost_usd', 0.0),
            log_data.get('duration_ms', 0),
            log_data.get('success', False),
            log_data.get('error_message'),
            log_data.get('raw_response')
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id
