import streamlit as st
from env.environment import EmailEnv

st.set_page_config(page_title="Email AI", layout="wide")

if "env" not in st.session_state:
    st.session_state.env = EmailEnv("easy")
    st.session_state.history = []

st.title("Email Smart Triage")
st.caption("Paste an email and get auto-detected category (education/promotions/spam/personal/urgent/work/finance/security/other) + main subject.")

with st.expander("Category Legend", expanded=False):
    st.markdown("- **education**: Course, training, academy, student, or faculty-related emails.")
    st.markdown("- **promotions**: Legitimate marketing offers, discounts, sales, and newsletters.")
    st.markdown("- **spam**: Scam-like or suspicious mass messages (lottery/prize/fraud patterns).")
    st.markdown("- **personal**: Family, friends, social plans, and casual personal communication.")
    st.markdown("- **urgent**: Time-critical requests requiring immediate attention.")
    st.markdown("- **work**: Professional collaboration, meetings, project updates, and office tasks.")
    st.markdown("- **finance**: Billing, invoice, payment, payroll, and transaction-related emails.")
    st.markdown("- **security**: Account safety, login alerts, OTP, verification, and access issues.")
    st.markdown("- **other**: Messages that do not strongly match any category.")

default_email = """Subject: URGENT - Project deadline moved to tomorrow

Hi team,
Client requested the updated report by tomorrow 10 AM. Please share your section tonight.
Thanks,
Manager"""

email_text = st.text_area(
    "Paste full email text",
    value=default_email,
    height=240,
    placeholder="Include Subject: line if available for better subject extraction.",
)

if st.button("Analyze Email"):
    if not email_text.strip():
        st.warning("Please paste an email before analyzing.")
    else:
        analysis = st.session_state.env.analyze_text(email_text)

        col1, col2, col3 = st.columns(3)
        col1.metric("Detected Category", analysis.category.upper())
        col2.metric("Main Subject", analysis.main_subject)
        col3.metric("Confidence", f"{int(analysis.confidence * 100)}%")

        st.info(analysis.reason)

        st.session_state.history.append(
            {
                "preview": email_text[:70].replace("\n", " ") + ("..." if len(email_text) > 70 else ""),
                "category": analysis.category,
                "subject": analysis.main_subject,
                "confidence": analysis.confidence,
            }
        )

st.markdown("---")
st.subheader("Recent Analyses")

if not st.session_state.history:
    st.write("No analyses yet.")
else:
    for item in st.session_state.history[::-1]:
        st.write(
            f"{item['preview']} -> {item['category']} | {item['subject']} | "
            f"{int(item['confidence'] * 100)}%"
        )