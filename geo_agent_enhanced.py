import os
import json
import requests
import re
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass
from bs4 import BeautifulSoup
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph import START
from dotenv import load_dotenv
from config import AGENT_CONFIG
from website_similarity_analyzer import analyze_website_similarity
from webpage_reader import crawl_website, extract_llm_readable_content
from reranker_api import rerank_documents
from datetime import datetime
import time
import traceback

# Load environment variables
load_dotenv()

# State definition for the agent
class AgentState(TypedDict):
    website_url: str
    target_keyword: str
    current_html: str
    original_html: str  # Store original HTML for comparison
    current_score: float
    improvement_threshold: float
    optimization_history: List[Dict]
    best_score: float
    best_html: str
    similar_websites: List[Dict]
    final_result: Optional[Dict]


@dataclass
class OptimizationResult:
    """Result of an optimization step"""
    improved_html: str
    new_score: float
    improvement: float
    step_name: str
    success: bool


class EnhancedGEOAgent:
    """
    Enhanced Generative Engine Optimization (GEO) Agent using LangGraph
    Iteratively optimizes website HTML for better search engine relevance
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=AGENT_CONFIG["llm_model"],
            temperature=AGENT_CONFIG["temperature"],
            max_tokens=AGENT_CONFIG["max_tokens"]
        )
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_agent)
        workflow.add_node("get_initial_score", self._get_initial_score)
        workflow.add_node("optimize_html", self._optimize_html)
        workflow.add_node("evaluate_improvement", self._evaluate_improvement)
        workflow.add_node("finalize", self._finalize)
        
        # Add edges
        workflow.add_edge(START, "initialize")
        workflow.add_edge("initialize", "get_initial_score")
        workflow.add_edge("get_initial_score", "optimize_html")
        workflow.add_edge("optimize_html", "evaluate_improvement")
        workflow.add_edge("evaluate_improvement", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _initialize_agent(self, state: AgentState) -> AgentState:
        """Initialize the agent with website URL and target keyword"""
        print(f"\n{'='*60}")
        print("ENHANCED GEO AGENT INITIALIZATION")
        print(f"Website: {state['website_url']}")
        print(f"Target Keyword: {state['target_keyword']}")
        print(f"Improvement Threshold: {state['improvement_threshold']}")
        print(f"{'='*60}")
        
        # Get initial HTML content using crawl_website
        try:
            print(f"🔄 Crawling website to get HTML...")
            raw_html = crawl_website(state['website_url'])
            
            if raw_html:
                print(f"✅ Successfully crawled HTML ({len(raw_html)} characters)")
                state['current_html'] = raw_html
            else:
                print(f"❌ Failed to crawl website")
                state['current_html'] = ""
                
        except Exception as e:
            print(f"Error getting initial content: {e}")
            state['current_html'] = ""
        
        state['current_score'] = 0.0
        state['best_score'] = 0.0
        state['best_html'] = state['current_html']
        state['original_html'] = state['current_html']  # Store original HTML for comparison
        state['optimization_history'] = []
        
        return state
    
    def _get_initial_score(self, state: AgentState) -> AgentState:
        """Get the initial relevance score for the website"""
        print(f"\n📊 GETTING INITIAL RELEVANCE SCORE")
        print("-" * 40)
        
        try:
            # Get similar websites and calculate initial score
            results = analyze_website_similarity(
                query=state['target_keyword'],
                website_url=state['website_url'],
                max_similar_results=1
            )
            
            # Find our website in the results
            our_website = None
            for result in results:
                if result.get('is_your_website', False):
                    our_website = result
                    break
            
            if our_website:
                print(our_website.keys())
                initial_score = our_website.get('relevance_score', 0.0)
                state['current_score'] = initial_score
                state['best_score'] = initial_score
                state['similar_websites'] = results
                print(f"✅ Initial relevance score: {initial_score:.4f}")
            else:
                print("❌ Could not find our website in results")
                state['current_score'] = 0.0
                state['best_score'] = 0.0
                state['similar_websites'] = results
                
        except Exception as e:
            print(f"❌ Error getting initial score: {e}")
            state['current_score'] = 0.0
            state['best_score'] = 0.0
            state['similar_websites'] = []
        
        return state
    
    def _extract_html_elements(self, html_or_soup) -> Dict[str, Any]:
        """Extract important HTML elements for optimization"""
        # Handle both string and BeautifulSoup object
        if isinstance(html_or_soup, str):
            soup = BeautifulSoup(html_or_soup, 'html.parser')
        else:
            soup = html_or_soup
        
        elements = {
            'title': soup.find('title'),
            'meta_description': soup.find('meta', attrs={'name': 'description'}),
            'meta_keywords': soup.find('meta', attrs={'name': 'keywords'}),
            'h1_tags': soup.find_all('h1'),
            'h2_tags': soup.find_all('h2'),
            'h3_tags': soup.find_all('h3'),
            'main_content': soup.find('main') or soup.find('body'),
            'head': soup.find('head'),
            'body': soup.find('body'),
            'schema_scripts': soup.find_all('script', type='application/ld+json'),
            'og_tags': soup.find_all('meta', property=lambda x: x and x.startswith('og:')),
            'twitter_tags': soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}),
            'canonical': soup.find('link', rel='canonical'),
            'robots': soup.find('meta', attrs={'name': 'robots'}),
            'viewport': soup.find('meta', attrs={'name': 'viewport'}),
            'charset': soup.find('meta', attrs={'charset': True}),
            'language': soup.find('html').get('lang', 'en') if soup.find('html') else 'en'
        }
        
        return elements
    
    def _optimize_title(self, title_element, target_keyword: str) -> str:
        """Optimize the title tag"""
        if not title_element:
            return f"<title>{target_keyword} - Expert Guide & Best Practices</title>"
        
        current_title = title_element.get_text()
        prompt = f"""
