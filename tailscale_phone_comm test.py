# ============================================================
# DIVYACHAKSHU
# LIVE PHONE CAMERA → LFM → PHONE SPEAKER
# ============================================================
#
# ARCHITECTURE
#
# PHONE CAMERA
#      |
#      | HTTPS / Tailscale
#      v
# FASTAPI :8000
#      |
#      +----> Save exact JPEG
#      |
#      v
# captured_images
#      |
#      v
# LATEST-FRAME WORKER
#      |
#      v
# llama-server :8080
#      |
#      v
# LFM2.5-VL
#      |
#      +----> Webpage
#      |
#      +----> Browser speech
#
#
# IMPORTANT
#
# 1. Phone JPEG is saved exactly as received.
# 2. No resizing/recompression happens on laptop.
# 3. Phone frames are fed directly to LFM.
# 4. Latest-frame logic prevents a backlog of stale frames.
# 5. Phone speaks the LFM output using browser speechSynthesis.
# 6. The next speech waits until the previous speech finishes.
#
# ============================================================


# ============================================================
# SECTION 1 — IMPORTS
# ============================================================

import base64
import time
import threading
from datetime import datetime
from pathlib import Path

import requests

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

import uvicorn


# QUICK DECODE:
# requests  -> communicates with llama-server
# FastAPI   -> receives phone frames + serves webpage
# threading -> runs LFM independently
# pathlib   -> handles image files
# uvicorn   -> HTTPS web server


# ============================================================
# SECTION 2 — SERVER CONFIGURATION
# ============================================================

HOST = "0.0.0.0"

PORT = 8000

TAILSCALE_IP = "Tailscale IP of your machine" 


# ============================================================
# SECTION 3 — LLAMA-SERVER CONFIGURATION
# ============================================================

LLAMA_PORT = 8080

BASE_URL = f"http://127.0.0.1:{LLAMA_PORT}/v1"

HEADERS = {}


# QUICK DECODE:
# Phone/web server:
#    
#
# LFM server:
#     http://127.0.0.1:8080


# ============================================================
# SECTION 4 — PHONE FRAME STORAGE
# ============================================================

CAPTURE_DIR = Path(
    r"D:\Project_DivyaChakshu\phone_camera\captured_images"
)

CAPTURE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SECTION 5 — HTTPS CERTIFICATES
# ============================================================

SSL_CERT = Path(
    rf"D:\Project_DivyaChakshu\{TAILSCALE_IP}.pem"
)

SSL_KEY = Path(
    rf"D:\Project_DivyaChakshu\{TAILSCALE_IP}-key.pem"
)


# QUICK DECODE:
# These are the mkcert files required for Android camera access.
#
# Expected:



# ============================================================
# SECTION 6 — STAGE-3 PROMPT
# ============================================================

PROMPT_FILE = Path(
    r"D:\Project_DivyaChakshu\o.txt"
)

PROMPT = PROMPT_FILE.read_text(
    encoding="utf-8"
).strip()


# QUICK DECODE:
# The exact Stage-3 prompt you have been using is loaded here.


# ============================================================
# SECTION 7 — LFM SETTINGS
# ============================================================

MAX_TOKENS = 40

TEMPERATURE = 0.20

REQUEST_TIMEOUT = 60


# ============================================================
# SECTION 8 — GLOBAL LFM STATE
# ============================================================

lfm_model = ""

lfm_running = False

lfm_error = None

lfm_output = "Waiting for phone camera..."

lfm_elapsed = 0.0

lfm_frame_name = "—"

lfm_frame_count = 0

lfm_processed_count = 0

last_processed_filename = ""

latest_frame_filename = ""

state_lock = threading.Lock()


# QUICK DECODE:
# These variables keep the webpage synchronized with the
# live LFM processing state.


# ============================================================
# SECTION 9 — FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="DivyaChakshu Live Camera"
)


# ============================================================
# SECTION 10 — WEBPAGE
# ============================================================

HTML_FILE = Path(
    r"D:\Project_DivyaChakshu\T_p_c.html"
)

if not HTML_FILE.exists():
    raise FileNotFoundError(
        f"HTML file not found:\n{HTML_FILE}"
    )

HTML_PAGE = HTML_FILE.read_text(
    encoding="utf-8"
)
# ============================================================
# SECTION 11 — HOME PAGE
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
async def home():

    return HTML_PAGE


# ============================================================
# SECTION 12 — RECEIVE PHONE FRAME
# ============================================================

