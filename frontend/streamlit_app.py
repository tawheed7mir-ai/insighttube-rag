"""Signal: a portfolio-ready research console for the YouTube Podcast RAG service."""

from __future__ import annotations

import os
from html import escape
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(
    page_title="Signal | Research console",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
    :root { --ink: #17202a; --muted: #68737b; --paper: #f2f0ea; --card: #fbfaf6; --acid: #d8f27c; --coral: #ef705c; --youtube: #ff0033; --sky: #c8e8e9; --line: #d8d8d1; }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background: var(--ink); border-right: 0; }
    [data-testid="stSidebar"] * { color: #f5f2e9; }
    [data-testid="stSidebar"] .stTextInput input { background: #27323c; border-color: #46535d; color: white; }
    h1, h2, h3, p, label, button { font-family: 'DM Sans', sans-serif; }
    h1 { letter-spacing: -0.035em; font-family: 'Instrument Serif', Georgia, serif; font-size: clamp(3.25rem, 6vw, 6.8rem); font-weight: 400; line-height: .86; margin: .35rem 0 1.25rem; }
    h2 { letter-spacing: -0.025em; font-size: 1.55rem; }
    h3 { font-size: 1.05rem; }
    .mono { font-family: 'DM Mono', monospace; text-transform: uppercase; font-size: .68rem; letter-spacing: .1em; color: var(--muted); }
    .hero { padding: 2.7rem 0 2.2rem; border-bottom: 1px solid var(--line); margin-bottom: 1.4rem; }
    .hero p { max-width: 610px; color: var(--muted); font-size: 1.02rem; line-height: 1.55; }
    .hero-mark { font-family: 'DM Mono', monospace; color: var(--coral); font-size: 1rem; }
    .status { display: inline-flex; align-items: center; gap: .55rem; padding: .48rem .72rem; border: 1px solid var(--line); background: var(--card); border-radius: 3px; font-family: 'DM Mono', monospace; font-size: .67rem; text-transform: uppercase; letter-spacing: .08em; }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: #77a44b; box-shadow: 0 0 0 4px #dfe9d5; }
    .dot.offline { background: var(--coral); box-shadow: 0 0 0 4px #f7d9d2; }
    .section-kicker { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid var(--ink); padding-bottom: .55rem; margin: 2rem 0 1rem; }
    .section-kicker h2 { margin: 0; }
    .section-kicker .mono { color: var(--ink); }
    .answer { background: var(--card); border: 1px solid var(--line); border-top: 5px solid var(--acid); padding: 1.25rem 1.35rem; font-size: 1.12rem; line-height: 1.65; min-height: 130px; }
    .answer-label { background: var(--acid); color: var(--ink); display: inline-block; padding: .3rem .45rem; font-family: 'DM Mono', monospace; font-size: .62rem; letter-spacing: .08em; text-transform: uppercase; margin-bottom: .8rem; }
    .library-item { border-bottom: 1px solid var(--line); padding: .85rem 0; }
    .library-item strong { font-size: .94rem; }
    [data-testid="stMetric"] { background: var(--card); border: 1px solid var(--line); padding: .7rem 1rem; border-radius: 3px; }
    [data-testid="stMetricLabel"] { font-family: 'DM Mono', monospace; text-transform: uppercase; font-size: .63rem; letter-spacing: .08em; }
    [data-testid="stMetricValue"] { font-family: 'DM Sans', sans-serif; }
    textarea, [data-baseweb="select"] > div { background: var(--card) !important; border-color: var(--line) !important; border-radius: 3px !important; }
    .stButton > button { border-radius: 3px; font-family: 'DM Sans', sans-serif; font-weight: 600; transition: transform .2s ease, box-shadow .2s ease, background .2s ease; }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 8px 16px rgba(23,32,42,.12); }
    .stButton > button[kind="primary"] { background: var(--ink); border-color: var(--ink); color: white; }
    .evidence-card { background: var(--card); border-left: 3px solid var(--coral); padding: .9rem 1rem; margin: .55rem 0; }
    .evidence-time { font-family: 'DM Mono', monospace; color: var(--coral); font-size: .72rem; letter-spacing: .04em; }
    .empty-state { border: 1px dashed #bfc3bb; padding: 2rem; text-align: center; color: var(--muted); background: rgba(251,250,246,.45); }
    .source-panel { background: linear-gradient(135deg, #17202a 0%, #243642 100%); color: #f5f2e9; padding: 1.5rem; border-radius: 3px; margin: 1.2rem 0 2rem; position: relative; overflow: hidden; box-shadow: 0 18px 36px rgba(23,32,42,.13); }
    .source-panel::after { content: ''; position: absolute; width: 180px; height: 180px; right: -58px; top: -72px; border: 1px solid rgba(200,232,233,.25); border-radius: 50%; box-shadow: 0 0 0 24px rgba(200,232,233,.04), 0 0 0 48px rgba(200,232,233,.035); pointer-events: none; }
    .source-panel h2 { color: #f5f2e9; margin: 0 0 .35rem; }
    .source-panel p { color: #b9c1c4; margin: 0 0 1rem; }
    .source-heading { display: flex; align-items: center; gap: .8rem; margin-bottom: .7rem; position: relative; z-index: 1; }
    .youtube-mark { width: 42px; height: 30px; display: grid; place-items: center; background: var(--youtube); border-radius: 8px; box-shadow: 0 8px 18px rgba(255,0,51,.24); }
    .youtube-mark::after { content: ''; width: 0; height: 0; border-top: 7px solid transparent; border-bottom: 7px solid transparent; border-left: 11px solid white; margin-left: 3px; }
    .source-panel .stTextInput, .source-panel .stButton { position: relative; z-index: 1; }
    .source-panel .stTextInput input { background: rgba(255,255,255,.1); border-color: rgba(200,232,233,.45); color: white; }
    .source-panel .stTextInput input:focus { border-color: var(--acid); box-shadow: 0 0 0 1px var(--acid); }
    .source-panel .stButton > button { background: var(--acid); border-color: var(--acid); color: var(--ink); box-shadow: 0 7px 16px rgba(216,242,124,.13); }
    .source-panel .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 11px 22px rgba(216,242,124,.22); }
    .active-source { border-left: 4px solid var(--coral); background: linear-gradient(90deg, #fff8f2, var(--card)); padding: .9rem 1rem; margin: .8rem 0 1.4rem; box-shadow: 0 8px 20px rgba(23,32,42,.05); }
    @keyframes signal-rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes signal-fade { from { opacity: 0; } to { opacity: 1; } }
    @keyframes signal-pulse { 0%, 100% { box-shadow: 0 0 0 4px #dfe9d5; } 50% { box-shadow: 0 0 0 7px rgba(223,233,213,.25); } }
    .hero { animation: signal-rise .7s cubic-bezier(.2,.8,.2,1) both; }
    .hero .status { animation: signal-fade .8s ease .35s both; }
    .dot:not(.offline) { animation: signal-pulse 2.8s ease-in-out infinite; }
    .source-panel { animation: signal-rise .7s cubic-bezier(.2,.8,.2,1) .12s both; }
    .active-source { animation: signal-rise .55s cubic-bezier(.2,.8,.2,1) both; }
    [data-testid="stMetric"] { animation: signal-rise .55s cubic-bezier(.2,.8,.2,1) both; }
    [data-testid="stMetric"]:nth-child(2) { animation-delay: .08s; }
    [data-testid="stMetric"]:nth-child(3) { animation-delay: .16s; }
    .answer { animation: signal-rise .55s cubic-bezier(.2,.8,.2,1) both; }
    .evidence-card { animation: signal-rise .45s cubic-bezier(.2,.8,.2,1) both; }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; }
    }
    @media (max-width: 700px) { h1 { font-size: 3.65rem; } .hero { padding-top: 1.3rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_request(method: str, path: str, *, show_error: bool = True, **kwargs: Any) -> Any | None:
    try:
        response = requests.request(method, f"{api_url.rstrip('/')}{path}", timeout=120, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        if show_error:
            detail = ""
            if exc.response is not None:
                try:
                    detail = f" Detail: {exc.response.json().get('detail', exc.response.text)}"
                except ValueError:
                    detail = f" Response: {exc.response.text}"
            st.error(f"API request failed: {exc}.{detail}")
    except ValueError:
        if show_error:
            st.error("The API returned an invalid response.")
    return None


if "query_result" not in st.session_state:
    st.session_state.query_result = None
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "active_video_id" not in st.session_state:
    st.session_state.active_video_id = None
if "active_source" not in st.session_state:
    st.session_state.active_source = None

api_url = os.getenv("API_URL", "http://localhost:8000")
health = api_request("GET", "/health", show_error=False)
videos = api_request("GET", "/videos", show_error=False) or []


with st.sidebar:
    st.markdown("# SIGNAL")
    st.markdown("<span class='mono'>Transcript research console</span>", unsafe_allow_html=True)
    st.write("")
    st.markdown("Ask questions against one transcript at a time.")
    st.divider()
status_text = "System online" if health else "API offline"
dot_class = "" if health else "offline"
st.markdown(f'<div class="hero"><div class="hero-mark">S / 01</div><h1>Find the signal<br><em>inside the noise.</em></h1><p>Ask questions across long-form conversations and get answers that point back to the exact words, speaker, and moment that support them.</p><div class="status"><span class="dot {dot_class}"></span>{status_text}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="source-panel">', unsafe_allow_html=True)
st.markdown('<div class="source-heading"><span class="youtube-mark" aria-label="YouTube"></span><div><span class="mono" style="color:#c8e8e9">SOURCE / YOUTUBE</span><h2>Start with a video</h2></div></div>', unsafe_allow_html=True)
st.markdown("Paste a YouTube link and Signal will fetch its transcript and prepare it for grounded questions.", unsafe_allow_html=True)
video_url = st.text_input("YouTube video link", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")
if st.button("Load transcript  →", type="primary", use_container_width=True):
    if not video_url.strip():
        st.warning("Paste a YouTube link first.")
    else:
        with st.spinner("Fetching transcript and building your research index..."):
            result = api_request("POST", "/ingest", json={"video_url": video_url.strip()})
        if result:
            st.session_state.active_video_id = result.get("video_id")
            st.session_state.active_source = result
            st.session_state.query_result = None
            st.session_state.last_question = ""
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

active_video_id = st.session_state.active_video_id
active_source = st.session_state.active_source or {}
if active_video_id:
    st.markdown(f'<div class="active-source"><span class="mono">Active transcript</span><br><strong>{escape(str(active_video_id))}</strong><br><span class="mono">{active_source.get("chunks", 0)} indexed chunks ready for questions</span></div>', unsafe_allow_html=True)

metric_one, metric_two, metric_three = st.columns(3)
metric_one.metric("Indexed sources", len(videos))
metric_two.metric("Retrieval stack", "Hybrid + MMR")
metric_three.metric("Evidence format", "Timestamped")

st.markdown('<div class="section-kicker"><h2>Research desk</h2><span class="mono">Query / 02</span></div>', unsafe_allow_html=True)
question = st.text_area("Question", placeholder="What did the speaker say about attention, craft, or the future?", height=105, label_visibility="collapsed", disabled=not active_video_id)

if st.button("Ask the transcript  →", type="primary", use_container_width=False, disabled=not active_video_id):
    if not question.strip():
        st.warning("Write a question to search the archive.")
    else:
        with st.spinner("Retrieving evidence..."):
            data = api_request("POST", "/query", json={"question": question.strip(), "video_id": active_video_id})
        if data:
            st.session_state.query_result = data
            st.session_state.last_question = question.strip()

result = st.session_state.query_result
if result:
    citations = result.get("citations", [])
    answer_col, evidence_col = st.columns([1.15, .85], gap="large")
    with answer_col:
        st.markdown('<div class="section-kicker"><h2>Grounded answer</h2><span class="mono">Dossier / 03</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="answer-label">Answer generated from indexed context</div>', unsafe_allow_html=True)
        answer_text = escape(str(result.get("answer", "No answer returned."))).replace("\n", "<br>")
        st.markdown(f'<div class="answer">{answer_text}</div>', unsafe_allow_html=True)
        st.caption(f"Asked: {st.session_state.last_question}")
    with evidence_col:
        st.markdown(f'<div class="section-kicker"><h2>Evidence</h2><span class="mono">{len(citations):02d} citations</span></div>', unsafe_allow_html=True)
        if citations:
            for index, source in enumerate(citations, start=1):
                timestamp = f"{source.get('start_timestamp', '00:00')} → {source.get('end_timestamp', '00:00')}"
                with st.expander(f"{index:02d}  {timestamp}"):
                    source_text = escape(str(source.get("text", ""))).replace("\n", "<br>")
                    st.markdown(f'<div class="evidence-card"><div class="evidence-time">{timestamp}</div><p>{source_text}</p></div>', unsafe_allow_html=True)
                    if source.get("url"):
                        st.link_button("Open moment in YouTube  ↗", source["url"])
                    st.caption(f"retrieval score: {source.get('score', 0):.3f}")
        else:
            st.markdown('<div class="empty-state">No evidence was returned for this question.</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-kicker"><h2>Indexed library</h2><span class="mono">{len(videos):02d} sources</span></div>', unsafe_allow_html=True)
if videos:
    library_cols = st.columns(2)
    for index, item in enumerate(videos):
        with library_cols[index % 2]:
            title_text = item.get("title") or "Untitled source"
            channel_text = item.get("channel") or "Unknown channel"
            st.markdown(f'<div class="library-item"><strong>{escape(str(title_text))}</strong><br><span class="mono">{escape(str(channel_text))} / {escape(str(item.get("video_id", "")))}</span></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="empty-state">Your first source becomes the beginning of the archive.<br>Use the feed panel to index a YouTube transcript.</div>', unsafe_allow_html=True)
