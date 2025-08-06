import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import requests

# --- Configuration ---
# It is highly recommended to use Streamlit Secrets to store your API key in production
os.environ['GOOGLE_API_KEY'] = ""
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


# --- All Agent and Helper Functions ---

def get_gemini_model():
    return genai.GenerativeModel('gemini-1.5-flash-latest')


def classifier_agent_process(model, image):
    prompt = "You are a Classifier Agent. Classify the waste in this image as 'biodegradable', 'non-biodegradable', 'mixed', or 'e-waste'. Give a one-sentence reason."
    response = model.generate_content([prompt, image])
    return response.text


def parse_classification(response_text):
    response_lower = response_text.lower()
    if 'e-waste' in response_lower or 'electronic' in response_lower:
        return 'e-waste'
    if 'mixed' in response_lower:
        return 'mixed'
    if 'biodegradable' in response_lower:
        return 'biodegradable'
    if 'non-biodegradable' in response_lower or 'non biodegradable' in response_lower:
        return 'non-biodegradable'
    return 'unknown'


def component_identification_agent(model, image, waste_type):
    st.info(f"Component Identification Agent is analyzing the {waste_type} waste...")
    prompt = f"You are a Component Identification Agent. Look at this image of {waste_type} waste. List the specific items you see as a simple bulleted list."
    with st.spinner("Identifying components..."):
        response = model.generate_content([prompt, image])
    return response.text


def separator_agent_process(model, image):
    prompt = "You are a specialized Separator Agent. Identify each distinct item in this image. Provide a count for each category you find (e.g., '- 2 Plastic bottles', '- 1 Apple core')."
    response = model.generate_content([prompt, image])
    return response.text


def parse_separator_report(report_text):
    components = {'biodegradable': 0, 'non-biodegradable': 0, 'e-waste': 0}
    lines = report_text.strip().split('\n')
    total_items = 0
    for line in lines:
        line_lower = line.lower()
        count_match = re.search(r'\d+', line_lower)
        count = int(count_match.group(0)) if count_match else 1
        total_items += count
        if any(kw in line_lower for kw in ['food', 'apple', 'peel', 'organic', 'paper']):
            components['biodegradable'] += count
        elif any(kw in line_lower for kw in ['plastic', 'bottle', 'can', 'metal', 'glass', 'wrapper']):
            components['non-biodegradable'] += count
        elif any(kw in line_lower for kw in ['electronic', 'battery', 'cable', 'phone', 'wire']):
            components['e-waste'] += count
    active_components = {k: v for k, v in components.items() if v > 0}
    if not active_components:
        return {}, None, 0
    major_category = max(active_components, key=active_components.get)
    return active_components, major_category, total_items


def count_items_from_report(report_text):
    return len(report_text.strip().split('\n'))


def calculate_honor_score(item_count, waste_type):
    points_mapping = {'e-waste': 25, 'non-biodegradable': 15, 'biodegradable': 10}
    return item_count * points_mapping.get(waste_type, 5)


# --- (UPDATED) Function to display full treatment protocols ---
def display_treatment_protocol(waste_type):
    st.subheader("B. Automated Treatment Protocol")
    if waste_type == 'biodegradable':
        st.markdown("""
            **1. Mechanical Shredding:** Waste is first shredded into smaller, uniform pieces. This increases the surface area, allowing microorganisms to break down the material much faster.

            **2. Anaerobic Digestion:** The shredded material is moved into an oxygen-free digester tank. Here, microorganisms consume the organic matter, producing valuable biogas for energy and a nutrient-rich solid called digestate.

            **3. Curing and Maturation:** The digestate is moved to curing piles where it matures over several weeks. This final aerobic phase stabilizes the material, eliminating pathogens and resulting in high-quality, safe-to-use compost.
        """)
    elif waste_type == 'non-biodegradable':
        st.markdown("""
            **1. AI-Powered Optical Sorting:** Waste travels on high-speed conveyors under advanced cameras. AI identifies the unique spectral signature of different materials, and precision air jets instantly sort them into pure streams.

            **2. Cleaning and Granulation:** Each sorted material stream is thoroughly washed to remove contaminants. It is then fed into a granulator that shreds the clean material into small, uniform flakes.

            **3. Extrusion and Pelletizing:** The dried flakes are melted and forced through an extruder, which forms long strands of molten material. These strands are then cooled and chopped into small pellets, the standard raw material format for manufacturing.
        """)
    elif waste_type == 'e-waste':
        st.warning("**CRITICAL:** E-waste contains toxic heavy metals like lead and mercury.")
        st.markdown("""
            **1. Robotic Dismantling:** Automated arms with computer vision precisely remove high-risk components like batteries and circuit boards to prevent contamination.

            **2. Secure Shredding:** The remaining components are shredded in an enclosed environment to capture and filter any hazardous dust released during the process.

            **3. Material Separation:** The shredded fragments pass through powerful magnets and eddy currents, which effectively separate ferrous metals, non-ferrous metals, and plastics into distinct streams.

            **4. Precious Metal Recovery:** The separated circuit boards undergo a specialized hydrometallurgical process to safely extract and refine valuable metals like gold, silver, and platinum for reuse.
        """)


