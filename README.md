# JW-Newsfeed

A content aggregation system that scrapes JW.ORG and generates an RSS feed for use with feed reader applications.

## Overview

JW-Newsfeed scrapes content directly from JW.ORG using Selenium and generates a unified RSS 2.0 feed (`jw_feed.xml`). This feed can be consumed by any RSS reader application, podcast app, or custom integration.

**All content is scraped directly from web pages** - no external RSS feeds are used.

## Features

- **Video Scraping**: Scrapes latest videos from the JW.ORG video library
- **Book Scraping**: Scrapes publications and books
- **News Scraping**: Scrapes news articles directly from the news page
- **Change Tracking**: Maintains history to identify new content
- **RSS 2.0 Output**: Generates a standards-compliant feed with media thumbnails
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Installation

```bash
# Clone the repository
git clone https://github.com/camster91/JW-Newsfeed.git
cd JW-Newsfeed

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- Chrome browser installed
- ChromeDriver (auto-managed via webdriver-manager)

## Usage

### Generate RSS Feed

```bash
python jw_news_parser.py
```

This will:
1. Scrape videos, books, and news from JW.ORG
2. Update the history file (`history.json`)
3. Generate the RSS feed (`jw_feed.xml`)

### Download Videos

```bash
python "JW.ORG Download.py"
```

Downloads videos from URLs listed in `urls_and_titles.txt` to `~/JW.ORG/`.

## Output

The main output is `jw_feed.xml` - an RSS 2.0 feed containing:
- Videos from the latest videos section
- Books and publications
- News articles

### Feed Structure

```xml
<rss version="2.0">
  <channel>
    <title>JW.ORG Updates</title>
    <item>
      <title>Content Title</title>
      <link>https://www.jw.org/...</link>
      <category>Video|Book|News</category>
      <media:thumbnail url="..."/>
    </item>
  </channel>
</rss>
```

## Configuration

Environment variables for customization:

| Variable | Description | Default |
|----------|-------------|---------|
| `JW_DATA_DIR` | Directory for data files | Script directory |
| `JW_OUTPUT_DIR` | Directory for RSS output | Script directory |
| `JW_FEED_URL` | Self-reference URL in feed | `https://example.com/jw_feed.xml` |
| `JW_DOWNLOAD_DIR` | Video download directory | `~/JW.ORG/` |

## Project Structure

```
JW-Newsfeed/
├── jw_news_parser.py      # Main RSS feed generator
├── JW.ORG Download.py     # Video downloader
├── create folders.py      # Folder structure setup
├── text_bible.py          # Daily text scraper
├── import datetime.py     # Bible reading schedule
├── requirements.txt       # Python dependencies
├── history.json           # Processed items tracking
├── jw_feed.xml           # Generated RSS feed (output)
├── urls_and_titles.txt    # Video download URLs
└── *.txt                  # Bible reading data files
```

## Integration

The generated `jw_feed.xml` can be used with:
- RSS reader apps (Feedly, Inoreader, etc.)
- Podcast apps that support RSS
- Custom applications via the RSS 2.0 standard
- Home automation systems
- Mobile apps

### Hosting the Feed

To make the feed accessible to external apps:

1. **Local Network**: Host with a simple HTTP server
   ```bash
   python -m http.server 8080
   ```

2. **Cloud Hosting**: Upload to any web server or cloud storage with public access

3. **Self-Hosted**: Use with services like Nginx, Apache, or Caddy

---

## Roadmap

### Planned Features

#### Content Expansion
- [ ] **Magazine Scraping** - Add Watchtower and Awake! magazines
- [ ] **Audio Content** - Include audio recordings and dramatic readings
- [ ] **Regional News** - Support for country-specific news sections
- [ ] **Convention/Assembly Content** - Scrape convention programs and talks
- [ ] **Multi-Language Support** - Configurable language selection

#### Feed Enhancements
- [ ] **Separate Category Feeds** - Generate individual feeds for videos, books, news
- [ ] **Full-Text Descriptions** - Include article content in feed descriptions
- [ ] **Enclosure Support** - Add direct media file links for podcast apps
- [ ] **Feed Pagination** - Limit feed size with archive support
- [ ] **OPML Export** - Export feed configuration for reader apps

#### Automation & Scheduling
- [ ] **Scheduled Runs** - Built-in cron/scheduler support
- [ ] **Webhook Notifications** - Notify when new content is found
- [ ] **Email Digest** - Optional email notifications for new content
- [ ] **Push Notifications** - Integration with Pushover, Ntfy, etc.

#### Technical Improvements
- [ ] **Headless Mode** - Run without visible browser window
- [ ] **Docker Support** - Containerized deployment
- [ ] **API Endpoint** - REST API for feed access and management
- [ ] **Database Backend** - SQLite/PostgreSQL for history storage
- [ ] **Rate Limiting** - Configurable request throttling
- [ ] **Proxy Support** - HTTP/SOCKS proxy configuration
- [ ] **Retry Logic** - Improved error handling with backoff

#### User Interface
- [ ] **Web Dashboard** - Browser-based management interface
- [ ] **Configuration UI** - GUI for settings management
- [ ] **Feed Preview** - View feed contents before publishing
- [ ] **Statistics** - Track new content over time

### Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is for personal use. JW.ORG content is property of Watch Tower Bible and Tract Society.
