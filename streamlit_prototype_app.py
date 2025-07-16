
import streamlit as st
import json
import os

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
