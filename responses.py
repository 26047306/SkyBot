from flask import Flask, render_template, request, jsonify
import openai
from langdetect import detect
from googletrans import Translator

app = Flask(__name__)

openai.api_key = "your-openai-api-key"

# Step 1: Keyword-based fallback response
def generate_response(user_input):
    user_input = user_input.lower()
    if "college" in user_input and "kaha" in user_input:
        return "Oriental College is located in Raisen Road, Bhopal, Madhya Pradesh."
    elif "courses" in user_input or "course" in user_input:
        return "The college offers B.Tech, M.Tech, MBA and Diploma courses in Computer Science, Mechanical, Civil, Electrical, and more."
    elif "placement" in user_input:
        return "Oriental College has tie-ups with top companies and provides good placement opportunities for students."
    elif "fees" in user_input or "fee" in user_input:
        return "Fees vary based on course. For example, B.Tech fees are approx ₹80,000 per year."
    elif "contact" in user_input or "email" in user_input:
        return "You can contact the college at info@oriental.ac.in or visit www.oriental.ac.in."
    else:
        return "I'm not sure about that. Please ask something related to the college."

# Step 2: Fallback multilingual response
def multilingual_response(user_input):
    try:
        lang = detect(user_input)
    except:
        lang = "en"
    if any(word in user_input.lower() for word in ["kya", "hai", "kaun", "kaha", "college", "placement", "courses"]):
        lang = "hi"
    response_en = generate_response(user_input)
    if lang == "en":
        return response_en
    translator = Translator()
    translated = translator.translate(response_en, dest=lang).text
    return translated

# Final chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        bot_reply = response.choices[0].message.content.strip()
        return jsonify({"reply": bot_reply})
    except Exception as e:
        print("❌ OpenAI Error:", e)
        fallback_reply = multilingual_response(user_input)
        return jsonify({"reply": fallback_reply})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)