import sys
import subprocess
import threading
import os
import streamlit as st

# Install streamlit jika belum ada
try:
    import streamlit as st
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st


def run_ffmpeg(video_path, stream_key, is_shorts, log_callback):
    output_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    scale = "-vf scale=720:1280" if is_shorts else ""
    cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1", "-i", video_path,
        "-c:v", "libx264", "-preset", "veryfast", "-b:v", "2500k",
        "-maxrate", "2500k", "-bufsize", "5000k",
        "-g", "60", "-keyint_min", "60",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "flv"
    ]
    if scale:
        cmd += scale.split()
    cmd.append(output_url)
    log_callback(f"Menjalankan: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            log_callback(line.strip())
        process.wait()
    except Exception as e:
        log_callback(f"Error: {e}")
    finally:
        log_callback("Streaming selesai atau dihentikan.")


def main():
    # Page configuration must be the first Streamlit command
    st.set_page_config(page_title="Streaming YT by didinchy", page_icon="📈")

    st.title("Upload Video & Jalankan Live via Parameter")

    # Upload video section
    uploaded_file = st.file_uploader("Upload video (mp4/flv - codec H264/AAC)", type=['mp4', 'flv'])

    video_path = None
    if uploaded_file:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ Video berhasil diupload.")
        video_path = uploaded_file.name

    # Log placeholder
    log_placeholder = st.empty()
    logs = []

    def log_callback(msg):
        logs.append(msg)
        try:
            log_placeholder.text("\n".join(logs[-20:]))
        except:
            print(msg)  # fallback ke terminal

    # Get parameters from URL
    query_params = st.experimental_get_query_params()
    auto_video = query_params.get("video", [None])[0]
    auto_key = query_params.get("key", [None])[0]
    auto_mode = query_params.get("mode", ["normal"])[0].lower() == "shorts"

    # Auto start streaming jika semua parameter tersedia
    if auto_video and auto_key and not st.session_state.get('auto_started', False):
        st.session_state['auto_started'] = True
        if os.path.exists(auto_video):
            video_to_stream = auto_video
        elif video_path:
            video_to_stream = video_path
        else:
            st.error("❌ Tidak ada video untuk distreaming.")
            return

        # Jalankan FFmpeg secara async
        thread = threading.Thread(target=run_ffmpeg, args=(video_to_stream, auto_key, auto_mode, log_callback), daemon=True)
        thread.start()
        st.success("🚀 Streaming otomatis dimulai!")


if __name__ == '__main__':
    main()
