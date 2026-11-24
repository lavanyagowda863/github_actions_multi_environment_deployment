from flask import Flask, jsonify
import os

app = Flask(__name__)

# Read environment variable
ENVIRONMENT = os.getenv("APP_ENV", "development")

# Home endpoint
@app.route("/")
def home():
    return jsonify({
        "application": "GitHub Actions Multi Environment",
        "environment": ENVIRONMENT,
        "status": "Running successfully"
    })

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "environment": ENVIRONMENT
    })

# Application entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
