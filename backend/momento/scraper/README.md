# Aviator Scraper

Standalone scraper for Aviator crash game data.

## Quick Start

### Python
```bash
cd backend
pip install -r requirements.txt
python scripts/run_scraper.py
```

### Docker
```bash
docker build -t momento-scraper -f Dockerfile.scraper .
docker run -d -v $(pwd)/backend/data:/app/backend/data momento-scraper
```

### Docker Compose
```bash
docker-compose -f docker-compose.scraper.yml up -d
```

## Configuration

### Environment Variables

```bash
SCRAPER_ENABLED=true
SCRAPER_INTERVAL=5
SCRAPER_AVIATOR_URLS=https://aviator.game
SCRAPER_STORE_DB=true
SCRAPER_DB_PATH=backend/data/momento.db
SCRAPER_BROADCAST=false
```

### Command Line

```bash
python scripts/run_scraper.py --url https://aviator.com --interval 10 --test
```

## Features

- WebSocket, API, and HTML scraping methods
- Rate limiting and retry logic
- SQLite database storage
- WebSocket broadcasting
- Multiple URL support

## Architecture

The scraper uses three methods in priority order:

1. **WebSocket**: Real-time connection for live data
2. **API**: REST endpoints for structured data
3. **HTML Parsing**: Fallback for any site

## Integration

Scraped data automatically integrates with MomentoFresh:
- Stored in SQLite database
- Available via API endpoints
- Compatible with analysis tools

## Deployment

### Local
```bash
python scripts/run_scraper.py --interval 5
```

### Docker
```bash
docker run -d -e SCRAPER_INTERVAL=5 momento-scraper
```

### Cloud
Deploy as a container with environment variables.

## Monitoring

Logs are written to:
- Console (stdout)
- scraper.log file

## Troubleshooting

- Check logs with: tail -f scraper.log
- Verify URLs are accessible
- Try test mode: --test flag
- Increase interval if rate limited

## Extending

Add new scrapers by creating classes in the scraper module.

## License

For educational and analytical purposes only.