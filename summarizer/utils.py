import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import json
from pdf2image import convert_from_path
from pathlib import Path
from openai import OpenAI  # if using their client; adapt if different
import logging
import re, json

logger = logging.getLogger(__name__)
#setx OPENAI_API_KEY "your_api_key_here"
# Load keys from env
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Initialize OpenAI client (adapt to your client)
client = OpenAI(api_key="ssh -xxxx ")

# ----- image helpers -----
def pdf_to_image(pdf_path, dpi=300):
    pages = convert_from_path(pdf_path, dpi=dpi)
    # return first page as PIL Image
    return pages[0]

def load_image(path_or_pil):
    if isinstance(path_or_pil, Image.Image):
        return cv2.cvtColor(np.array(path_or_pil), cv2.COLOR_RGB2BGR)
    else:
        return cv2.imread(str(path_or_pil))

def preprocess_image_cv2(cv_img):
    # cv_img: BGR image
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    return gray

def ocr_image(pil_or_cv_image):
    # accept PIL or cv2
    if isinstance(pil_or_cv_image, Image.Image):
        img = pil_or_cv_image
    else:
        # cv2 image -> PIL
        img = Image.fromarray(cv2.cvtColor(pil_or_cv_image, cv2.COLOR_BGR2RGB))
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config)
    return text

# ----- OpenAI helper -----
SYSTEM_PROMPT = ("You are a medical assistant that analyzes individual medical test results and outputs information strictly in JSON format. "
            "For each result, return a dictionary with the following keys:\n\n"
            "- \"value_comparison\": for each values that can be explained to the patient, if the values are very different from ideal values, describe only those values, based on the reference range and also provide the comparision for the values.\n"
            "- \"severity\": Mild, Moderate, or Severe, depending on how far the value is from normal. Provide what are the concerning factors and what are not \n"
            "- \"what_to_do_next\": A plain-language suggestion, (e.g., consult a doctor, no immediate concern, retest later). Provide a short summary to tell the patient what to do next\n\n"
            "**Important:** Output only a JSON object. Do not include explanations, markdown, or any other text."
        )


def call_openai_for_summary(extracted_text, age=None, gender=None):
    # Build prompt
    user_prompt = f"Patient age: {age}\nGender: {gender}\n\nReport Text:\n{extracted_text}\n\nReturn JSON as specified."
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT},
        {"role":"user", "content": user_prompt}
    ]
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0)
        raw = resp.choices[0].message.content.strip()
        # Try to parse JSON
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()

        if "```" in raw:
            raw = re.sub(r"```[a-zA-Z]*", "", raw)
            raw = raw.replace("```", "").strip()

        parsed = json.loads(raw) 

        return parsed
    except json.JSONDecodeError:
        logger.exception("OpenAI output not valid JSON")
        # fallback: try to find JSON substring
        try:
            start = raw.index('{')
            end = raw.rindex('}') + 1
            raw_json = raw[start:end]
            return json.loads(raw_json)
        except Exception:
            return {"error": "Could not parse model output", "raw": raw}
    except Exception as e:
        logger.exception("OpenAI call failed")
        return {"error": str(e)}
