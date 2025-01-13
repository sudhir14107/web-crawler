# Web Crawler

## Step by Step Guide to Set Up Web Crawler

### 1. Project Setup with FastAPI
### 2. Create an endpoint that takes input of a list of domains
### 3. Queue these domains to a queue
### 4. Load from environment variables:
- `MAX_TIME_PAGE`
- `MAX_THREADS`

### 5. Based on the queue and threads:
- Create a new thread and assign a URL for crawling
- Add the URL to the visited set

### 6. Look for `<a>` tags and `href` URLs:
- a. If a URL matches a pattern like `/product/`, `/p/`, `/dp/`, and so on, save it in JSON (key as URL and domain as value)
- b. If no match is found:
  - i. If the URL is already in the visited set, discard it
  - ii. If not, add it to the queue
