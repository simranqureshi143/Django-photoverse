# streamlit_app.py
import streamlit as st
from PIL import Image
import os, json, uuid
from pathlib import Path
from datetime import datetime

# ========= PATH SETTINGS ==========
BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media" / "photos"
DB_FILE = BASE_DIR / "media" / "photos_meta.json"

# Create folders if not exist
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# If metadata file doesn't exist, create it
if not DB_FILE.exists():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    DB_FILE.write_text(json.dumps({}, indent=2))


# ========= LOAD / SAVE METADATA ==========
def load_meta():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_meta(meta):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


# ========= HELPER FUNCTIONS ==========
def save_upload(uploaded_file, caption=""):
    ext = Path(uploaded_file.name).suffix.lower()
    fname = f"{uuid.uuid4().hex}{ext}"

    fpath = MEDIA_DIR / fname
    with open(fpath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    meta = load_meta()
    meta[fname] = {
        "original_name": uploaded_file.name,
        "caption": caption,
        "likes": 0,
        "uploaded_at": datetime.now().timestamp()
    }

    save_meta(meta)
    return fname

def list_photos():
    meta = load_meta()
    photos = []

    for fname, info in meta.items():
        fpath = MEDIA_DIR / fname
        if fpath.exists():
            photos.append((fpath, info))

    photos.sort(key=lambda x: x[1].get("uploaded_at", 0), reverse=True)
    return photos

def delete_photo(fname):
    meta = load_meta()
    fpath = MEDIA_DIR / fname
    if fpath.exists():
        fpath.unlink()
    if fname in meta:
        meta.pop(fname)
    save_meta(meta)

def like_photo(fname):
    meta = load_meta()
    if fname in meta:
        meta[fname]["likes"] += 1
        save_meta(meta)
        return meta[fname]["likes"]
    return 0


# ========= STREAMLIT UI ==========
st.set_page_config(
    page_title="Django PhotoVerse v1.0",
    layout="wide"
)

# ----- HEADER -----
st.markdown(
    """
    <h1 style='text-align:center; color:#4C6EF5;'>
        📸 Django PhotoVerse v1.0
    </h1>
    <p style='text-align:center; color:gray; font-size:18px;'>
        A Beautiful Photo Gallery System built with Streamlit + Django Media Storage
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# ========= UPLOAD SECTION ==========
with st.expander("🔼 Upload New Photo", expanded=True):
    file = st.file_uploader("Choose Photo", type=["png","jpg","jpeg","webp"])
    caption = st.text_input("Photo Caption (optional)")

    if st.button("Upload Photo"):
        if file:
            save_upload(file, caption)
            st.success("Photo Uploaded Successfully! 🎉")
            st.experimental_rerun()
        else:
            st.warning("Please select a photo first!")


st.markdown("---")


# ========= SHOW GALLERY ==========
photos = list_photos()

if not photos:
    st.info("No photos uploaded yet. Upload your first photo above.")
else:
    per_row = 3
    rows = (len(photos) + per_row - 1) // per_row

    index = 0
    for r in range(rows):
        cols = st.columns(per_row)

        for col in cols:
            if index >= len(photos):
                break

            fpath, info = photos[index]
            fname = fpath.name
            index += 1

            with col:
                st.image(str(fpath), use_column_width=True)
                st.write(f"**Caption:** {info['caption']}")
                st.write(f"❤️ Likes: {info['likes']}")
                st.write(f"📅 Uploaded: {datetime.fromtimestamp(info['uploaded_at']).strftime('%Y-%m-%d %H:%M')}")

                c1, c2 = st.columns(2)

                with c1:
                    if st.button("❤️ Like", key=f"like_{fname}"):
                        new_likes = like_photo(fname)
                        st.success(f"Liked! Total Likes: {new_likes}")
                        st.experimental_rerun()

                with c2:
                    if st.button("🗑 Delete", key=f"del_{fname}"):
                        delete_photo(fname)
                        st.warning("Photo Deleted.")
                        st.experimental_rerun()


st.markdown("---")
st.caption("Django PhotoVerse v1.0 · Made by Simran 💛")
