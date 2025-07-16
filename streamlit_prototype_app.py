
import streamlit as st
import json
import os
import requests
import time
import json

# === ASSEMBLYAI API LOGIC ===
ASSEMBLYAI_API_KEY = st.secrets["ASSEMBLYAI"]["api_key"]
upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
headers = {"authorization": ASSEMBLYAI_API_KEY}

def upload_to_assemblyai(file_path):
    with open(file_path, "rb") as f:
        response = requests.post(upload_endpoint, headers=headers, files={"file": f})
    return response.json()["upload_url"]

def transcribe_with_assemblyai(audio_url):
    json_data = {
        "audio_url": audio_url,
        "speaker_labels": True,
        "auto_chapters": False
    }
    response = requests.post(transcript_endpoint, json=json_data, headers=headers)
    transcript_id = response.json()["id"]

    # Polling
    status = "queued"
    while status not in ("completed", "error"):
        polling = requests.get(f"{transcript_endpoint}/{transcript_id}", headers=headers)
        status = polling.json()["status"]
        if status == "completed":
            return polling.json()
        elif status == "error":
            raise Exception(f"Transcription failed: {polling.json()}")
        time.sleep(3)
    return None

def generate_schema1(transcript_json):
    result = []
    for utterance in transcript_json.get("utterances", []):
        result.append({
            "speaker": utterance["speaker"],
            "start": utterance["start"] / 1000,
            "end": utterance["end"] / 1000,
            "text": utterance["text"]
        })
    return result

# Load Google Credentials from Streamlit secrets
if "GOOGLE_CREDENTIALS" in st.secrets:
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmpfile:
        tmpfile.write(st.secrets["GOOGLE_CREDENTIALS"].encode("utf-8"))
        tmpfile_path = tmpfile.name
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmpfile_path


st.set_page_config(page_title="Hindi Serial Video Analytics", layout="wide")

st.title("📺 Hindi Serial Video Content Analyzer (Prototype)")

# Upload or input video
st.subheader("🎞️ Video Source")
video_option = st.radio("Select video input method:", ("Upload Video File", "Enter YouTube Link"))

if video_option == "Upload Video File":
    uploaded_video = st.file_uploader("Upload a Hindi serial episode video", type=["mp4", "mkv", "avi"])
    if uploaded_video:
        st.video(uploaded_video)
elif video_option == "Enter YouTube Link":
    youtube_link = st.text_input("Enter YouTube Video URL:")
    if youtube_link:
        st.video(youtube_link)

# Load schemas
schema_dir = "video_analytics_schemas"
os.makedirs(schema_dir, exist_ok=True)

schema_files = [f for f in os.listdir(schema_dir) if f.endswith(".json")]
schema_selections = st.multiselect("Select one or more schemas to view analysis structure", schema_files)

for selected_schema in schema_selections:
    schema_path = os.path.join(schema_dir, selected_schema)
    with open(schema_path, "r") as f:
        schema_json = json.load(f)

    st.subheader(f"🧩 Schema: {selected_schema}")
    st.json(schema_json)

    st.markdown("---")
    st.subheader("🔍 Placeholder Output")
    st.write(f"This is where AI-generated metadata for **{selected_schema.replace('.json', '')}** will be shown after analysis.")
    st.info("Note: In a full version, AI modules would process the uploaded or linked video and generate timestamped metadata for each schema.")

st.sidebar.title("ℹ️ Info")
st.sidebar.markdown("This prototype lets you explore multiple schema structures used for analyzing Hindi TV serials. Upload a video or enter a YouTube link, then select one or more schemas to view.")

# Clean up the temporary credential file
if "tmpfile_path" in globals() and os.path.exists(tmpfile_path):
    os.remove(tmpfile_path)

# === Streamlit Interface for Transcription ===
st.header("AssemblyAI Transcription & Diarization")

input_type = st.radio("Choose input type", ["Upload Video", "YouTube Link"])

if input_type == "Upload Video":
    uploaded_file = st.file_uploader("Upload your video or audio file", type=["mp4", "mp3", "wav"])
    if uploaded_file:
        with open("temp_upload.mp4", "wb") as f:
            f.write(uploaded_file.read())
        st.info("Uploading to AssemblyAI...")
        audio_url = upload_to_assemblyai("temp_upload.mp4")
        st.success("Uploaded. Transcribing...")
        result = transcribe_with_assemblyai(audio_url)
        schema_output = generate_schema1(result)
        st.subheader("Speaker-wise Transcript")
        st.json(schema_output)
        json_str = json.dumps(schema_output, indent=2)
        st.download_button("Download JSON", data=json_str, file_name="schema1_transcript.json")

elif input_type == "YouTube Link":
    yt_url = st.text_input("Paste YouTube video link")
    if yt_url:
        st.warning("YouTube audio download + AssemblyAI integration will be added next.")
