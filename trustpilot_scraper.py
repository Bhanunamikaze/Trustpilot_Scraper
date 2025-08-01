import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
import os
import argparse
from datetime import datetime
from urllib.parse import urlparse

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Trustpilot Multi-Company Scraper')
    parser.add_argument('-company', type=str, help='Single company name, domain, or full Trustpilot URL')
    parser.add_argument('-companies', type=str, help='File path with list of companies (one per line)')
    return parser.parse_args()

def load_companies(company_arg=None, companies_file_arg=None):
    """Load company names from command line arguments or input files"""
    companies = []
    
    # Priority 1: Command line arguments
    if company_arg:
        companies = [company_arg.strip()]
        print(f"Loaded 1 company from command line: {company_arg}")
    elif companies_file_arg:
        if os.path.exists(companies_file_arg):
            with open(companies_file_arg, 'r', encoding='utf-8') as f:
                companies = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(companies)} companies from file: {companies_file_arg}")
        else:
            print(f"Error: Companies file '{companies_file_arg}' not found")
            return []
    
    # Priority 2: Fallback to legacy file detection
    elif os.path.exists('companies'):
        with open('companies', 'r', encoding='utf-8') as f:
            companies = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(companies)} companies from 'companies' file")
    elif os.path.exists('company'):
        with open('company', 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            if line:
                companies = [line]
        print(f"Loaded 1 company from 'company' file")
    
    else:
        print("No input found. Please provide either:")
        print("  -company <company_name_or_url>")
        print("  -companies <file_path>")
        print("  Or create 'companies' or 'company' file")
        return []
    
    return companies

def get_trustpilot_url(company_input):
    """Generate Trustpilot URL from company name, domain, or full URL"""
    company_input = company_input.strip()
    
    # Handle full Trustpilot URLs
    if company_input.startswith('http'):
        try:
            parsed = urlparse(company_input)
            if 'trustpilot.com' in parsed.netloc and '/review/' in parsed.path:
                # Normalize and return the URL
                return f"https://www.trustpilot.com{parsed.path.rstrip('/')}"
            else:
                # If it's not a Trustpilot URL, extract domain
                domain = parsed.netloc.replace('www.', '')
                return f'https://www.trustpilot.com/review/{domain}'
        except Exception:
            pass
    
    # Handle domains (with dots)
    if '.' in company_input:
        domain = company_input.replace('www.', '')
        return f'https://www.trustpilot.com/review/{domain}'
    
    # Handle company names without domains (don't add .com automatically)
    return f'https://www.trustpilot.com/review/{company_input.lower()}'

def get_reviews_from_page(url):
    """Fetch reviews from a single page"""
    try:
        req = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        req.raise_for_status()
        time.sleep(2)
        soup = BeautifulSoup(req.text, 'html.parser')
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if not script_tag:
            return []
        reviews_raw = json.loads(script_tag.string)
        return reviews_raw["props"]["pageProps"]["reviews"]
    except (requests.RequestException, json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"Error fetching page: {e}")
        return []

def load_existing_jsonl(output_file):
    """Load existing JSONL data or return empty list"""
    try:
        if os.path.exists(output_file):
            reviews = []
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        reviews.append(json.loads(line))
            return reviews
        return []
    except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
        print(f"Warning: Could not load existing file {output_file}: {e}")
        return []

def append_to_jsonl(review_data, output_file):
    """Append a single review to JSONL file"""
    try:
        with open(output_file, 'a', encoding='utf-8') as f:
            json.dump(review_data, f, ensure_ascii=False)
            f.write('\n')
        return True
    except Exception as e:
        print(f"Error saving to file: {e}")
        return False

def get_safe_filename(company_name):
    """Generate a safe filename from company name"""
    # Remove URLs and clean up
    if company_name.startswith('http'):
        try:
            parsed = urlparse(company_name)
            company_name = parsed.path.replace('/review/', '').strip('/')
        except:
            pass
    
    # Clean up the name
    safe_name = company_name.replace('www.', '').replace('.com', '').replace('.', '_')
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '-_').lower()
    return f"{safe_name}.jsonl"

