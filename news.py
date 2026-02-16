#!/usr/bin/env python3
"""
Advanced Automated News Website Generator
Scrapes Tech & Motor news from BBC/CNN with images
AI-powered rewriting with premium design
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import re
from urllib.parse import urljoin
import google.generativeai as genai
import base64

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def scrape_bbc_tech_news(self, limit=6):
        """Scrape tech and innovation news from BBC with images"""
        articles = []
        try:
            # BBC Technology section
            url = "https://www.bbc.com/news/technology"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article cards
            cards = soup.find_all('div', {'data-testid': 'card-text-wrapper'})
            
            for card in cards[:limit]:
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
                    img_container = card.find_parent('div', class_='gel-layout__item')
                    if img_container:
                        img_tag = img_container.find('img')
                        if img_tag:
                            image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
                            if image_url and not image_url.startswith('http'):
                                image_url = 'https:' + image_url if image_url.startswith('//') else urljoin('https://www.bbc.com', image_url)
                    
                    if title and article_url:
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
    
    def scrape_bbc_business_news(self, limit=4):
        """Scrape business/motor news from BBC with images"""
        articles = []
        try:
            url = "https://www.bbc.com/news/business"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            cards = soup.find_all('div', {'data-testid': 'card-text-wrapper'})
            
            for card in cards[:limit]:
                try:
                    title_elem = card.find('h2')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Filter for automotive/motor news
                    keywords = ['car', 'auto', 'vehicle', 'electric', 'tesla', 'ford', 'toyota', 'motor', 'ev', 'automotive']
                    if not any(keyword in title.lower() for keyword in keywords):
                        continue
                    
                    desc_elem = card.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    link_parent = card.find_parent('a')
                    url_path = link_parent.get('href', '') if link_parent else ''
                    article_url = urljoin('https://www.bbc.com', url_path) if url_path else ''
                    
                    # Get image
                    image_url = ''
                    img_container = card.find_parent('div', class_='gel-layout__item')
                    if img_container:
                        img_tag = img_container.find('img')
                        if img_tag:
                            image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
                            if image_url and not image_url.startswith('http'):
                                image_url = 'https:' + image_url if image_url.startswith('//') else urljoin('https://www.bbc.com', image_url)
                    
                    if title and article_url:
                        article = {
                            'title': title,
                            'description': description,
                            'url': article_url,
                            'source': 'BBC Business',
                            'image': image_url,
                            'category': 'Automotive'
                        }
                        articles.append(article)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping BBC Business: {e}")
        
        return articles
    
    def scrape_cnn_tech_news(self, limit=6):
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
        
        prompt = f"""Rewrite this news article in your own words. Make it unique and engaging while preserving the key facts.

Original Title: {article['title']}
Original Description: {article['description']}

Provide:
1. A new catchy headline (max 100 characters)
2. A rewritten summary (2-3 sentences, 150-200 words)

