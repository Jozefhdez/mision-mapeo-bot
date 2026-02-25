"""
Punto de entrada principal del bot de Misión Mapeo.
"""
import os
import logging
from dotenv import load_dotenv

from src.database import Database
from src.scraper import Scraper
from src.extractor import LLMExtractor
from src.validator import Validator
from src.bekaab_client import BekaabClient
from src.bot import InitiativeBot


def setup_logging():
    """Configura el logging."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, log_level)
    )
    
    # Reducir verbosidad de librerías externas
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)


def main():
    """Función principal."""
    # Cargar variables de entorno
    load_dotenv()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Misión Mapeo Bot...")
    
    # Validar variables de entorno requeridas
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_ADMIN_USER_ID',
        'OLLAMA_BASE_URL',
        'OLLAMA_MODEL',
        'BEKAAB_API_URL',
        'CODE_SNIPPET_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    # Inicializar componentes
    logger.info("Initializing components...")
    
    db = Database(
        db_path=os.getenv('DATABASE_PATH', './data/initiatives.db')
    )
    
    scraper = Scraper(
        timeout=int(os.getenv('SCRAPER_TIMEOUT', 10))
    )
    
    extractor = LLMExtractor(
        base_url=os.getenv('OLLAMA_BASE_URL'),
        model=os.getenv('OLLAMA_MODEL')
    )
    
    validator = Validator(
        db=db,
        similarity_threshold=85
    )
    
    bekaab_client = BekaabClient(
        api_url=os.getenv('BEKAAB_API_URL'),
        api_key=os.getenv('CODE_SNIPPET_API_KEY')
    )
    
    bot = InitiativeBot(
        token=os.getenv('TELEGRAM_BOT_TOKEN'),
        admin_user_id=int(os.getenv('TELEGRAM_ADMIN_USER_ID')),
        db=db,
        scraper=scraper,
        extractor=extractor,
        validator=validator,
        bekaab_client=bekaab_client
    )
    
    # Iniciar bot
    logger.info("Bot components initialized successfully")
    logger.info("Starting Telegram bot polling...")
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise


if __name__ == "__main__":
    main()
