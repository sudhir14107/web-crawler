from fastapi import FastAPI, APIRouter
from app.routes.crawler import router as crawler_routes

# Create a FastAPI app instance
app = FastAPI(title="Web Crawler API")

# add router
api_router = APIRouter()
api_router.include_router(crawler_routes)

app.include_router(api_router, prefix='/api')