@app.post("/frame")
async def receive_frame(
    request: Request
):

    global latest_frame_filename
    global lfm_frame_count


    data = await request.body()


    if not data:

        return JSONResponse(

            {
                "ok": False,
                "error": "empty frame"
            },

            status_code=400

        )


    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S_%f"
        )
    )


    filename = (
        f"frame_{timestamp}.jpg"
    )


    output_path = (
        CAPTURE_DIR /
        filename
    )


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Save EXACTLY the bytes received from the phone.
    # No resize.
    # No OpenCV.
    # No recompression.
    # --------------------------------------------------------

    output_path.write_bytes(
        data
    )


    with state_lock:

     latest_frame_filename = filename

    lfm_frame_count += 1


    return {

        "ok":
            True,

        "filename":
            filename,

        "bytes":
            len(data)

    }


# QUICK DECODE:
# Phone JPEG → disk.
#
# The exact JPEG bytes are preserved.
#
# The LFM worker will pick up the newest file.


# ============================================================
# SECTION 13 — SYSTEM STATUS
# ============================================================

@app.get("/status")
async def status():

    saved_frames = len(
        list(
            CAPTURE_DIR.glob(
                "*.jpg"
            )
        )
    )


    lfm_status = "OFFLINE"


    try:

        response =requests.get(

                f"{BASE_URL}/models",

                timeout=2

            )


        if response.ok:

            lfm_status ="ONLINE"


    except Exception:

        lfm_status = "OFFLINE"


    with state_lock:


        processing = "PROCESSING"

        if lfm_running:

            processing = "PROCESSING"

        else:

            processing = "IDLE"


    return {

        "ok":
            True,

        "tailscale_ip":
            TAILSCALE_IP,

        "saved_frames":
            saved_frames,

        "lfm":
            lfm_status,

        "processing":
            processing

    }


# ============================================================
# SECTION 14 — LFM STATUS
# ============================================================

@app.get("/lfm-status")
async def get_lfm_status():

    with state_lock:

        return {

            "output":
                lfm_output,

            "elapsed":
                lfm_elapsed,

            "frame":
                lfm_frame_name,

            "latest_frame":
                latest_frame_filename,

            "processed_count":
                lfm_processed_count

        }


# ============================================================
# SECTION 15 — FIND NEWEST PHONE FRAME
# ============================================================

def get_newest_frame():

    frames = list(
        CAPTURE_DIR.glob(
            "*.jpg"
        )
    )


    if not frames:

        return None


    return max(
        frames,
        key=lambda p:
            p.stat().st_mtime_ns
    )


# QUICK DECODE:
# Finds the newest JPEG received from the phone.


# ============================================================
# SECTION 16 — PROCESS ONE PHONE FRAME
# ============================================================

def process_frame(
    image_path
):

    global lfm_output
    global lfm_elapsed
    global lfm_frame_name
    global lfm_processed_count
    global lfm_error


    try:

        # ----------------------------------------------------
        # READ EXACT SAVED JPEG
        # ----------------------------------------------------

        image_b64 = base64.b64encode(
            image_path.read_bytes()
        ).decode()


        # ----------------------------------------------------
        # SEND TO LFM
        # ----------------------------------------------------

        start =time.perf_counter()


        response =requests.post(

                f"{BASE_URL}/chat/completions",

                headers=HEADERS,

                json={

                    "model":
                        lfm_model,

                    "messages": [

                        {

                            "role":
                                "user",

                            "content": [

                                {

                                    "type":
                                        "text",

                                    "text":
                                        PROMPT

                                },

                                {

                                    "type":
                                        "image_url",

                                    "image_url": {

                                        "url":
                                            (
                                                "data:image/jpeg;base64,"
                                                +
                                                image_b64
                                            )

                                    }

                                }

                            ]

                        }

                    ],

                    "max_tokens":
                        MAX_TOKENS,

                    "temperature":
                        TEMPERATURE,

                    "stream":
                        False

                },

                timeout=
                    REQUEST_TIMEOUT

            )


        elapsed =time.perf_counter() - start


        response.raise_for_status()


        data =response.json()


        output =(
                data["choices"][0]
                ["message"]["content"]
            )


        # ----------------------------------------------------
        # UPDATE STATE
        # ----------------------------------------------------

        with state_lock:

            lfm_output = output

            lfm_elapsed =elapsed

            lfm_frame_name =image_path.name

            lfm_processed_count += 1

            lfm_error =None


        print(

            f"LFM | "
            f"{image_path.name} | "
            f"{elapsed:.3f} s | "
            f"{output}"

        )


        return True


    except Exception as e:

        with state_lock:

            lfm_error =str(e)

            lfm_output = (
                "LFM ERROR:\n"
                +
                str(e)
            )


        print(
            "LFM ERROR:",
            e
        )


        return False