# --- (UPDATED) Simplified function to post data to Relay App ---
def send_to_relay_app(user_email, waste_type, honor_score):
    relay_url = "https://hook.relay.app/api/v1/playbook/cme06lc810l0f0plz46vv7v4x/trigger/D4LqC6ILqJ7H71IZ-3oWTQ"

    email_subject = f"Your {waste_type.replace('_', ' ').title()} Waste Has Been Successfully Treated!"
    email_body = f"Dear User,\n\nThis is to confirm that the waste you submitted has been fully processed. For your contribution, you have been awarded {honor_score} Honor Points.\n\nThank you."

    payload = {
        "email_to": user_email,
        "honor_score": honor_score,
        "waste_type": waste_type
    }

    try:
        with st.spinner("Sending confirmation..."):
            response = requests.post(relay_url, json=payload, timeout=10)

        if response.status_code in [200, 201]:
            st.success("✅ Process confirmation sent successfully.")
        else:
            st.error(f"❌ Confirmation could not be sent (Status: {response.status_code}).")

    except requests.exceptions.RequestException:
        st.error("❌ Connection Error: Could not connect to the confirmation service.")


# --- Main Treatment Process Function ---
def run_treatment_process(model, image, waste_type, user_email):
    st.subheader("A. Component Identification")
    component_report = component_identification_agent(model, image, waste_type)
    st.markdown(component_report)

    item_count = count_items_from_report(component_report)
    honor_score = calculate_honor_score(item_count, waste_type)

    display_treatment_protocol(waste_type)

    st.success(f"**PROCESS COMPLETE:** {waste_type.replace('_', ' ').title()} waste fully treated.")
    st.markdown("---")

    send_to_relay_app(user_email, waste_type, honor_score)


# --- Streamlit App Interface ---
st.set_page_config(page_title="Multi-Agent Waste AI", page_icon="♻️")
st.title("♻️ Automated Multi-Agent Waste Processing System")
st.write("Upload an image of waste to simulate the automated treatment workflow.")

user_email = st.text_input("Enter Your Email Address for Confirmation")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Initiate Automated Treatment"):
        if user_email:
            model = get_gemini_model()

            with st.spinner("Classifier Agent is analyzing the image..."):
                classifier_response = classifier_agent_process(model, image)
                category = parse_classification(classifier_response)

            st.header("1. Classifier Agent Report")
            st.write(f"**Determined Category:** `{category.upper()}`")
            st.markdown("---")

            st.header("2. Automated Treatment Workflow")

            if category in ['biodegradable', 'non-biodegradable', 'e-waste']:
                run_treatment_process(model, image, category, user_email)

            elif category == 'mixed':
                st.warning("🟡 Classifier identified MIXED waste. Routing to Separator Agent...")
                with st.spinner("Separator Agent is performing detailed analysis..."):
                    separator_report = separator_agent_process(model, image)

                st.subheader("A. Separator Agent Report")
                st.markdown(separator_report)

                components, major_category, total_items = parse_separator_report(separator_report)

                if not components:
                    st.error("Separator Agent could not identify specific items to route.")
                else:
                    st.subheader("B. Routing Plan")
                    for comp_cat, count in components.items():
                        st.write(
                            f"🔹 **{count} {comp_cat.replace('_', ' ')}** item(s) logged for the `{comp_cat.upper()}` treatment workflow.")

                    honor_score = calculate_honor_score(total_items, major_category)
                    st.markdown("---")
                    st.subheader(f"C. Primary Treatment Protocol (based on {major_category.replace('_', ' ').title()})")

                    display_treatment_protocol(major_category)

                    st.success(
                        f"**PROCESS COMPLETE:** Primary treatment for {major_category.replace('_', ' ').title()} finished.")
                    st.markdown("---")

                    send_to_relay_app(user_email, f"Mixed (Major: {major_category.replace('_', ' ').title()})",
                                      honor_score)
        else:
            st.error("❗ Please enter your email address to proceed.")