
import asyncio
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def scrape_url(url: str):
    schema = {
        "name": "Company Info",
        "fields": [
            {"name": "company_name", "type": "text"},
            {"name": "contact_email", "type": "text"},
            {"name": "context", "type": "text"}
        ]
    }

    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        data = json.loads(result.extracted_content)
        return data


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        url = query_params.get('url', [None])[0]

        if not url:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'error': 'Missing "url" query parameter'}
            self.wfile.write(json.dumps(response).encode())
            return

        try:
            data = asyncio.run(scrape_url(url))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response).encode())