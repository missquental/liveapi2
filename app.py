# live_streaming.py
import streamlit as st
import requests
import pandas as pd
import sqlite3
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Live Streaming Video",
    page_icon="📺",
    layout="wide"
)

st.title("📺 Live Streaming Video")
st.markdown("---")

# URL gudang video
GUDANG_URL = "https://gudangvideo.streamlit.app"

# Fungsi untuk mendapatkan daftar video dari gudang
@st.cache_data(ttl=300)  # Cache selama 5 menit
def get_video_list():
    try:
        # Simulasi API call - dalam praktiknya ini akan menjadi endpoint API
        conn = sqlite3.connect('videos.db')
        df = pd.read_sql_query("SELECT * FROM videos ORDER BY upload_date DESC", conn)
        conn.close()
        return df
    except:
        # Jika tidak bisa mengakses database lokal, gunakan data dummy
        return pd.DataFrame({
            'filename': ['sample_video.mp4', 'demo_video.mov'],
            'original_name': ['Sample Video', 'Demo Video'],
            'upload_date': ['2024-01-15 10:30:00', '2024-01-14 15:45:00'],
            'file_size': [1024000, 2048000]
        })

# Sidebar untuk pemilihan video
st.sidebar.header("🎬 Pilih Video")

# Refresh button
if st.sidebar.button("🔄 Refresh Daftar Video"):
    st.cache_data.clear()

# Dapatkan daftar video
try:
    videos_df = get_video_list()
    
    if len(videos_df) > 0:
        # Dropdown untuk memilih video
        selected_video = st.sidebar.selectbox(
            "Pilih Video untuk Ditonton:",
            options=videos_df['original_name'].tolist(),
            format_func=lambda x: f"📹 {x}"
        )
        
        # Dapatkan detail video yang dipilih
        selected_row = videos_df[videos_df['original_name'] == selected_video].iloc[0]
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"🎥 Sedang Menonton: {selected_video}")
            
            # Video player
            video_path = os.path.join("videos", selected_row['filename'])
            if os.path.exists(video_path):
                st.video(video_path)
            else:
                # Gunakan URL streaming dari gudang
                stream_url = f"{GUDANG_URL}/videos/{selected_row['filename']}"
                st.warning("Video sedang dimuat dari server...")
                st.video(stream_url)
        
        with col2:
            st.subheader("📊 Informasi Video")
            st.metric("Nama File", selected_row['original_name'])
            st.metric("Tanggal Upload", selected_row['upload_date'])
            st.metric("Ukuran", f"{selected_row['file_size'] / (1024*1024):.2f} MB")
            
            st.divider()
            
            st.subheader("🔗 Akses Langsung")
            direct_url = f"{GUDANG_URL}/videos/{selected_row['filename']}"
            st.code(direct_url, language="url")
            st.markdown(f"[🎬 Buka di Tab Baru]({direct_url})")
            
            st.divider()
            
            st.subheader("📋 Daftar Video Lain")
            for idx, row in videos_df.head(10).iterrows():
                if row['original_name'] != selected_video:
                    if st.button(f"▶️ {row['original_name']}", key=f"btn_{idx}"):
                        st.experimental_set_query_params(video=row['filename'])
                        st.experimental_rerun()
    
    else:
        st.info("Belum ada video tersedia. Silakan upload video di gudang terlebih dahulu.")
        
except Exception as e:
    st.error(f"Terjadi kesalahan: {str(e)}")
    st.info("Pastikan aplikasi gudang video sudah berjalan dan dapat diakses.")

# Fitur tambahan
st.sidebar.divider()
st.sidebar.subheader("⚙️ Pengaturan Streaming")

autoplay = st.sidebar.checkbox("Autoplay", value=True)
loop = st.sidebar.checkbox("Loop", value=False)
volume = st.sidebar.slider("Volume", 0, 100, 80)

st.sidebar.divider()
st.sidebar.markdown("### ℹ️ Informasi")
st.sidebar.info("""
Aplikasi ini mengambil video dari gudang.streamlit.app
dan menampilkannya secara streaming real-time.
""")

# Footer
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.caption("© 2024 Live Streaming Video")
with col2:
    st.caption(f"Gudang: {GUDANG_URL}")
