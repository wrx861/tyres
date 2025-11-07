from fastapi import FastAPI, APIRouter, Request, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

# Import routers
from routers import auth, products, cars, orders, admin, cart

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    title="Tires Shop API",
    description="API for tire and disk shop with Telegram Mini App",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {
        "message": "Tires Shop API is running",
        "version": "1.0.0",
        "status": "ok"
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        await db.command('ping')
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Include routers
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(cars.router)
api_router.include_router(orders.router)
api_router.include_router(admin.router)
api_router.include_router(cart.router)

# Middleware для проверки блокировки пользователей
class BlockedUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Пропускаем проверку для определенных путей
        excluded_paths = ["/api/", "/api/health", "/api/auth/telegram", "/api/auth/me"]
        if request.url.path in excluded_paths or request.url.path == "/api":
            return await call_next(request)
        
        # Проверяем telegram_id в query параметрах
        telegram_id = request.query_params.get("telegram_id")
        
        if telegram_id and telegram_id != "None":
            try:
                user = await db.users.find_one({"telegram_id": telegram_id})
                if user and user.get("is_blocked"):
                    return HTTPException(
                        status_code=403,
                        detail="Слишком много запросов, подождите еще и вернитесь не скоро"
                    )
            except Exception as e:
                logger.error(f"Error checking user block status: {e}")
        
        return await call_next(request)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(BlockedUserMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()