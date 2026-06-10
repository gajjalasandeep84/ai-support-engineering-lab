# Similar to:
# import org.springframework.web.client.RestTemplate;
import requests

# Similar to:
# import com.fasterxml.jackson.databind.ObjectMapper;
import json

# Similar to:
# import org.slf4j.Logger;
# import org.slf4j.LoggerFactory;
import logging

# Similar to:
# import java.nio.file.Path;
import pathlib
from pathlib import Path


# ==========================================================
# Logging Configuration
# Similar to configuring Logback / Log4j
# ==========================================================
logging.basicConfig(
    # Log INFO and above
    level=logging.INFO,

    # Log message format
    format="%(asctime)s [%(levelname)s] — %(message)s",

    # Write logs to console and file
    handlers=[
        logging.StreamHandler(),           # Console
        logging.FileHandler("chatbot.log") # File
    ]
)

# Similar to:
# private static final Logger logger =
#      LoggerFactory.getLogger(MyClass.class);
logger = logging.getLogger(__name__)


# ==========================================================
# Application Constants
# Similar to:
# private static final String ...
# ==========================================================
OLLAMA_URL = "http://localhost:11434/api/chat"

# LLM model name
MODEL = "llama3.2:3b"

# Keep only last 20 chat messages   
MAX_HISTORY = 20

# Similar to a System Message in ChatGPT
# Think of this as instructions sent before user prompts
SYSTEM_PROMPT = """
You are an expert Java and Spring Boot engineer
with deep knowledge of enterprise systems.
You help investigate production issues, review code,
and explain technical concepts clearly.
Keep answers concise and technical.
"""


# ==========================================================
# Save Conversation
# Similar to:
# Files.write(...)
# ==========================================================
def save_conversation(messages: list[dict], filepath: str):

    # Create directory if it doesn't exist
    # Similar to:
    # Files.createDirectories(path.getParent())
    Path(filepath).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Open file in write mode
    with open(filepath, "w") as f:

        # Convert Python object to JSON and save
        # Similar to:
        # objectMapper.writeValue(...)
        json.dump(messages, f, indent=2)

    logger.info(f"Conversation saved to {filepath}")


# ==========================================================
# Call Ollama LLM
# Similar to a service method making REST call
# ==========================================================
def chat(messages: list[dict]) -> str:

    # Request body
    # Similar to creating DTO object
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    try:

        logger.info(
            f"Sending {len(messages)} messages to LLM"
        )

        # Similar to:
        # restTemplate.postForObject(...)
        response = requests.post(
            OLLAMA_URL,

            # Automatically converts payload to JSON
            json=payload,

            # Wait max 60 seconds
            timeout=60
        )

        # Throw exception if status != 200
        # Similar to checking response status
        response.raise_for_status()

        # Parse JSON response
        # Similar to:
        # objectMapper.readValue(...)
        data = response.json()

        # Extract response text
        content = data["message"]["content"]

        logger.info(
            f"Response received — {len(content)} chars"
        )

        return content

    # Similar to:
    # catch(SocketTimeoutException e)
    except requests.Timeout:

        logger.error(
            "LLM timed out",
            exc_info=True
        )

        return "Sorry — request timed out. Try again."

    # Similar to:
    # catch(HttpClientErrorException e)
    except requests.HTTPError as e:

        logger.error(
            f"HTTP error: {e}",
            exc_info=True
        )

        return f"Error: {e}"

    # Similar to:
    # catch(Exception e)
    except Exception as e:

        logger.error(
            f"Unexpected error: {e}",
            exc_info=True
        )

        return "Something went wrong."


# ==========================================================
# Application Entry Point
# Similar to Spring Boot main() method
# ==========================================================
def main():

    print("\n=== Java Expert Chatbot ===")
    print("Type 'quit' to exit\n")

    # Chat history
    # Similar to:
    # List<Message> messages = new ArrayList<>();
    messages = [

        # First message is always system prompt
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Infinite loop
    while True:

        # Read user input from console
        user_input = input("You: ").strip()

        # Ignore blank input
        if not user_input:
            continue

        # Exit condition
        if user_input.lower() == "quit":

            save_conversation(
                messages,
                "conversations/session.json"
            )

            print("Conversation saved. Goodbye!")

            logger.info("Session ended")

            break

        # --------------------------------------------------
        # Context Window Management
        # --------------------------------------------------
        # Keep only:
        # System prompt +
        # Last 20 messages
        #
        # LLMs have limited memory (context window)
        # --------------------------------------------------
        if len(messages) > MAX_HISTORY + 1:

            # Save system prompt
            system = messages[0]

            # Keep latest messages only
            messages = (
                [system]
                + messages[-MAX_HISTORY:]
            )

            logger.warning(
                "Context trimmed — kept last 20 messages"
            )

        # --------------------------------------------------
        # Add User Message
        # --------------------------------------------------
        messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        # --------------------------------------------------
        # Call LLM
        # --------------------------------------------------
        print("Bot: ", end="", flush=True)

        response = chat(messages)

        print(response)

        print(
            f"[Context: {len(messages)} messages in memory]\n"
        )

        # --------------------------------------------------
        # Save Assistant Response
        # --------------------------------------------------
        messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )


# ==========================================================
# Program Entry Point
# Similar to:
#
# public static void main(String[] args) {
#     SpringApplication.run(...)
# }
# ==========================================================
if __name__ == "__main__":
    main()