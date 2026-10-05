"""Streamlit interface for the FastAPI meeting summarizer backend."""
import requests
import streamlit as st


st.set_page_config(page_title="Meeting Summarizer", page_icon="📝", layout="wide")
st.title("AI Meeting Summarizer & Action Tracker")

api_url = st.sidebar.text_input("FastAPI URL", "http://127.0.0.1:8000").rstrip("/")
st.sidebar.caption("Start the API first: `uvicorn app:app --reload`")


def call_api(method, path, **kwargs):
    try:
        # The first local Whisper use may need time to download and initialize a model.
        response = requests.request(method, f"{api_url}{path}", timeout=300, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        detail = None
        if exc.response is not None:
            try:
                detail = exc.response.json().get("detail")
            except ValueError:
                pass
        st.error(detail or f"API request failed: {exc}")
        return None


summary_tab, tracker_tab, ask_tab = st.tabs(["Summarize meeting", "Action tracker", "Ask past meetings"])

with summary_tab:
    st.subheader("Meeting recording")
    audio = st.audio_input("Record audio", key="meeting_audio")
    uploaded_audio = st.file_uploader("Or upload an audio file", type=["wav", "mp3", "m4a", "mp4", "webm", "ogg"])
    recording = audio or uploaded_audio
    model = st.selectbox("Speech-to-text model", ["tiny", "base"], index=0)
    st.caption("Transcription runs locally. The selected model downloads once to .whisper_models.")
    if recording and st.button("Transcribe recording"):
        with st.spinner("Transcribing the recording… the model may download on its first use."):
            transcript_result = call_api(
                "POST",
                "/transcribe",
                files={"file": (recording.name, recording.getvalue(), recording.type)},
                data={"model": model},
            )
        if transcript_result:
            st.session_state["transcript_text"] = transcript_result["text"]
            st.success(f"Transcribed in {transcript_result['language']} using the {transcript_result['model']} model.")

    st.subheader("Meeting transcript")
    transcript = st.text_area(
        "Paste a meeting transcript",
        height=260,
        placeholder="Alice: I will share the proposal by Friday.\nBob: We should review the budget next week.",
        key="transcript_text",
    )
    if st.button("Analyze meeting", type="primary"):
        if not transcript.strip():
            st.warning("Paste a transcript before analyzing it.")
        else:
            ingested = call_api("POST", "/ingest", json={"text": transcript})
            if ingested:
                transcript_id = ingested["transcript_id"]
                summary = call_api("POST", "/summarize", json={"transcript_id": transcript_id})
                action_items = call_api("POST", "/extract_actions", json={"transcript_id": transcript_id})
                st.session_state["transcript_id"] = transcript_id
                if summary:
                    st.subheader("Summary")
                    st.write(summary["summary"])
                if action_items:
                    st.subheader("Action items")
                    st.dataframe(action_items["actions"], use_container_width=True)
    ##########
    if st.session_state.get("transcript_id"):
        st.subheader("Export")
        if st.button("Prepare export"):
            resp = requests.get(f"{api_url}/export", params={"transcript_id": st.session_state["transcript_id"]})
            if resp.status_code == 200:
                st.session_state["export_content"] = resp.content
            else:
                st.error("Export failed.")
        if st.session_state.get("export_content"):
            st.download_button(
                label="Download Markdown",
                data=st.session_state["export_content"],
                file_name=f"export_{st.session_state['transcript_id']}.md",
                mime="text/markdown",
            )
###########

with tracker_tab:
    status_filter = st.selectbox("Filter by status", ["all", "open", "done"], index=0)
    if st.button("Load action items") or "tracker_actions" in st.session_state:
        params = {} if status_filter == "all" else {"status": status_filter}
        listing = call_api("GET", "/track/list", params=params)
        if listing is not None:
            st.session_state["tracker_actions"] = listing["actions"]

    actions = st.session_state.get("tracker_actions", [])
    if not actions:
        st.info("No action items loaded yet. Click 'Load action items'.")
    for a in actions:
        col1, col2, col3 = st.columns([5, 2, 1])
        with col1:
            st.write(f"**{a.get('task')}**")
            st.caption(f"Owner: {a.get('owner') or 'Unassigned'} · Deadline: {a.get('deadline') or 'No deadline'}")
        with col2:
            st.write(f"Status: `{a.get('status')}`")
        with col3:
            label = "Mark done" if a.get("status") != "done" else "Reopen"
            new_status = "done" if a.get("status") != "done" else "open"
            if st.button(label, key=f"toggle_{a.get('id')}"):
                result = call_api("POST", "/track/update", json={"action_id": a["id"], "status": new_status})
                if result:
                    a["status"] = new_status
                    st.rerun()

with ask_tab:
    question = st.text_input("Ask a question about past meetings")
    if st.button("Ask"):
        if not question.strip():
            st.warning("Type a question first.")
        else:
            result = call_api("GET", "/query", params={"q": question})
            if result:
                st.subheader("Answer")
                st.write(result["answer"])
                st.caption("Sources")
                for src in result["sources"]:
                    st.markdown(f"- *(score {src['score']:.2f})* {src['text'][:200]}...")
