from flask import Flask, request, jsonify, render_template, session
from google import genai
import re

app = Flask(__name__)
app.secret_key = "your-secret-session-key"  # change this in production

def clean_text(text):
    return re.sub(r'[\*]+', '', text).strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    session['api_key'] = request.json['key']
    return '', 204

@app.route('/generate', methods=['POST'])
def generate():
    if 'api_key' not in session:
        return jsonify({"error": "API key not set"}), 403

    client = genai.Client(api_key=session['api_key'])
    data = request.json
    filenames = data['filenames']
    lang = data.get('language', 'en')
    results = []

    for name in filenames:
        prompt = f"Generate metadata in {lang} for stock image '{name}':\nTitle (max 100 characters), Description, and 30 clean, comma-separated SEO keywords."
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        output = response.text

        title, description, keywords = "", "", ""
        for line in output.splitlines():
            if "Title:" in line:
                title = clean_text(line.split("Title:")[1])[:100]
            elif "Description:" in line:
                description = clean_text(line.split("Description:")[1])
            elif "Keywords:" in line:
                keyword_line = clean_text(line.split("Keywords:")[1])
                keywords = ",".join(keyword_line.split(",")[:30])

        results.append({
            "filename": name,
            "title": title,
            "description": description,
            "keywords": keywords
        })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
