import requests
import base64
import time
from pathlib import Path
import statistics
import subprocess
import re
import os
import time
from google import genai

API_KEY = "ENTER LOCAL API KEY HERE(apni nahi de raha mai yaha)"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set.")


client = genai.Client(api_key=API_KEY)


# ============================================================
# DIRECT LLAMA-SERVER
# ============================================================



# ============================================================
# DIRECT LLAMA-SERVER
# ============================================================

PORT = 8080

BASE_URL = f"http://127.0.0.1:{PORT}/v1"

HEADERS = {}

print(f"llama-server: 127.0.0.1:{PORT}")

IMAGE_DIR = Path(
    r"D:\Project_DivyaChakshu\dataset\guidedog_gold"
)

# 10 DIFFERENT fresh images
# images = sorted(IMAGE_DIR.glob("*.jpg"))[121:152]
images = [IMAGE_DIR / "a.png"] * 20
# images = "D:\Project_DivyaChakshu\dataset\11111.png"

# ============================================================
# LOAD STAGE-3 PROMPT FROM FILE
# ============================================================

PROMPT_FILE = Path(
    r"D:\Project_DivyaChakshu\o.txt"
)

PROMPT = PROMPT_FILE.read_text(
    encoding="utf-8"
).strip()
# PROMPT = "Describe the image in detail."


# ============================================================
# GET MODEL
# ============================================================

models_response = requests.get(
    f"{BASE_URL}/models",
    headers=HEADERS,
    timeout=10
)

models_response.raise_for_status()

model = models_response.json()["data"][0]["id"]


# ============================================================
# START BENCHMARK
# ============================================================

print()
print("=" * 75)
print("DIRECT LLAMA-SERVER BENCHMARK")
print("=" * 75)

print(f"MODEL : {model}")
print(f"SERVER: {BASE_URL}")
print(f"IMAGES: {len(images)}")
print("=" * 75)
print()

results = []


for i, image_path in enumerate(images, 1):

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image_b64 = base64.b64encode(
        image_path.read_bytes()
    ).decode()


    # --------------------------------------------------------
    # Send request directly to llama-server
    # --------------------------------------------------------

    start = time.perf_counter()

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=HEADERS,

        json={
            "model": model,

            "messages": [
                {
                    "role": "user",

                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT
                        },

                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],

            "max_tokens": 350,
            "temperature": 0.25,
            # "repeat_penalty": 1.3,
            "stream": False,
            # "stop": ["[END]"],
            # "top_p": 0.9
            
        },

        timeout=60
    )

    
    
    elapsed = time.perf_counter() - start

    response.raise_for_status()

    data = response.json()

    output = data["choices"][0]["message"]["content"]

    results.append(elapsed)
    
    
    
    
    
    
    
    
    
    
    
    
    # response.raise_for_status()

    # output_parts = []

    # for line in response.iter_lines(decode_unicode=True):

    #     if not line:
    #         continue

    #     if line.startswith("data: "):
    #         chunk = line[6:]

    #         if chunk == "[DONE]":
    #             continue

    #         data = requests.models.complexjson.loads(chunk)

    #         delta = data["choices"][0].get("delta", {})
    #         text = delta.get("content", "")

    #         if text:
    #             output_parts.append(text)

    # elapsed = time.perf_counter() - start

    # output = "".join(output_parts)

    # results.append(elapsed)
    
    
    


    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print(
        f"{i:02d} | "
        f"{image_path.name} | "
        f"{elapsed:.3f} s | "
        f"{output}"
    )


# ============================================================
# SUMMARY
# ============================================================

average = statistics.mean(results)
median = statistics.median(results)
fastest = min(results)
slowest = max(results)
fps = 1 / average


print()
print("=" * 75)
print("SUMMARY")
print("=" * 75)

print(f"Average latency : {average:.3f} s")
print(f"Median latency  : {median:.3f} s")
print(f"Fastest         : {fastest:.3f} s")
print(f"Slowest         : {slowest:.3f} s")
print(f"Effective FPS   : {fps:.2f}")

print("=" * 75)