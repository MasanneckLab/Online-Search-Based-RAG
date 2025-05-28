import os
import requests
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


def call_perplexity_api(
    question: str,
    model: str = "sonar",
    whitelist: list = None,
    temperature: float = 0.9,
    max_tokens: int = 8000,
    **api_params,
) -> dict:
    """
    Wrapper for calling the Perplexity API chat completions endpoint.

    Parameters:
      question (str): The medical question to query.
      model (str): Which model to use for the API call.
      whitelist (list): List of allowed URL domains to whitelist. MAX of 3!
      api_params: Additional API parameters (e.g., temperature, max_tokens).

    Returns:
      dict: A dictionary with keys "answer" (a str) and "sources" (a list).
            Example:
                {
                    "answer": <str>,
                    "sources": <list>
                }

    Raises:
      ValueError: If the PERPLEXITY_API_KEY is not set.
      Exception: If the API call fails.

    For further details, see the Perplexity API Reference at:
    https://docs.perplexity.ai/api-reference/chat-completions
    and the API cookbook at:
    https://github.com/ppl-ai/api-cookbook
    """
    API_KEY = os.getenv("PERPLEXITY_API_KEY")
    if not API_KEY:
        raise ValueError("PERPLEXITY_API_KEY not set in environment variables.")

    endpoint = "https://api.perplexity.ai/chat/completions"

    auth_header = "Bearer " + API_KEY
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_header,
    }

    # System prompt for the medical assistant
    system_prompt = """You are a dedicated AI medical assistant specializing in 
neurology. Your answers should be based on medical guidelines such as the most 
recent AAN guidelines and are strictly truthful. If the information is not 
available in guidelines, state it clearly. Refrain from including irrelevant or 
out-of-context details.
Please respond to the following question using information from guidelines. 
Focus on providing answers that are:
    - Directly linked to the guidelines, citing specific sections or page 
      numbers when possible. Make sure to mention the guidelines you are 
      referencing and the source.
    - Presented in concise bullet points. Do not bloat the answer 
      unnecessarily. Keep it short and professional.
    - Comprehensive, including all relevant details about disease type, 
      disease stage, patient age, and clinical trials when applicable.
    - Honest, clearly stating if the information is not covered in the 
      guidelines.
    - Including citations to the guidelines or other reputable sources 
      as needed.
Based on guidelines such as the most recent AAN guidelines, provide a 
detailed and truthful response that addresses the specifics of the question.
Ensure all relevant medical and scientific details are included to support 
your answer."""

    payload = {
        "model": model,
        "search_domain_filter": whitelist,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    }

    # Incorporate any additional API parameters
    payload.update(api_params)

    try:
        # Remove the detailed API call messages
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(response.json())
        logger.exception("Error calling Perplexity API")
        raise Exception(f"Failed to call Perplexity API: {e}") from e

    data = response.json()
    answer = ""
    if "choices" in data and data["choices"]:
        answer = data["choices"][0].get("message", {}).get("content", "")
    sources = data.get("citations", data.get("sources", []))
    return {
        "model": data.get("model", ""),
        "whitelist": whitelist,
        "answer": answer,
        "sources": sources,
    }


def run_experiment_on_question(
    question: str,
    iterations: int = 4,
    model: str = "sonar",
    temperature: float = 0.9,
    max_tokens: int = 3000,
    whitelist: list = None,
    **api_params,
) -> list:
    """
    Run the same question multiple times to collect responses for
    statistical variance.

    Parameters:
      question (str): The medical question to query.
      iterations (int): Number of times to call the API (default is 4).
      model (str): Which model to use for the API call.
      whitelist (list): List of allowed URL domains. MAX of 3.
                        Blacklisting via -
      api_params: Additional API parameters.

    Returns:
      list: A list of response dictionaries from the API.
    """
    results = []
    for i in range(iterations):
        max_retries = 2
        retry_count = 0
        success = False

        while retry_count <= max_retries and not success:
            try:
                result = call_perplexity_api(
                    question,
                    model=model,
                    whitelist=whitelist,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **api_params,
                )
                # append batch number to result
                result["batch"] = i
                results.append(result)
                success = True
            except Exception as e:
                retry_count += 1
                if retry_count <= max_retries:
                    logger.warning(
                        f"Attempt {retry_count} failed for question: "
                        f"'{question[:50]}...' "
                        f"Retrying... "
                        f"Error: {str(e)}"
                    )
                else:
                    # After max retries, log the error and continue with next iteration
                    logger.error(
                        f"Failed after {max_retries} retries for question: "
                        f"'{question}'. Error: {str(e)}"
                    )
                    print(
                        f"SKIPPING QUESTION (after {max_retries} retries): "
                        f"{question}"
                    )

    return results


