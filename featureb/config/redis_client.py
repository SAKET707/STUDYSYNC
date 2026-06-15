import redis
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True 
    )
    
    redis_client.ping()
    logger.info(" Redis client successfully connected.")
except Exception as e:
    logger.warning(f" Redis connection failed on startup: {e}")
    redis_client = None
