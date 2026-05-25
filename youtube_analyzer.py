import os
import re
import time

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_groq import ChatGroq

load_dotenv()

# works both locally (.env) and on streamlit cloud (st.secrets)
def get_key(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, "")

GROQ_API_KEY = get_key("GROQ_API_KEY")
YOUTUBE_API_KEY = get_key("YOUTUBE_API_KEY")
BATCH_SIZE = 15

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #05050f 0%, #0a0d1a 60%, #080514 100%);
    font-family: 'Inter', sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }

html, body { max-width: 100% !important; overflow-x: hidden !important; }
.block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 100% !important; }
@media (min-width: 768px) {
    .block-container { padding: 2rem 3rem 3rem 3rem !important; max-width: 780px !important; margin: 0 auto !important; }
}

.glow-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.2rem, 5vw, 2rem);
    font-weight: 900;
    text-align: center;
    color: #00d4ff;
    text-shadow: 0 0 8px #00d4ff, 0 0 20px #00d4ff, 0 0 50px #00d4ff;
    animation: pulsate 2.5s ease-in-out infinite;
    margin-bottom: 0.3rem;
    letter-spacing: clamp(0px, 1vw, 2px);
    word-break: break-word;
}
@keyframes pulsate {
    0%, 100% { text-shadow: 0 0 8px #00d4ff, 0 0 20px #00d4ff, 0 0 50px #00d4ff; }
    50%       { text-shadow: 0 0 16px #00d4ff, 0 0 40px #00d4ff, 0 0 90px #7c3aed, 0 0 130px #7c3aed; }
}

.subtitle {
    text-align: center;
    color: rgba(255,255,255,0.4);
    font-size: clamp(0.75rem, 2.5vw, 0.88rem);
    letter-spacing: 1px;
    margin-bottom: 2rem;
    padding: 0 0.5rem;
}

.neon-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #00d4ff, #7c3aed, transparent);
    border: none;
    margin: 1.5rem 0;
    box-shadow: 0 0 8px #00d4ff44;
}

.stTextInput > label { color: rgba(255,255,255,0.7) !important; font-size: 0.9rem !important; }
.stTextInput input {
    background: rgba(0,212,255,0.04) !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-size: 0.97rem !important;
    transition: all 0.3s ease !important;
}
.stTextInput input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 18px rgba(0,212,255,0.25) !important;
    background: rgba(0,212,255,0.08) !important;
}

.stSlider > label { color: rgba(255,255,255,0.7) !important; font-size: 0.9rem !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: #00d4ff !important;
    box-shadow: 0 0 10px #00d4ff !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.35), 0 4px 15px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 0 45px rgba(0,212,255,0.6), 0 0 80px rgba(124,58,237,0.35), 0 8px 25px rgba(0,0,0,0.4) !important;
}
.stButton > button:active { transform: translateY(0) scale(0.99) !important; }

[data-testid="metric-container"] {
    background: rgba(0,212,255,0.04) !important;
    border: 1px solid rgba(0,212,255,0.18) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    transition: all 0.35s ease !important;
    backdrop-filter: blur(6px) !important;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(0,212,255,0.55) !important;
    box-shadow: 0 0 25px rgba(0,212,255,0.18), 0 0 50px rgba(124,58,237,0.1) !important;
    transform: translateY(-4px) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.95rem !important; }

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #00d4ff, #7c3aed) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 10px #00d4ff66 !important;
}
.stProgress > div > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
}

div[data-testid="stAlert"] {
    border-radius: 12px !important;
    backdrop-filter: blur(6px) !important;
}

.stExpander {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    margin-bottom: 0.6rem !important;
    transition: border-color 0.3s ease !important;
}
.stExpander:hover { border-color: rgba(0,212,255,0.3) !important; }

