import os
import re
import subprocess
import streamlit as st
from pytubefix import YouTube

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_hd_video(url, save_path='downloads'):
    try:
        yt = YouTube(url)
        st.info(f"📹 Title: {yt.title}")

        video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()

        if not video_stream or not audio_stream:
            st.error("❌ Suitable streams not found.")
            return None

        os.makedirs(save_path, exist_ok=True)

        video_path = os.path.join(save_path, "video.mp4")
        audio_path = os.path.join(save_path, "audio.mp4")
        output_filename = sanitize_filename(f"{yt.title}.mp4")
        output_path = os.path.join(save_path, output_filename)

        st.write("⬇️ Downloading video stream...")
        video_stream.download(filename=video_path)

        st.write("⬇️ Downloading audio stream...")
        audio_stream.download(filename=audio_path)

        st.write("🔀 Merging video and audio with ffmpeg...")
        command = [
            'ffmpeg',
            '-y',  # Overwrite if file exists
            '-i', sanitize_filename(video_path),
            '-i', sanitize_filename(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            sanitize_filename(output_path)
        ]

        subprocess.run(command, check=True)

        os.remove(sanitize_filename(video_path))
        os.remove(sanitize_filename(audio_path))

        st.success(f"✅ HD Video downloaded and saved as: {sanitize_filename(output_filename)}")
        return output_path

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# Streamlit UI
st.title("🎥 YouTube HD Video Downloader")

with st.form("yt_form"):
    url = st.text_input("Enter YouTube Video URL")
    submitted = st.form_submit_button("Download HD Video")

if submitted and url:
    result = download_hd_video(url)
    if result and os.path.exists(result):
        with open(result, "rb") as f:
            st.download_button(
                label="📥 Download Merged Video",
                data=f,
                file_name=os.path.basename(result),
                mime="video/mp4"
            )