def scrape_company_reviews(company_name, has_tqdm=False):
    """Scrape reviews for a single company"""
    base_url = get_trustpilot_url(company_name)
    output_file = get_safe_filename(company_name)
    
    print(f"\nScraping reviews for: {company_name}")
    print(f"URL: {base_url}")
    print(f"Output file: {output_file}")
    
    # Load existing reviews to avoid duplicates
    existing_reviews = load_existing_jsonl(output_file)
    existing_bodies = {review.get('body', '') for review in existing_reviews}
    
    if existing_reviews:
        print(f"Found {len(existing_reviews)} existing reviews")
    
    page_number = 1
    new_reviews_added = 0
    
    # Setup progress bar for pages if tqdm is available
    if has_tqdm:
        from tqdm import tqdm
        page_pbar = tqdm(desc=f"Pages for {company_name[:20]}", unit="page")
    
    while True:
        url = f"{base_url}?page={page_number}"
        reviews = get_reviews_from_page(url)
        
        if not reviews:
            if has_tqdm:
                page_pbar.close()
            break
        
        # Process reviews from current page
        page_new_reviews = 0
        for review in reviews:
            try:
                review_data = {
                    'company': company_name,
                    'date': pd.to_datetime(review["dates"]["publishedDate"]).strftime("%Y-%m-%d"),
                    'author': review["consumer"]["displayName"],
                    'body': review["text"],
                    'heading': review["title"],
                    'rating': review["rating"],
                    'location': review["consumer"]["countryCode"],
                    'scraped_at': datetime.now().isoformat(),
                    'source_url': base_url
                }
                
                # Check for duplicates
                if review_data['body'] not in existing_bodies:
                    if append_to_jsonl(review_data, output_file):
                        existing_bodies.add(review_data['body'])
                        page_new_reviews += 1
                        new_reviews_added += 1
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping malformed review: {e}")
                continue
        
        total_in_file = len(existing_reviews) + new_reviews_added
        
        if has_tqdm:
            page_pbar.set_postfix({
                'New': page_new_reviews,
                'Total new': new_reviews_added,
                'Total': total_in_file
            })
            page_pbar.update(1)
        
        page_number += 1
        time.sleep(1)
    
    print(f"Completed scraping {company_name}")
    print(f"New reviews added: {new_reviews_added}")
    print(f"Total reviews in file: {len(existing_reviews) + new_reviews_added}")
    
    return new_reviews_added

def scrape_all_companies(company_arg=None, companies_file_arg=None):
    """Main function to scrape all companies"""
    # Try to import tqdm for progress bars
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False
        print("Note: Install tqdm for enhanced progress bars: pip install tqdm")
    
    companies = load_companies(company_arg, companies_file_arg)
    if not companies:
        return
    
    print(f"\nStarting to scrape {len(companies)} companies")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    summary = {}
    total_new_reviews = 0
    
    # Setup main progress bar for companies
    if has_tqdm:
        company_pbar = tqdm(companies, desc="Companies", unit="company")
        companies_iter = company_pbar
    else:
        companies_iter = companies
    
    for i, company in enumerate(companies_iter, 1):
        if has_tqdm:
            company_pbar.set_postfix_str(f"Processing: {company[:25]}")
        else:
            print(f"\n[{i}/{len(companies)}] Processing: {company}")
        
        try:
            new_reviews = scrape_company_reviews(company, has_tqdm)
            summary[company] = {
                'new_reviews': new_reviews,
                'output_file': get_safe_filename(company),
                'status': 'success'
            }
            total_new_reviews += new_reviews
            
        except Exception as e:
            print(f"Failed to scrape {company}: {e}")
            summary[company] = {
                'new_reviews': 0,
                'output_file': get_safe_filename(company),
                'status': 'failed',
                'error': str(e)
            }
        
        # Add delay between companies
        if i < len(companies):
            time.sleep(5)
    
    if has_tqdm:
        company_pbar.close()
    
    # Print final summary
    print(f"\nAll companies completed!")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total new reviews scraped: {total_new_reviews}")
    print("\nSummary:")
    
    for company, stats in summary.items():
        status = "Success" if stats['status'] == 'success' else "Failed"
        print(f"{status}: {company}")
        print(f"  File: {stats['output_file']}")
        print(f"  New reviews: {stats['new_reviews']}")
        if stats['status'] == 'failed':
            print(f"  Error: {stats['error']}")
    
    # Save summary to JSON
    try:
        with open('scraping_summary.json', 'w', encoding='utf-8') as f:
            json.dump({
                'completed_at': datetime.now().isoformat(),
                'total_companies': len(companies),
                'total_new_reviews': total_new_reviews,
                'companies': summary
            }, f, indent=2, ensure_ascii=False)
        print("\nSummary saved to: scraping_summary.json")
    except Exception as e:
        print(f"Warning: Could not save summary: {e}")
    
    return summary

if __name__ == "__main__":
    print("Trustpilot Multi-Company Scraper")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Run scraper with arguments
    scrape_all_companies(args.company, args.companies)
