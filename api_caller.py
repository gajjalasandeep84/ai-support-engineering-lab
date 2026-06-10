import logging
import requests
import json

# Configure logging ONCE at the top
# This replaces your manual file writing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] — %(message)s",
    handlers=[
        logging.StreamHandler(),              # console
        logging.FileHandler("api_caller.log") # file — auto-handled
    ]
)
logger = logging.getLogger(__name__)


class ApiCallError(Exception):
    pass


def call_api_with_retry(url: str, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} — calling {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logger.info("API call successful")
            return response.json()    # ← return dict not response object
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            logger.error(f"HTTP error {status} on attempt {attempt + 1}",
                         exc_info=True)
            if status == 404:
                raise ApiCallError("Resource not found") from e
            if attempt == max_retries - 1:
                raise ApiCallError("API call failed after retries") from e

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed on attempt {attempt + 1}",
                         exc_info=True)
            if attempt == max_retries - 1:
                raise ApiCallError("API request failed after retries") from e

# Now call the function and use the returned dict
url  = "https://jsonplaceholder.typicode.com/todos/1"
data = call_api_with_retry(url)    # ← data is a dict

# Print formatted JSON
formatted = json.dumps(data, indent=4)
print(formatted)
logger.info(f"Response received: {len(formatted)} characters")

# Save to file
with open("todo_result.json", "w") as f:
    json.dump(data, f, indent=2)
logger.info("Saved to todo_result.json")

# Read back and log title
with open("todo_result.json", "r") as f:
    todo = json.load(f)
logger.info(f"Title from file: {todo['title']}")