import streamlit as st
import asyncio
import os
from typing import Dict, List, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
import base64
from pathlib import Path
import json

# Page config
st.set_page_config(page_title="AI Book Writer", page_icon="📚", layout="wide")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #13151a, #2d1922, #332211);
    }
    
    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 4rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1rem;
        line-height: 1.2;
        text-align: center;
        background: linear-gradient(90deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .tagline {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 600;
        text-align: center;
        color: #FFD700;
        margin: 2rem 0;
        padding: 1rem;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        to { text-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
    }
    
    .sub-header {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.5rem;
        font-weight: 400;
        margin-bottom: 3rem;
        text-align: center;
    }
    
    .form-container {
        background: rgba(255, 255, 255, 0.03);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin: 2rem 0;
    }
    
    .input-label {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        font-weight: 500;
        margin: 1.5rem 0 0.5rem 0;
    }
    
    .stTextInput > div > div {
        background-color: rgba(255, 255, 255, 0.07);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0.75rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        border: none;
        border-radius: 12px;
        color: #1a1a1a;
        padding: 1rem 3rem;
        font-weight: 600;
        width: 100%;
        margin-top: 2rem;
    }
    
    .status-box {
        background: rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        border: 2px solid rgba(255, 215, 0, 0.1);
    }
    
    .download-btn {
        display: inline-block;
        padding: 1rem 3rem;
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        text-decoration: none;
        border-radius: 12px;
        font-weight: 600;
        margin-top: 1.5rem;
        text-align: center;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

class BookWriter:
    def __init__(self, preferences: Dict[str, str]):
        self.preferences = preferences
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        groq_api_key = st.secrets["GROQ_API_KEY"]
        return ChatGroq(
            api_key=groq_api_key,
            model_name="mixtral-8x7b-32768",
            temperature=0.7
        )
    
    async def create_outline(self) -> Dict[str, Any]:
        """Create book outline"""
        system_prompt = """Create a concise outline for a {book_type} book in the style of {writing_style}.
        Create exactly 3 chapters, each around 2,000 words (6,000 total).
        Keep key points minimal (2-3 per chapter) but impactful."""
        
        messages = [
            SystemMessage(content=system_prompt.format(**self.preferences)),
            HumanMessage(content=f"Create a concise book outline for: {self.preferences['book_description']}")
        ]
        
        response = await self.llm.ainvoke(messages)
        return self._parse_outline(response.content)
    
    def _parse_outline(self, content: str) -> Dict[str, Any]:
        """Parse the outline response"""
        lines = content.split('\n')
        outline = {
            "title": "",
            "chapters": [],
            "total_word_count": 0
        }
        
        current_chapter = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.lower().startswith("title:"):
                outline["title"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("chapter"):
                if current_chapter:
                    outline["chapters"].append(current_chapter)
                current_chapter = {
                    "title": line,
                    "key_points": [],
                    "word_count": 2000
                }
            elif line.startswith("-"):
                if current_chapter:
                    current_chapter["key_points"].append(line.lstrip("- "))
        
        if current_chapter:
            outline["chapters"].append(current_chapter)
        
        return outline
    
    async def write_chapter(self, chapter: Dict[str, Any]) -> str:
        """Write a single chapter"""
        prompt = f"""Write a complete chapter covering these key points:
        {', '.join(chapter['key_points'])}
        Target word count: {chapter['word_count']} words."""
        
        messages = [
            SystemMessage(content=f"You are writing in the style of {self.preferences['writing_style']}"),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def create_pdf(self, title: str, chapters: Dict[str, str]) -> str:
        """Create PDF from chapters"""
        output_path = "book.pdf"
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title page
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph(title, title_style))
        story.append(PageBreak())
        
        # Chapters
        chapter_title_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            leading=14,
            spaceAfter=12
        )
        
        for chapter_title, content in chapters.items():
            story.append(Paragraph(chapter_title, chapter_title_style))
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, body_style))
            story.append(PageBreak())
        
        doc.build(story)
        return output_path

def get_download_link(file_path: str) -> str:
    """Generate download link for PDF"""
    with open(file_path, "rb") as f:
        pdf_data = f.read()
    b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    return f'<a href="data:application/pdf;base64,{b64_pdf}" download="your_book.pdf" class="download-btn">Download Your Book</a>'

async def main():
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">AI Book Writer</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="tagline">Write Your Dream Book</h2>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your ideas into a professionally written book in minutes</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    with st.form("book_form"):
        st.markdown('<p class="input-label">What type of book would you like to write?</p>', unsafe_allow_html=True)
        book_type = st.text_input("", placeholder="E.g., Self-help, Business, Fiction...", key="book_type")
        
        st.markdown('<p class="input-label">Whose writing style would you like to emulate?</p>', unsafe_allow_html=True)
        writing_style = st.text_input("", placeholder="E.g., Malcolm Gladwell, Stephen King...", key="writing_style")
        
        st.markdown('<p class="input-label">What\'s your book about?</p>', unsafe_allow_html=True)
        book_description = st.text_area("", placeholder="Enter a brief description of your book's main theme or plot...", key="book_description")
        
        submitted = st.form_submit_button("Begin Your Writing Journey")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if submitted:
        preferences = {
            "book_type": book_type,
            "writing_style": writing_style,
            "book_description": book_description
        }
        
        try:
            writer = BookWriter(preferences)
            
            with st.status("Creating your book...", expanded=True) as status:
                st.write("🎨 Creating outline...")
                outline = await writer.create_outline()
                
                chapters = {}
                for i, chapter in enumerate(outline["chapters"], 1):
                    st.write(f"✍️ Writing Chapter {i}...")
                    st.progress(i / len(outline["chapters"]))
                    content = await writer.write_chapter(chapter)
                    chapters[chapter["title"]] = content
                    await asyncio.sleep(65)  # Respect rate limits
                
                st.write("📚 Formatting book...")
                pdf_path = writer.create_pdf(outline["title"], chapters)
                
                status.update(label="Book completed!", state="complete")
                st.success("🎉 Your book is ready!")
                st.markdown(get_download_link(pdf_path), unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    asyncio.run(main()) 