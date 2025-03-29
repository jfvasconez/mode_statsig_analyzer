"""
Handles API logic related to experiments, primarily interfacing between routes and logic handlers.
"""

from flask import jsonify
from werkzeug.datastructures import FileStorage
from backend.logic_handlers.experiment_logic import process_and_analyze_experiment, get_experiment_results
from werkzeug.utils import secure_filename
import tempfile
import os
import logging
import io # Import io for BytesIO

def handle_upload_experiment(file: FileStorage):
  """
  Handles the uploaded CSV file and processes the experiment data.
  """
  logging.info(f"handle_upload_experiment received file: {file.filename}")
  # Validate file
  if not file or not file.filename:
    logging.error("handle_upload_experiment received invalid file object")
    return {"error": "Invalid file"}, 400
  
  filename = secure_filename(file.filename)
  
  try:
    # Read the file content into a BytesIO stream
    file_stream = io.BytesIO(file.read())
    # Reset stream position to the beginning
    file_stream.seek(0)

    logging.info(f"Calling process_and_analyze_experiment for file: {filename}")
    # Call the correct logic handler function with the stream and filename
    result_data = process_and_analyze_experiment(file_stream, filename)
    logging.info(f"process_and_analyze_experiment returned successfully: {result_data}")
    return {
      "message": result_data.get('message', f"Successfully processed experiment: {filename}"),
      "experiment_id": str(result_data.get('experiment_id'))
    }, 201
  except ValueError as ve:
    logging.error(f"Validation error during processing: {ve}", exc_info=True)
    return {"error": str(ve)}, 400
  except Exception as e:
    logging.error(f"Error calling process_and_analyze_experiment: {e}", exc_info=True)
    # Return a generic error message to the client
    return {"error": "An internal server error occurred during file processing."}, 500

def handle_get_experiment(experiment_id):
  """
  Retrieves experiment results by ID.
  """
  logging.info(f"handle_get_experiment called with experiment_id: {experiment_id}")
  try:
    # Get experiment results using the logic handler
    logging.info(f"Calling get_experiment_results for ID: {experiment_id}")
    results = get_experiment_results(experiment_id)
    logging.info(f"get_experiment_results returned: {results}")

    if not results:
      logging.warning(f"No results found for experiment ID: {experiment_id}")
      return {"error": f"Experiment with ID {experiment_id} not found"}, 404

    logging.info(f"Successfully retrieved results for experiment ID: {experiment_id}")
    return results, 200
  except ValueError as e:
    # Catch validation errors
    logging.error(f"Validation error in handle_get_experiment for ID {experiment_id}: {e}", exc_info=True)
    return {"error": str(e)}, 400
  except Exception as e:
    # Catch other errors
    logging.error(f"Unexpected error in handle_get_experiment for ID {experiment_id}: {e}", exc_info=True)
    return {"error": f"Failed to retrieve experiment results: {str(e)}"}, 500 