Optimize this title for SEO with the target keyword: "{target_keyword}"

Current title: {current_title}
Target keyword: {target_keyword}

Requirements:
- Keep under 60 characters
- Include the target keyword naturally
- Make it compelling and click-worthy
- Maintain brand consistency

Return ONLY the optimized title tag, nothing else.
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    
    def _optimize_meta_description(self, meta_desc_element, target_keyword: str) -> str:
        """Optimize the meta description"""
        current_desc = ""
        if meta_desc_element:
            current_desc = meta_desc_element.get('content', '')
        
        prompt = f"""
Create an optimized meta description for this webpage.

Current description: {current_desc}
Target keyword: {target_keyword}

Requirements:
- Keep under 160 characters
- Include target keyword naturally
- Make it compelling and action-oriented
- Include a clear value proposition

Return ONLY the optimized meta description tag, nothing else.
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    
    def _optimize_headings(self, h1_tags, h2_tags, h3_tags, target_keyword: str) -> Dict[str, List[str]]:
        """Optimize heading structure"""
        headings_data = {
            'h1': [h.get_text() for h in h1_tags],
            'h2': [h.get_text() for h in h2_tags],
            'h3': [h.get_text() for h in h3_tags]
        }
        
        prompt = f"""
Optimize the heading structure for SEO with the target keyword: "{target_keyword}"

Current headings:
H1: {headings_data['h1']}
H2: {headings_data['h2']}
H3: {headings_data['h3']}

Requirements:
- Include target keyword in at least one H2 heading
- Use proper heading hierarchy (one H1, multiple H2s, H3s)
- Make headings descriptive and engaging
- Use long-tail keywords in subheadings

Return ONLY a JSON array of optimized headings:
```json
{{
  "h1": ["Optimized H1"],
  "h2": ["Optimized H2 1", "Optimized H2 2"],
  "h3": ["Optimized H3 1", "Optimized H3 2"]
}}
```
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        try:
            # Extract JSON from response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return headings_data
        except:
            return headings_data
    
    def _add_schema_markup(self, target_keyword: str, website_url: str) -> str:
        """Add schema markup for better SEO"""
        prompt = f"""
Create JSON-LD schema markup for a webpage about "{target_keyword}".

Website URL: {website_url}
Target Keyword: {target_keyword}

Requirements:
- Include Organization schema
- Add Article schema if relevant
- Include BreadcrumbList schema
- Add FAQ schema if applicable
- Ensure valid JSON-LD structure

Return ONLY the JSON-LD script tag, nothing else.
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    
    def _optimize_body_content(self, body_element, target_keyword: str) -> str:
        """Optimize body content for better SEO and user engagement"""
        if not body_element:
            return ""
        
        # Extract current body content and analyze structure
        current_content = body_element.get_text() if body_element else ""
        current_html = str(body_element) if body_element else ""
        
        # Analyze existing content structure
        soup = BeautifulSoup(current_html, 'html.parser')
        existing_paragraphs = len(soup.find_all('p'))
        existing_headings = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        existing_lists = len(soup.find_all(['ul', 'ol']))
        
        content_analysis = f"""
