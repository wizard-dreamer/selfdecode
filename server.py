from pathlib import Path
import os

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Flask
BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
CORS(app)

# Load API keys
groq_key = os.getenv("GROQ_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Initialize clients
groq_client = Groq(api_key=groq_key) if groq_key else None
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None


def get_missing_env():
    return [
        name for name, value in {
            "GROQ_API_KEY": groq_key,
            "SUPABASE_URL": supabase_url,
            "SUPABASE_KEY": supabase_key,
        }.items() if not value
    ]


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/health")
def health():
    missing_env = get_missing_env()
    status_code = 200 if not missing_env else 503
    return jsonify({
        "status": "ok" if status_code == 200 else "degraded",
        "missing_env": missing_env,
    }), status_code


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        missing_env = get_missing_env()
        if missing_env:
            return jsonify({
                "error": "Server is missing required environment variables.",
                "missing_env": missing_env,
            }), 503

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON."}), 400

        name = data.get("name")
        traits = data.get("traits")
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Field 'name' is required."}), 400
        if not isinstance(traits, dict) or not traits:
            return jsonify({"error": "Field 'traits' must be a non-empty object."}), 400

        prompt = f"""
You are a brutally honest personality analyst.

Scores:
{traits}

Speak directly to the person.

Use simple English and small paragraphs.

Be honest. Do not sugarcoat negative traits.

Describe:
overall personality,
strengths,
weaknesses,
relationship behavior,
possible red flags.
"""
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        analysis = completion.choices[0].message.content

        # Save to database
        if supabase is not None:
            supabase.table("personality_results").insert({
                "name": name,
                "traits": traits,
                "analysis": analysis
            }).execute()

        return jsonify({
            "analysis": analysis
        })

    except Exception as e:
        app.logger.exception("Error generating personality analysis: %s", e)
        return jsonify({
            "error": "Error generating personality analysis."
        }), 500


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(BASE_DIR, path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
