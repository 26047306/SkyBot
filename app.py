from flask import Flask, request, jsonify, render_template
import requests
from langdetect import detect
from googletrans import Translator  # For multilingual support

app = Flask(__name__)
API_KEY = "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"  # 🔑 Replace with your OpenRouter API key

# --- STEP 1: Bot ka default response logic ---
def generate_response(user_input):
    user_input = user_input.lower()

    if "college" in user_input and "kaha" in user_input:
        return "Oriental College is located in Raisen Road, Bhopal, Madhya Pradesh."
    elif "courses" in user_input or "course" in user_input:
        return "The college offers B.Tech, M.Tech, MBA, and Diploma courses in Computer Science, Mechanical, Civil, Electrical, and more."
    elif "placement" in user_input:
        return "Oriental College has tie-ups with top companies and provides good placement opportunities for students."
    elif "fees" in user_input or "fee" in user_input:
        return "Fees vary based on course. For example, B.Tech fees are approx ₹80,000 per year."
    elif "contact" in user_input or "email" in user_input:
        return "You can contact the college at info@oriental.ac.in or visit www.oriental.ac.in."
    else:
        return "I'm not sure about that. Please ask something related to the college."

# --- STEP 2: Multilingual response with stepwise format ---
def get_response(user_input):
    try:
        lang = detect(user_input)
    except:
        lang = "en"

    # Force Hindi for common Hindi words
    if any(word in user_input.lower() for word in ["kya", "hai", "kaun", "kaha", "college", "placement", "courses"]):
        lang = "hi"

    response_en = generate_response(user_input)

    # Format response stepwise
    steps = response_en.split(". ")
    stepwise_response = ""
    for idx, step in enumerate(steps, 1):
        if step.strip() != "":
            stepwise_response += f"{idx}️⃣ {step.strip()}\n"

    # Translate to Hindi if needed
    if lang == "hi":
        translator = Translator()
        translated_response = translator.translate(stepwise_response, dest='hi').text
        return translated_response
    else:
        return stepwise_response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    try:
        lang = detect(user_input)
        if lang == 'hi':
            system_prompt = "तुम एक सहायक कॉलेज असिस्टेंट हो जिसका नाम SkyBot है। हमेशा हिंदी में उत्तर दो।"
        else:
            system_prompt = "You are a helpful college assistant named SkyBot. Always reply in English."

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # First, try to get response from predefined logic (like college-related queries)
        response = generate_response(user_input)

        # If it does not match predefined queries, use the AI model
        if "I'm not sure about that" in response:
            payload = {
                "model": "deepseek/deepseek-chat-v3-0324",  # Model ID for DeepSeek V3
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            }

            api_response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            api_result = api_response.json()

            reply = api_result['choices'][0]['message']['content']
            return jsonify({"response": reply})
        else:
            return jsonify({"response": get_response(user_input)})  # Stepwise response

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"response": "Something went wrong! Please try again."})

if __name__ == '__main__':
    app.run(debug=True)