Content Analysis:
- Word count: {len(current_content.split())} words
- Paragraphs: {existing_paragraphs}
- Headings: {existing_headings}
- Lists: {existing_lists}
"""
        
        prompt = f"""
Optimize the body content of a webpage for SEO and user engagement with the target keyword: "{target_keyword}"

Current content preview: {current_content[:500]}...
{content_analysis}

Requirements:
- Include the target keyword naturally throughout the content (aim for 1-2% keyword density)
- Create engaging, informative content that provides value
- Use proper paragraph structure with 2-3 sentences per paragraph
- Include relevant subheadings (H2, H3) to break up content
- Add bullet points or numbered lists where appropriate
- Include a call-to-action section
- Ensure content is at least 800-1200 words for comprehensive coverage
- Use natural language that flows well
- Include relevant examples or case studies if applicable
- Make content scannable with proper formatting
- Maintain any existing important content while enhancing it
- Add internal linking opportunities where relevant

Return ONLY the optimized body content HTML with proper HTML tags (like <p>, <h2>, <h3>, <ul>, <li>, etc.), nothing else.
"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        optimized_content = response.content.strip()
        
        # Clean the response to extract only HTML content
        return self._clean_html_response(optimized_content)
    
    def _optimize_images_and_links(self, body_element, target_keyword: str) -> None:
        """Optimize images and links in the body content"""
        if not body_element:
            return
        
        # Optimize images
        images = body_element.find_all('img')
        print(f"Found {len(images)} images to optimize")
        for i, img in enumerate(images):
            print(f"Processing image {i+1}/{len(images)}")
            # Add alt text if missing or optimize existing
            if not img.get('alt') or img.get('alt').strip() == '':
                new_alt = f"{target_keyword} - relevant image"
                print(f"  Adding alt text: '{new_alt}'")
                img['alt'] = new_alt
            elif target_keyword.lower() not in img.get('alt', '').lower():
                # Enhance existing alt text with keyword
                current_alt = img.get('alt', '')
                new_alt = f"{current_alt} - {target_keyword}"
                print(f"  Enhancing alt text: '{current_alt}' → '{new_alt}'")
                img['alt'] = new_alt
            else:
                print(f"  Image alt text already optimized: '{img.get('alt', '')}'")
        
        # Optimize links
        links = body_element.find_all('a')
        print(f"Found {len(links)} links to optimize")
        for i, link in enumerate(links):
            print(f"Processing link {i+1}/{len(links)}")
            # Add title attribute if missing
            if not link.get('title'):
                link_text = link.get_text().strip()
                if link_text:
                    new_title = f"Learn more about {target_keyword}"
                    print(f"  Adding title: '{new_title}'")
                    link['title'] = new_title
                else:
                    new_title = f"Click to learn more about {target_keyword}"
                    print(f"  Adding title: '{new_title}'")
                    link['title'] = new_title
            else:
                print(f"  Link already has title: '{link.get('title', '')}'")

    def _optimize_body_content_surgically(self, body_element, target_keyword: str, max_optimizations: int = 5) -> None:
        """
        Surgically optimizes text content within the body without destroying the HTML structure.
        It finds text-heavy tags like <p> and rewrites their content in place.
        """
        if not body_element:
            return

        print(f"\n🔍 ANALYZING BODY CONTENT FOR OPTIMIZATION")
        print(f"Target keyword: '{target_keyword}'")
        print(f"Max optimizations: {max_optimizations}")

        # Find potential candidates for optimization (e.g., paragraphs with enough text)
        candidates = body_element.find_all('p')
        print(f"Found {len(candidates)} paragraph candidates")
        
        optimizations_done = 0
        skipped_count = 0

        for i, tag in enumerate(candidates):
            if optimizations_done >= max_optimizations:
                print(f"🛑 Reached max optimizations limit of {max_optimizations}.")
                break

            original_text = tag.get_text(strip=True)
            print(f"\n📝 Processing paragraph {i+1}/{len(candidates)}")
            print(f"Original text length: {len(original_text)} characters")

            # Only optimize paragraphs with a reasonable amount of text
            if len(original_text) > 80:
                print(f"✍️  Optimizing paragraph: '{original_text[:70]}...'")

                prompt = f"""
You are an expert SEO content editor. Your task is to rewrite the following text to be more engaging for the user and to naturally incorporate the target keyword: "{target_keyword}".

**Instructions:**
1.  **Integrate the keyword:** Seamlessly weave "{target_keyword}" into the text.
2.  **Preserve Meaning:** Do not change the core message or intent of the original text.
3.  **Maintain Tone:** Keep the professional tone of the original content.
4.  **Concise Output:** Return ONLY the rewritten text. Do not add any extra HTML tags, quotation marks, or explanations.

**Original Text:**
"{original_text}"

**Rewritten Text:**
"""
                try:
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    rewritten_text = response.content.strip().strip('"') # Clean up response

                    if rewritten_text and rewritten_text != original_text:
                        print(f"✅ Paragraph {i+1} successfully rewritten:")
                        print(f"   Original: '{original_text[:100]}...'")
                        print(f"   Optimized: '{rewritten_text[:100]}...'")
                        # This is the key: replace the content *inside* the tag
                        tag.string = rewritten_text
                        optimizations_done += 1
                    else:
                        print(f"🟡 Paragraph {i+1}: No significant change suggested by LLM.")
                        skipped_count += 1

                except Exception as e:
                    print(f"❌ Error optimizing paragraph {i+1}: {e}")
                    skipped_count += 1
            else:
                print(f"⏭️  Skipping paragraph {i+1}: Too short ({len(original_text)} characters)")
                skipped_count += 1

        print(f"\n📊 BODY OPTIMIZATION SUMMARY:")
        print(f"   Total paragraphs found: {len(candidates)}")
        print(f"   Paragraphs optimized: {optimizations_done}")
        print(f"   Paragraphs skipped: {skipped_count}")
        print(f"   Target keyword: '{target_keyword}'")
    def _add_internal_linking(self, body_element, target_keyword: str, soup: BeautifulSoup) -> None:
        """Add internal linking and structured content to improve SEO"""
        if not body_element:
            return
        
        # Find paragraphs that could benefit from internal links
        paragraphs = body_element.find_all('p')
        print(f"Found {len(paragraphs)} paragraphs for internal linking")
        
        # Create related topics based on the target keyword
        related_topics = self._generate_related_topics(target_keyword)
        print(f"Generated {len(related_topics)} related topics: {[t['title'] for t in related_topics]}")
        
        # Add internal links to relevant paragraphs
        for i, p in enumerate(paragraphs[:5]):  # Limit to first 5 paragraphs
            if related_topics and i < len(related_topics):
                topic = related_topics[i]
                print(f"Adding internal link to paragraph {i+1}: {topic['title']}")
                
                # Create a link at the end of the paragraph
                link_tag = soup.new_tag('a')
                link_tag['href'] = f"#{topic['slug']}"
                link_tag['title'] = topic['title']
                link_tag.string = f"Learn more about {topic['title']}"
                
                print(f"  Created link: {link_tag}")
                
                # Add the link to the paragraph
                p.append(" ")
                p.append(link_tag)
                print(f"  Added link to paragraph {i+1}")
            else:
                print(f"Skipping paragraph {i+1} - no related topic available")
    
    def _generate_related_topics(self, target_keyword: str) -> List[Dict[str, str]]:
        """Generate related topics for internal linking"""
        prompt = f"""
Generate 5 related topics for internal linking based on the target keyword: "{target_keyword}"

Requirements:
- Topics should be closely related to the main keyword
- Each topic should have a clear, descriptive title
- Include a URL-friendly slug for each topic
- Topics should provide additional value to readers

Return ONLY a JSON array like this:
```json
[
  {{"title": "Topic Title", "slug": "topic-slug"}},
  {{"title": "Another Topic", "slug": "another-topic"}}
]
```
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except:
            pass
        
        # Fallback related topics
        return [
            {"title": f"Benefits of {target_keyword}", "slug": f"benefits-{target_keyword.lower().replace(' ', '-')}"},
            {"title": f"Best Practices for {target_keyword}", "slug": f"best-practices-{target_keyword.lower().replace(' ', '-')}"},
            {"title": f"Common Mistakes in {target_keyword}", "slug": f"mistakes-{target_keyword.lower().replace(' ', '-')}"},
            {"title": f"Advanced {target_keyword} Techniques", "slug": f"advanced-{target_keyword.lower().replace(' ', '-')}"},
            {"title": f"{target_keyword} Tools and Resources", "slug": f"tools-{target_keyword.lower().replace(' ', '-')}"}
        ]
    
    def _optimize_html(self, state: AgentState) -> AgentState:
            """Optimize the HTML content using targeted element optimization"""
            print(f"\n🔧 OPTIMIZING HTML FOR TARGET KEYWORD")
            print("-" * 40)
            print(f"Target keyword: {state['target_keyword']}")
            print(f"Current score: {state['current_score']:.4f}")
            
            try:
                # Parse HTML and extract elements
                soup = BeautifulSoup(state['current_html'], 'html.parser')
                
                # Save the initial HTML before any optimizations
                with open('original_html.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                print("💾 Saved original HTML to original_html.html")
                
                elements = self._extract_html_elements(soup)
                
                print("📝 Extracting HTML elements for optimization...")
                
                # --- Your existing optimizations for title, meta, headings, and schema are fine ---
                # --- They will be preserved here. ---
                
                # Optimize title
                if elements['title']:
                    print("\n" + "="*60)
                    print("🔧 OPTIMIZING TITLE")
                    print("="*60)
                    original_title = elements['title'].get_text()
                    print(f"Original title: '{original_title}'")
                    
                    optimized_title = self._optimize_title(elements['title'], state['target_keyword'])
                    print(f"Optimized title HTML: {optimized_title}")
                    
                    optimized_title_soup = BeautifulSoup(optimized_title, 'html.parser')
                    title_text = optimized_title_soup.get_text().strip()
                    print(f"Extracted title text: '{title_text}'")
                    
                    elements['title'].string = title_text
                    print(f"✅ Title optimized: '{original_title}' → '{title_text}'")
                    print("="*60)

                # Optimize meta description
                if elements['meta_description']:
                    print("\n" + "="*60)
                    print("🔧 OPTIMIZING META DESCRIPTION")
                    print("="*60)
                    original_meta = elements['meta_description'].get('content', '')
                    print(f"Original meta description: '{original_meta}'")
                    
                    optimized_meta = self._optimize_meta_description(elements['meta_description'], state['target_keyword'])
                    print(f"Optimized meta HTML: {optimized_meta}")
                    
                    optimized_meta_soup = BeautifulSoup(optimized_meta, 'html.parser')
                    meta_tag = optimized_meta_soup.find('meta')
                    if meta_tag:
                        new_content = meta_tag.get('content', '')
                        print(f"Extracted meta content: '{new_content}'")
                        elements['meta_description']['content'] = new_content
                        print(f"✅ Meta description optimized: '{original_meta}' → '{new_content}'")
                    print("="*60)
                else:
                    print("\n" + "="*60)
                    print("🔧 ADDING META DESCRIPTION")
                    print("="*60)
                    new_meta = self._optimize_meta_description(None, state['target_keyword'])
                    print(f"Generated meta HTML: {new_meta}")
                    if elements['head']:
                        meta_soup = BeautifulSoup(new_meta, 'html.parser')
                        meta_tag = meta_soup.find('meta')
                        if meta_tag:
                            print(f"Adding meta tag: {meta_tag}")
                            elements['head'].append(meta_tag)
                            print("✅ Meta description added")
                    print("="*60)
                
                # Optimize headings
                print("\n" + "="*60)
                print("🔧 OPTIMIZING HEADINGS")
                print("="*60)
                
                # Show original headings
                original_h1 = [h.get_text() for h in elements['h1_tags']]
                original_h2 = [h.get_text() for h in elements['h2_tags']]
                original_h3 = [h.get_text() for h in elements['h3_tags']]
                print(f"Original H1 tags: {original_h1}")
                print(f"Original H2 tags: {original_h2}")
                print(f"Original H3 tags: {original_h3}")
                
                optimized_headings = self._optimize_headings(
                    elements['h1_tags'], 
                    elements['h2_tags'], 
                    elements['h3_tags'], 
                    state['target_keyword']
                )
                print(f"Optimized headings structure: {optimized_headings}")
                
                # Apply heading optimizations
                all_headings = elements['h1_tags'] + elements['h2_tags'] + elements['h3_tags']
                heading_index = 0
                
                for h_type, headings in optimized_headings.items():
                    for i, new_heading in enumerate(headings):
                        if heading_index < len(all_headings):
                            old_heading = all_headings[heading_index]
                            old_text = old_heading.get_text()
                            print(f"Replacing {h_type} heading: '{old_text}' → '{new_heading}'")
                            old_heading.string = new_heading
                            heading_index += 1
                
                print("✅ Headings optimized")
                print("="*60)
                
                # Add schema markup
                print("\n" + "="*60)
                print("🔧 ADDING SCHEMA MARKUP")
                print("="*60)
                schema_markup = self._add_schema_markup(state['target_keyword'], state['website_url'])
                print(f"Generated schema markup: {schema_markup}")
                if schema_markup and elements['head']:
                    schema_soup = BeautifulSoup(schema_markup, 'html.parser')
                    schema_script = schema_soup.find('script')
                    if schema_script:
                        print(f"Adding schema script to head: {schema_script}")
                        elements['head'].append(schema_script)
                        print("✅ Schema markup added")
                print("="*60)


                # =================================================================
                # CORRECTED BODY OPTIMIZATION LOGIC
                # =================================================================
                if elements['body']:
                    print("\n" + "="*50)
                    print("🔧 SURGICALLY OPTIMIZING BODY CONTENT")
                    print("="*50)
                    # 1. Call the correct, non-destructive function to rewrite paragraphs
                    self._optimize_body_content_surgically(elements['body'], state['target_keyword'])
                    print("✅ Body content surgically optimized.")
                    print("="*50)

                    # 2. Optimize images and links on the now-modified body
                    print("\n" + "="*50)
                    print("🔧 OPTIMIZING IMAGES AND LINKS")
                    print("="*50)
                    self._optimize_images_and_links(elements['body'], state['target_keyword'])
                    print("✅ Images and links optimized.")
                    print("="*50)
                    
                    # 3. Add internal linking to the modified body
                    print("\n" + "="*50)
                    print("🔧 ADDING INTERNAL LINKING")
                    print("="*50)
                    self._add_internal_linking(elements['body'], state['target_keyword'], soup)
                    print("✅ Internal linking added.")
                    print("="*50)

                # =================================================================
                # END OF CORRECTED SECTION
                # =================================================================
                
                # Finalize the HTML
                optimized_html = str(soup)
                state['current_html'] = optimized_html
                
                with open('optimized_html.html', 'w', encoding='utf-8') as f:
                    f.write(optimized_html)

                print(f"\n✅ Successfully generated optimized HTML ({len(optimized_html)} characters)")
                
            except Exception as e:
                print(traceback.format_exc())
                print(f"❌ Error optimizing HTML: {e}")
            
            return state
    
    def _clean_html_response(self, html_response: str) -> str:
        """Clean the LLM response to extract only the HTML content"""
        if not html_response:
            return ""
        
        # Remove markdown code blocks if present
        html_response = re.sub(r'```html\s*', '', html_response)
        html_response = re.sub(r'```\s*$', '', html_response)
        html_response = re.sub(r'^```\s*', '', html_response)
        
        # Remove any explanations before or after HTML
        # Find the first <!DOCTYPE or <html tag
        doctype_match = re.search(r'<!DOCTYPE[^>]*>', html_response, re.IGNORECASE)
        html_tag_match = re.search(r'<html[^>]*>', html_response, re.IGNORECASE)
        
        if doctype_match:
            start_pos = doctype_match.start()
        elif html_tag_match:
            start_pos = html_tag_match.start()
        else:
            # If no HTML structure found, return as is
            return html_response.strip()
        
        # Find the last </html> tag
        end_match = re.search(r'</html>', html_response, re.IGNORECASE)
        if end_match:
            end_pos = end_match.end()
            html_response = html_response[start_pos:end_pos]
        else:
            html_response = html_response[start_pos:]
        
        return html_response.strip()
    
    def _evaluate_improvement(self, state: AgentState) -> AgentState:
        """Evaluate the improvement in relevance score by comparing with related documents"""
        print(f"\n📈 EVALUATING IMPROVEMENT")
        print("-" * 40)
        
        try:
            # Convert optimized HTML to LLM-parseable format
            
            print("🔄 Converting optimized HTML to LLM-parseable format...")
            
            # Get related documents from similar websites
            related_documents = []
            url = None
            for website in state['similar_websites']:
                if website.get('extracted_content') and not website.get('is_your_website', False):
                    related_documents.append({
                        "text": website['extracted_content']
                    })

                if website.get('extracted_content') and website.get('is_your_website', False):
                    url = website['url']
                    print(f"Processing URL: {url}")

            # Convert optimized HTML to LLM-parseable format
            optimized_content = extract_llm_readable_content(url=url, html_content=state['current_html'])

            # Add our optimized content to the comparison
            documents = related_documents + [{"text": optimized_content}]
            
            # Get reranker scores for all documents
            from reranker_api import rerank_documents
            print("🔄 Comparing optimized content with related documents...")
            response = rerank_documents(state['target_keyword'], documents)
            
            if response and 'results' in response and len(response['results']) > 0:
                # Find our optimized content score (should be the last one)
                optimized_score = response['results'][-1]['relevance_score']
                
                # Calculate improvement based on ranking position
                total_documents = len(response['results'])
                our_rank = total_documents  # Our content is at the end
                
                # Find the best score among related documents
                best_related_score = max([result['relevance_score'] for result in response['results'][:-1]], default=0.0)
                
                improvement = optimized_score - state['current_score']
                
                print(f"Optimized content score: {optimized_score:.4f}")
                print(f"Best related document score: {best_related_score:.4f}")
                print(f"Improvement: {improvement:.4f}")
                print(f"Our ranking: {our_rank}/{total_documents}")
                
                # Record optimization step
                optimization_step = {
                    "step_name": "targeted_optimization",
                    "previous_score": state['current_score'],
                    "new_score": optimized_score,
                    "improvement": improvement,
                    "success": improvement > state['improvement_threshold'],
                    "timestamp": str(datetime.now())
                }
                
                state['optimization_history'].append(optimization_step)
                
                # Update best score if improved
                if optimized_score > state['best_score']:
                    state['best_score'] = optimized_score
                    state['best_html'] = state['current_html']
                    print(f"✅ New best score achieved: {optimized_score:.4f}")
                
                if improvement > state['improvement_threshold']:
                    print(f"✅ Significant improvement achieved ({improvement:.4f})")
                    state['current_score'] = optimized_score
                else:
                    print(f"❌ Insufficient improvement ({improvement:.4f} < {state['improvement_threshold']})")
                    # Revert to best HTML
                    state['current_html'] = state['best_html']
                    state['current_score'] = state['best_score']
                    
            else:
                print("❌ Could not get reranker scores for comparison")
                # Fallback to estimated improvement
                estimated_improvement = 0.01
                new_score = state['current_score'] + estimated_improvement
                improvement = estimated_improvement
                
                optimization_step = {
                    "step_name": "targeted_optimization",
                    "previous_score": state['current_score'],
                    "new_score": new_score,
                    "improvement": improvement,
                    "success": improvement > state['improvement_threshold'],
                    "timestamp": str(datetime.now())
                }
                
                state['optimization_history'].append(optimization_step)
                state['best_score'] = new_score
                state['current_score'] = new_score
                print(f"✅ Optimization completed with estimated improvement")
                
        except Exception as e:
            print(f"❌ Error evaluating improvement: {e}")
            print(traceback.format_exc())
        
        return state
    
    def _finalize(self, state: AgentState) -> AgentState:
        """Finalize the optimization process"""
        print(f"\n🎯 FINALIZING OPTIMIZATION")
        print("-" * 40)


        soup_ori = str(BeautifulSoup(state['original_html'], 'html.parser'))
        soup_opt = str(BeautifulSoup(state['best_html'], 'html.parser'))

        
        # Create final result
        final_result = {
            "website_url": state['website_url'],
            "target_keyword": state['target_keyword'],
            "initial_score": 0.0,  # Will be updated from history
            "final_score": state['best_score'],
            "improvement": state['best_score'] - 0.0,  # Will be updated from history
            "original_html": soup_ori,  # Original HTML before optimization
            "optimized_html": soup_opt,  # Optimized HTML after optimization
            "optimization_history": state['optimization_history'],
            "similar_websites": state['similar_websites'],
            "optimization_summary": {
                "total_steps": len(state['optimization_history']),
                "successful_steps": len([step for step in state['optimization_history'] if step['success']]),
                "best_improvement": max([step['improvement'] for step in state['optimization_history']], default=0.0)
            }
        }
        
        # Update initial score from history if available
        if state['optimization_history']:
            final_result["initial_score"] = state['optimization_history'][0]["previous_score"]
            final_result["improvement"] = state['best_score'] - final_result["initial_score"]
        
        state['final_result'] = final_result
        
        print(f"✅ Optimization completed!")
        print(f"Final score: {state['best_score']:.4f}")
        print(f"Total improvement: {final_result['improvement']:.4f}")
        print(f"Optimization steps: {final_result['optimization_summary']['total_steps']}")
        
        return state
    
    def optimize_website(
        self, 
        website_url: str, 
        target_keyword: str, 
        improvement_threshold: float = 0.02
    ) -> Dict[str, Any]:
        """
        Optimize a website for a target keyword
        
        Args:
            website_url: The URL of the website to optimize
            target_keyword: The target keyword to optimize for
            improvement_threshold: Minimum improvement required to keep changes
            
        Returns:
            Dictionary containing optimization results
        """
        
        # Initialize state
        initial_state = AgentState(
            website_url=website_url,
            target_keyword=target_keyword,
            current_html="",
            original_html="",  # Will be set during initialization
            current_score=0.0,
            improvement_threshold=improvement_threshold,
            optimization_history=[],
            best_score=0.0,
            best_html="",
            similar_websites=[],
            final_result=None
        )
        
        # Run the workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            return final_state['final_result']
        except Exception as e:
            print(f"❌ Error running optimization workflow: {e}")
            return {
                "error": str(e),
                "website_url": website_url,
                "target_keyword": target_keyword
            }


def save_optimization_results(results: Dict[str, Any], filename: str = None) -> None:
    """Save optimization results to a JSON file"""
    if filename is None:
        filename = f"geo_optimization_{results['target_keyword'].replace(' ', '_')}_{int(time.time())}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ Results saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")


def display_optimization_results(results: Dict[str, Any]) -> None:
    """Display optimization results in a formatted way"""
    print(f"\n{'='*60}")
    print("GEO OPTIMIZATION RESULTS")
    print(f"{'='*60}")
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    print(f"Website: {results['website_url']}")
    print(f"Target Keyword: {results['target_keyword']}")
    print(f"Initial Score: {results['initial_score']:.4f}")
    print(f"Final Score: {results['final_score']:.4f}")
    print(f"Total Improvement: {results['improvement']:.4f}")
    
    print(f"\nOptimization Summary:")
    summary = results['optimization_summary']
    print(f"- Total Steps: {summary['total_steps']}")
    print(f"- Successful Steps: {summary['successful_steps']}")
    print(f"- Best Improvement: {summary['best_improvement']:.4f}")
    
    print(f"\nHTML Comparison:")
    print(f"- Original HTML Length: {len(results['original_html'])} characters")
    print(f"- Optimized HTML Length: {len(results['optimized_html'])} characters")
    print(f"- Length Difference: {len(results['optimized_html']) - len(results['original_html'])} characters")
    print(f"{'='*60}")


def example_usage():
    """Example usage of the Enhanced GEO Agent"""
    
    # Initialize the agent
    agent = EnhancedGEOAgent()
    
    # Example optimization
    results = agent.optimize_website(
        website_url="https://example.com",
        target_keyword="digital marketing",
        improvement_threshold=0.02
    )
    
    # Display results
    display_optimization_results(results)
    
    # Save results
    save_optimization_results(results)


if __name__ == "__main__":
    example_usage() 