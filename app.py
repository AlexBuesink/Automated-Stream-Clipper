import os
import difflib
import streamlit as st

from src.transcriber import transcribe_audio
from src.detector import detect_viral_moments
from src.subtitles import generate_ass_file, generate_hook_header_file
from src.render import render_clip

class EditableWord:
    def __init__(self, word, start, end):
        self.word = word
        self.start = start
        self.end = end

class EditableSegment:
    def __init__(self, words):
        self.words = words

st.set_page_config(page_title="Stream Clipper Studio", layout="wide")
st.title("🎬 Stream Clipper Studio")

if "transcribed" not in st.session_state:
    st.session_state.transcribed = False
    st.session_state.word_dicts = []
    st.session_state.moments = []
    st.session_state.input_video = ""

def process_render(idx, start_val, end_val, hook_val, cap_mode, ratio):
    output_clip = f"data/clips/ui_clip_{idx+1}.mp4"
    output_ass = f"data/clips/ui_clip_{idx+1}.ass"
    
    custom_words = [EditableWord(w["Word"], w["Start"], w["End"]) for w in st.session_state.word_dicts]
    custom_segments = [EditableSegment(custom_words)]
    
    ass_path = None
    if cap_mode == "subtitles":
        if generate_ass_file(
            raw_segments=custom_segments, 
            clip_start=start_val, 
            clip_end=end_val, 
            output_ass_path=output_ass,
            max_words_per_line=st.session_state.get("style_max_words", 4),
            font_name=st.session_state.get("style_font", "Arial Black"),
            font_size=st.session_state.get("style_size", 54),
            primary_color_hex=st.session_state.get("style_primary_color", "#FFFF00"),
            secondary_color_hex=st.session_state.get("style_secondary_color", "#FFFFFF"),
            outline_color_hex=st.session_state.get("style_outline_color", "#000000"),
            outline_thickness=st.session_state.get("style_outline_size", 5)
        ):
            ass_path = output_ass
            
    elif cap_mode == "hook":
        if hook_val.strip():
            if generate_hook_header_file(hook_val, end_val - start_val, output_ass):
                ass_path = output_ass

    success = render_clip(
        input_path=st.session_state.input_video,
        output_path=output_clip,
        start_time=start_val,
        end_time=end_val,
        aspect_ratio=ratio,
        subtitle_path=ass_path
    )
    return success, output_clip

with st.sidebar:
    st.header("⚙️ Global Settings")
    input_path = st.text_input("Input Video Path", value="data/raw/test_audio.mp4")
    
    if st.button("🚀 Analyze Video", type="primary"):
        if not os.path.exists(input_path):
            st.error(f"File not found: {input_path}")
        else:
            with st.spinner("Transcribing and analyzing..."):
                transcript, raw_segments = transcribe_audio(input_path)
                moments = detect_viral_moments(transcript)
                
                words_flat = []
                for seg in raw_segments:
                    if hasattr(seg, "words") and seg.words:
                        for w in seg.words:
                            words_flat.append({"Word": w.word, "Start": w.start, "End": w.end})
                
                st.session_state.word_dicts = words_flat
                st.session_state.transcribed = True
                st.session_state.moments = moments
                st.session_state.input_video = input_path
                st.success(f"Analysis complete! Found {len(moments)} moments.")

