from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import csv
import re

from dotenv import load_dotenv
import glob
from llama_cpp import Llama
from bs4 import BeautifulSoup
import uuid 
import zipfile
import shutil
import ast
import io
import os
from io import BytesIO
import pandas as pd
from pypdf import PdfReader
from ollama import chat
import re
from pywebio.input import input, TEXT, file_upload
from pywebio.output import put_text, use_scope, put_table, put_markdown, put_file, put_loading
from pathlib import Path


def chat_app():
    xlsm_file = file_upload("Upload Race Weekend Schedule as Excel file:", accept=".xlsm")
    with open("./uploaded.xlsm", "wb") as f:
        f.write(xlsm_file["content"])
    user_question = input("Enter race weekend information:", type=TEXT).strip()
    
    put_text(user_question).style('color:green')
    plain_text = user_question
         # Load CPU GGUF model
    MODEL_FILE = r"C:\Users\ArjanFaberVAR\OneDrive - Van Amersfoort Racing B.V\ExceltoCalendarTool-VAR - Documenten\Meta-Llama-3-8B-Instruct.Q4_0.gguf"
   
    with put_loading():
        model = Llama(
            model_path=MODEL_FILE,
            n_threads=64,
            )
    
        messages = [
        {
            "role": "system",
            "content": "Acknowledge the user's request briefly in one sentence."
        },
        {
            "role": "user",
            "content": plain_text
        }
    ]
    with put_loading():
        res = model.create_chat_completion(
            messages=messages,
            temperature=0,
            max_tokens=32,
        )
    generated_text = res["choices"][0]["message"]["content"].strip()
    put_text(generated_text)

    with put_loading():

        # Load CPU GGUF model
        MODEL_FILE = r"C:\Users\ArjanFaberVAR\OneDrive - Van Amersfoort Racing B.V\ExceltoCalendarTool-VAR - Documenten\Meta-Llama-3-8B-Instruct.Q4_0.gguf"

        model = Llama(
            model_path=MODEL_FILE,
            n_threads=64,
        )
        iana_time_zones = [
            "Australia/Melbourne",
            "Asia/Bahrain",
            "Asia/Riyadh",
            "America/New_York",
            "America/Toronto",
            "Europe/Monaco",
            "Europe/Madrid",
            "Europe/Vienna",
            "Europe/London",
            "Europe/Brussels",
            "Europe/Budapest",
            "Europe/Rome",
            "America/Los_Angeles",
            "Asia/Qatar",
            "Asia/Dubai",
            "Asia/Kolkata",
            "Europe/Paris",
            "Europe/Amsterdam",
            "America/Sao_Paulo",
            "Africa/Casablanca",
            "Europe/Lisbon",
            "Europe/Berlin",
            "Asia/Seoul",
            "Asia/Kuala_Lumpur",
            "Africa/Johannesburg"
        ]
        messages = [
        {
            "role": "system",
            "content": (
                f"You are a strict extraction engine. "
                f"Output ONLY a Python list of strings. "
                f"First include all Excel sheet name(s) exactly as written in the e-mail text. "
                f"Then include the race location's IANA time zone. "
                f"The time zone MUST be selected from the list below.\n\n"
                f"If the exact city mentioned in the text is not present, choose the time zone whose city or region "
                f"is geographically closest to the location mentioned in the text.\n\n"
                f"Do NOT add any extra words, explanations, or bullet points.\n"
                f"Example structure (DO NOT COPY): ['Sheet1', 'Area/City']\n\n"
                f"Allowed IANA time zones:\n{iana_time_zones}"
            )
        },
        {
            "role": "user",
            "content": (
                f"Extract the Excel sheet name(s) and determine the correct IANA time zone for the race location mentioned "
                f"in the text below. If the exact city is not in the allowed list, choose the geographically closest one.\n\n"
                f"Output ONLY a Python list.\n\n{plain_text}"
            )
        }
        ]

        res = model.create_chat_completion(
        messages=messages,
        temperature=0,
        max_tokens=32,
        )

        generated_text = res["choices"][0]["message"]["content"].strip()

        try:
            sheet_list = ast.literal_eval(generated_text)

            # Handle nested string list
            if len(sheet_list) == 1 and isinstance(sheet_list[0], str) and sheet_list[0].startswith("["):
                sheet_list = ast.literal_eval(sheet_list[0])

        except Exception:
            sheet_list = [generated_text]
        print("Sheets found:", sheet_list)
        text = "Using time zone " + sheet_list[-1] + "..."
        put_text(text).style("color: grey")
        messages = [
            {
            "role": "system",
            "content": (
                "You are a strict extraction engine. Output only the categories that appear in the text. "
                "Here are the categories and their keywords:\n"
                "MEAL: breakfast, lunch, dinner\n"
                "TRAVEL: leaving hotel, arrival circuit, team arrival\n"
                "MEETING: meeting, briefing, pm, db\n"
                "GARAGE: engine, fuel, tyre, fire up, cars stand, drivers ready\n"
                "SESSION: practice session, qualifying session, sprint race, feature race\n"
                "TRACK: track walk, systems checks, track test\n"
                "FIA: scrutineering, fia, deadline\n"
                "MEDIA: press conference, photo\n"
                "PIRELLI: pirelli, parc ferme\n"
                "OPERATIONS: pit lane, trolleys, cars released\n"
                "Each category should appear only once if present. If none identified, return a single value list ['ALL']. "
                "Do not output anything else."
            )
            },
            {
                "role": "user",
                "content": f"Extract the categories from this text:\n\n{plain_text}"
            }
        ]
        res = model.create_chat_completion(
            messages=messages,
            temperature=0,
            max_tokens=32,
        )

        generated_text2 = res["choices"][0]["message"]["content"].strip()


        # Remove brackets and quotes
        clean_text = re.sub(r"[\[\]'\"\s]", "", generated_text2)

        # Split on commas and convert to uppercase
        cat_list = [c.upper() for c in clean_text.split(",") if c]
        cat_list_str = " ".join([c.upper() for c in clean_text.split(",") if c])
        print("Categories found: ", cat_list)
        text = "Found categories " + cat_list_str
        put_text(text).style("color: grey")

        ACTIVITY_RULES = {
        "MEAL": ["breakfast", "lunch", "dinner"],
        "TRAVEL": ["Leaving hotel", "Arrival circuit", "team arrival"],
        "MEETING": ["meeting", "briefing", "pm", "db"],
        "GARAGE": ["engine", "fuel", "tyre", "fire up", "cars stand", "drivers ready"],
        "SESSION": ["practice session", "qualifying session", "sprint race", "feature race"],
        "TRACK": ["track walk", "systems checks", "track test"],
        "FIA": ["scrutineering", "fia", "deadline"],
        "MEDIA": ["press conference", "photo"],
        "PIRELLI": ["pirelli", "parc ferme"],
        "OPERATIONS": ["pit lane", "trolleys", "cars released"],
        }

        def detect_category(title):
            title_lower = str(title).lower()

            for category, keywords in ACTIVITY_RULES.items():
                for kw in keywords:
                    if kw in title_lower:
                        return category

            
            return None

        def functionality(sheet,tz_str):
            df = []

            df = pd.read_excel("./uploaded.xlsm", sheet_name=sheet)


            def detect_date(row):
                for value in row.dropna():
                    value = str(value)  # convert everything to string

                    match_textual = re.search(
                        r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b",
                        value
                    )
                    if match_textual:
                        return match_textual.group(0)

        
                    match_datetime = re.search(
                        r"\b\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\b",
                        value
                    )
                    if match_datetime:
                        return match_datetime.group(0)

                return None

            def indices_per_day(df):
                date_rows = []
                dates = []

                for i in range(len(df)):
                    row = df.iloc[i]  # a Series

                    # Check if "DAY" appears in any cell
                    if row.astype(str).str.contains("DAY", case=False, na=False).any():
                        # Extract the date from the row, converting all values to strings
                        row_str = " ".join([str(x) for x in row])
                        match = re.search(
                        r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b",
                        row_str
                        )
                        if match:
                            date_rows.append(i)
                            dates.append(match.group(0))

                return date_rows, dates

            def convert_to_full_format(value):
                try:
                    # Try parsing normally first
                    dt = pd.to_datetime(value)
                except:
                    # If it's like "27 October", explicitly parse it
                    dt = pd.to_datetime(value, format="%d %B")

                # Platform-safe day without leading zero
                return f"{dt.strftime('%A')} {dt.day} {dt.strftime('%B')}"

            date_rows, dates = indices_per_day(df)

            converted = [convert_to_full_format(day) for day in dates]

            def build_day_blocks(df, date_rows):
                blocks = []

                for i in range(len(date_rows)):
                    start = date_rows[i] + 2
                    end = date_rows[i + 1] if i + 1 < len(date_rows) else len(df)
                    blocks.append(df[start:end])

                return blocks

            df_schedule = build_day_blocks(df, date_rows)

            df_clean = []

            for block in df_schedule:
                temp = block[['Unnamed: 1', 'Unnamed: 4', 'Unnamed: 7', 'Unnamed: 9']].copy()
                temp.columns = ['start_time', 'end_time', 'duration', 'event']
                temp = temp.dropna(how='all')

                df_clean.append(temp)


            def infer_year(day_month_str):
                """
                Converts a day/month string like 'Monday 9 February' to a datetime object with inferred year.
                """
                # Use a temporary year so strptime works
                temp_date = datetime.strptime(day_month_str + " 2000", "%A %d %B %Y")
                now = datetime.now()

                # Replace year with current year
                candidate_date = temp_date.replace(year=now.year)

                # If this date already passed, use next year
                if candidate_date < now:
                    candidate_date = candidate_date.replace(year=now.year + 1)

                return candidate_date

    #def combine_date_time(base_date, time_val):
    #    """
    #    time_val: either a string 'HH:MM:SS' or a datetime.time object
    #    """
    #    if isinstance(time_val, str):
    #        t = datetime.strptime(time_val, "%H:%M:%S").time()
    #    elif isinstance(time_val, time):
    #        t = time_val
    #    else:
    #        raise ValueError(f"Unexpected time type: {type(time_val)}")
   # 
   #    return datetime.combine(base_date.date(), t)

            def combine_date_time(base_date, time_val, tz_str):
                """
                Combine a date with a time (string 'HH:MM:SS' or datetime.time)
                and return a timezone-aware datetime in tz_str
                """
                if isinstance(time_val, str):
                    t = datetime.strptime(time_val, "%H:%M:%S").time()
                elif isinstance(time_val, time):
                    t = time_val
                else:
                    raise ValueError(f"Unexpected time type: {type(time_val)}")

                naive_dt = datetime.combine(base_date.date(), t)
                aware_dt = naive_dt.replace(tzinfo=ZoneInfo(tz_str))
                return aware_dt
    #def create_calendar(df_clean, base_date, sheet):
    #    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Schedule Export//EN\n"

    #    for _, row in df_clean.iterrows():
    #        start_time = row["start_time"]
    #        end_time = row["end_time"]
    #        title = row["event"]

            # Skip TBC or NaN
    #        if start_time == "TBC" or pd.isna(start_time):
    #            continue

    #        start_dt = combine_date_time(base_date, start_time)

    #        if pd.isna(end_time):
    #            end_dt = start_dt + timedelta(hours=1)
    #        else:
    #            end_dt = combine_date_time(base_date, end_time)

            # Generate a unique UID for each event
    #        event_uid = str(uuid.uuid4())

            # Escape special characters in title
    #        title_escaped = title.replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

    #        ics_content += (
    #            "BEGIN:VEVENT\n"
    #            f"UID:{event_uid}\n"
    #            f"SUMMARY:{title_escaped}\n"
    #            f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\n"
    #            f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}\n"
    #            "END:VEVENT\n"
    #        )

    #    ics_content += "END:VCALENDAR"

    #    with open(f"./ICS_Docs/{sheet}_full_schedule_{base_date.strftime('%Y%m%d')}.ics", "w", encoding="utf-8") as f:
    #        f.write(ics_content)

    #    print("ICS file created successfully")

            def create_calendar(df_clean, base_date, sheet, tz_str):
                ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Schedule Export//EN\n"

                for _, row in df_clean.iterrows():
                    start_time = row["start_time"]
                    end_time = row["end_time"]
                    title = row["event"]

                    if start_time == "TBC" or start_time =="ASAP" or pd.isna(start_time):
                        continue

                # Make aware datetimes in the given timezone
                    start_dt = combine_date_time(base_date, start_time, tz_str)
                    end_dt = combine_date_time(base_date, end_time, tz_str) if not pd.isna(end_time) else start_dt + timedelta(hours=1)

                    # Convert both to UTC
                    start_utc = start_dt.astimezone(timezone.utc)
                    end_utc = end_dt.astimezone(timezone.utc)

                # UID and escape title
                    event_uid = str(uuid.uuid4())
                    title_escaped = title.replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")
                    category = detect_category(title)

                    user_input = cat_list if cat_list else ["ALL"]

                    if user_input == ["ALL"]:
                        INCLUDED_CATEGORIES = set(ACTIVITY_RULES.keys())
                    else:
                        INCLUDED_CATEGORIES = set(user_input)

                    # Skip if category not selected
                    if category not in INCLUDED_CATEGORIES:
                        continue
                    ics_content += (
                "BEGIN:VEVENT\n"
                f"UID:{event_uid}\n"
                f"SUMMARY:[{sheet}] {title_escaped}\n"
                f"CATEGORIES:{sheet},{category}\n"
                f"DTSTART:{start_utc.strftime('%Y%m%dT%H%M%SZ')}\n"
                f"DTEND:{end_utc.strftime('%Y%m%dT%H%M%SZ')}\n"
                "END:VEVENT\n"
                )

                ics_content += "END:VCALENDAR"

                os.makedirs("./ICS_Docs", exist_ok=True)
                with open(f"./ICS_Docs/{sheet}_full_schedule_{base_date.strftime('%Y%m%d')}.ics", "w", encoding="utf-8") as f:
                    f.write(ics_content)

                print(f"ICS file for '{sheet}' created successfully.")
    
            for i in range(len(converted)):
                base_date = infer_year(converted[i])
                create_calendar(df_clean[i], base_date, sheet, tz_str)

        ics_folder = "./ICS_Docs"
    

        for s in sheet_list[:-1]:
            try:
                functionality(s, sheet_list[-1])
            except Exception as e:
                put_text(f"Error: {e}")
                return
 
        zip_folder = "./zipfolder"
        os.makedirs(zip_folder, exist_ok=True)

        zip_filename = os.path.join(zip_folder, "calendar_files.zip")

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir(ics_folder):
                if filename.lower().endswith(".ics"):
                    file_path = os.path.join(ics_folder, filename)

                    if os.path.isfile(file_path):
                        zipf.write(file_path, arcname=filename)
    
    zip_filename = os.path.join(zip_folder, "calendar_files.zip")
    # Only ONE download button
    rows = [['Type', 'Content']]

    with open(zip_filename, 'rb') as f:
        rows.append([
            'zip',
            put_file("calendar_files.zip", f.read())
        ])

    put_text("Here you go!")
    put_table(rows)
# ==========================================================
# 🔟 Start server
# ==========================================================

from pywebio import start_server
start_server(chat_app, port=8086, debug=True)