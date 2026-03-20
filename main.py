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
    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Misión Mapeo Bot...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'OPENROUTER_API_KEY',
        'BEKAAB_API_URL',
        'CODE_SNIPPET_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return

    # Load allowed users
    allowed_ids_str = os.getenv('ALLOWED_TELEGRAM_IDS', '')
    allowed_user_ids = []
    
    if allowed_ids_str:
        try:
            allowed_user_ids = [int(id.strip()) for id in allowed_ids_str.split(',') if id.strip()]
        except ValueError:
            logger.error("ALLOWED_TELEGRAM_IDS contains non-numeric values")
            return
            
    # Backward compatibility
    if not allowed_user_ids:
        admin_id = os.getenv('TELEGRAM_ADMIN_USER_ID')
        if admin_id:
            allowed_user_ids = [int(admin_id)]
        else:
            logger.error("Neither ALLOWED_TELEGRAM_IDS nor TELEGRAM_ADMIN_USER_ID is set")
            return
    
    logger.info(f"Initializing components... (Allowed users: {len(allowed_user_ids)})")
    
    db = Database(
        db_path=os.getenv('DATABASE_PATH', './data/initiatives.db')
    )
    
    scraper = Scraper(
        timeout=int(os.getenv('SCRAPER_TIMEOUT', 10))
    )
    
    extractor = LLMExtractor(
        api_key=os.getenv('OPENROUTER_API_KEY'),
        model=os.getenv('LLM_MODEL', 'google/gemini-2.5-flash-lite')
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
        allowed_user_ids=allowed_user_ids,
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