if st.session_state.transcribed:
    tab1, tab2, tab3 = st.tabs(["🎬 Clip Editor", "📝 Quick Paragraph Editor", "🎨 Subtitle Styling"])
    
    # ----------------------------------------
    # TAB 1: CLIP EDITOR
    # ----------------------------------------
    with tab1:
        st.subheader(f"Detected Highlights ({len(st.session_state.moments)})")
        if st.button("⚡ Render All Clips", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(len(st.session_state.moments)):
                status_text.text(f"Rendering Clip {i+1} of {len(st.session_state.moments)}...")
                process_render(
                    i, 
                    st.session_state[f"start_{i}"], st.session_state[f"end_{i}"], 
                    st.session_state[f"hook_{i}"], st.session_state[f"cap_{i}"], st.session_state[f"ratio_{i}"]
                )
                progress_bar.progress((i + 1) / len(st.session_state.moments))
                
            status_text.text("✅ All clips rendered successfully!")
        
        st.markdown("---")
        
        for idx, moment in enumerate(st.session_state.moments):
            with st.expander(f"Clip #{idx + 1}: Score {moment.get('virality_score', 'N/A')}/100", expanded=True):
                col_edit, col_render = st.columns([1, 1])

                with col_edit:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.number_input("Start Time (s)", value=float(moment["start_time"]), step=0.5, key=f"start_{idx}")
                    with c2:
                        st.number_input("End Time (s)", value=float(moment["end_time"]), step=0.5, key=f"end_{idx}")
                    
                    st.text_area("Hook Title", value=moment.get("hook_summary", "").replace("\\n", "\n"), key=f"hook_{idx}", height=68)
                    
                    c3, c4 = st.columns(2)
                    with c3:
                        st.selectbox("Caption Style", ["hook", "subtitles", "none"], key=f"cap_{idx}")
                    with c4:
                        st.selectbox("Aspect Ratio", ["1:1", "9:16", "16:9"], key=f"ratio_{idx}")

                with col_render:
                    output_clip_path = f"data/clips/ui_clip_{idx+1}.mp4"
                    if st.button(f"🎬 Render Clip #{idx+1}"):
                        with st.spinner("Rendering video..."):
                            success, out_path = process_render(
                                idx, st.session_state[f"start_{idx}"], st.session_state[f"end_{idx}"], 
                                st.session_state[f"hook_{idx}"], st.session_state[f"cap_{idx}"], st.session_state[f"ratio_{idx}"]
                            )
                        if success and os.path.exists(out_path):
                            st.video(out_path)
                    elif os.path.exists(output_clip_path):
                        st.video(output_clip_path)

    # ----------------------------------------
    # TAB 2: SMART PARAGRAPH EDITOR
    # ----------------------------------------
    with tab2:
        st.markdown("### 📝 Edit Captions like a Word Document")
        st.info("Fix typos, add words, or delete text normally. Timings for unchanged words are perfectly preserved.")
        
        clip_options = [f"Clip {i+1}" for i in range(len(st.session_state.moments))]
        selected_clip = st.selectbox("Select a clip to edit:", clip_options)
        
        if selected_clip:
            c_idx = int(selected_clip.replace("Clip ", "")) - 1
            c_start = st.session_state.get(f"start_{c_idx}", st.session_state.moments[c_idx]["start_time"])
            c_end = st.session_state.get(f"end_{c_idx}", st.session_state.moments[c_idx]["end_time"])
            
            global_indices = [i for i, w in enumerate(st.session_state.word_dicts) if w["Start"] >= c_start and w["End"] <= c_end]
            
            if global_indices:
                original_words_slice = [st.session_state.word_dicts[i] for i in global_indices]
                original_text = " ".join([w["Word"] for w in original_words_slice])
                
                new_text = st.text_area("Edit Transcript", value=original_text, height=200, key=f"text_edit_{c_idx}")
                
                if st.button("💾 Save Text Changes", type="primary"):
                    new_words = new_text.strip().split()
                    
                    if not new_words:
                        st.error("Transcript cannot be empty!")
                    elif len(new_words) == len(original_words_slice):
                        # 1:1 Replacement (Keeps Whisper's original timing exactly)
                        for i, nw in enumerate(new_words):
                            st.session_state.word_dicts[global_indices[i]]["Word"] = nw
                        st.success("Changes saved! All original timings perfectly preserved.")
                    else:
                        # Smart Difflib Recalculation (Locks untouched words, recalculates only changed words)
                        old_words = [w["Word"] for w in original_words_slice]
                        new_slice = [{"Word": w, "Start": 0.0, "End": 0.0} for w in new_words]
                        
                        matcher = difflib.SequenceMatcher(None, old_words, new_words)
                        
                        # Pass 1: Copy exact timings for untouched words
                        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                            if tag == 'equal':
                                for i, j in zip(range(i1, i2), range(j1, j2)):
                                    new_slice[j]["Start"] = original_words_slice[i]["Start"]
                                    new_slice[j]["End"] = original_words_slice[i]["End"]
                                    new_slice[j]["matched"] = True
                        
                        # Pass 2: Interpolate timings only for gaps/changed words
                        for j in range(len(new_slice)):
                            if not new_slice[j].get("matched"):
                                # Find time constraints from nearest locked words
                                prev_end = original_words_slice[0]["Start"]
                                for k in range(j-1, -1, -1):
                                    if new_slice[k].get("matched"):
                                        prev_end = new_slice[k]["End"]
                                        break
                                
                                next_start = original_words_slice[-1]["End"]
                                for k in range(j+1, len(new_slice)):
                                    if new_slice[k].get("matched"):
                                        next_start = new_slice[k]["Start"]
                                        break
                                
                                # Find boundaries of the current block of changed words
                                b_start = j
                                while b_start > 0 and not new_slice[b_start-1].get("matched"):
                                    b_start -= 1
                                b_end = j
                                while b_end < len(new_slice)-1 and not new_slice[b_end+1].get("matched"):
                                    b_end += 1
                                
                                block = new_slice[b_start:b_end+1]
                                total_chars = max(sum(len(w["Word"]) for w in block), 1)
                                time_gap = max(next_start - prev_end, 0.1) # Minimum 100ms gap failsafe
                                
                                current_t = prev_end
                                for idx in range(b_start, b_end + 1):
                                    dur = time_gap * (len(new_slice[idx]["Word"]) / total_chars)
                                    new_slice[idx]["Start"] = current_t
                                    new_slice[idx]["End"] = current_t + dur
                                    new_slice[idx]["matched"] = True
                                    current_t += dur

                        # Clean up temp flags
                        for w in new_slice:
                            w.pop("matched", None)

                        st.session_state.word_dicts[global_indices[0]:global_indices[-1]+1] = new_slice
                        st.success(f"Changes saved! Timing for untouched words locked. Edited words were intelligently synced.")
            else:
                st.warning("No words found for this clip's specific time range.")

    # ----------------------------------------
    # TAB 3: SUBTITLE STYLING
    # ----------------------------------------
    with tab3:
        st.markdown("### 🎨 Design Your Subtitles")
        st.info("These settings apply to 'subtitles' Caption Style. Tweak them and re-render a clip to see changes.")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.slider("Max Words Per Line", min_value=1, max_value=8, value=4, key="style_max_words")
            st.selectbox("Font Family", ["Arial Black", "Impact", "Verdana", "Tahoma", "Comic Sans MS"], key="style_font")
            st.slider("Font Size", min_value=30, max_value=100, value=54, key="style_size")
            st.slider("Outline Thickness", min_value=0, max_value=20, value=5, key="style_outline_size")
            
        with col_s2:
            st.color_picker("Primary Color (Active spoken word)", value="#FFFF00", key="style_primary_color")
            st.color_picker("Secondary Color (Inactive words)", value="#FFFFFF", key="style_secondary_color")
            st.color_picker("Outline/Border Color", value="#000000", key="style_outline_color")

else:
    st.info("👈 Enter the path to your video in the sidebar and click **Analyze Video** to load your clips.")