.stSpinner > div { border-top-color: #00d4ff !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0d1a; }
::-webkit-scrollbar-thumb { background: linear-gradient(#00d4ff, #7c3aed); border-radius: 3px; }

.app-footer {
    text-align: center;
    padding: 2rem 0 0.5rem 0;
    margin-top: 3rem;
    border-top: 1px solid rgba(0,212,255,0.12);
    color: rgba(255,255,255,0.25);
    font-size: 0.78rem;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.app-footer .name {
    background: linear-gradient(135deg, #00d4ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    font-size: 0.85rem;
}
</style>
"""

SPLASH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@300;400&display=swap');
.splash-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 78vh;
    text-align: center;
    gap: 0.4rem;
}
.splash-made {
    font-family: 'Inter', sans-serif;
    color: rgba(255,255,255,0.35);
    font-size: 0.85rem;
    letter-spacing: 6px;
    text-transform: uppercase;
    animation: riseUp 0.9s ease both;
}
.splash-name {
    font-family: 'Orbitron', monospace;
    font-size: clamp(2rem, 10vw, 3.8rem);
    font-weight: 900;
    background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 30px rgba(0,212,255,0.5));
    animation: riseUp 0.9s ease 0.25s both;
    line-height: 1.1;
}
.splash-bar {
    width: 80px;
    height: 2px;
    background: linear-gradient(90deg, #00d4ff, #7c3aed);
    box-shadow: 0 0 12px #00d4ff;
    border-radius: 2px;
    animation: growBar 0.9s ease 0.6s both;
    margin: 0.8rem 0;
}
.splash-tag {
    font-family: 'Inter', sans-serif;
    color: rgba(255,255,255,0.3);
    font-size: 0.78rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    animation: riseUp 0.9s ease 0.8s both;
    margin-bottom: 2.5rem;
}
@keyframes riseUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes growBar {
    from { width: 0; opacity: 0; }
    to   { width: 80px; opacity: 1; }
}
</style>
"""


@st.cache_resource
def load_model():
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY, temperature=0)


def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None


def fetch_comments(video_id, max_comments):
    yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    video_resp = yt.videos().list(part="snippet", id=video_id).execute()
    if not video_resp["items"]:
        raise ValueError("Video not found. Please check the URL.")
    title = video_resp["items"][0]["snippet"]["title"]

    comments = []
    next_page = None

    while len(comments) < max_comments:
        resp = yt.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_comments - len(comments)),
            pageToken=next_page,
            textFormat="plainText",
        ).execute()

        for item in resp["items"]:
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(text)

        next_page = resp.get("nextPageToken")
        if not next_page:
            break

    return comments, title


def classify_batch(comments, model):
    numbered = "\n".join(f"{i+1}. {c[:250]}" for i, c in enumerate(comments))
    prompt = f"""Classify each comment's sentiment. Use only these labels:
P = Positive, N = Negative, U = Neutral

Return a comma-separated list of labels in the same order as the comments. Nothing else.

Comments:
{numbered}

Example output for 3 comments: P, N, U"""

    try:
        response = model.invoke(prompt).content.strip().split("\n")[0]
        labels = [x.strip().upper() for x in response.split(",")]
        labels = [x if x in ("P", "N", "U") else "U" for x in labels]
        if len(labels) < len(comments):
            labels += ["U"] * (len(comments) - len(labels))
        return labels[:len(comments)]
    except Exception:
        return ["U"] * len(comments)


def build_pie_chart(pos, neg, neu):
    total = pos + neg + neu
    fig = go.Figure(data=[go.Pie(
        labels=["Positive", "Negative", "Neutral"],
        values=[pos, neg, neu],
        hole=0.52,
        marker=dict(
            colors=["#00ff99", "#ff4466", "#ffcc00"],
            line=dict(color="#05050f", width=3),
        ),
        textfont=dict(size=13, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value} comments<br>%{percent}<extra></extra>",
        pull=[0.04, 0.04, 0.02],
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="Inter"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=13)),
        margin=dict(t=20, b=20, l=20, r=20),
        height=380,
        annotations=[dict(
            text=f"<b>{total}</b><br><span style='font-size:11px'>Comments</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="#00d4ff"),
        )],
    )
    return fig


def splash_page():
    st.markdown(SPLASH_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div class="splash-wrap">
        <div class="splash-made">Made by</div>
        <div class="splash-name">Bilal Madni</div>
        <div class="splash-bar"></div>
        <div class="splash-tag">YouTube · Sentiment Analyzer · AI Powered</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if st.button("Launch App →", type="primary"):
            st.session_state.splash_shown = True
            st.rerun()


def main_app():
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    st.markdown('<div class="glow-title">📊 YouTube Sentiment Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Paste any YouTube URL · AI analyzes every comment · Any language</div>', unsafe_allow_html=True)
    st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)

    url = st.text_input("🔗 YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
    max_comments = st.slider("Comments to analyze", 50, 500, 100, step=50)

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.button("🔍 Analyze Comments", type="primary"):
        st.markdown("""
        <div style="text-align:center; color:rgba(255,255,255,0.2); font-size:0.8rem; margin-top:3rem; letter-spacing:2px;">
            ↑ &nbsp; Paste a URL and hit Analyze
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="app-footer">Made by &nbsp;<span class="name">Bilal Madni</span></div>', unsafe_allow_html=True)
        return

    if not url.strip():
        st.error("Please enter a YouTube URL.")
        return

    video_id = extract_video_id(url)
    if not video_id:
        st.error("Couldn't find a valid video ID. Double-check the URL.")
        return

    with st.spinner("Fetching comments from YouTube..."):
        try:
            comments, video_title = fetch_comments(video_id, max_comments)
        except HttpError as e:
            st.error(f"YouTube API error: {e}")
            return
        except ValueError as e:
            st.error(str(e))
            return

    if not comments:
        st.warning("No comments found. Comments might be disabled on this video.")
        return

    st.info(f"**{video_title}** — {len(comments)} comments loaded")

    model = load_model()
    all_labels = []
    batches = [comments[i: i + BATCH_SIZE] for i in range(0, len(comments), BATCH_SIZE)]

    progress_bar = st.progress(0)
    status = st.empty()

    for i, batch in enumerate(batches):
        status.text(f"Analyzing... {i + 1}/{len(batches)} batches done")
        all_labels.extend(classify_batch(batch, model))
        progress_bar.progress((i + 1) / len(batches))
        time.sleep(0.2)

    status.markdown("✅ &nbsp; **Done!**")

    pos = all_labels.count("P")
    neg = all_labels.count("N")
    neu = all_labels.count("U")
    total = len(all_labels)

    st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)
    st.subheader("📈 Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Positive", pos, f"{pos / total * 100:.1f}%")
    c2.metric("❌ Negative", neg, f"{neg / total * 100:.1f}%")
    c3.metric("😐 Neutral",  neu, f"{neu / total * 100:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(build_pie_chart(pos, neg, neu), use_container_width=True)

    if pos > neg and pos > neu:
        st.success(f"🎉 Overall: Audience is **POSITIVE** about this video — {pos / total * 100:.0f}% positive comments")
    elif neg > pos and neg > neu:
        st.error(f"😞 Overall: Audience is **NEGATIVE** about this video — {neg / total * 100:.0f}% negative comments")
    else:
        st.info("😐 Overall: Audience has **MIXED** views about this video")

    st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)

    pairs = list(zip(comments, all_labels))

    with st.expander(f"✅ Positive Comments — {pos} total"):
        for c, _ in [x for x in pairs if x[1] == "P"][:8]:
            st.markdown(f"<div style='padding:0.4rem 0; color:rgba(255,255,255,0.8); border-bottom:1px solid rgba(255,255,255,0.05);'>• {c[:300]}</div>", unsafe_allow_html=True)

    with st.expander(f"❌ Negative Comments — {neg} total"):
        for c, _ in [x for x in pairs if x[1] == "N"][:8]:
            st.markdown(f"<div style='padding:0.4rem 0; color:rgba(255,255,255,0.8); border-bottom:1px solid rgba(255,255,255,0.05);'>• {c[:300]}</div>", unsafe_allow_html=True)

    with st.expander(f"😐 Neutral Comments — {neu} total"):
        for c, _ in [x for x in pairs if x[1] == "U"][:8]:
            st.markdown(f"<div style='padding:0.4rem 0; color:rgba(255,255,255,0.8); border-bottom:1px solid rgba(255,255,255,0.05);'>• {c[:300]}</div>", unsafe_allow_html=True)

    st.markdown('<div class="app-footer">Made by &nbsp;<span class="name">Bilal Madni</span></div>', unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="YouTube Sentiment Analyzer",
        page_icon="📊",
        layout="centered",
    )

    if "splash_shown" not in st.session_state:
        st.session_state.splash_shown = False

    if not st.session_state.splash_shown:
        splash_page()
    else:
        main_app()


if __name__ == "__main__":
    main()
