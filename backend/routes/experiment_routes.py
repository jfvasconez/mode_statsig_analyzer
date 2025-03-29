"""
Defines API routes related to experiments.
"""

from flask import Blueprint, request, jsonify
# Import the handler
from backend.api_handlers.experiment_handler import handle_upload_experiment, handle_get_experiment

# Create a Blueprint
experiment_bp = Blueprint('experiment_bp', __name__)

@experiment_bp.route('/', methods=['POST'])
def upload_experiment():
  """Route to upload a CSV file and initiate analysis."""
  if 'file' not in request.files:
    return jsonify({"error": "No file part in the request"}), 400

  file = request.files['file']

  if file.filename == '':
    return jsonify({"error": "No selected file"}), 400

  if file and file.filename and file.filename.endswith('.csv'):
    try:
      # Call the API handler
      response_data, status_code = handle_upload_experiment(file)
      return jsonify(response_data), status_code
    except Exception as e:
      # Log the exception in a real app
      print(f"Unhandled exception in upload_experiment route: {e}")
      return jsonify({"error": "An unexpected error occurred on the server."}), 500
  else:
    return jsonify({"error": "Invalid file type, please upload a CSV file"}), 400

@experiment_bp.route('/<experiment_id>/', methods=['GET'])
def get_experiment(experiment_id):
  """Route to get experiment results by ID."""
  try:
    # Call the API handler to get experiment results
    response_data, status_code = handle_get_experiment(experiment_id)
    return jsonify(response_data), status_code
  except Exception as e:
    # Log the exception in a real app
    print(f"Unhandled exception in get_experiment route: {e}")
    return jsonify({"error": "An unexpected error occurred on the server."}), 500 