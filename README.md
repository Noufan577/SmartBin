 # WasteWise: AI-Powered Agentic Waste Management
 
A sophisticated, multi-agent system that classifies waste from images, identifies components, and engages users with a gamified scoring system. Developed for the IBM AI Summer Certification Program.

![WasteWise App Demo ]  (https://github.com/user-attachments/assets/eac93d0b-52fd-4e86-b64e-989b72c1875b)


## About The Project
Manual waste sorting is inefficient, costly, and prone to error. This project, WasteWise, addresses these challenges by leveraging the power of Google's Gemini AI to create an automated, end-to-end workflow.

Our system doesn't just classify waste; it uses a team of specialized AI agents to analyze the components, route them to simulated treatment protocols, and reward users for proper segregation through a unique Honor Score, creating a complete and engaging feedback loop.

### Key Features
 Gemini-Powered Classification: Utilizes Google Gemini's advanced multimodal capabilities to accurately classify waste into Biodegradable, Non-Biodegradable, E-Waste, and Mixed categories from a single image.

 Multi-Agent Architecture: Deploys specialized agents, including a Classifier Agent for initial analysis and a Separator Agent for identifying individual items in mixed waste.

 Automated Treatment Protocols: Simulates realistic, industrial-scale treatment workflows for different types of waste, providing detailed process descriptions.

Gamified "Honor Score": Engages users by awarding points for responsible waste disposal, with scores stored and tracked in a MongoDB database.

 Automated Email Notifications: Uses Relay.app to automatically send users a confirmation email with their updated Honor Score, completing the user feedback loop.

 Interactive Web UI: A clean and user-friendly interface built with Streamlit.

## Technology Stack
Core AI Engine: Google Gemini (gemini-1.5-flash)

Application Framework: Streamlit

Database: MongoDB

Automation & Notifications: Relay.app

Core Language: Python

## Getting Started
To get a local copy up and running, follow these simple steps.

### Prerequisites
Make sure you have Python 3.8+ and pip installed. 

Also get gemini api key from the https://aistudio.google.com/prompts/new_chat and paste it in the are of the code provided.

Also get the relay app url from https://www.relay.app/ and paste it in the area provided in the code.

### Installation
Clone the repo

Bash

git clone https://github.com/your_username/WasteWise.git
cd WasteWise
Create and activate a virtual environment (recommended)

Bash

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install requirements
(First, create a requirements.txt file with the following content):

Plaintext

streamlit
google-generativeai
Pillow
requests
pymongo # If you're connecting to MongoDB directly
Now, run the installation command:

Bash

pip install -r requirements.txt
Set up your environment variables
Create a file named .env in the root directory and add your API keys.

GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
RELAY_URL="YOUR_RELAY_APP_WEBHOOK_URL"
MONGO_URI="YOUR_MONGODB_CONNECTION_STRING"
(Important: Update your Python code to load these variables using a library like python-dotenv instead of hardcoding them. This is a much safer practice!)

### Running the Application
Once everything is installed, run the Streamlit app from your terminal:

Bash

streamlit run your_app_file.py
## Usage
Open the Streamlit application in your browser.

Enter your email address to receive notifications.

Upload an image of waste (.jpg, .jpeg, or .png).

Click the "Initiate Automated Treatment" button.

Watch as the AI agents classify the waste, identify components, and detail the treatment process.

Check your email for your Honor Score confirmation!

## Acknowledgments
This project was developed as part of the IBM AI Summer Certification Program.

Thanks to all the frameworks and libraries that made this project possible.
