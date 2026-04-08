# app.py
import logging
from build_graph import react_agent
from langchain_core.messages import HumanMessage
import requests
import os
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

username = os.environ.get("USERNAME")
agent_code = os.environ.get("AGENT_CODE")

missing = []

if not username:
    missing.append("USERNAME")

if not agent_code:
    missing.append("AGENT_CODE")

if missing:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")



DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"

api_url = DEFAULT_API_URL
questions_url = f"{api_url}/questions" # get
submit_url = f"{api_url}/submit" #post
random_question_url = f"{api_url}/random-question" #get


def get_questions():
    # 2. Fetch Questions
    print(f"Fetching questions from: {questions_url}")
    try:
        response = requests.get(questions_url, timeout=15)
        response.raise_for_status()
        questions_data = response.json()
        if not questions_data:
             print("Fetched questions list is empty.")
             return "Fetched questions list is empty or invalid format.", None
        print(f"Fetched {len(questions_data)} questions.")
        return questions_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching questions: {e}")
        return f"Error fetching questions: {e}", None
    except requests.exceptions.JSONDecodeError as e:
         print(f"Error decoding JSON response from questions endpoint: {e}")
         print(f"Response text: {response.text[:500]}")
         return f"Error decoding server response for questions: {e}", None
    except Exception as e:
        print(f"An unexpected error occurred fetching questions: {e}")
        return f"An unexpected error occurred fetching questions: {e}", None
    

def get_answers(questions):
    try:
        answers_payload = []
        for i, question in enumerate(questions):
            print(f'Solving question {i+1}\n')
            task_id = question.get('task_id')
            q = question.get('question')
            file_name = question.get('file_name')

            if file_name and file_name.strip():
                submitted_answer = "default answer"  #no tools to process files, add tools for proper file handling

            else:
                message = [HumanMessage(content = q)]
                try:
                    answer = react_agent.invoke({
                        "messages": message
                    })
                    submitted_answer = answer['messages'][-1].content
                    submitted_answer = submitted_answer.strip()
                except Exception as e:
                    submitted_answer = f"Error: {type(e).__name__}"

            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})
        return answers_payload
    except Exception as e:
        return f'Error while solving answer: {type(e).__name__ }'
    


questions = get_questions()
if not isinstance(questions, list):
    raise ValueError("Invalid questions format")

answers_payload = get_answers(questions)


def submit_ans(answers_payload):
    try:

        submission_data = {"username": username, "agent_code": agent_code, "answers": answers_payload}

        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        return final_status
    except requests.exceptions.HTTPError as e:
        error_detail = f"Server responded with status {e.response.status_code}."
        try:
            error_json = e.response.json()
            error_detail += f" Detail: {error_json.get('detail', e.response.text)}"
        except requests.exceptions.JSONDecodeError:
            error_detail += f" Response: {e.response.text[:500]}"
        status_message = f"Submission Failed: {error_detail}"
        return status_message
    except requests.exceptions.Timeout:
        status_message = "Submission Failed: The request timed out."
        return status_message
    except requests.exceptions.RequestException as e:
        status_message = f"Submission Failed: Network error - {e}"
        return status_message
    except Exception as e:
        status_message = f"An unexpected error occurred during submission: {e}"
        return status_message

status = submit_ans(answers_payload)
print(status)
