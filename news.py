#!/usr/bin/env python3
"""
PyCast - Advanced Automated News Website Generator
Scrapes Tech & Motor news from BBC/CNN/TechCrunch/TheVerge with images
AI-powered rewriting with premium dark-mode design
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import re
from urllib.parse import urljoin
import google.generativeai as genai
import shutil

class NewsAutomation:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
        
        # Headers for web requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
    def download_image(self, url, filename):
        """Download image to local directory"""
        try:
            if not url or 'placeholder' in url.lower():
                return ''
            
            # Create directory if it doesn't exist
            os.makedirs('img/news', exist_ok=True)
            
            # File path
            filepath = os.path.join('img/news', filename)
            
            # Download
            response = requests.get(url, headers=self.headers, stream=True, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
                return filepath
            else:
                print(f"Failed to download {url}: Status {response.status_code}")
            return ''
        except Exception as e:
            print(f"Error downloading image {url}: {e}")
            return ''

    def scrape_bbc_tech_news(self, limit=8):
        """Scrape tech and innovation news from BBC with images"""
        articles = []
        try:
            # BBC Technology section
            url = "https://www.bbc.com/news/technology"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find Next.js data
            script = soup.find('script', id='__NEXT_DATA__')
            # Extracting image from JSON is complex, let's stick to DOM parsing for now
            # but with better selectors

            # Find article cards
            cards = soup.find_all('div', {'data-testid': 'card-text-wrapper'})
            
            for i, card in enumerate(cards[:limit]):
                try:
                    # Get title
                    title_elem = card.find('h2')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Get description
                    desc_elem = card.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    # Get link
                    link_parent = card.find_parent('a')
                    url_path = link_parent.get('href', '') if link_parent else ''
                    article_url = urljoin('https://www.bbc.com', url_path) if url_path else ''
                    
                    # Get image
                    image_url = ''
                    # Try finding image in the parent container
                    parent = card.find_parent('div', {'data-testid': 'card-wrapper'}) or card.parent.parent
                    if parent:
                        img_tag = parent.find('img')
                        
                        if img_tag:
                            # Try to get high-res image from srcset
                            srcset = img_tag.get('srcset', '')
                            if srcset:
                                # Parse srcset to get the largest image
                                try:
                                    candidates = []
                                    for entry in srcset.split(','):
                                        parts = entry.strip().split(' ')
                                        if len(parts) >= 2:
                                            url = parts[0]
                                            width = int(re.sub(r'\D', '', parts[1]))
                                            candidates.append((width, url))
                                    
                                    if candidates:
                                        # Sort by width descending
                                        candidates.sort(key=lambda x: x[0], reverse=True)
                                        image_url = candidates[0][1]
                                except Exception:
                                    pass
                            
                            # Fallback to src if srcset failed
                            if not image_url:
                                image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
                            
                            # Check for placeholder
                            if 'placeholder' in image_url or 'grey' in image_url:
                                image_url = ''

                            if image_url and not image_url.startswith('http'):
                                image_url = 'https:' + image_url if image_url.startswith('//') else urljoin('https://www.bbc.com', image_url)
                    
                    if not image_url and article_url and 'bbc.com' in article_url:
                        # Fallback: Fetch article page to get og:image
                        try:
                            # print(f"DEBUG: Fetching article page {article_url}")
                            art_resp = requests.get(article_url, headers=self.headers, timeout=5)
                            if art_resp.status_code == 200:
                                art_soup = BeautifulSoup(art_resp.content, 'html.parser')
                                og_image = art_soup.find('meta', property='og:image')
                                if og_image:
                                    image_url = og_image.get('content')
                        except Exception:
                            pass

                    if title and article_url:
                        print(f"  Found: {title[:30]}... | Img: {'Yes' if image_url else 'No'}")
                        article = {
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': 'BBC Tech',
                            'image': image_url,
                            'category': 'Technology'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    print(f"Error parsing BBC article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping BBC Tech: {e}")
        
        return articles
    
    def scrape_bbc_business_news(self, limit=6):
        """Scrape business news from BBC with images"""
        articles = []
        try:
            url = "https://www.bbc.com/news/business"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article cards
            cards = soup.find_all('div', {'data-testid': 'card-text-wrapper'})
            
            for i, card in enumerate(cards[:limit]):
                try:
                    title_elem = card.find('h2')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    print(f"  Found: {title[:30]}... | Source: BBC Business")
                    
                    # Removed strict keyword filter to get more news
                    
                    desc_elem = card.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    link_parent = card.find_parent('a')
                    # Fallback: look for link inside the card
                    if not link_parent:
                        link_parent = card.find('a')
                        
                    url_path = link_parent.get('href', '') if link_parent else ''
                    article_url = urljoin('https://www.bbc.com', url_path) if url_path else ''
                    
                    if not article_url:
                        # print(f"DEBUG: No article URL for card {i}")
                        pass
                    
                    # Get image (using same robust logic as Tech)
                    image_url = ''
                    parent = card.find_parent('div', {'data-testid': 'card-wrapper'}) or card.parent.parent
                    if parent:
                        img_tag = parent.find('img')
                        if img_tag:
                            srcset = img_tag.get('srcset', '')
                            if srcset:
                                try:
                                    candidates = []
                                    for entry in srcset.split(','):
                                        parts = entry.strip().split(' ')
                                        if len(parts) >= 2:
                                            url = parts[0]
                                            width = int(re.sub(r'\D', '', parts[1]))
                                            candidates.append((width, url))
                                    if candidates:
                                        candidates.sort(key=lambda x: x[0], reverse=True)
                                        image_url = candidates[0][1]
                                except Exception:
                                    pass
                            
                            if not image_url:
                                image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
                                
                            if 'placeholder' in image_url or 'grey' in image_url:
                                image_url = ''

                            if image_url and not image_url.startswith('http'):
                                image_url = 'https:' + image_url if image_url.startswith('//') else urljoin('https://www.bbc.com', image_url)
                    
                    if not image_url and article_url and 'bbc.com' in article_url:
                        try:
                            art_resp = requests.get(article_url, headers=self.headers, timeout=5)
                            if art_resp.status_code == 200:
                                art_soup = BeautifulSoup(art_resp.content, 'html.parser')
                                og_image = art_soup.find('meta', property='og:image')
                                if og_image:
                                    image_url = og_image.get('content')
                        except Exception:
                            pass

                    if title and article_url:
                        article = {
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': 'BBC Business',
                            'image': image_url,
                            'category': 'Business'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    # print(f"DEBUG: Business loop error: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping BBC Business: {e}")
        
        return articles

    def scrape_hacker_news(self, limit=30):
        """Scrape top stories from Hacker News"""
        articles = []
        try:
            url = "https://news.ycombinator.com/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rows = soup.select('tr.athing')
            # print(f"DEBUG: Hacker News found {len(rows)} items")
            
            for row in rows[:limit]:
                try:
                    title_elem = row.select_one('td.title > span.titleline > a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    article_url = title_elem.get('href', '')
                    
                    if not article_url.startswith('http'):
                        article_url = urljoin('https://news.ycombinator.com/', article_url)
                    
                    # HN doesn't have images or descriptions usually, so we use placeholders/defaults
                    article = {
                        'title': title,
                        'description': 'Discussion on Hacker News',
                        'url': article_url,
                        'source': 'Hacker News',
                        'image': '',
                        'category': 'Tech'
                    }
                    articles.append(article)
                except Exception:
                    continue
        except Exception as e:
            print(f"Error scraping Hacker News: {e}")
            
        return articles

    def scrape_cnn_tech_news(self, limit=8):
        """Scrape tech news from CNN with images"""
        articles = []
        try:
            url = "https://www.cnn.com/business/tech"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news cards
            cards = soup.find_all('div', {'data-component-name': 'card'})
            
            for card in cards[:limit]:
                try:
                    container = card.find('div', class_='container__text')
                    if not container:
                        continue
                        
                    title_elem = container.find('span', {'data-editable': 'headline'})
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    
                    link_elem = card.find('a', class_='container__link')
                    url_path = link_elem.get('href', '') if link_elem else ''
                    article_url = urljoin('https://www.cnn.com', url_path) if url_path else ''
                    
                    if not article_url:
                        continue
                        
                    # Get image
                    image_url = ''
                    img_container = card.find('div', class_='container__media')
                    if img_container:
                        img_tag = img_container.find('img')
                        if img_tag:
                            image_url = img_tag.get('data-src-medium', '') or img_tag.get('src', '')
                    
                    if title and article_url:
                        article = {
                            'title': title,
                            'description': '', # CNN cards might not have descriptions
                            'url': article_url,
                            'source': 'CNN Tech',
                            'image': image_url,
                            'category': 'Technology'
                        }
                        articles.append(article)
                except Exception:
                    continue
                    
        except Exception:
            pass
            
        return articles

    def scrape_techcrunch_news(self, limit=5):
        """Scrape news from TechCrunch"""
        articles = []
        try:
            url = "https://techcrunch.com/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles_elems = soup.find_all('h2', class_='post-block__title')
            
            for elem in articles_elems[:limit]:
                try:
                    link = elem.find('a')
                    if not link:
                        continue
                        
                    title = link.get_text(strip=True)
                    article_url = link.get('href', '')
                    
                    # Find description/image from parent
                    parent = elem.find_parent('div', class_='post-block')
                    description = ''
                    image_url = ''
                    
                    if parent:
                        content = parent.find('div', class_='post-block__content')
                        if content:
                            description = content.get_text(strip=True)
                            
                        # Try to find image
                        img_wrapper = parent.find('footer', class_='post-block__footer')
                        if not img_wrapper:
                            # Try header
                            header = parent.find('header', class_='post-block__header')
                            if header:
                                img_tag = header.find_previous_sibling('div').find('img') if header.find_previous_sibling('div') else None
                                if img_tag:
                                     image_url = img_tag.get('src', '')
                    
                    if title and article_url:
                        article = {
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': 'TechCrunch',
                            'image': image_url,
                            'category': 'Startups'
                        }
                        articles.append(article)
                except Exception:
                    continue
        except Exception:
            pass
            
        return articles

    def scrape_verge_tech_news(self, limit=5):
        """Scrape news from The Verge"""
        articles = []
        try:
            url = "https://www.theverge.com/tech"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # The Verge structure
            articles_elems = soup.find_all('h2', class_='font-polysans')
            
            for elem in articles_elems[:limit]:
                try:
                    link = elem.find('a')
                    if not link:
                        continue
                        
                    title = link.get_text(strip=True)
                    article_url = urljoin('https://www.theverge.com', link.get('href', ''))
                    
                    article = {
                        'title': title,
                        'description': '',
                        'url': article_url,
                        'source': 'The Verge',
                        'image': '',
                        'category': 'Technology'
                    }
                    articles.append(article)
                except Exception:
                    continue
        except Exception:
            pass
            
        return articles
    
    def rewrite_article(self, article):
        """Simulate AI rewriting (placeholder)"""
        # If we had an API key, we would use it here.
        # Since we don't, we just pass through.
        article['rewritten_title'] = article['title']
        article['rewritten_content'] = article.get('description', '')
        return article
        
    def run(self):
        print(f"🚀 Starting PyCast news automation...")
        print("=" * 60)
        
        # Scrape tech news from multiple sources
        print("\n🌍 Scraping BBC Home News (Max 50)...")
        bbc_home = self.scrape_bbc_home_news(limit=50)

        print("\n📱 Scraping BBC Technology (Max 30)...")
        bbc_tech = self.scrape_bbc_tech_news(limit=30)
        
        print("\n🚗 Scraping BBC Business (Max 30)...")
        bbc_auto = self.scrape_bbc_business_news(limit=30)

        print("\n🔬 Scraping Hacker News (Max 30)...")
        hn_articles = self.scrape_hacker_news(limit=30)
        
        print("\n💻 Scraping CNN Tech (Max 20)...")
        cnn_tech = self.scrape_cnn_tech_news(limit=20)
        
        print("\n🔧 Scraping TechCrunch (Max 20)...")
        tc_articles = self.scrape_techcrunch_news(limit=20)
        
        print("\n📲 Scraping The Verge (Max 20)...")
        verge_articles = self.scrape_verge_tech_news(limit=20)
         
        # Combine all articles
        all_articles = bbc_home + bbc_tech + bbc_auto + hn_articles + cnn_tech + tc_articles + verge_articles
    
    def scrape_bbc_home_news(self, limit=50):
        """Scrape general news from BBC Home with images"""
        articles = []
        try:
            url = "https://www.bbc.com/news"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all card wrappers
            cards = soup.find_all('div', {'data-testid': 'card-text-wrapper'})
            print(f"DEBUG: BBC Home found {len(cards)} cards")
            
            for i, card in enumerate(cards[:limit]):
                try:
                    title_elem = card.find('h2')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    desc_elem = card.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    link_parent = card.find_parent('a')
                    url_path = link_parent.get('href', '') if link_parent else ''
                    article_url = urljoin('https://www.bbc.com', url_path) if url_path else ''
                    
                    # Get image using robust logic
                    image_url = ''
                    parent = card.find_parent('div', {'data-testid': 'card-wrapper'}) or card.parent.parent
                    if parent:
                        img_tag = parent.find('img')
                        if img_tag:
                            srcset = img_tag.get('srcset', '')
                            if srcset:
                                try:
                                    candidates = []
                                    for entry in srcset.split(','):
                                        parts = entry.strip().split(' ')
                                        if len(parts) >= 2:
                                            url = parts[0]
                                            width = int(re.sub(r'\D', '', parts[1]))
                                            candidates.append((width, url))
                                    if candidates:
                                        candidates.sort(key=lambda x: x[0], reverse=True)
                                        image_url = candidates[0][1]
                                except Exception:
                                    pass
                            
                            if not image_url:
                                image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
                                
                            if 'placeholder' in image_url or 'grey' in image_url:
                                image_url = ''

                            if image_url and not image_url.startswith('http'):
                                image_url = 'https:' + image_url if image_url.startswith('//') else urljoin('https://www.bbc.com', image_url)
                    
                    if not image_url and article_url and 'bbc.com' in article_url:
                        try:
                            art_resp = requests.get(article_url, headers=self.headers, timeout=5)
                            if art_resp.status_code == 200:
                                art_soup = BeautifulSoup(art_resp.content, 'html.parser')
                                og_image = art_soup.find('meta', property='og:image')
                                if og_image:
                                    image_url = og_image.get('content')
                        except Exception:
                            pass

                    if title and article_url:
                        article = {
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': 'BBC News',
                            'image': image_url,
                            'category': 'World'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error scraping BBC Home: {e}")
            
        return articles

    def scrape_cnn_tech_news(self, limit=8):
        """Scrape tech news from CNN with images"""
        articles = []
        try:
            url = "https://edition.cnn.com/business/tech"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # CNN article containers
            containers = soup.find_all('div', class_='container__item')[:limit*2]
            
            for container in containers:
                if len(articles) >= limit:
                    break
                    
                try:
                    # Get headline
                    headline = container.find('span', class_='container__headline-text')
                    if not headline:
                        continue
                    
                    title = headline.get_text(strip=True)
                    
                    # Get link
                    link_tag = container.find('a', class_='container__link')
                    article_url = ''
                    if link_tag and link_tag.get('href'):
                        article_url = link_tag['href']
                        if not article_url.startswith('http'):
                            article_url = 'https://edition.cnn.com' + article_url
                    
                    # Get image
                    image_url = ''
                    img_tag = container.find('img', class_='image__dam-img')
                    if img_tag:
                        image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
                        if image_url and not image_url.startswith('http'):
                            image_url = 'https:' + image_url if image_url.startswith('//') else ''
                    
                    # Get description (if available)
                    desc_elem = container.find('div', class_='container__description')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    if title and article_url:
                        article = {
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': 'CNN Tech',
                            'image': image_url,
                            'category': 'Technology'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping CNN Tech: {e}")
        
        return articles
    
    def scrape_techcrunch_news(self, limit=6):
        """Scrape tech news from TechCrunch with images"""
        articles = []
        try:
            url = "https://techcrunch.com/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # TechCrunch article listings
            article_blocks = soup.find_all('div', class_='post-block')[:limit]
            
            for block in article_blocks:
                try:
                    # Get title
                    title_tag = block.find('a', class_='post-block__title__link')
                    if not title_tag:
                        title_tag = block.find('h2')
                    
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    article_url = title_tag.get('href', '') if title_tag.name == 'a' else ''
                    
                    # Get image
                    image_url = ''
                    img_tag = block.find('img')
                    if img_tag:
                        image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
                    
                    # Get description
                    desc_elem = block.find('div', class_='post-block__content')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    if title:
                        article = {
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': 'TechCrunch',
                            'image': image_url,
                            'category': 'Technology'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping TechCrunch: {e}")
        
        return articles
    
    def scrape_verge_tech_news(self, limit=4):
        """Scrape tech news from The Verge with images"""
        articles = []
        try:
            url = "https://www.theverge.com/tech"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article containers
            article_containers = soup.find_all('div', class_='duet--content-cards--content-card')[:limit]
            
            for container in article_containers:
                try:
                    # Get title
                    title_tag = container.find('h2')
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    
                    # Get link
                    link_tag = container.find('a')
                    article_url = link_tag.get('href', '') if link_tag else ''
                    if article_url and not article_url.startswith('http'):
                        article_url = 'https://www.theverge.com' + article_url
                    
                    # Get image
                    image_url = ''
                    img_tag = container.find('img')
                    if img_tag:
                        image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
                    
                    # Get description
                    desc_elem = container.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    if title and article_url:
                        article = {
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': 'The Verge',
                            'image': image_url,
                            'category': 'Technology'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping The Verge: {e}")
        
        return articles
    
    def rewrite_article(self, article):
        """Rewrite article content using Gemini AI to avoid copyright"""
        if not self.model:
            print("Warning: No API key set. Using original content.")
            return article
        
        prompt = f'''Rewrite this news article in your own words. Make it unique and engaging while preserving the key facts.

Original Title: {article['title']}
Original Description: {article['description']}

Provide:
1. A new catchy headline (max 100 characters)
2. A rewritten summary (2-3 sentences, 150-200 words)

Format your response as JSON:
{{"headline": "...", "summary": "..."}}'''

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                rewritten = json.loads(response_text[start:end])
                article['rewritten_title'] = rewritten.get('headline', article['title'])
                article['rewritten_content'] = rewritten.get('summary', article['description'])
            else:
                article['rewritten_title'] = article['title']
                article['rewritten_content'] = article['description']
                
        except Exception as e:
            print(f"Error rewriting article: {e}")
            article['rewritten_title'] = article['title']
            article['rewritten_content'] = article['description']
        
        return article
    
    def generate_html(self, articles):
        """Generate premium, PyCast-style responsive news.html with images"""
        today = datetime.now().strftime("%B %d, %Y")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PyCast — Automated Python News Aggregator | Asbin Thapa</title>
  <meta name="description" content="PyCast News — A Python-powered news aggregator displaying the latest tech, AI, and cybersecurity headlines. Built by Asbin Thapa.">
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:ital,wght@0,300;0,700;1,300&family=Syne:wght@400;800&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #0d0e0f;
      --surface: #141516;
      --border: #222426;
      --accent: #c8f135;
      --accent2: #3bffbd;
      --muted: #5a5e64;
      --text: #e8eaed;
      --text-dim: #868b92;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Syne', sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
    }}

    /* ── GRID NOISE TEXTURE ── */
    body::before {{
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(255, 255, 255, 0.018) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(255, 255, 255, 0.018) 40px);
      pointer-events: none;
      z-index: 0;
    }}

    /* ── GLOW BLOB ── */
    .glow {{
      position: fixed;
      width: 700px;
      height: 700px;
      border-radius: 50%;
      filter: blur(140px);
      pointer-events: none;
      z-index: 0;
      opacity: 0.15;
    }}

    .glow-1 {{
      background: var(--accent);
      top: -200px;
      left: -200px;
    }}

    .glow-2 {{
      background: var(--accent2);
      bottom: -200px;
      right: -200px;
    }}

    /* ── NAV ── */
    nav {{
      position: relative;
      z-index: 10;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 24px 48px;
      border-bottom: 1px solid var(--border);
    }}

    .nav-logo {{
      font-family: 'DM Mono', monospace;
      font-size: 1rem;
      letter-spacing: 0.05em;
    }}

    .nav-logo span {{
      color: var(--accent);
    }}
    
    .nav-links {{
      display: flex;
      gap: 36px;
      list-style: none;
    }}
    
    .nav-links a {{
      text-decoration: none;
      color: var(--text-dim);
      font-size: 0.82rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      transition: color 0.2s;
    }}
    
    .nav-links a:hover {{
      color: var(--accent);
    }}

    /* ── HERO ── */
    .hero {{
      position: relative;
      z-index: 5;
      padding: 80px 48px 60px;
      max-width: 1400px;
      margin: 0 auto;
    }}

    .hero-eyebrow {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
    }}

    .eyebrow-dot {{
      width: 8px;
      height: 8px;
      background: var(--accent);
      border-radius: 50%;
      animation: blink 1.4s step-end infinite;
    }}

    @keyframes blink {{
      0%, 100% {{ opacity: 1 }}
      50% {{ opacity: 0 }}
    }}

    .eyebrow-text {{
      font-family: 'DM Mono', monospace;
      font-size: 0.75rem;
      color: var(--accent);
      letter-spacing: 0.15em;
      text-transform: uppercase;
    }}

    .hero-title {{
      font-family: 'Fraunces', serif;
      font-size: clamp(3rem, 6vw, 5rem);
      font-weight: 700;
      line-height: 1.05;
      margin-bottom: 24px;
    }}

    .hero-title span {{
      color: var(--accent);
      font-style: italic;
      font-weight: 300;
    }}

    .hero-desc {{
      color: var(--text-dim);
      font-size: 1.1rem;
      line-height: 1.6;
      max-width: 600px;
      font-family: 'Syne', sans-serif;
    }}

    /* ── NEWS GRID ── */
    .news-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 32px;
        margin-top: 40px;
    }}

    .news-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        transition: transform 0.3s, border-color 0.3s;
        text-decoration: none;
        color: inherit;
        overflow: hidden;
    }}

    .news-card:hover {{
        transform: translateY(-8px);
        border-color: var(--accent);
    }}

    .card-img {{
        width: 100%;
        height: 220px;
        object-fit: cover;
        border-bottom: 1px solid var(--border);
    }}
    
    .card-placeholder {{
        width: 100%;
        height: 220px;
        background: linear-gradient(45deg, #1a1a1a, #2a2a2a);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        border-bottom: 1px solid var(--border);
    }}

    .card-body {{
        padding: 24px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }}

    .card-meta {{
        display: flex;
        justify-content: space-between;
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-dim);
        margin-bottom: 12px;
        text-transform: uppercase;
    }}

    .card-source {{
        color: var(--accent);
    }}

    .card-title {{
        font-family: 'Fraunces', serif;
        font-size: 1.4rem;
        font-weight: 600;
        line-height: 1.3;
        margin-bottom: 12px;
    }}
    
    .card-desc {{
        font-family: 'DM Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-dim);
        line-height: 1.6;
        margin-bottom: 20px;
        flex: 1;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}

    .read-more {{
        font-family: 'DM Mono', monospace;
        font-size: 0.8rem;
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: auto;
    }}

    @media (max-width: 1024px) {{
        .news-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}

    @media (max-width: 768px) {{
        .news-grid {{
            grid-template-columns: 1fr;
        }}
        .hero {{
            padding: 60px 24px;
        }}
        nav {{
            padding: 20px;
        }}
    }}
    .terminal-container {{
        max-width: 1200px;
        margin: 60px auto;
        background: #0d0e0f;
        border: 1px solid #333;
        border-radius: 6px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        font-family: 'DM Mono', monospace;
        overflow: hidden;
    }}

    .terminal-header {{
        background: #1a1b1c;
        padding: 10px 15px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #333;
    }}

    .terminal-buttons {{
        display: flex;
        gap: 8px;
    }}

    .t-btn {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }}

    .t-close {{ background: #ff5f56; }}
    .t-min {{ background: #ffbd2e; }}
    .t-max {{ background: #27c93f; }}

    .terminal-title {{
        margin-left: 20px;
        color: #888;
        font-size: 0.8rem;
    }}

    .terminal-body {{
        padding: 20px;
        color: #3bffbd;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    
    .t-line {{ margin-bottom: 5px; }}
    .t-cmd {{ color: #fff; }}
    .t-cursor {{
        display: inline-block;
        width: 8px;
        height: 15px;
        background: #3bffbd;
        animation: blink 1s infinite;
        vertical-align: middle;
    }}
    
    @keyframes blink {{ 50% {{ opacity: 0; }} }}

    /* ── CYBER STACK ── */
    .cyber-stack {{
        max-width: 1400px;
        margin: 0 auto 60px;
        padding: 0 48px;
        font-family: 'DM Mono', monospace;
    }}
    
    .cyber-header {{
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid var(--border);
        padding-bottom: 12px;
        margin-bottom: 24px;
        color: var(--accent2);
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }}
    
    .status-dot {{
        display: inline-block;
        width: 6px;
        height: 6px;
        background: var(--accent2);
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 10px var(--accent2);
        animation: blink 2s infinite;
    }}
    
    .cyber-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }}
    
    @keyframes float {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-4px); }}
        100% {{ transform: translateY(0px); }}
    }}

    .tech-badge {{
        background: rgba(20, 21, 22, 0.6);
        border: 1px solid var(--border);
        padding: 8px 16px;
        font-size: 0.9rem;
        color: var(--text-dim);
        transition: all 0.3s;
        cursor: default;
        position: relative;
        overflow: hidden;
        animation: float 4s ease-in-out infinite;
    }}
    
    .tech-badge:nth-child(even) {{
        animation-delay: 1s;
    }}

    .tech-badge:nth-child(3n) {{
        animation-delay: 2s;
    }}
    
    .tech-badge:hover {{
        border-color: var(--accent);
        color: var(--accent);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(200, 241, 53, 0.1);
        animation-play-state: paused;
    }}
    
    .tech-badge::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transition: 0.5s;
    }}
    
    .tech-badge:hover::before {{
        left: 100%;
    }}
  </style>
</head>
<body>
  <div class="glow glow-1"></div>
  <div class="glow glow-2"></div>

  <nav>
    <div class="nav-logo">PyCast <span>News</span></div>
    <ul class="nav-links">
      <li><a href="index.html">Home</a></li>
      <li><a href="p.html">Portfolio</a></li>
    </ul>
  </nav>

  <section class="hero">
    <div class="hero-eyebrow">
        <div class="eyebrow-dot"></div>
        <div class="eyebrow-text">Live Feed • {today}</div>
    </div>
    <h1 class="hero-title">Latest Tech<br><span>Headlines</span></h1>
    <p class="hero-desc">
        Curated daily by AI from top sources like BBC, CNN, TechCrunch, and The Verge. 
        Stay ahead with the most important updates in technology and innovation.
    </p>
  </section>

  <section class="cyber-stack">
    <div class="cyber-header">
        <div class="cyber-status">
            <span class="status-dot"></span> SYSTEM ONLINE
        </div>
        <div class="cyber-id">ID: 0x93FA2</div>
    </div>
    <div class="cyber-grid">
        <div class="tech-badge">Python 3.12</div>
        <div class="tech-badge">React</div>
        <div class="tech-badge">TypeScript</div>
        <div class="tech-badge">Node.js</div>
        <div class="tech-badge">Docker</div>
        <div class="tech-badge">AWS Lambda</div>
        <div class="tech-badge">GraphQL</div>
        <div class="tech-badge">Next.js 14</div>
        <div class="tech-badge">TailwindCSS</div>
        <div class="tech-badge">PostgreSQL</div>
        <div class="tech-badge">Redis</div>
        <div class="tech-badge">OpenAI API</div>
    </div>
  </section>

  <div class="container">
    <div class="news-grid">
"""
        
        for article in articles:
            title = article.get('rewritten_title', article['title'])
            content = article.get('rewritten_content', article['description'])
            source = article['source']
            url = article['url']
            image = article.get('image', '')
            category = article.get('category', 'News')
            
            html += f"""
      <a href="{url}" target="_blank" class="news-card">
"""
            if image:
                html += f'        <img src="{image}" alt="{title}" class="card-img" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">\n'
                html += f'        <div class="card-placeholder" style="display:none">📰</div>\n'
            else:
                html += f'        <div class="card-placeholder">📰</div>\n'
                
            html += f"""        <div class="card-body">
          <div class="card-meta">
            <span class="card-category">{category}</span>
            <span class="card-source">{source}</span>
          </div>
          <h3 class="card-title">{title}</h3>
          <p class="card-desc">{content}</p>
          <div class="read-more">Read Article →</div>
        </div>
      </a>
"""
        
        html += f"""    </div>
  </div>

  <div class="terminal-container">
    <div class="terminal-header">
        <div class="terminal-buttons">
            <div class="t-btn t-close"></div>
            <div class="t-btn t-min"></div>
            <div class="t-btn t-max"></div>
        </div>
        <div class="terminal-title">user@pycast: ~/scripts</div>
    </div>
    <div class="terminal-body">
        <div class="t-line"><span class="t-cmd">user@pycast:~$</span> python3 news_scraper.py</div>
        <div class="t-line">🚀 Starting PyCast automation engine...</div>
        <div class="t-line">📱 Connecting to BBC Technology... <span style="color:#27c93f">Connected</span></div>
        <div class="t-line">🚗 Connecting to BBC Business... <span style="color:#27c93f">Connected</span></div>
        <div class="t-line">📥 Downloading {len(articles)} images to local cache...</div>
        <div class="t-line">⚙️ Processing neural style transfer...</div>
        <div class="t-line">✅ Build complete. Serving {len(articles)} articles.</div>
        <div class="t-line"><span class="t-cmd">user@pycast:~$</span> <span class="t-cursor"></span></div>
    </div>
  </div>
</body>
</html>
"""
        return html
    
    def run(self):
        """Main execution function"""
        print("🚀 Starting PyCast news automation...")
        print("=" * 60)
        
        # Scrape tech news from multiple sources
        print("\n🌍 Scraping BBC Home News (Max 60)...")
        bbc_home = self.scrape_bbc_home_news(limit=60)

        print("\n📱 Scraping BBC Technology (Max 40)...")
        bbc_tech = self.scrape_bbc_tech_news(limit=40)
        
        print("\n🚗 Scraping BBC Business (Max 60)...")
        bbc_auto = self.scrape_bbc_business_news(limit=60)

        print("\n🔬 Scraping Hacker News (Max 30)...")
        hn_articles = self.scrape_hacker_news(limit=30)
        
        print("\n💻 Scraping CNN Tech (Max 20)...")
        cnn_tech = self.scrape_cnn_tech_news(limit=20)
        
        print("\n🔧 Scraping TechCrunch (Max 20)...")
        tc_articles = self.scrape_techcrunch_news(limit=20)
        
        print("\n📲 Scraping The Verge (Max 20)...")
        verge_articles = self.scrape_verge_tech_news(limit=20)
         
        # Combine all articles
        all_articles = bbc_home + bbc_tech + bbc_auto + hn_articles + cnn_tech + tc_articles + verge_articles
        
        # Remove duplicates based on title similarity
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            title_words = set(article['title'].lower().split())
            is_duplicate = False
            
            for seen in seen_titles:
                seen_words = set(seen.lower().split())
                if len(title_words & seen_words) / len(title_words | seen_words) > 0.6:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(article['title'])
        
        print(f"\n✅ Total unique articles found: {len(unique_articles)}")
        
        # Limit to 120 articles
        final_articles = unique_articles[:120]
        
        # Download images
        print(f"\n📥 Downloading images for {len(final_articles)} articles...")
        for i, article in enumerate(final_articles):
            if article.get('image'):
                filename = f"article_{i}.jpg"
                local_path = self.download_image(article['image'], filename)
                if local_path:
                    article['image'] = local_path
        
        # Rewrite articles with AI if API key is present
        if self.model:
            print(f"\n🤖 Rewriting {len(final_articles)} articles with Gemini AI...")
            print("-" * 60)
            for i, article in enumerate(final_articles, 1):
                print(f"  [{i}/{len(final_articles)}] {article['title'][:50]}...")
                final_articles[i-1] = self.rewrite_article(article)
        else:
            print("\n⚠️ No Gemini API key found. Skipping AI rewriting.")
        
        print("\n" + "=" * 60)
        
        # Generate HTML
        print("🎨 Generating localized black-themed HTML...")
        html_content = self.generate_html(final_articles)
        
        # Save to file
        output_path = 'news.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ {output_path} generated successfully!")
        print(f"📊 Total Articles Displayed: {len(final_articles)}")
        print("=" * 60)

if __name__ == "__main__":
    automation = NewsAutomation()
    automation.run()