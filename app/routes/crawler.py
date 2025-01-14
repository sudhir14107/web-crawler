from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.crawler import CrawlerService

# Create a router instance
router = APIRouter()

# Define the request model
class CrawlRequest(BaseModel):
    urls: list[str]  # Array of strings for the URLs to crawl

# Dependency injection for the service
def get_crawler_service():
    return CrawlerService()

@router.post("/crawl")
async def crawl_api(
    request: CrawlRequest,
    service: CrawlerService = Depends(get_crawler_service)
):
    """
    Handles the crawl API.
    This function will trigger the crawling task synchronously in the service and
    return a response with the results after crawling is completed.
    """
    # Perform the crawling task directly in the service
    service.handle_crawl(request.urls)

    # Return the crawled data
    return {"message": "Crawling in progress"}
