# app.py

from flask import Flask, request, jsonify
from argos import argos_translate_text, DEFAULT_FROM_CODE, DEFAULT_TO_CODE

app = Flask(__name__)

# Basic CORS support
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
  response.headers.add('Access-Control-Allow-Methods', 'POST')
  return response

@app.route('/translate', methods=['POST'])
def translate_api():
  """API endpoint to handle dynamic translation requests for DE <-> EN only."""
  
  # 1. Get and validate text input
  data = request.get_json()
  if not data or 'text' not in data:
    return jsonify({"error": "Missing 'text' field in request body"}), 400

  text_to_translate = data['text']
  
  # 2. Get language codes with fallback to defaults
  from_code = data.get('from', DEFAULT_FROM_CODE).lower()
  to_code = data.get('to', DEFAULT_TO_CODE).lower()

  # 3. ENFORCE GERMAN AND ENGLISH RESTRICTION
  supported_codes = {"de", "en"}
  if from_code not in supported_codes or to_code not in supported_codes:
    return jsonify({
      "error": "Only German ('de') and English ('en') translation is supported."
    }), 400
  
  # 4. Perform translation
  try:
    translated_text = argos_translate_text(text_to_translate, from_code, to_code)
    
    # Check for error message returned from the core function
    if translated_text.startswith("Error:"):
      return jsonify({"error": translated_text}), 503
        
    # 5. Return the JSON response
    return jsonify({
      "translatedText": translated_text,
      "sourceLanguage": from_code,
      "targetLanguage": to_code,
      "model": "Argos Translate"
    }), 200

  except Exception:
    # Catch unexpected server errors
    return jsonify({"error": "An unexpected server error occurred."}), 500

@app.route('/', methods=['GET'])
def status():
  return jsonify({
    "status": "ready",
    "supported_models": "de <-> en",
    "instructions": "Send a POST request to /translate with {'text': '...', 'from': 'de', 'to': 'en'}"
  }), 200


if __name__ == '__main__':
  # Run the server. The models are loaded before this point.
  app.run(host='0.0.0.0', port=5000, debug=False)