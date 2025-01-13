from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.crawler import CrawlerService

# Create a router instance
router = APIRouter()

# Define the request model
class CrawlRequest(BaseModel):
    urls: list[str]  # Array of strings

# Dependency injection for the service
def get_crawler_service():
    return CrawlerService()

@router.post("/crawl")
def crawl_api(
    request: CrawlRequest,
    service: CrawlerService = Depends(get_crawler_service)
):
    """
    Handles the crawl API.
    """
    response = service.handle_crawl(request.urls)
    return response
