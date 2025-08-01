# Trustpilot Review Scraper

A robust Python script for scraping customer reviews from Trustpilot with progress tracking and continuous data saving.

## Features

- **Multi-company support**: Scrape reviews for single or multiple companies
- **Flexible input formats**: Supports company names, domains, and full Trustpilot URLs
- **Command-line interface**: Easy-to-use CLI with argument support
- **Progress tracking**: Enhanced progress bars with real-time updates
- **Continuous saving**: Data saved immediately to prevent loss
- **Duplicate detection**: Automatically avoids re-scraping existing reviews
- **JSONL format**: Structured data output for easy processing
- **Resume capability**: Can resume interrupted scraping sessions
- **Summary statistics**: Comprehensive scraping summary and analytics
- **Robust error handling**: Graceful handling of network issues and malformed data

## Installation

### Prerequisites

```bash
pip install requests beautifulsoup4 pandas tqdm
```

### Clone Repository

```bash
git clone https://github.com/Bhanunamikaze/Trustpilot_Scraper.git
cd Trustpilot_Scraper
```

## Usage

### Single Company

```bash
# Using company name (will look for exact match on Trustpilot)
python trustpilot_scraper.py -company starbucks

# Using company domain
python trustpilot_scraper.py -company starbucks.com

# Using full domain with www
python trustpilot_scraper.py -company www.nike.com

# Using full Trustpilot URL
python trustpilot_scraper.py -company https://www.trustpilot.com/review/amazon.com

# Using any website URL (domain will be extracted)
python trustpilot_scraper.py -company https://www.apple.com
```

### Multiple Companies

Create a text file with company names (one per line):

**companies.txt**
```
amazon.com
starbucks
www.nike.com
https://www.trustpilot.com/review/spotify.com
https://www.tesla.com
```

Run the scraper:
```bash
python trustpilot_scraper.py -companies companies.txt
```

### Legacy File Support

You can also use the traditional file-based approach:

- Create a `company` file with a single company name
- Create a `companies` file with multiple company names (one per line)
- Run: `python trustpilot_scraper.py`

## Output Format

### JSONL Files

Each company's reviews are saved to a separate JSONL file (e.g., `amazon.jsonl`):

```json
{"company": "amazon.com", "date": "2024-01-15", "author": "John D.", "body": "Great service and fast delivery!", "heading": "Excellent experience", "rating": 5, "location": "US", "scraped_at": "2024-01-15T10:30:45.123456", "source_url": "https://www.trustpilot.com/review/amazon.com"}
{"company": "amazon.com", "date": "2024-01-14", "author": "Sarah M.", "body": "Had some issues with my order but customer service resolved it quickly.", "heading": "Good customer service", "rating": 4, "location": "GB", "scraped_at": "2024-01-15T10:30:46.789012", "source_url": "https://www.trustpilot.com/review/amazon.com"}
```

### Summary File

A comprehensive summary is saved to `scraping_summary.json`:

```json
{
  "completed_at": "2024-01-15T10:45:30.123456",
  "total_companies": 3,
  "total_new_reviews": 1250,
  "companies": {
    "amazon.com": {
      "new_reviews": 500,
      "output_file": "amazon.jsonl",
      "status": "success"
    },
    "starbucks": {
      "new_reviews": 350,
      "output_file": "starbucks.jsonl", 
      "status": "success"
    },
    "nike.com": {
      "new_reviews": 0,
      "output_file": "nike.jsonl",
      "status": "failed",
      "error": "No reviews found"
    }
  }
}
```

## Data Schema

Each review contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `company` | string | Company name as provided in input |
| `date` | string | Review publication date (YYYY-MM-DD) |
| `author` | string | Review author's display name |
| `body` | string | Full review text content |
| `heading` | string | Review title/heading |
| `rating` | integer | Star rating (1-5) |
| `location` | string | Author's country code (e.g., "US", "GB") |
| `scraped_at` | string | ISO timestamp when review was scraped |
| `source_url` | string | Trustpilot page URL |