Format your response as JSON:
{{"headline": "...", "summary": "..."}}"""

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
        """Generate premium, BBC-style responsive news.html with images"""
        today = datetime.now().strftime("%B %d, %Y")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Latest tech and automotive news updated daily">
    <meta property="og:title" content="Tech & Motor News - Daily Updates">
    <meta property="og:description" content="Your source for technology and automotive news">
    <title>Tech & Motor News - {today}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Reith+Sans:wght@400;500;700&family=Reith+Serif:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary-color: #1a1a1a;
            --secondary-color: #CC0000;
            --text-color: #3c3c3c;
            --light-gray: #f5f5f5;
            --border-color: #e0e0e0;
            --card-shadow: 0 2px 8px rgba(0,0,0,0.08);
            --hover-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}
        
        body {{
            font-family: 'Reith Sans', 'Helvetica Neue', Arial, sans-serif;
            background: #ffffff;
            color: var(--text-color);
            line-height: 1.6;
        }}
        
        /* Header Styles */
        header {{
            background: var(--primary-color);
            color: white;
            padding: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        .header-container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 20px 24px;
        }}
        
        .site-title {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        
        .site-tagline {{
            font-size: 1.1em;
            opacity: 0.9;
            font-weight: 400;
        }}
        
        .date-badge {{
            display: inline-block;
            background: var(--secondary-color);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
            margin-top: 12px;
        }}
        
        /* Navigation Tabs */
        .category-nav {{
            background: white;
            border-bottom: 1px solid var(--border-color);
            padding: 0;
        }}
        
        .category-nav-container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            gap: 32px;
        }}
        
        .nav-tab {{
            padding: 16px 0;
            font-weight: 500;
            font-size: 1em;
            color: var(--text-color);
            border-bottom: 4px solid transparent;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .nav-tab.active {{
            border-bottom-color: var(--secondary-color);
            color: var(--primary-color);
        }}
        
        /* Main Container */
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 32px 24px;
        }}
        
        /* Featured Story */
        .featured-story {{
            margin-bottom: 48px;
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 32px;
            padding-bottom: 32px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .featured-image {{
            width: 100%;
            height: 450px;
            object-fit: cover;
            border-radius: 0;
        }}
        
        .featured-content {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .featured-badge {{
            display: inline-block;
            background: var(--secondary-color);
            color: white;
            padding: 4px 12px;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
            width: fit-content;
        }}
        
        .featured-title {{
            font-family: 'Reith Serif', Georgia, serif;
            font-size: 2.5em;
            font-weight: 600;
            line-height: 1.2;
            margin-bottom: 16px;
            color: var(--primary-color);
        }}
        
        .featured-description {{
            font-size: 1.2em;
            line-height: 1.6;
            margin-bottom: 20px;
            color: var(--text-color);
        }}
        
        .featured-meta {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .source-badge {{
            font-weight: 600;
            color: var(--secondary-color);
        }}
        
        /* News Grid */
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 32px;
            margin-bottom: 32px;
        }}
        
        .news-card {{
            background: white;
            border: 1px solid var(--border-color);
            overflow: hidden;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .news-card:hover {{
            box-shadow: var(--hover-shadow);
            transform: translateY(-2px);
        }}
        
        .card-image-wrapper {{
            width: 100%;
            height: 200px;
            overflow: hidden;
            background: var(--light-gray);
            position: relative;
        }}
        
        .card-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}
        
        .news-card:hover .card-image {{
            transform: scale(1.05);
        }}
        
        .card-category {{
            position: absolute;
            top: 12px;
            left: 12px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 4px 12px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .card-content {{
            padding: 20px;
        }}
        
        .card-title {{
            font-family: 'Reith Serif', Georgia, serif;
            font-size: 1.3em;
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: 12px;
            color: var(--primary-color);
        }}
        
        .card-description {{
            font-size: 0.95em;
            line-height: 1.5;
            color: var(--text-color);
            margin-bottom: 16px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid var(--border-color);
        }}
        
        .card-source {{
            font-size: 0.85em;
            font-weight: 600;
            color: var(--secondary-color);
        }}
        
        .read-more {{
            font-size: 0.85em;
            font-weight: 600;
            color: var(--primary-color);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .read-more:hover {{
            color: var(--secondary-color);
        }}
        
        /* Footer */
        footer {{
            background: var(--primary-color);
            color: white;
            padding: 48px 24px 32px;
            margin-top: 64px;
        }}
        
        .footer-content {{
            max-width: 1280px;
            margin: 0 auto;
            text-align: center;
        }}
        
        .footer-logo {{
            font-size: 1.8em;
            font-weight: 700;
            margin-bottom: 16px;
        }}
        
        .footer-text {{
            font-size: 0.95em;
            opacity: 0.8;
            margin-bottom: 24px;
        }}
        
        .auto-update-badge {{
            background: rgba(255,255,255,0.1);
            padding: 12px 24px;
            border-radius: 8px;
            display: inline-block;
            font-size: 0.9em;
        }}
        
        /* Placeholder for missing images */
        .placeholder-image {{
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3em;
        }}
        
        /* Responsive Design */
        @media (max-width: 1024px) {{
            .news-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 24px;
            }}
            
            .featured-story {{
                grid-template-columns: 1fr;
            }}
            
            .featured-image {{
                height: 350px;
            }}
        }}
        
        @media (max-width: 768px) {{
            .site-title {{
                font-size: 2em;
            }}
            
            .category-nav-container {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            
            .news-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .featured-title {{
                font-size: 1.8em;
            }}
            
            .featured-image {{
                height: 250px;
            }}
            
            .card-image-wrapper {{
                height: 180px;
            }}
        }}
        
        /* Loading Animation */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .news-card {{
            animation: fadeIn 0.6s ease-out forwards;
        }}
        
        .news-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .news-card:nth-child(2) {{ animation-delay: 0.2s; }}
        .news-card:nth-child(3) {{ animation-delay: 0.3s; }}
        .news-card:nth-child(4) {{ animation-delay: 0.4s; }}
        .news-card:nth-child(5) {{ animation-delay: 0.5s; }}
        .news-card:nth-child(6) {{ animation-delay: 0.6s; }}
    </style>
</head>
<body>
    <header>
        <div class="header-container">
            <h1 class="site-title">⚡ Tech & Motor News</h1>
            <p class="site-tagline">Your daily source for technology and automotive innovation</p>
            <div class="date-badge">📅 {today}</div>
        </div>
    </header>
    
    <nav class="category-nav">
        <div class="category-nav-container">
            <div class="nav-tab active">All News</div>
            <div class="nav-tab">Technology</div>
            <div class="nav-tab">Automotive</div>
        </div>
    </nav>
    
    <div class="container">
"""
        
        # Featured Story (first article with image)
        if articles:
            featured = articles[0]
            title = featured.get('rewritten_title', featured['title'])
            content = featured.get('rewritten_content', featured['description'])
            source = featured['source']
            url = featured['url']
            image = featured.get('image', '')
            category = featured.get('category', 'News')
            
            html += f"""
        <article class="featured-story">
            <div>
"""
            if image:
                html += f'                <img src="{image}" alt="{title}" class="featured-image">\n'
            else:
                html += f'                <div class="featured-image placeholder-image">📰</div>\n'
            
            html += f"""            </div>
            <div class="featured-content">
                <span class="featured-badge">{category}</span>
                <h2 class="featured-title">{title}</h2>
                <p class="featured-description">{content}</p>
                <div class="featured-meta">
                    <span class="source-badge">{source}</span>
                    <span>•</span>
                    <a href="{url}" target="_blank" class="read-more">Read full article →</a>
                </div>
            </div>
        </article>
"""
        
        # News Grid (remaining articles)
        html += '        <div class="news-grid">\n'
        
        for article in articles[1:]:
            title = article.get('rewritten_title', article['title'])
            content = article.get('rewritten_content', article['description'])
            source = article['source']
            url = article['url']
            image = article.get('image', '')
            category = article.get('category', 'News')
            
            html += f"""
            <article class="news-card" onclick="window.open('{url}', '_blank')">
                <div class="card-image-wrapper">
"""
            if image:
                html += f'                    <img src="{image}" alt="{title}" class="card-image">\n'
            else:
                html += f'                    <div class="placeholder-image">📰</div>\n'
            
            html += f"""                    <span class="card-category">{category}</span>
                </div>
                <div class="card-content">
                    <h3 class="card-title">{title}</h3>
                    <p class="card-description">{content}</p>
                    <div class="card-meta">
                        <span class="card-source">{source}</span>
                        <a href="{url}" target="_blank" class="read-more">Read →</a>
                    </div>
                </div>
            </article>
"""
        
        html += """        </div>
    </div>
    
    <footer>
        <div class="footer-content">
            <div class="footer-logo">⚡ Tech & Motor News</div>
            <p class="footer-text">Bringing you the latest in technology and automotive innovation, updated daily.</p>
            <div class="auto-update-badge">
                ✨ Automatically updated daily with AI-curated content
            </div>
            <p style="margin-top: 24px; font-size: 0.85em; opacity: 0.6;">
                © """ + str(datetime.now().year) + """ Tech & Motor News. Content curated from multiple sources.
            </p>
        </div>
    </footer>
    
    <script>
        // Simple category filter (optional enhancement)
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', function() {
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    </script>
</body>
</html>
"""
        return html
    
    def run(self):
        """Main execution function"""
        print("🚀 Starting advanced news automation...")
        print("=" * 60)
        
        # Scrape tech news from multiple sources
        print("\n📱 Scraping BBC Technology...")
        bbc_tech = self.scrape_bbc_tech_news(limit=5)
        print(f"   Found {len(bbc_tech)} articles")
        
        print("\n🚗 Scraping BBC Business (Auto/Motor)...")
        bbc_auto = self.scrape_bbc_business_news(limit=3)
        print(f"   Found {len(bbc_auto)} articles")
        
        print("\n💻 Scraping CNN Tech...")
        cnn_tech = self.scrape_cnn_tech_news(limit=5)
        print(f"   Found {len(cnn_tech)} articles")
        
        print("\n🔧 Scraping TechCrunch...")
        tc_articles = self.scrape_techcrunch_news(limit=4)
        print(f"   Found {len(tc_articles)} articles")
        
        print("\n📲 Scraping The Verge...")
        verge_articles = self.scrape_verge_tech_news(limit=3)
        print(f"   Found {len(verge_articles)} articles")
        
        # Combine all articles
        all_articles = bbc_tech + bbc_auto + cnn_tech + tc_articles + verge_articles
        
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
        
        print(f"\n✅ Total unique articles: {len(unique_articles)}")
        
        # Limit to top 15 articles
        all_articles = unique_articles[:15]
        
        # Rewrite articles with AI
        print(f"\n🤖 Rewriting {len(all_articles)} articles with Gemini AI...")
        print("-" * 60)
        for i, article in enumerate(all_articles, 1):
            print(f"  [{i}/{len(all_articles)}] {article['title'][:50]}...")
            all_articles[i-1] = self.rewrite_article(article)
        
        print("\n" + "=" * 60)
        
        # Generate HTML
        print("🎨 Generating premium HTML with images...")
        html_content = self.generate_html(all_articles)
        
        # Save to file
        with open('/home/claude/news.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ news.html generated successfully!")
        print(f"📊 Articles: {len(all_articles)}")
        print(f"🖼️  With images: {sum(1 for a in all_articles if a.get('image'))}")
        print("=" * 60)
        
        return html_content

if __name__ == "__main__":
    automation = NewsAutomation()
    automation.run()