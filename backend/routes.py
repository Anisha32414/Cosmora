import os

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from rag.skin_rag import skin_rag
from rag.hair_rag import hair_rag
from agents.skin_agent import run_skin_agent


api = Blueprint("api", __name__)


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)


# ============================================================
# ALLOWED IMAGE EXTENSIONS
# ============================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# FRONTEND PAGES
# ============================================================

# Home page
@api.route("/", methods=["GET"])
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# Skin questionnaire page
@api.route("/skin/questionnaire", methods=["GET"])
def skin_questionnaire_page():

    return send_from_directory(
        FRONTEND_DIR,
        "skin-questionnaire.html"
    )


# Hair questionnaire page
@api.route("/hair/questionnaire", methods=["GET"])
def hair_questionnaire_page():

    return send_from_directory(
        FRONTEND_DIR,
        "hair-questionnaire.html"
    )


# Face image analysis page
@api.route("/skin-analysis", methods=["GET"])
def skin_analysis_page():

    return send_from_directory(
        FRONTEND_DIR,
        "skin-analysis.html"
    )


# ============================================================
# SKIN QUESTIONNAIRE API
# ============================================================

@api.route(
    "/skin/questionnaire",
    methods=["POST"]
)
def skin_questionnaire():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No questionnaire data received."

            }), 400


        # ----------------------------------------------------
        # Convert questionnaire answers into user profile
        # ----------------------------------------------------

        user_profile = {

            "face_washing":
                data.get("face_washing", ""),

            "diet":
                data.get("diet", ""),

            "sunscreen":
                data.get("sunscreen", ""),

            "cosmetics":
                data.get("cosmetics", ""),

            "water_intake":
                data.get("water_intake", ""),

            "sun_exposure":
                data.get("sun_exposure", ""),

            "sleep":
                data.get("sleep", ""),

            "stress":
                data.get("stress", ""),

            "skin_concerns":
                data.get("skin_concerns", "")
        }


        # ----------------------------------------------------
        # Skin RAG + LLM
        # ----------------------------------------------------

        response = skin_rag(
            user_profile
        )


        return jsonify({

            "success": True,

            "type":
                "skin_questionnaire",

            "response":
                response

        })


    except Exception as e:

        print(
            "Skin questionnaire error:",
            e
        )


        return jsonify({

            "success": False,

            "error":
                "Unable to generate skincare guidance."

        }), 500


# ============================================================
# HAIR QUESTIONNAIRE API
# ============================================================

@api.route(
    "/hair/questionnaire",
    methods=["POST"]
)
def hair_questionnaire():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No questionnaire data received."

            }), 400


        # ----------------------------------------------------
        # Convert questionnaire answers into user profile
        # ----------------------------------------------------

        user_profile = {

            "hair_washing":
                data.get("hair_washing", ""),

            "shampoo":
                data.get("shampoo", ""),

            "conditioner":
                data.get("conditioner", ""),

            "oiling":
                data.get("oiling", ""),

            "pollution":
                data.get("pollution", ""),

            "hair_treatments":
                data.get("hair_treatments", ""),

            "heat_styling":
                data.get("heat_styling", ""),

            "pillow_cover":
                data.get("pillow_cover", ""),

            "diet":
                data.get("diet", ""),

            "hydration":
                data.get("hydration", ""),

            "sleep":
                data.get("sleep", ""),

            "stress":
                data.get("stress", ""),

            "hair_problems":
                data.get("hair_problems", "")
        }


        # ----------------------------------------------------
        # Hair RAG + LLM
        # ----------------------------------------------------

        response = hair_rag(
            user_profile
        )


        return jsonify({

            "success": True,

            "type":
                "hair_questionnaire",

            "response":
                response

        })


    except Exception as e:

        print(
            "Hair questionnaire error:",
            e
        )


        return jsonify({

            "success": False,

            "error":
                "Unable to generate haircare guidance."

        }), 500


# ============================================================
# SKIN FACE IMAGE ANALYSIS API
# ============================================================

