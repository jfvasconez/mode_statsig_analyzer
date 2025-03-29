"""
Handles API logic related to experiments, primarily interfacing between routes and logic handlers.
"""

from flask import jsonify
from werkzeug.datastructures import FileStorage
from backend.logic_handlers.experiment_logic import process_experiment_upload, get_experiment_results
from werkzeug.utils import secure_filename
import tempfile
import os

def handle_upload_experiment(file: FileStorage):
  """
  Handles the uploaded CSV file and processes the experiment data.
  """
  # Validate file
  if not file or not file.filename:
    return {"error": "Invalid file"}, 400
  
  # Create a secure filename and save to temp file
  filename = secure_filename(file.filename)
  
  # Create temp file
  fd, temp_path = tempfile.mkstemp(suffix='.csv')
  try:
    # Close the file descriptor
    os.close(fd)
    # Save uploaded file to temp path
    file.save(temp_path)
    
    # Process the experiment data via the logic handler
    try:
      experiment_id, name = process_experiment_upload(temp_path)
      return {
        "message": f"Successfully processed experiment: {name}",
        "experiment_id": str(experiment_id)  # Convert ID to string for JSON serialization
      }, 201
    except Exception as e:
      return {"error": str(e)}, 400
  finally:
    # Ensure temp file is removed, even if there's an exception
    if os.path.exists(temp_path):
      os.remove(temp_path)

def handle_get_experiment(experiment_id):
  """
  Retrieves experiment results by ID.
  """
  try:
    # Get experiment results using the logic handler
    results = get_experiment_results(experiment_id)
    
    if not results:
      return {"error": f"Experiment with ID {experiment_id} not found"}, 404
    
    return results, 200
  except ValueError as e:
    # Catch validation errors
    return {"error": str(e)}, 400
  except Exception as e:
    # Catch other errors
    return {"error": f"Failed to retrieve experiment results: {str(e)}"}, 500 