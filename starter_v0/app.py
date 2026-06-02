from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    json_text,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@st.cache_resource(show_spinner=False)
def provider_for(name: str) -> Any:
    return make_provider(name)


@st.cache_data(show_spinner=False)
def load_artifacts(system_prompt_path: str, tools_path: str) -> tuple[str, list[dict[str, Any]]]:
    system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(Path(tools_path))
    return system_prompt, to_openai_tools(tool_declarations)


def transcript_path(version: str, provider_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(["ui", safe_slug(version), safe_slug(provider_name), timestamp])
    return TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"


def make_transcript(
    *,
    version: str,
    provider_name: str,
    model: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    return {
        "transcript_id": "",
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
        "ui": "streamlit",
    }


def reset_chat() -> None:
    for key in ["history", "turns", "transcript", "transcript_file"]:
        st.session_state.pop(key, None)


def ensure_session(
    *,
    version: str,
    provider_name: str,
    model: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "transcript_file" not in st.session_state:
        path = transcript_path(version, provider_name)
        st.session_state.transcript_file = path
        transcript = make_transcript(
            version=version,
            provider_name=provider_name,
            model=model,
            system_prompt_path=system_prompt_path,
            tools_path=tools_path,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )
        transcript["transcript_id"] = path.stem.replace(".transcript", "")
        st.session_state.transcript = transcript


def main() -> None:
    st.set_page_config(page_title="Research Agent", layout="wide")
    load_lab_env(ROOT)

    st.title("Research Agent")

    with st.sidebar:
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
        version = st.text_input("Version", value="v3")
        model_input = st.text_input("Model override", value="")
        history_window = st.slider("History window", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Max tool rounds", min_value=1, max_value=6, value=4)
        system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        tools_path = ARTIFACTS_DIR / "tools.yaml"

        if st.button("Reset chat", use_container_width=True):
            reset_chat()
            st.rerun()

        st.caption("Transcript")
        if "transcript_file" in st.session_state:
            st.code(str(st.session_state.transcript_file.relative_to(ROOT)))

    model = model_input.strip() or None
    ensure_session(
        version=version,
        provider_name=provider_name,
        model=model,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )

    try:
        system_prompt, openai_tools = load_artifacts(str(system_prompt_path), str(tools_path))
        provider = provider_for(provider_name)
    except Exception as exc:
        st.error(f"Startup error: {type(exc).__name__}: {exc}")
        return

    st.caption(f"{len(openai_tools)} tools loaded from artifacts/tools.yaml")

    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            if turn.get("assistant_text"):
                st.write(turn["assistant_text"])

    user_text = st.chat_input("Ask for research, tweets, article summaries, papers, or policy lookup")
    if not user_text:
        return

    with st.chat_message("user"):
        st.write(user_text)

    turn_index = len(st.session_state.turns) + 1
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        with st.spinner("Running agent and tools..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model,
                    max_tool_rounds=max_tool_rounds,
                )
                turn_record.update(result)
                assistant_text = result.get("assistant_text", "")
                st.write(assistant_text)
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
            except Exception as exc:
                turn_record.update({
                    "status": "provider_error",
                    "error": f"{type(exc).__name__}: {str(exc)}",
                    "assistant_text": "Provider or tool error. Check configuration and transcript details.",
                })
                st.error(turn_record["error"])

    turn_record["ended_at"] = now_iso()
    st.session_state.turns.append(turn_record)
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_file, st.session_state.transcript)

    with st.sidebar:
        st.download_button(
            "Download transcript JSON",
            data=json_text(st.session_state.transcript),
            file_name=st.session_state.transcript_file.name,
            mime="application/json",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
