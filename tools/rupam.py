
import os
import io
import requests

from PIL import Image
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# RUPAM CONFIGURATION
# ============================================================

RUPAM_API_KEY = os.getenv("RUPAM_API_KEY")

BASE_URL = "https://xidomain.com/rupam/v1"

TOKEN_URL = f"{BASE_URL}/auth/token"
ANALYZE_URL = f"{BASE_URL}/analyze"


# ============================================================
# GET RUPAM ACCESS TOKEN
# ============================================================

def get_rupam_token():

    if not RUPAM_API_KEY:
        raise ValueError(
            "RUPAM_API_KEY not found in .env"
        )

    headers = {
        "Authorization": f"Bearer {RUPAM_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        TOKEN_URL,
        headers=headers,
        timeout=30
    )

    print(
        "Rupam token status:",
        response.status_code
    )

    response.raise_for_status()

    data = response.json()

    token = data.get("access_token")

    if not token:
        raise ValueError(
            "Access token missing from Rupam response."
        )

    print(
        "Rupam token obtained successfully."
    )

    return token


# ============================================================
# PREPARE IMAGE
# ============================================================

def prepare_jpeg(image_path):

    image = Image.open(image_path)

    print(
        "Original image:",
        image.format,
        image.mode,
        image.size
    )

    # Convert to RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=95
    )

    buffer.seek(0)

    return buffer


# ============================================================
# NORMALIZE RUPAM CONDITIONS
# ============================================================

def normalize_conditions(conditions):

    normalized = []

    for condition in conditions:

        normalized.append({

            "condition_id":
                condition.get(
                    "condition_id"
                ),

            "condition_name":
                condition.get(
                    "condition_name"
                ),

            "severity":
                condition.get(
                    "severity"
                ),

            "score":
                condition.get(
                    "score"
                ),

            "grade":
                condition.get(
                    "grade"
                ),

            "confidence":
                condition.get(
                    "confidence"
                ),

            "detection_count":
                condition.get(
                    "detection_count"
                ),

            "suggestions_key":
                condition.get(
                    "suggestions_key"
                )

        })

    return normalized


# ============================================================
# ANALYZE WITH RUPAM
# ============================================================

def analyze_with_rupam(image_path):

    try:

        # ----------------------------------------------------
        # GET TOKEN
        # ----------------------------------------------------

        token = get_rupam_token()

        # ----------------------------------------------------
        # PREPARE IMAGE
        # ----------------------------------------------------

        image_buffer = prepare_jpeg(
            image_path
        )

        # ----------------------------------------------------
        # AUTHORIZATION
        # ----------------------------------------------------

        headers = {
            "Authorization":
                f"Bearer {token}"
        }

        # ----------------------------------------------------
        # MULTIPART IMAGE
        # ----------------------------------------------------

        files = {

            "image": (

                "skin_image.jpg",

                image_buffer,

                "image/jpeg"

            )

        }

        print(
            "Sending image to Rupam..."
        )

        # ----------------------------------------------------
        # API REQUEST
        # ----------------------------------------------------

        response = requests.post(

            ANALYZE_URL,

            headers=headers,

            files=files,

            timeout=60

        )

        print(
            "Rupam analysis status:",
            response.status_code
        )

        response.raise_for_status()

        # ----------------------------------------------------
        # JSON RESPONSE
        # ----------------------------------------------------

        result = response.json()

        # ----------------------------------------------------
        # GET CONDITIONS
        # ----------------------------------------------------

        conditions = result.get(
            "conditions",
            []
        )

        # ----------------------------------------------------
        # NORMALIZE CONDITIONS
        # ----------------------------------------------------

        findings = normalize_conditions(
            conditions
        )

        # ----------------------------------------------------
        # OVERALL SCORE
        # ----------------------------------------------------

        overall_score = result.get(
            "overall_skin_health_score"
        )

        # ----------------------------------------------------
        # IMAGE QUALITY
        # ----------------------------------------------------

        image_quality = result.get(
            "image_quality",
            {}
        )

        # ----------------------------------------------------
        # SKIN PROFILE
        # ----------------------------------------------------

        skin_profile = result.get(
            "skin_profile",
            {}
        )

        # ----------------------------------------------------
        # SUGGESTIONS
        # ----------------------------------------------------

        # ----------------------------------------------------
# SUGGESTIONS
# ----------------------------------------------------

        raw_suggestions = result.get(
            "suggestions",
            []
        )

        suggestions = []

        for suggestion in raw_suggestions:

            suggestions.append({

                "condition_id":
                    suggestion.get("condition_id"),

                "severity":
                    suggestion.get("severity_tier"),

                "category":
                    suggestion.get("category"),

                "priority":
                    suggestion.get("priority"),

                "text":
                    suggestion.get("text")

            })

        # ----------------------------------------------------
        # SUCCESSFUL RESULT
        # ----------------------------------------------------

        return {

            "tool": "Rupam.ai",

            "success": True,

            "overall_skin_score":
                overall_score,

            "skin_profile":
                skin_profile,

            "image_quality":
                image_quality,

            "findings":
                findings,

            "suggestions":
                suggestions

        }

    except Exception as e:

        print(
            "Rupam error:",
            str(e)
        )

        return {

            "tool": "Rupam.ai",

            "success": False,

            "overall_skin_score":
                None,

            "skin_profile":
                {},

            "image_quality":
                {},

            "findings":
                [],

            "suggestions":
                [],

            "error":
                str(e)

        }
