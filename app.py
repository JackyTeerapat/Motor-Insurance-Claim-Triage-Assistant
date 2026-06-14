import os
from datetime import datetime
from unittest import result
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


POLICY_RULES = """
=== MOTOR INSURANCE POLICY RULES ===

1. COVERED EVENTS
The policy covers:
- Accidental collision
- Theft
- Fire
- Flood
- Third-party property damage

2. EXCLUSIONS
The policy does NOT cover:
- Driving under influence of alcohol or drugs
- Illegal racing
- Intentional damage
- Vehicle used outside permitted geographic area
- Claim filed more than 30 days after incident without valid reason

3. REQUIRED DOCUMENTS

For ALL claims:
- Claim form
- Driving license
- Vehicle registration
- Photos of damage
- Incident report

For THEFT claims only (additional):
- Police report

For THIRD-PARTY DAMAGE only (additional):
- Third-party contact information and evidence

4. ROUTING RULES
- Standard processing : covered event + complete docs + no risk flags
- Manual review       : unclear coverage / incomplete docs / conflicting info
- Fraud review        : suspicious pattern / repeated claims / weak evidence
- Rejection review    : clear exclusion applies
=== END OF POLICY RULES ===
"""
SYSTEM_PROMPT = f"""
You are a Motor Insurance Claim Triage Assistant.

Your role is to SUPPORT human claim officers only.
You do NOT make final decisions on claims.

=== POLICY RULES ===
{POLICY_RULES}
=== END OF POLICY RULES ===

GUARDRAILS:
- If information is missing or unclear, say "Cannot determine" — do NOT guess
- If confidence is Low and NO fraud signal detected,recommend Manual review
- Never approve, reject, or calculate payment amounts
- Base your assessment ONLY on the policy rules provided above
- If ANY fraud signal is detected:
  → Set Initial Coverage Assessment to "Cannot determine"
  → Set Confidence Level to "Low"
  → Set Recommended Routing to "Fraud review"
- If ANY exclusion risk applies but cannot be fully confirmed:
  → Set Initial Coverage Assessment to "Cannot determine"
  → Set Confidence Level to "Medium"


INSTRUCTIONS:
Before checking required documents, you must:
1. Identify the claim type from the description:
   - If another vehicle or third party is involved → third-party damage
   - If vehicle is missing/stolen → theft
   - Otherwise → collision / fire / flood
2. Then check required documents based on that claim type
3. Flag any documents missing for that specific claim type
4. Check for fraud signals — flag as Fraud review if ANY of these appear:
   - Customer has submitted more than 3 claims within 12 months
   - Damage described as severe but evidence is weak or unclear
   - Inconsistent or conflicting information in the description
   - Story or timeline does not match submitted documents

OUTPUT FORMAT (follow exactly):
Claim Summary: [2-3 sentences]
Initial Coverage Assessment: [Likely covered / Possibly covered / Not covered / Cannot determine]
Missing Information: [list items or write "None"]
Risk Flags: [list items or write "None"]
Recommended Routing: [Standard processing / Manual review / Fraud review / Rejection review]
Reasoning: [explain clearly why]
Confidence Level: [High / Medium / Low]
"""


from datetime import datetime
def analyze_claim(claim: dict) -> str:
    
    incident  = datetime.strptime(claim['incident_date'],  "%Y-%m-%d")
    submitted = datetime.strptime(claim['submitted_date'], "%Y-%m-%d")
    days_diff = (submitted - incident).days

    user_prompt = f"""
    Please analyze this insurance claim:

    Claim ID       : {claim['claim_id']}
    Customer       : {claim['customer']}
    Vehicle        : {claim['vehicle']}
    Incident Date  : {claim['incident_date']}
    Submitted Date : {claim['submitted_date']}
    Days between incident and submission: {days_diff} days
    Description    : {claim['description']}
    Documents      : {claim['documents']}
    Claim History  : {claim['claim_history']}
    """

    response = client.chat.completions.create(
        model       = "gpt-4o-mini",
        messages    = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ],
        temperature = 0.0,
        max_tokens  = 1000,
    )

    # print(repr(response.choices[0].message.content))
    return response.choices[0].message.content

def parse_result(result: str) -> dict:
    fields = {
        "Claim Summary"                : "",
        "Initial Coverage Assessment"  : "",
        "Missing Information"          : "",
        "Risk Flags"                   : "",
        "Recommended Routing"          : "",
        "Reasoning"                    : "",
        "Confidence Level"             : ""
    }

    current_field = None

    for line in result.split("\n"):
        for field in fields:
            if line.startswith(field + ":"):
                current_field = field
                fields[field] = line[len(field)+1:].strip()
                break
        else:
            if current_field:
                fields[current_field] += " " + line.strip()

    return fields

st.title("Motor Insurance Claim Triage Assistant")
st.markdown("---")


st.subheader("Claim Information")

claim_id       = st.text_input("Claim ID", "CLM-001")
customer       = st.text_input("Customer", "Customer A")
vehicle        = st.text_input("Vehicle", "Honda Civic 2022")
incident_date  = st.text_input("Incident Date", "2026-05-01")
submitted_date = st.text_input("Submitted Date", "2026-05-05")
description = st.text_area("Claim Description","My parked vehicle was hit by another car at a shopping mall parking lot",height=120)
documents = st.text_area("Documents Submitted","Claim form, vehicle registration, photos of damage",height=80)
claim_history  = st.text_input("Claim History", "No prior claims")

analyze_button = st.button("Analyze Claim")

st.subheader("Result :")
if analyze_button:

    # Validation — เช็คก่อนว่ากรอกครบไหม
    errors = []

    if not claim_id:
        errors.append("Claim ID")
    if not customer:
        errors.append("Customer")
    if not vehicle:
        errors.append("Vehicle")
    if not incident_date:
        errors.append("Incident Date")
    if not submitted_date:
        errors.append("Submitted Date")
    if not description:
        errors.append("Claim Description")
    if not documents:
        errors.append("Documents Submitted")

    if errors:
        st.error(f"Please fill in: {', '.join(errors)}")

    else:
        claim = {
            "claim_id"       : claim_id,
            "customer"       : customer,
            "vehicle"        : vehicle,
            "incident_date"  : incident_date,
            "submitted_date" : submitted_date,
            "description"    : description,
            "documents"      : documents,
            "claim_history"  : claim_history
        }

        with st.spinner("Analyzing claim..."):
            result = analyze_claim(claim)
            parsed = parse_result(result)

        # แสดงผลเหมือนเดิม
        st.markdown("### Claim Summary")
        st.write(parsed["Claim Summary"])
        st.markdown("---")

        st.markdown("### Initial Coverage Assessment")
        st.write(parsed["Initial Coverage Assessment"])
        st.markdown("---")

        st.markdown("### Missing Information")
        st.write(parsed["Missing Information"])
        st.markdown("---")

        st.markdown("### Risk Flags")
        st.write(parsed["Risk Flags"])
        st.markdown("---")

        st.markdown("### Recommended Routing")
        st.write(parsed["Recommended Routing"])
        st.markdown("---")

        st.markdown("### Reasoning")
        st.write(parsed["Reasoning"])
        st.markdown("---")

        st.markdown("### Confidence Level")
        st.write(parsed["Confidence Level"])

else:
    st.info("Fill in the claim details and click Analyze")