@api.route(
    "/skin-analysis",
    methods=["POST"]
)
def analyze_face():

    try:

        # ====================================================
        # 1. CHECK IMAGE
        # ====================================================

        if "image" not in request.files:

            return jsonify({

                "success": False,

                "error":
                    "No image uploaded."

            }), 400


        image = request.files["image"]


        # ====================================================
        # 2. CHECK FILENAME
        # ====================================================

        if image.filename == "":

            return jsonify({

                "success": False,

                "error":
                    "Please select an image."

            }), 400


        # ====================================================
        # 3. CHECK IMAGE FORMAT
        # ====================================================

        if not allowed_file(
            image.filename
        ):

            return jsonify({

                "success": False,

                "error":
                    (
                        "Invalid image format. "
                        "Please upload JPG, JPEG, PNG or WEBP."
                    )

            }), 400


        # ====================================================
        # 4. GET USER CONCERN
        # ====================================================

        concern = request.form.get(
            "concern",
            "General skin concern"
        )


        # ====================================================
        # 5. CREATE UPLOAD DIRECTORY
        # ====================================================

        os.makedirs(
            UPLOAD_FOLDER,
            exist_ok=True
        )


        # ====================================================
        # 6. CREATE SECURE FILENAME
        # ====================================================

        filename = secure_filename(
            image.filename
        )


        image_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )


        # ====================================================
        # 7. SAVE IMAGE
        # ====================================================

        image.save(
            image_path
        )


        print(
            f"Image uploaded successfully: {image_path}"
        )


        # ====================================================
        # 8. RUN SKIN ANALYSIS AGENT
        # ====================================================

        assessment = run_skin_agent(

            image_path=image_path,

            user_concern=concern

        )


        # ====================================================
        # 9. RETURN COMPLETE DASHBOARD DATA
        # ====================================================

                # ========================================================
        # RETURN COMPLETE DASHBOARD DATA TO FRONTEND
        # ========================================================

        return jsonify({

            "success":
                assessment.get(
                    "success",
                    False
                ),

            "type":
                "skin_face_analysis",

            # ====================================================
            # USER INFORMATION
            # ====================================================

            "user_concern":
                assessment.get(
                    "user_concern",
                    concern
                ),

            # ====================================================
            # OVERALL SCORE
            # ====================================================

            "overall_skin_score":
                assessment.get(
                    "overall_skin_score"
                ),

            # ====================================================
            # INDIVIDUAL AI TOOL RESULTS
            # ====================================================

            "rupam":
                assessment.get(
                    "rupam",
                    {}
                ),

            "dermaiq":
                assessment.get(
                    "dermaiq",
                    {}
                ),

            "tool_results":
                assessment.get(
                    "tool_results",
                    []
                ),

            # ====================================================
            # COMBINED ANALYSIS
            # ====================================================

            "combined_findings":
                assessment.get(
                    "combined_findings",
                    []
                ),

            "common_concerns":
                assessment.get(
                    "common_concerns",
                    []
                ),

            "finding_summary":
                assessment.get(
                    "finding_summary",
                    []
                ),

            # ====================================================
            # RAG + LLM
            # ====================================================

            "rag_guidance":
                assessment.get(
                    "rag_guidance",
                    ""
                ),

            "final_guidance":
                assessment.get(
                    "final_guidance",
                    ""
                ),

            "final_assessment":
                assessment.get(
                    "final_assessment",
                    ""
                ),

            # ====================================================
            # STRUCTURED RAG SECTIONS
            # ====================================================

            "rag_sections":
                assessment.get(
                    "rag_sections",
                    {}
                ),

            # ====================================================
            # COMPLETE DASHBOARD OBJECT
            # ====================================================

            "dashboard_data":
                assessment.get(
                    "dashboard_data",
                    {}
                )

        })


    except Exception as e:

        print(
            "Face analysis error:",
            e
        )


        return jsonify({

            "success": False,

            "error":
                "Unable to analyze the uploaded image."

        }), 500