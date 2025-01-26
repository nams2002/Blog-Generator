from flask import Flask, render_template, request, jsonify
import markdown
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_with_gpt(prompt, max_tokens=500):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating content: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_blog():
    data = request.get_json()
    topic = data.get('topic')
    length = data.get('length', 'medium')
    
    # Generate keywords
    keyword_prompt = f"Generate 5 relevant SEO keywords for the topic: {topic}"
    keywords = generate_with_gpt(keyword_prompt, 100).split('\n')
    keywords = [k.strip('- ') for k in keywords if k.strip()][:5]
    
    # Generate outline
    outline_prompt = f"Create a detailed outline for a blog post about: {topic}"
    outline_raw = generate_with_gpt(outline_prompt, 200)
    outline = [line.strip('- ') for line in outline_raw.split('\n') if line.strip()]
    
    # Generate content
    content_lengths = {'short': 300, 'medium': 600, 'long': 1000}
    content_prompt = f"""Write a detailed blog post about {topic}. Include:
    1. Engaging introduction
    2. Detailed body following the outline
    3. Actionable conclusion
    Length: approximately {content_lengths[length]} words"""
    
    content = generate_with_gpt(content_prompt, content_lengths[length])
    formatted_content = markdown.markdown(content)
    
    return jsonify({
        'content': formatted_content,
        'outline': outline,
        'keywords': keywords
    })

if __name__ == '__main__':
    app.run(debug=True)