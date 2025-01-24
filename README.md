# AI Book Writer

Transform your ideas into professionally written books using AI. This web application uses Groq's powerful language model to generate books in any style you prefer.

## Features
- Generate books in any genre
- Emulate famous writing styles
- Get a professionally formatted PDF
- Real-time progress tracking
- Modern, user-friendly interface

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-book-writer.git
cd ai-book-writer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
Create a `.env` file and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

## Usage
1. Enter your book type (e.g., Self-help, Fiction)
2. Choose an author's style to emulate
3. Describe your book's theme or plot
4. Click "Begin Your Writing Journey"
5. Wait for the AI to generate your book
6. Download the finished PDF

## Deployment
The app is deployed using Streamlit Cloud. Visit [your-app-url] to use it online.

## Rate Limits
- The app uses Groq's API which has a rate limit of 5,000 tokens per minute
- Each book is around 6,000 words (3 chapters)
- Please be patient during generation

## Contributing
Feel free to open issues or submit pull requests to improve the application.

## License
MIT License - feel free to use this code for your own projects! 