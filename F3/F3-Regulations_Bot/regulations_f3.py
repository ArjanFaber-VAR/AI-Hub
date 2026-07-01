# ==========================================================
# F3 Regulations RAG System - CPU Optimized, GGUF 8-bit
# ==========================================================

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
# 1️⃣ Load PDFs as full text
# ==========================================================

pdf_files = {
    "2025_regs": "regulations_f3_2025.pdf",
    "2026_regs": "regulations_f3_2026.pdf",
    "driving_standards": "DrivingStandards.pdf",
    "sporting_code": "SportingCode.pdf",
    "penalty_guidelines": "PenaltyGuideLines.pdf"
}


documents = {}

print("Loading PDFs...")

for year, filename in pdf_files.items():
    print(f"Processing {filename}...")
    reader = PdfReader(filename)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    documents[year] = text
    print(f" PDF loaded for {year}, length: {len(text)} characters")

pattern = r'^(?:ARTICLE\s+\d+.*|\d+(?:\.\d+)+.*)'
headings_2025 = re.findall(pattern, documents["2025_regs"], re.MULTILINE)
headings_2026 = re.findall(pattern, documents["2026_regs"], re.MULTILINE)
headings_driving_standards= re.findall(pattern, documents["driving_standards"], re.MULTILINE)
headings_sporting_code= re.findall(pattern, documents["sporting_code"], re.MULTILINE)
headings_penalty_guidelines= re.findall(pattern, documents["penalty_guidelines"], re.MULTILINE)
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
user_question = get_user_question("Enter the question about F3 regulations: ")
print(f"\nQuestion: {user_question[:100]}...\n")

# ==========================================================
# 3️⃣ Reason about relevant sections based on question
# ==========================================================

reason_prompt = f"""
You are analyzing the Formula 3 sporting regulations changes from 2025 and 2026.

Question: {user_question}

Available Headings (2026):
{headings_2026}
And:
{headings_driving_standards}
And:
{headings_sporting_code}
And:
{headings_penalty_guidelines}

Task:
Identify the relevant section headings from the list above that directly help answer the question.

Rules:
- Only select headings from the 'Available Headings (2026)' list.
- Each heading must exactly match an item in the list; do NOT modify or paraphrase.
- Do NOT add explanations, notes, or any text beyond the headings.
- Output must be a valid Python list of strings.
- Do not include any text before or after the list.
- Do not use f-string braces or any other Python syntax outside the list.

Example of correct output:
["Heading 1", "Heading 2"]
"""

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


def ask_ollama(prompt, system=None, max_tokens=12000, temperature=0.0):
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
relevant_sections_text = ask_ollama(reason_prompt, max_tokens=12000, temperature=0.0)

# Split output
raw_sections = re.split(r'[,\n]', relevant_sections_text)

sections_to_include = ["__FULL_DOC__"]

print("Sections to include for comparison:", sections_to_include)

# ==========================================================
# 5️⃣ System prompt
# ==========================================================

system_prompt = """ 
You are scanning and comparing technical regulation texts and driving standards, sporting code and general guidelines. 
Strict rules: 
1. Comparison Scope: 
- If needed, compare **only** the 2025 text against the 2026 text. 
- Otherwise, provide answers based solely on the context of the text in question. 
2. Show Only Changes: 
- Display **only the wording that changed** between the two years. 
- Do not repeat lines or sections that are identical. 
3. Clear Year Labels: 
- Use this format for each change: 2025: [text from 2025] 2026: [text from 2026] 
- If a line was **added** in 2026, show it only under 2026. 
- If a line was **removed** in 2026, show it only under 2025. 
4. Formatting: 
- Maintain a **clean, readable format**; avoid any extraneous symbols, line numbers, or Git diff metadata. 
- Do not include explanations, comments, or analysis 
— just the text changes. 
5. Identical Lines: 
- If the line or section is identical in both years, do **not** include it. 
6. Edge Cases: 
- If a line was modified slightly (e.g., wording change, punctuation, or numeric value), show the old version under 2025 
and the new version under 2026. 
- Preserve the exact wording, including punctuation, capitalization, and spacing. 
- If context is required to understand a change, provide only what is necessary to show the change clearly, without adding extra text. 
7. Output Only: - Only provide the changed lines as specified. Do also summarize, interpret. Make sure to add reference of the article or section where the exact answer can be found in the technical regulations
8. Write it nicely please, so that it is easy to read."""
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

for section in sections_to_include:
    text_2025 = extract_section_text(documents["2025_regs"], section)
    text_2026 = extract_section_text(documents["2026_regs"], section)

    if not text_2025 or not text_2026:
        print(f"⚠ Section '{section}' missing in one of the documents")
        continue

    chunks_2025 = split_text(text_2025)
    chunks_2026 = split_text(text_2026)

    for i, (c1, c2) in enumerate(zip(chunks_2025, chunks_2026), start=1):
        print(
        f"🔍 Processing section: {section} | "
        f"chunk {i}/{min(len(chunks_2025), len(chunks_2026))} | "
        f"2025 chars: {len(c1)} | 2026 chars: {len(c2)}"
        )
        extra_context = f"""

DRIVING STANDARDS:
{documents["driving_standards"][:25000]}

SPORTING CODE:
{documents["sporting_code"][:25000]}

PENALTY GUIDELINES:
{documents["penalty_guidelines"][:25000]}
"""
        prompt = f"""

{system_prompt}

2025:
{c1}

2026:
{c2}

Extra FIA data:
{extra_context}
"""

        answer_text = ask_ollama(prompt, system=system_prompt, max_tokens=12000)
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
        user_question = input("Enter your F3 technical regulation question (just type exit to leave the chat):", type=TEXT).strip()

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
                    augmented_system = (system_prompt + "\n\nDifferences:\n" + final_answer + "\n\nAdditional FIA Documents:\n" + extra_context )
                    response = ask_ollama(user_question, system=augmented_system, max_tokens=12000)

                put_text(response)

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
start_server(chat_app, host="0.0.0.0", port=8083, debug=True)