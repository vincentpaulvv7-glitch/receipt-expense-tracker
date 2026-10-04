import streamlit as st
import re

from google import genai
from google.genai import types


# ==============================
# GEMINI SETUP
# ==============================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)


# ==============================
# PAGE CONFIGURATION
# ==============================

st.set_page_config(
    page_title="Receipt & Expense Tracker",
    page_icon="🧾",
    layout="centered"
)


# ==============================
# TITLE
# ==============================

st.title("🧾 Receipt & Expense Tracker")

st.write(
    "Upload a receipt and Gemini will extract "
    "the items, prices, and total amount."
)


# ==============================
# SESSION STATE
# ==============================

if "receipt_text" not in st.session_state:
    st.session_state.receipt_text = None

if "total" not in st.session_state:
    st.session_state.total = None

if "share" not in st.session_state:
    st.session_state.share = None

if "people" not in st.session_state:
    st.session_state.people = None


# ==============================
# UPLOAD RECEIPT
# ==============================

uploaded_file = st.file_uploader(
    "📸 Upload your receipt",
    type=["jpg", "jpeg", "png"]
)


# ==============================
# SHOW RECEIPT IMAGE
# ==============================

if uploaded_file:

    st.image(
        uploaded_file,
        caption="Uploaded Receipt",
        width=400
    )


# ==============================
# ANALYZE RECEIPT
# ==============================

if uploaded_file:

    if st.button("🔍 Analyze Receipt"):

        with st.spinner(
            "🤖 Gemini is analyzing your receipt..."
        ):

            try:

                photo_bytes = uploaded_file.getvalue()

                response = client.models.generate_content(

                    model="gemini-3.8-flash",

                    contents=[

                        types.Part.from_bytes(
                            data=photo_bytes,
                            mime_type=uploaded_file.type
                        ),

                        """
                        Analyze this receipt carefully.

                        Extract the following:

                        1. Store name
                        2. Every item and its price
                        3. Total amount

                        Present the result clearly.

                        At the very end, write the total
                        in exactly this format:

                        TOTAL: 123.45

                        Do not include ₹ or any other symbol
                        after TOTAL.
                        """
                    ]
                )

                # Save Gemini response
                st.session_state.receipt_text = response.text

                # Extract total amount
                match = re.search(
                    r"TOTAL:\s*([0-9]+(?:\.[0-9]+)?)",
                    response.text
                )

                if match:

                    st.session_state.total = float(
                        match.group(1)
                    )

                else:

                    st.session_state.total = None

                    st.warning(
                        "⚠️ Total amount could not be detected."
                    )

            except Exception as e:

                st.error(
                    "❌ Something went wrong while "
                    "analyzing the receipt."
                )

                st.error(str(e))


# ==============================
# DISPLAY RECEIPT DETAILS
# ==============================

if st.session_state.receipt_text:

    st.subheader("🧾 Receipt Details")

    st.write(
        st.session_state.receipt_text
    )


# ==============================
# DISPLAY TOTAL
# ==============================

if st.session_state.total is not None:

    total = st.session_state.total

    st.success(
        f"💰 Total Amount: ₹{total:.2f}"
    )


    # ==============================
    # BILL SPLITTING
    # ==============================

    st.subheader("👥 Split the Bill")

    people = st.number_input(
        "How many people?",
        min_value=1,
        max_value=20,
        value=2,
        step=1
    )


    if st.button("💰 Calculate Split"):

        share = total / people

        st.session_state.share = share
        st.session_state.people = people


    # ==============================
    # SHOW SPLIT RESULT
    # ==============================

    if st.session_state.share is not None:

        st.success(
            f"Each person should pay "
            f"₹{st.session_state.share:.2f}"
        )


        # ==============================
        # EXPENSE SUMMARY
        # ==============================

        st.subheader("📄 Expense Summary")

        summary = f"""
RECEIPT & EXPENSE SUMMARY
=========================

Total Amount: ₹{total:.2f}

Number of People: {st.session_state.people}

Each Person Pays: ₹{st.session_state.share:.2f}

Thank you!
"""


        st.text_area(
            "Summary",
            summary,
            height=250
        )


        # ==============================
        # DOWNLOAD SUMMARY
        # ==============================

        st.download_button(

            label="📥 Download Expense Summary",

            data=summary,

            file_name="expense_summary.txt",

            mime="text/plain"
        )


# ==============================
# FOOTER
# ==============================

st.divider()

st.caption(
    "🤖 Powered by Gemini Vision + Streamlit"
)

    