from dotenv import load_dotenv
from flask import Flask, jsonify, request

from ds.search import react_agent

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)


@app.route("/search", methods=["GET"])
def search():
    """
    Endpoint to handle search requests.

    Query parameters:
        q: The search query string

    Returns:
        JSON response with the search results
    """
    # Get the query parameter
    query = request.args.get("q", "")

    if not query:
        return jsonify({"error": "No query provided. Use /search?q=your query"}), 400

    try:
        # Use the existing react_agent to process the query
        result = react_agent(query, max_steps=5)

        # Return the result as JSON
        return jsonify({"query": query, "result": result})
    except Exception as e:
        # Handle errors
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run the Flask app on port 8000
    app.run(host="0.0.0.0", port=8000, debug=True)
