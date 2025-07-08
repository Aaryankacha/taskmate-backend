from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import replicate
import os
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
replicate.Client(api_token=REPLICATE_API_TOKEN)

# 🚀 Flask Setup
app = Flask(__name__)
CORS(app)

# 📁 Uploads folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ File Upload Endpoint ------------------

@app.route("/upload", methods=["POST", "OPTIONS"])
def upload_file():
    if request.method == "OPTIONS":
        return '', 200

    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename or "unnamed_file")
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    return jsonify({"url": f"/uploads/{filename}"}), 200

@app.route("/uploads/<filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ------------------ TaskPilot Chat Endpoint ------------------

@app.route("/ask", methods=["POST"])
def ask_taskpilot():
    prompt = request.get_json().get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is missing"}), 400

    try:
        # 💬 Generate chat response from Mistral
        output = replicate.run(
            "meta/llama-2-7b-chat",
            input={
            "prompt": prompt,
            "temperature": 0.5,
            "top_p": 0.9,
            "max_new_tokens": 250,
            }
        )

        return jsonify({"response": "".join(output)})
    except Exception as e:
        return jsonify({"error": f"TaskPilot Error: {str(e)}"}), 500

# ------------------ Run Server ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
