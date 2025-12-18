"""
Bangladesh News Scraper - Collects 2600+ articles per language

Assignment: CLIR System Dataset Builder
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import random
import os
from urllib.parse import urljoin, urlparse


class NewsScraperCLIR:
    def __init__(self):
        # Bangla news sources
        self.bangla_sites = {
            'Prothom Alo': 'https://www.prothomalo.com',
            'BD News 24': 'https://bangla.bdnews24.com',
            'Kaler Kantho': 'https://www.kalerkantho.com',
            'Bangla Tribune': 'https://www.banglatribune.com',
            'Dhaka Post': 'https://www.dhakapost.com'
        }
        
        # English news sources
        self.english_sites = {
            'The Daily Star': 'https://www.thedailystar.net',
            'Dhaka Tribune': 'https://www.dhakatribune.com',
            'New Age': 'https://www.newagebd.net',
            'Daily Sun': 'https://www.daily-sun.com',
            'The Business Standard': 'https://www.tbsnews.net'
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Create data directory
        os.makedirs('data/raw', exist_ok=True)
        
        self.bangla_articles = []
        self.english_articles = []
        self.total_target = 2600

    def scrape_site_comprehensive(self, base_url, language, source, target=600):
        """
        Comprehensive scraper for any news site
        Attempts multiple strategies to collect articles
        """
        print(f"\nScraping {source} (Target: {target} articles)...")
        articles = []
        visited_urls = set()
        
        # Common news categories to explore
        categories = [
            'bangladesh', 'national', 'politics', 'business', 'sports',
            'world', 'entertainment', 'technology', 'health', 'education',
            'opinion', 'lifestyle', 'economy', 'culture', 'environment'
        ]
        
        # Different URL patterns to try
        url_patterns = [
            f"{base_url}/collection/latest",
            f"{base_url}/latest",
            f"{base_url}/all-news",
            f"{base_url}/archive",
            base_url
        ]
        
        try:
            # Strategy 1: Category-based scraping
            for category in categories:
                if len(articles) >= target:
                    break
                
                category_urls = [
                    f"{base_url}/{category}",
                    f"{base_url}/category/{category}",
                    f"{base_url}/{category}/news",
                ]
                
                for cat_url in category_urls:
                    try:
                        response = requests.get(cat_url, headers=self.headers, timeout=10)
                        if response.status_code != 200:
                            continue
                        
                        soup = BeautifulSoup(response.content, 'html.parser')
                        links = soup.find_all('a', href=True)
                        
                        for link in links:
                            if len(articles) >= target:
                                break
                            
                            href = link.get('href', '')
                            full_url = urljoin(base_url, href)
                            
                            # Check if valid article URL
                            if (base_url.replace('https://', '').replace('www.', '') in full_url 
                                and full_url not in visited_urls 
                                and self.is_article_url(full_url)):
                                
                                visited_urls.add(full_url)
                                article = self.scrape_generic_article(full_url, language, source)
                                
                                if article:
                                    articles.append(article)
                                    print(f"  {source}: {len(articles)}/{target}", end='\r')
                                    time.sleep(random.uniform(0.3, 1.0))
                        
                        break
                    except Exception as e:
                        continue
            
            # Strategy 2: Pagination-based scraping if needed
            if len(articles) < target:
                for pattern in url_patterns:
                    if len(articles) >= target:
                        break
                    
                    # Try up to 50 pages
                    for page in range(1, 50):
                        if len(articles) >= target:
                            break
                        
                        try:
                            page_url = f"{pattern}?page={page}"
                            response = requests.get(page_url, headers=self.headers, timeout=10)
                            
                            if response.status_code != 200:
                                continue
                            
                            soup = BeautifulSoup(response.content, 'html.parser')
                            links = soup.find_all('a', href=True)
                            page_articles = 0
                            
                            for link in links:
                                if len(articles) >= target:
                                    break
                                
                                href = link.get('href', '')
                                full_url = urljoin(base_url, href)
                                
                                if (full_url not in visited_urls 
                                    and self.is_article_url(full_url)):
                                    
                                    visited_urls.add(full_url)
                                    article = self.scrape_generic_article(full_url, language, source)
                                    
                                    if article:
                                        articles.append(article)
                                        page_articles += 1
                                        print(f"  {source}: {len(articles)}/{target}", end='\r')
                                        time.sleep(random.uniform(0.3, 1.0))
                            
                            # No new articles on this page, try next pattern
                            if page_articles == 0:
                                break
                        
                        except Exception as e:
                            continue
        
        except Exception as e:
            print(f"\n  Warning: {source} error: {e}")
        
        print(f"\n  Completed {source}: {len(articles)} articles collected")
        return articles[:target]

    def is_article_url(self, url):
        """Check if URL is likely an article"""
        # Exclude non-article patterns
        exclude_patterns = [
            '/tag/', '/category/', '/author/', '/page/', '/feed/',
            '/rss/', '/search/', '/login/', '.jpg', '.png', '.pdf',
            '/static/', '/assets/'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False
        
        # Include article patterns
        include_patterns = [
            '/bangladesh/', '/national/', '/politics/', '/sports/',
            '/business/', '/world/', '/entertainment/', '/technology/',
            '/news/', '/story/', '/article/', '/post/', '/detail/',
            '/opinion/', '/feature/'
        ]
        
        return any(pattern in url.lower() for pattern in include_patterns)

    def scrape_generic_article(self, url, language, source):
        """Generic article scraper - works for most news sites"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            for tag in ['h1', 'h2']:
                title_tag = soup.find(tag)
                if title_tag:
                    title = title_tag.get_text().strip()
                    break
            
            if not title or len(title) < 10:
                return None
            
            # Extract body text
            body_texts = []
            
            # Try common paragraph containers
            for tag in ['article', 'div', 'section']:
                container = soup.find(tag, class_=lambda x: x and any(
                    word in str(x).lower() for word in 
                    ['story', 'content', 'article', 'body', 'text', 'detail']
                ))
                
                if container:
                    paragraphs = container.find_all('p')
                    body_texts = [p.get_text().strip() for p in paragraphs 
                                 if len(p.get_text().strip()) > 50]
                    if body_texts:
                        break
            
            # Fallback: get all paragraphs
            if not body_texts:
                paragraphs = soup.find_all('p')
                body_texts = [p.get_text().strip() for p in paragraphs 
                             if len(p.get_text().strip()) > 50]
            
            body = ' '.join(body_texts)
            
            # Quality check: minimum 200 chars and 30 words
            if len(body) < 200 or len(body.split()) < 30:
                return None
            
            # Extract date
            date = datetime.now().isoformat()
            for tag in soup.find_all(['time', 'span', 'div']):
                if tag.get('datetime'):
                    date = tag['datetime']
                    break
                
                date_text = tag.get_text()
                if any(month in date_text for month in 
                       ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    date = date_text
                    break
            
            word_count = len(body.split())
            
            return {
                'title': title,
                'body': body,
                'url': url,
                'date': date,
                'language': language,
                'source': source,
                'word_count': word_count,
                'tokens': len(body.split())
            }
        
        except Exception as e:
            return None

    def scrape_all(self):
        """Main scraping orchestrator - Target: 2600+ per language"""
        print("=" * 70)
        print("Bangladesh News Scraper - CLIR Assignment")
        print("=" * 70)
        print(f"Target: 2600+ articles per language (Total: 5200+)\n")
        
        # Scrape Bangla sites (520 articles per site x 5 = 2600)
        print("\n" + "=" * 70)
        print("BANGLA ARTICLES COLLECTION")
        print("=" * 70)
        
        target_per_site_bn = 520
        for source, url in self.bangla_sites.items():
            articles = self.scrape_site_comprehensive(url, 'bn', source, target_per_site_bn)
            self.bangla_articles.extend(articles)
            self.save_intermediate('bangla')
        
        # Scrape English sites (520 articles per site x 5 = 2600)
        print("\n" + "=" * 70)
        print("ENGLISH ARTICLES COLLECTION")
        print("=" * 70)
        
        target_per_site_en = 520
        for source, url in self.english_sites.items():
            articles = self.scrape_site_comprehensive(url, 'en', source, target_per_site_en)
            self.english_articles.extend(articles)
            self.save_intermediate('english')
        
        # Save final data
        self.save_data()
        self.show_summary()

    def save_intermediate(self, lang_type):
        """Save intermediate progress for crash recovery"""
        if lang_type == 'bangla':
            with open('data/raw/bangla_articles_temp.json', 'w', encoding='utf-8') as f:
                json.dump(self.bangla_articles, f, ensure_ascii=False, indent=2)
        else:
            with open('data/raw/english_articles_temp.json', 'w', encoding='utf-8') as f:
                json.dump(self.english_articles, f, ensure_ascii=False, indent=2)

    def save_data(self):
        """Save collected articles to JSON files"""
        print("\n" + "=" * 70)
        print("SAVING DATA")
        print("=" * 70)
        
        # Save Bangla articles
        with open('data/raw/bangla_articles.json', 'w', encoding='utf-8') as f:
            json.dump(self.bangla_articles, f, ensure_ascii=False, indent=2)
        
        bangla_size = os.path.getsize('data/raw/bangla_articles.json') / (1024 * 1024)
        print(f"Saved: bangla_articles.json ({len(self.bangla_articles)} articles, {bangla_size:.2f} MB)")
        
        # Save English articles
        with open('data/raw/english_articles.json', 'w', encoding='utf-8') as f:
            json.dump(self.english_articles, f, ensure_ascii=False, indent=2)
        
        english_size = os.path.getsize('data/raw/english_articles.json') / (1024 * 1024)
        print(f"Saved: english_articles.json ({len(self.english_articles)} articles, {english_size:.2f} MB)")
        
        # Save combined dataset
        all_articles = self.bangla_articles + self.english_articles
        with open('data/raw/all_articles.json', 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        all_size = os.path.getsize('data/raw/all_articles.json') / (1024 * 1024)
        print(f"Saved: all_articles.json ({len(all_articles)} articles, {all_size:.2f} MB)")
        
        # Clean up temporary files
        for temp_file in ['bangla_articles_temp.json', 'english_articles_temp.json']:
            temp_path = f'data/raw/{temp_file}'
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def show_summary(self):
        """Display collection summary"""
        print("\n" + "=" * 70)
        print("COLLECTION SUMMARY")
        print("=" * 70)
        
        total = len(self.bangla_articles) + len(self.english_articles)
        print(f"\nTotal Articles: {total}")
        print(f"  - Bangla: {len(self.bangla_articles)}")
        print(f"  - English: {len(self.english_articles)}")
        
        # Check target achievement
        target_met_bn = "[ACHIEVED]" if len(self.bangla_articles) >= 2600 else "[PARTIAL]"
        target_met_en = "[ACHIEVED]" if len(self.english_articles) >= 2600 else "[PARTIAL]"
        
        print(f"\nTarget Achievement:")
        print(f"  {target_met_bn} Bangla: {len(self.bangla_articles)}/2600")
        print(f"  {target_met_en} English: {len(self.english_articles)}/2600")
        
        # Bangla statistics
        if self.bangla_articles:
            avg_words_bn = sum(a['word_count'] for a in self.bangla_articles) / len(self.bangla_articles)
            sources_bn = {}
            for a in self.bangla_articles:
                sources_bn[a['source']] = sources_bn.get(a['source'], 0) + 1
            
            print(f"\nBangla Statistics:")
            print(f"  - Average words per article: {avg_words_bn:.0f}")
            print(f"  - Sources:")
            for source, count in sources_bn.items():
                print(f"    * {source}: {count} articles")
        
        # English statistics
        if self.english_articles:
            avg_words_en = sum(a['word_count'] for a in self.english_articles) / len(self.english_articles)
            sources_en = {}
            for a in self.english_articles:
                sources_en[a['source']] = sources_en.get(a['source'], 0) + 1
            
            print(f"\nEnglish Statistics:")
            print(f"  - Average words per article: {avg_words_en:.0f}")
            print(f"  - Sources:")
            for source, count in sources_en.items():
                print(f"    * {source}: {count} articles")
        
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE")
        print("=" * 70)
        
        print("\nFiles saved in: data/raw/")
        print("  - bangla_articles.json")
        print("  - english_articles.json")
        print("  - all_articles.json")
        
        print("\nNext step: Build your indexing & search engine")
        
        # Colab download instructions
        print("\nTo download files in Google Colab:")
        print("  from google.colab import files")
        print("  files.download('data/raw/bangla_articles.json')")
        print("  files.download('data/raw/english_articles.json')")


def setup_colab():
    """Setup function for Google Colab environment"""
    print("Setting up environment for Google Colab...")
    import subprocess
    subprocess.run(['pip', 'install', '-q', 'beautifulsoup4', 'requests'])
    print("Setup complete. Ready to scrape.")


# Main execution
if __name__ == "__main__":
    # Uncomment next line if running on Colab for first time
    # setup_colab()
    
    scraper = NewsScraperCLIR()
    scraper.scrape_all()