"""
Handles API logic related to experiments, primarily interfacing between routes and logic handlers.
"""

from werkzeug.datastructures import FileStorage
from typing import Dict, Any, Tuple
import io # Import io module

# Import the logic handler
from ..logic_handlers.experiment_logic import process_and_analyze_experiment


def handle_upload_experiment(file: FileStorage) -> Tuple[Dict[str, Any], int]:
  """
  Handles the initial processing of an uploaded experiment CSV file.
  Calls the logic handler and returns its results.

  Args:
    file: The FileStorage object from the Flask request.

  Returns:
    A tuple containing a dictionary (the result from the logic handler) 
    and an HTTP status code.
  """
  try:
    if not file or not file.filename:
      return {"error": "Invalid file provided to handler"}, 400

    # Wrap the stream in BytesIO before passing
    file_stream_bytesio = io.BytesIO(file.stream.read())
    result_data = process_and_analyze_experiment(file_stream_bytesio, file.filename)

    # Pass the logic handler's result directly (contains ID and message)
    return result_data, 201 # Use 201 Created as a resource (Experiment) was created

  except ValueError as e:
      # Catch specific data validation/parsing errors from logic handler
      print(f"Validation Error in handle_upload_experiment: {e}") 
      return {"error": str(e)}, 400 # Return the specific error message
  except Exception as e:
    # Catch unexpected errors from logic handler or db handler
    print(f"Error in handle_upload_experiment: {e}") 
    return {"error": "An internal error occurred processing the experiment."}, 500 