## Input Format Support

The scraper intelligently handles various input formats:

| Input Format | Example | Trustpilot URL Generated |
|-------------|---------|--------------------------|
| Company name | `starbucks` | `https://www.trustpilot.com/review/starbucks` |
| Domain | `amazon.com` | `https://www.trustpilot.com/review/amazon.com` |
| Domain with www | `www.nike.com` | `https://www.trustpilot.com/review/nike.com` |
| Full Trustpilot URL | `https://www.trustpilot.com/review/spotify.com` | `https://www.trustpilot.com/review/spotify.com` |
| Any website URL | `https://www.apple.com` | `https://www.trustpilot.com/review/apple.com` |

## Features in Detail

### Progress Tracking

- **Company Progress**: Shows overall progress across multiple companies
- **Page Progress**: Displays scraping progress for each company's pages
- **Real-time Stats**: Live updates on reviews found and saved
- **Clean Output**: Professional, symbol-free progress messages

### Duplicate Handling

- **Content-based Detection**: Uses review text to identify duplicates
- **Resume Capability**: Automatically resumes from where it left off
- **Efficient Storage**: Only saves new reviews to minimize file size
- **Cross-session Memory**: Remembers previously scraped reviews

### Error Handling

- **Network Resilience**: Handles connection errors and timeouts gracefully
- **Data Validation**: Skips malformed reviews with warnings
- **Graceful Failures**: Continues with other companies if one fails
- **Detailed Logging**: Clear error messages without technical jargon

### Rate Limiting

- **Respectful Scraping**: 2-second delay between page requests
- **Company Delays**: 5-second pause between different companies
- **Server-friendly**: Avoids overwhelming Trustpilot servers

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `-company` | Single company name, domain, or URL | `-company nike.com` |
| `-companies` | Path to file with company list | `-companies my_list.txt` |
| `-h, --help` | Show help message | `-h` |

## File Naming

Output files are automatically generated with safe filenames:

| Input | Output File |
|-------|-------------|
| `amazon.com` | `amazon.jsonl` |
| `www.starbucks.com` | `starbucks.jsonl` |
| `https://www.trustpilot.com/review/nike.com` | `nike.jsonl` |
| `coffee-shop` | `coffee-shop.jsonl` |

## Requirements

- Python 3.6+
- Internet connection
- Required packages: `requests`, `beautifulsoup4`, `pandas`, `tqdm` (optional)

## Example Session

```bash
$ python trustpilot_scraper.py -company amazon.com
Trustpilot Multi-Company Scraper
Loaded 1 company from command line: amazon.com

Starting to scrape 1 companies
Started at: 2024-01-15 10:30:00

Scraping reviews for: amazon.com
URL: https://www.trustpilot.com/review/amazon.com
Output file: amazon.jsonl
Found 150 existing reviews
Companies: 100%|████████████| 1/1 [02:30<00:00, 150.45s/company]
Completed scraping amazon.com
New reviews added: 25
Total reviews in file: 175

All companies completed!
Finished at: 2024-01-15 10:32:30
Total new reviews scraped: 25

Summary:
Success: amazon.com
  File: amazon.jsonl
  New reviews: 25

Summary saved to: scraping_summary.json
```

## Troubleshooting

### Common Issues

**No reviews found**: 
- Check if the company exists on Trustpilot
- Verify the company name spelling
- Try different input formats (domain vs company name)

**Permission errors**: 
- Ensure write permissions in the current directory
- Run with appropriate user permissions

**Network timeouts**: 
- Check internet connection
- Trustpilot may be temporarily unavailable
- Script will retry automatically

**Import errors**: 
- Install required packages: `pip install requests beautifulsoup4 pandas tqdm`

### Tips for Success

- Use exact company names as they appear on Trustpilot
- For better results, use domain names (e.g., `amazon.com`) rather than company names
- Large companies may take significant time to scrape completely
- The script can be safely interrupted and resumed later

