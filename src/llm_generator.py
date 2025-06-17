import json
import logging
import datetime
import time
from openai import OpenAI, RateLimitError, APIError
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.api_core.exceptions import GoogleAPICallError

class OpenAIClient:
    """A client for interacting with the OpenAI API."""
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise ValueError("API key is required for OpenAIClient.")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str, destination_id: str) -> str:
        """
        Generates a response from the LLM, with retries for rate limits.
        """
        logging.info(f"Generating LLM response via OpenAI for model: {self.model_name} for {destination_id}")
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a travel data expert. Respond only with the requested JSON object."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content
            except RateLimitError as e:
                logging.warning(f"OpenAI Rate limit exceeded on attempt {attempt + 1}. Retrying... Error: {e}")
                time.sleep(retry_delay * (attempt + 1))
            except APIError as e:
                logging.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return f'{{"error": "APIError", "details": "{str(e)}"}}'
                time.sleep(retry_delay * (attempt + 1))
        
        logging.error(f"Failed to get response from OpenAI after {max_retries} retries.")
        return '{"error": "Max retries exceeded with OpenAI"}'

class GeminiClient:
    """A client for interacting with the Google Gemini API."""
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise ValueError("API key is required for GeminiClient.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def generate(self, prompt: str, destination_id: str) -> str:
        logging.info(f"Generating LLM response via Gemini for model: {self.model_name} for {destination_id}")
        # Gemini requires a specific config for JSON output
        generation_config = GenerationConfig(response_mime_type="application/json")
        try:
            response = self.model.generate_content(prompt, generation_config=generation_config)
            # The response text itself should be the JSON string
            return response.text
        except GoogleAPICallError as e:
            logging.error(f"Gemini API error: {e}")
            return f'{{"error": "GoogleAPICallError", "details": "{str(e)}"}}'
        except Exception as e:
            logging.error(f"An unexpected error occurred with Gemini: {e}")
            return f'{{"error": "UnexpectedError", "details": "{str(e)}"}}'

class LLMGenerator:
    """
    Handles the generation of baseline destination affinities using a real LLM.
    """
    def __init__(self, config: dict):
        self.config = config
        api_keys = self.config.get("api_keys", {})
        llm_settings = self.config.get("llm_settings", {})
        
        provider = llm_settings.get("provider", "openai")
        
        if provider == "openai":
            api_key = api_keys.get("openai_api_key")
            model_name = llm_settings.get("openai_model_name")
            self.client = OpenAIClient(api_key=api_key, model_name=model_name)
        elif provider == "gemini":
            api_key = api_keys.get("gemini_api_key")
            model_name = llm_settings.get("gemini_model_name")
            self.client = GeminiClient(api_key=api_key, model_name=model_name)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        self.prompt_template = self.config.get("affinity_prompt", "")
        if not self.prompt_template:
            raise ValueError("Affinity prompt not found in configuration.")

    def generate_baseline(self, destination_name: str) -> dict:
        """
        Generates a baseline set of affinities for a given destination.
        """
        prompt = self.prompt_template.format(destination=destination_name)
        
        raw_response = self.client.generate(prompt, destination_id=destination_name)
        
        try:
            parsed_response = json.loads(raw_response)

            # Handle cases where the LLM returns a list with one item
            if isinstance(parsed_response, list) and len(parsed_response) > 0:
                logging.warning("LLM returned a list, extracting the first element.")
                parsed_response = parsed_response[0]

            if not isinstance(parsed_response, dict):
                 raise json.JSONDecodeError("Response is not a dictionary after potential list extraction.", raw_response, 0)

            if "error" in parsed_response:
                logging.error(f"LLM client returned an error for {destination_name}: {parsed_response['error']}")
                return parsed_response

            if "meta" not in parsed_response:
                parsed_response["meta"] = {}
            parsed_response["meta"]["generated_at"] = datetime.datetime.now().isoformat()
            
            if "destination_id" not in parsed_response or not parsed_response["destination_id"]:
                 parsed_response["destination_id"] = destination_name.lower().replace(" ", "_")

            return parsed_response
        except (json.JSONDecodeError, TypeError):
            logging.error(f"Error: LLM response for {destination_name} was not valid JSON. Response:\n{raw_response}")
            return {"error": "Invalid JSON response from LLM"} 