def run_experiment_on_excel(
    input_file: str,
    output_file: str,
    iterations: int = 4,
    model: str = "sonar",
    whitelist: list = None,
    temperature: float = 0.9,
    max_tokens: int = 3000,
    **api_params,
):
    """
    Read questions from an Excel file, run experiments for each question,
    and write the results to another Excel file.

    Parameters:
      input_file (str): Path to the input Excel file containing questions.
      output_file (str): Path to the output Excel file to save results.
      iterations (int): Number of times to call the API (default is 4).
      model (str): Which model to use for the API call.
      whitelist (list): List of allowed URL domains. MAX of 3.
                        Blacklisting via -
      temperature (float): Temperature for the API call.
      max_tokens (int): Maximum tokens for the API call.
      api_params: Additional API parameters.

    The input Excel file must contain a column named "Question".
    The output will include all original columns plus:
      - model: The model used for responses
      - whitelist: The whitelist settings used
      - complete_answer: The answer with sources for each iteration
      - batch: The iteration number
    """
    import pandas as pd

    input_df = pd.read_excel(input_file)
    results = []
    total_questions = len(input_df)

    print("Running experiment...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Iterations: {iterations}")
    print(f"Model: {model}")
    print(f"Whitelist: {whitelist}")
    print(f"Temperature: {temperature}")
    print(f"Max tokens: {max_tokens}")
    print("--------------------------------")
    print(f"Total questions to process: {total_questions}")
    print(f"Total API calls to make: {total_questions * iterations}")
    print("--------------------------------")

    # Create a progress bar with a descriptive format
    progress_bar = tqdm(
        total=total_questions,
        desc="Processing questions",
        unit="question",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, "
        "{rate_fmt}]",
    )

    for _, row in input_df.iterrows():
        q = row["Question"]
        # Display current question in progress bar description
        if len(q) > 30:
            q_short = q[:30] + "..."
        else:
            q_short = q
        progress_desc = f"Processing: {q_short}"
        progress_bar.set_description(progress_desc)

        rep_results = run_experiment_on_question(
            q,
            iterations=iterations,
            model=model,
            whitelist=whitelist,
            temperature=temperature,
            max_tokens=max_tokens,
            **api_params,
        )

        # Create a new row for each iteration, including original columns
        for result in rep_results:
            new_row = row.to_dict()  # Keep all original columns
            sources_text = "\n\nSources:\n" + "\n".join(result.get("sources", []))
            complete_answer = result.get("answer", "") + sources_text
            new_row.update(
                {
                    "model": result.get("model", ""),
                    "whitelist": result.get("whitelist", ""),
                    "complete_answer": complete_answer,
                    "batch": result.get("batch", 0),
                }
            )
            results.append(new_row)

        # Update progress bar
        progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()

    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"Experiment completed. Results saved to {output_file}")


if __name__ == "__main__":
    print("Running experiment...")
    print("Input file: questions.xlsx")
    print("Output file: results.xlsx")
    print("Iterations: 4")
    print("Model: sonar")
    print("Whitelist: https://www.aan.com")
    print("Temperature: 0.9")
    print("Max tokens: 3000")
    run_experiment_on_excel(
        input_file="questions.xlsx",
        output_file="results.xlsx",
        iterations=4,
        model="sonar",
        whitelist=["https://www.aan.com"],
        temperature=0.9,
        max_tokens=8000,
    )
