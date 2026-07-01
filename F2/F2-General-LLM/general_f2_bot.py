import ast
import os
from bs4 import BeautifulSoup
from pypdf import PdfReader
from ollama import chat
import re
from pywebio.input import input, TEXT
from pywebio.output import put_text, use_scope, put_table, put_markdown, put_file, put_loading
from pathlib import Path

# ==========================================================
# 2️⃣ Load question from email
# ==========================================================

import sys

# ==========================================================
# 2️⃣ Load question (HTML OR terminal)
# ==========================================================

def get_user_question(prompt_text="Type your question:"):
    """
    Prompt the user for a question directly.
    Returns the entered question as a string.
    """
    question = "Compare all sections"
    if not question:
        raise ValueError("No question provided.")
    return question


# Example usage
user_question = get_user_question("Enter the question about F2 regulations: ")
print(f"\nQuestion: {user_question[:100]}...\n")

# ==========================================================
# 3️⃣ Reason about relevant sections based on question
# ==========================================================

reason_prompt = f"""
You are a general bot assistant helping out engineers from F2 during race weekends.

Question: {user_question}"""

# ==========================================================
# 4️⃣ Load GGUF 8-bit model
# ==========================================================

GGUF_MODEL_PATH = r"C:\Users\ArjanFaberVAR\OneDrive - Van Amersfoort Racing B.V\Regulations-VAR - Documenten\Meta-Llama-3-8B-Instruct.Q4_0.gguf"
n_threads = os.cpu_count() - 1

import subprocess
import time

# Start Ollama server
OLLAMA_EXE = r"C:\Users\ArjanFaberVAR\AppData\Local\Programs\Ollama\Ollama.exe"
MODEL_NAME = "gpt-oss:120b-cloud"
API_KEY = "c109ad8c287f14ba1be1c61a0e09fc1fe.tU6J3r7fqva9UKVFYjPRghw2"

os.environ["OLLAMA_API_KEY"] = API_KEY

# 1️⃣ Pull the model if it doesn't exist
try:
    result = subprocess.run([OLLAMA_EXE, "list"], capture_output=True, text=True)

    if MODEL_NAME not in result.stdout:
        print(f"Model '{MODEL_NAME}' not found. Pulling it now...")
        subprocess.run([OLLAMA_EXE, "pull", MODEL_NAME], check=True)
    else:
        print(f"Model '{MODEL_NAME}' is already downloaded.")

except Exception as e:
    print("Error checking/pulling Ollama model:", e)
    raise

# 2️⃣ Start Ollama server
subprocess.Popen([OLLAMA_EXE, "serve"])

# 3️⃣ Give it time
time.sleep(5)
print("Ollama server should be ready to accept requests.")


def ask_ollama(prompt, system=None, max_tokens=800, temperature=0.0):
    messages = []

    if system:
        messages.append({"role": "system", "content": system})

    messages.append({"role": "user", "content": prompt})

    response = chat(
        model=MODEL_NAME,
        messages=messages,
        options={
            "temperature": temperature,
            "num_predict": max_tokens
        }
    )

    return response["message"]["content"]


# Ask the model
relevant_sections_text = ask_ollama(reason_prompt, max_tokens=800, temperature=0.0)

# Split output
raw_sections = re.split(r'[,\n]', relevant_sections_text)

sections_to_include = ["__FULL_DOC__"]

print("Sections to include for comparison:", sections_to_include)

# ==========================================================
# 5️⃣ System prompt
# ==========================================================

system_prompt = """ 
You are an intelligent bot that help out engineers during raceweekends.

Hurry up and be fast and accurate in answering the questions
"""
# ==========================================================
# 6️⃣ Helpers
# ==========================================================

def extract_section_text(full_text, section_name):
    if section_name == "__FULL_DOC__":
        return full_text

    pattern = rf'({re.escape(section_name)}.*?)(?=^\s*(Article|Section)\s+\d+|\Z)'
    match = re.search(pattern, full_text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)

    return match.group(1).strip() if match else ""


def split_text(text, max_words=1200):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


# ==========================================================
# 7️⃣ Generate answers
# ==========================================================

answers = []


answer_text = ask_ollama(system_prompt, system=system_prompt, max_tokens=12000)
answers.append(answer_text)
        

# ==========================================================
# 8️⃣ Save
# ==========================================================

final_answer = "\n".join(answers)

os.makedirs("./answers", exist_ok=True)

with open("./answers/first_answer_0.txt", "w", encoding="utf-8") as f:
    f.write(final_answer)

print("Answer saved.")

# ==========================================================
# 9️⃣ Chat UI
# ==========================================================

def chat_app():
    answer_counter = 0

    while answer_counter < 100:
        user_question = input("Enter your general question (just type exit to leave the chat):", type=TEXT).strip()

        if user_question.lower() == "exit":
            put_text("Exiting chat. Goodbye!")
            break

        if not user_question:
            put_text("⚠ No question entered. Please try again.")
            continue

        with use_scope(f"q{answer_counter}", clear=True):
            put_text(user_question).style('color:green')

            try:
                with put_loading():
                    augmented_system = system_prompt + "\n\nDifferences:\n" + final_answer                
                    response = ask_ollama(user_question, system=augmented_system, max_tokens=4500)

                put_text(response)
                put_text(answers)

                with open(f"./answers/answer_{answer_counter}.txt", "w", encoding="utf-8") as f:
                    f.write(response)

            except Exception as e:
                put_text(f"⚠ Error: {e}")

        answer_counter += 1

    files = list(Path("./answers").glob("*.txt"))

    rows = [['Type', 'Content']]

    for file in files:
        rows.append([
            'file',
            put_file(file.name, open(file, 'rb').read())
        ])

    put_table(rows)


# ==========================================================
# 🔟 Start server
# ==========================================================

from pywebio import start_server
start_server(chat_app, port=8082, debug=True)