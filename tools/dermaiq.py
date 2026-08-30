import os
import time
import requests

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# DERMIQ CONFIGURATION
# ============================================================

DERMIQ_API_KEY = os.getenv(
    "DERMIQ_API_KEY"
)

BASE_URL = "https://dev.dermiq.cloud"

ANALYZE_URL = (
    f"{BASE_URL}/v1/analyze"
)

RESULT_URL = (
    f"{BASE_URL}/v1/results"
)


# ============================================================
# VALIDATE API KEY
# ============================================================

def validate_api_key():

    if not DERMIQ_API_KEY:

        raise ValueError(
            "DERMIQ_API_KEY not found in .env"
        )


# ============================================================
# GET AUTH HEADERS
# ============================================================

def get_headers():

    validate_api_key()

    return {

        "Authorization":
            f"Bearer {DERMIQ_API_KEY}"

    }


# ============================================================
# CREATE ANALYSIS
# ============================================================

def create_dermiq_analysis(
    image_path
):

    validate_api_key()


    # --------------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------------

    if not os.path.exists(
        image_path
    ):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    # --------------------------------------------------------
    # PREPARE IMAGE
    # --------------------------------------------------------

    file_name = os.path.basename(
        image_path
    )


    print(
        "Sending image to DermIQ..."
    )


    headers = get_headers()


    # --------------------------------------------------------
    # MULTIPART UPLOAD
    # --------------------------------------------------------

    with open(
        image_path,
        "rb"
    ) as image_file:

        files = {

            "file": (

                file_name,

                image_file,

                "image/jpeg"

            )

        }


        response = requests.post(

            ANALYZE_URL,

            headers=headers,

            files=files,

            timeout=120

        )


    print(
        "DermIQ analysis status:",
        response.status_code
    )


    # --------------------------------------------------------
    # DISPLAY API ERROR
    # --------------------------------------------------------

    if response.status_code not in [
        200,
        202
    ]:

        print()
        print(
            "=" * 60
        )
        print(
            "DERMIQ API RESPONSE"
        )
        print(
            "=" * 60
        )

        print(
            response.text
        )

        print(
            "=" * 60
        )


    response.raise_for_status()


    # --------------------------------------------------------
    # PARSE RESPONSE
    # --------------------------------------------------------

    data = response.json()


    analysis_id = data.get(
        "analysis_id"
    )


    if not analysis_id:

        raise ValueError(
            "DermIQ analysis_id missing "
            "from response."
        )


    print(
        "DermIQ analysis created successfully."
    )


    print(
        "Analysis ID:",
        analysis_id
    )


    return analysis_id


# ============================================================
# GET ANALYSIS RESULT
# ============================================================

def get_dermiq_result(
    analysis_id
):

    headers = get_headers()


    url = (
        f"{RESULT_URL}/{analysis_id}"
    )


    # --------------------------------------------------------
    # POLLING
    # --------------------------------------------------------

    max_attempts = 30

    poll_interval = 2


    for attempt in range(
        max_attempts
    ):

        print(

            f"Checking DermIQ result "
            f"({attempt + 1}/{max_attempts})..."

        )


        response = requests.get(

            url,

            headers=headers,

            timeout=60

        )


        print(
            "DermIQ result status:",
            response.status_code
        )


        response.raise_for_status()


        data = response.json()


        status = data.get(
            "status"
        )


        print(
            "Analysis status:",
            status
        )


        # ----------------------------------------------------
        # COMPLETED
        # ----------------------------------------------------

        if status == "completed":

            return data


        # ----------------------------------------------------
        # FAILED
        # ----------------------------------------------------

        if status == "failed":

            raise RuntimeError(

                "DermIQ analysis failed: "

                + str(data)

            )


        # ----------------------------------------------------
        # CONTINUE POLLING
        # ----------------------------------------------------

        time.sleep(
            poll_interval
        )


    raise TimeoutError(
        "DermIQ analysis timed out."
    )


# ============================================================
# NORMALIZE METRIC
# ============================================================