# QUICK DECODE:
# This function takes the saved phone JPEG and sends that
# exact image to LFM.


# ============================================================
# SECTION 17 — LIVE LFM WORKER
# ============================================================

def lfm_worker():

    global lfm_model
    global lfm_running
    global last_processed_filename
    global lfm_output


    print()
    print("=" * 75)
    print("LIVE PHONE FRAME → LFM WORKER")
    print("=" * 75)
    print()


    # --------------------------------------------------------
    # WAIT FOR LLAMA-SERVER
    # --------------------------------------------------------

    while True:

        try:

            response = requests.get(

                    f"{BASE_URL}/models",

                    timeout=3

                )


            response.raise_for_status()


            lfm_model = response.json()[
                    "data"
                ][0][
                    "id"
                ]


            break


        except Exception as e:

            print(
                "Waiting for llama-server..."
            )

            time.sleep(2)


    print(
        f"MODEL : {lfm_model}"
    )

    print(
        f"SERVER: {BASE_URL}"
    )

    print()
    print(
        "Waiting for phone frames..."
    )
    print()


    while True:

        newest =get_newest_frame()


        if newest is None:

            time.sleep(
                0.05
            )

            continue


        # ----------------------------------------------------
        # LATEST-FRAME LOGIC
        # ----------------------------------------------------

        if (
            newest.name ==
            last_processed_filename
        ):

            time.sleep(
                0.05
            )

            continue


        # ----------------------------------------------------
        # CLAIM THIS FRAME
        # ----------------------------------------------------

        last_processed_filename = newest.name


        with state_lock:

            lfm_running = True

            # lfm_output ="Processing..."


        # ----------------------------------------------------
        # PROCESS
        # ----------------------------------------------------

        success = process_frame(
                newest
            )


        with state_lock:

            lfm_running =False


        # ----------------------------------------------------
        # DELETE PROCESSED FRAME
        # ----------------------------------------------------

        if success:

            try:

                newest.unlink()

            except FileNotFoundError:

                pass


        # ----------------------------------------------------
        # SMALL PAUSE
        # ----------------------------------------------------

        time.sleep(
            0.01
        )


# QUICK DECODE:
# This continuously watches captured_images.
#
# If a newer phone frame exists:
#
#     newest JPEG
#          ↓
#         LFM
#          ↓
#       result
#          ↓
#      delete JPEG
#
# This prevents an ever-growing processing backlog.


# ============================================================
# SECTION 18 — VERIFY CONFIGURATION
# ============================================================

print()
print("=" * 75)
print("DIVYACHAKSHU LIVE CAMERA SERVER")
print("=" * 75)
print()


if not PROMPT_FILE.exists():

    raise FileNotFoundError(

        "Prompt file not found:\n"
        +
        str(PROMPT_FILE)

    )


if not SSL_CERT.exists():

    raise FileNotFoundError(

        "mkcert certificate not found:\n"
        +
        str(SSL_CERT)

    )


if not SSL_KEY.exists():

    raise FileNotFoundError(

        "mkcert private key not found:\n"
        +
        str(SSL_KEY)

    )


print(
    "PHONE WEBPAGE:"
)

print(
    f"https://{TAILSCALE_IP}:{PORT}"
)

print()


print(
    "PHONE FRAME DIRECTORY:"
)

print(
    CAPTURE_DIR
)

print()


print(
    "LFM:"
)

print(
    "LIVE PHONE FRAMES"
)

print()


# ============================================================
# SECTION 19 — START LFM WORKER
# ============================================================

worker_thread = threading.Thread(

    target=lfm_worker,

    daemon=True

)

worker_thread.start()


# QUICK DECODE:
# Starts the live phone-frame → LFM pipeline in the background.


# ============================================================
# SECTION 20 — START UVICORN
# ============================================================

print(
    "Starting HTTPS Uvicorn..."
)

print()


uvicorn.run(

    app,

    host=HOST,

    port=PORT,

    ssl_keyfile=
        str(SSL_KEY),

    ssl_certfile=
        str(SSL_CERT)

)