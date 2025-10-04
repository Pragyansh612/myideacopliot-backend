"""Competitor research service with web scraping"""
import os
import uuid
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import google.generativeai as genai
from app.core.database import supabase_client
from app.utils.exceptions import ValidationError
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = settings.GEMINI_API_KEY
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class CompetitorService:
    """Service for competitor research and web scraping"""
    
    @staticmethod
    async def scrape_website(url: str) -> Dict[str, Any]:
        """
        Scrape a website and extract key information
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc or parsed_url.path
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    html = await response.text()
                    status_code = response.status
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.string if title else domain
            
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            # Extract headings
            headings = {
                'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
                'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
                'h3': [h.get_text(strip=True) for h in soup.find_all('h3')]
            }
            
            # Extract main content
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            content_text = ' '.join(paragraphs[:20])  # First 20 paragraphs
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http'):
                    links.append(href)
            
            # Extract buttons/CTAs
            buttons = [button.get_text(strip=True) for button in soup.find_all('button')]
            buttons.extend([a.get_text(strip=True) for a in soup.find_all('a', class_=lambda x: x and 'button' in x.lower())])
            
            return {
                'url': url,
                'domain': domain,
                'status_code': status_code,
                'title': title_text,
                'description': description,
                'headings': headings,
                'content': content_text[:2000],  # Limit content length
                'buttons': buttons[:10],
                'link_count': len(links),
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout scraping {url}")
            return {'url': url, 'error': 'Timeout', 'scraped_at': datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {'url': url, 'error': str(e), 'scraped_at': datetime.utcnow().isoformat()}
    
    @staticmethod
    async def analyze_competitor(scraped_data: Dict[str, Any], idea_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze scraped competitor data using AI
        """
        try:
            if not GEMINI_API_KEY:
                raise ValidationError("Gemini API key not configured")
            
            # Construct analysis prompt
            prompt = f"""
            Analyze this competitor website data and provide structured insights:
            
            Website: {scraped_data.get('title', 'Unknown')}
            URL: {scraped_data.get('url', '')}
            Description: {scraped_data.get('description', '')}
            
            Key Headings:
            {json.dumps(scraped_data.get('headings', {}), indent=2)}
            
            Content Preview:
            {scraped_data.get('content', '')[:1000]}
            
            Call-to-Actions:
            {', '.join(scraped_data.get('buttons', [])[:5])}
            
            {f'My Product Context: {idea_context}' if idea_context else ''}
            
            Provide a comprehensive analysis in JSON format with:
            1. competitor_name: The company/product name
            2. description: Brief description of what they offer (2-3 sentences)
            3. strengths: Array of 3-5 key strengths
            4. weaknesses: Array of 3-5 potential weaknesses or gaps
            5. differentiation_opportunities: Array of 3-5 ways to differentiate from this competitor
            6. market_position: Their apparent market position (leader/challenger/niche/emerging)
            7. key_features: Array of 5-7 main features they offer
            8. target_audience: Who they seem to be targeting
            9. pricing_strategy: Their apparent pricing approach (if visible)
            10. confidence_score: Your confidence in this analysis (0.0-1.0)
            
            Be objective and analytical. Focus on actionable insights.
            """
            
            # Generate analysis using Gemini
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            ai_response = response.text
            
            # Parse JSON response
            try:
                if "```json" in ai_response:
                    ai_response = ai_response.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_response:
                    ai_response = ai_response.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback to basic analysis
                analysis = {
                    "competitor_name": scraped_data.get('title', 'Unknown'),
                    "description": scraped_data.get('description', ''),
                    "raw_analysis": ai_response
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing competitor: {e}")
            return {
                "competitor_name": scraped_data.get('title', 'Unknown'),
                "error": str(e)
            }
    
    @staticmethod
    async def scrape_and_analyze(
        user_id: str,
        idea_id: str,
        urls: List[str],
        analyze: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs and optionally analyze them
        """
        try:
            supabase = supabase_client
            
            # Get idea context
            idea_context = None
            if analyze:
                idea_response = supabase.table("ideas").select("title, description").eq("id", idea_id).single().execute()
                if idea_response.data:
                    idea = idea_response.data
                    idea_context = f"Title: {idea['title']}\nDescription: {idea.get('description', '')}"
            
            # Scrape all URLs
            scrape_tasks = [CompetitorService.scrape_website(url) for url in urls]
            scraped_results = await asyncio.gather(*scrape_tasks)
            
            results = []
            
            for scraped_data in scraped_results:
                if scraped_data.get('error'):
                    logger.warning(f"Skipping failed scrape: {scraped_data}")
                    continue
                
                # Analyze if requested
                analysis = {}
                if analyze:
                    analysis = await CompetitorService.analyze_competitor(scraped_data, idea_context)
                
                # Save to database
                research_record = {
                    "id": str(uuid.uuid4()),
                    "idea_id": idea_id,
                    "user_id": user_id,
                    "competitor_name": str(analysis.get('competitor_name', scraped_data.get('title', 'Unknown')))[:255],
                    "competitor_url": scraped_data.get('url'),
                    "description": str(analysis.get('description', scraped_data.get('description', '')))[:2000],
                    "strengths": analysis.get('strengths', [])[:10],  # Limit array size
                    "weaknesses": analysis.get('weaknesses', [])[:10],
                    "differentiation_opportunities": analysis.get('differentiation_opportunities', [])[:10],
                    "market_position": str(analysis.get('market_position', ''))[:255] if analysis.get('market_position') else None,
                    "funding_info": {},
                    "research_date": datetime.utcnow().isoformat(),
                    "data_sources": [scraped_data.get('url')],
                    "confidence_score": analysis.get('confidence_score', 0.7)
                }
                
                result = supabase.table("competitor_research").insert(research_record).execute()
                results.append(result.data[0])
            
            return results
            
        except Exception as e:
            logger.error(f"Error in scrape_and_analyze: {e}")
            raise
    
    @staticmethod
    async def get_research(user_id: str, idea_id: str) -> List[Dict[str, Any]]:
        """Get all competitor research for an idea"""
        try:
            supabase = supabase_client
            
            response = supabase.table("competitor_research")\
                .select("*")\
                .eq("idea_id", idea_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"Error getting research: {e}")
            raise