def normalize_metric(
    metric_name,
    metric_data
):

    # --------------------------------------------------------
    # SIMPLE NUMERIC VALUE
    # --------------------------------------------------------

    if isinstance(
        metric_data,
        (int, float)
    ):

        return {

            "condition_id":
                metric_name,

            "condition_name":
                metric_name,

            "score":
                metric_data,

            "raw_score":
                metric_data,

            "region":
                "whole"

        }


    # --------------------------------------------------------
    # DICTIONARY
    # --------------------------------------------------------

    if isinstance(
        metric_data,
        dict
    ):

        # ----------------------------------------------------
        # DIRECT SCORE
        # ----------------------------------------------------

        if (
            "ui_score"
            in metric_data
        ):

            return {

                "condition_id":
                    metric_name,

                "condition_name":
                    metric_name,

                "score":
                    metric_data.get(
                        "ui_score"
                    ),

                "raw_score":
                    metric_data.get(
                        "raw_score"
                    ),

                "region":
                    "whole"

            }


        # ----------------------------------------------------
        # REGIONAL METRICS
        # ----------------------------------------------------

        results = []


        for region, value in metric_data.items():

            if not isinstance(
                value,
                dict
            ):

                continue


            if (
                "ui_score"
                not in value
            ):

                continue


            results.append({

                "condition_id":
                    metric_name,

                "condition_name":
                    metric_name,

                "score":
                    value.get(
                        "ui_score"
                    ),

                "raw_score":
                    value.get(
                        "raw_score"
                    ),

                "region":
                    region

            })


        return results


    return None


# ============================================================
# NORMALIZE DERMIQ RESULTS
# ============================================================

def normalize_dermiq_result(
    result
):

    result_json = result.get(
        "result_json",
        {}
    )


    findings = []


    metric_names = [

        "hd_acne",

        "hd_wrinkle",

        "hd_pore",

        "hd_redness",

        "hd_oiliness",

        "hd_texture",

        "hd_dark_circles",

        "hd_firmness"

    ]


    # --------------------------------------------------------
    # PROCESS SKIN METRICS
    # --------------------------------------------------------

    for metric_name in metric_names:

        if metric_name not in result_json:

            continue


        normalized = normalize_metric(

            metric_name,

            result_json[
                metric_name
            ]

        )


        if normalized is None:

            continue


        if isinstance(
            normalized,
            list
        ):

            findings.extend(
                normalized
            )

        else:

            findings.append(
                normalized
            )


    return findings


# ============================================================
# GET SKIN PROFILE
# ============================================================

def get_skin_profile(
    result
):

    result_json = result.get(
        "result_json",
        {}
    )


    skin_profile = {

        "skin_age":
            result.get(
                "skin_age"
            ),

        "skin_tone":
            result_json.get(
                "skin_tone",
                {}
            ),

        "skin_type":
            result_json.get(
                "skin_type",
                {}

            ),

        "face_shape":
            result_json.get(
                "faceshape"
            )

    }


    return skin_profile


# ============================================================
# ANALYZE WITH DERMIQ
# ============================================================

def analyze_with_dermaiq(
    image_path
):

    try:

        # ----------------------------------------------------
        # 1. CREATE ANALYSIS
        # ----------------------------------------------------

        analysis_id = (
            create_dermiq_analysis(
                image_path
            )
        )


        # ----------------------------------------------------
        # 2. GET RESULT
        # ----------------------------------------------------

        result = (
            get_dermiq_result(
                analysis_id
            )
        )


        # ----------------------------------------------------
        # 3. NORMALIZE FINDINGS
        # ----------------------------------------------------

        findings = (
            normalize_dermiq_result(
                result
            )
        )


        # ----------------------------------------------------
        # 4. OVERALL SCORE
        # ----------------------------------------------------

        overall_score = result.get(
            "overall_score"
        )


        # ----------------------------------------------------
        # 5. SKIN AGE
        # ----------------------------------------------------

        skin_age = result.get(
            "skin_age"
        )


        # ----------------------------------------------------
        # 6. SKIN PROFILE
        # ----------------------------------------------------

        skin_profile = (
            get_skin_profile(
                result
            )
        )


        skin_profile[
            "skin_age"
        ] = skin_age


        # ----------------------------------------------------
        # 7. SUCCESSFUL RESULT
        # ----------------------------------------------------

        return {

            "tool":
                "DermIQ",

            "success":
                True,

            "overall_skin_score":
                overall_score,

            "skin_profile":
                skin_profile,

            "image_quality":
                {},

            "findings":
                findings,

            "suggestions":
                [],

            "analysis_id":
                analysis_id,

            "raw_result":
                result

        }


    except Exception as e:

        print(
            "DermIQ error:",
            str(e)
        )


        return {

            "tool":
                "DermIQ",

            "success":
                False,

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