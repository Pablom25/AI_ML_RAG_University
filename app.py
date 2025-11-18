import os
import streamlit as st

from doc_loader import doc_loader
from routing import get_known_students, detect_route
from retriever import retriever
from generator import generator
from styles import apply_custom_styles
from file_converter import convert_and_save
from audio_transcriber import transcribe_audio_file

from audio_recorder_streamlit import audio_recorder
import io
import datetime

# Page configuration
st.set_page_config(
    page_title="AI Admissions Helper",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

def _student_name_to_id(name: str) -> str:
    return "".join(name.split())


def save_student_files(student_name: str, cv_file, essay_file, rec_file):
    student_id = _student_name_to_id(student_name)
    base_dir = os.path.join("data", "students", student_id)
    os.makedirs(base_dir, exist_ok=True)

    def _save_uploaded(uploaded_file, filename: str) -> bool:
        """Return True if saved OK or file was None; False if failed."""
        if uploaded_file is None:
            return True  # nothing to do, but it's not an error
        target_path = os.path.join(base_dir, filename)
        result = convert_and_save(uploaded_file, target_path)
        return result is not None

    ok_cv = _save_uploaded(cv_file, "cv.txt")
    ok_essay = _save_uploaded(essay_file, "admission_essay.txt")
    ok_rec = _save_uploaded(rec_file, "recommendation_1.txt")

    success = ok_cv and ok_essay and ok_rec
    return student_id, base_dir, success

def save_interview_audio_and_transcript(student_name: str, audio_file, transcript_text: str):
    """
    Save the raw audio file and its transcript under the student's folder.

    Returns:
        student_id (str), audio_path (str), transcript_path (str)
    """
    student_id = _student_name_to_id(student_name)
    base_dir = os.path.join("data", "students", student_id)
    os.makedirs(base_dir, exist_ok=True)

    # Build filenames with timestamp to avoid collisions
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Audio file
    audio_ext = os.path.splitext(audio_file.name)[1] or ".wav"
    audio_filename = f"interview_{timestamp}{audio_ext}"
    audio_path = os.path.join(base_dir, audio_filename)

    # Transcript file
    transcript_filename = f"interview_{timestamp}.txt"
    transcript_path = os.path.join(base_dir, transcript_filename)

    # Save audio bytes
    audio_bytes = audio_file.getvalue()  # works reliably even after .read()
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    # Save transcript text
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(
            f"Source: Interview audio\n"
            f"Student ID: {student_id}\n"
            f"Date: {datetime.datetime.now().isoformat()}\n\n"
            f"{transcript_text}"
        )

    return student_id, audio_path, transcript_path


def main():
    # Header with icon
    st.markdown("<h1>AI Admissions Helper</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 2rem;'>Your intelligent assistant for university admissions</p>", unsafe_allow_html=True)

    tab_ask, tab_add, tab_interview, tab_fit = st.tabs(
        ["💬 Ask Questions", "➕ Add Student", "🎙️ Interview Audio", "📊 Student Fit Test"]
    )

    # ----------------------------
    # TAB 1: Ask Questions
    # ----------------------------
    with tab_ask:
        st.markdown("### Ask questions about students and the university")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input("🔍 Enter your question:", placeholder="e.g., What are the most common nationalities?")
        with col2:
            st.write("")  # Spacing
            submit_btn = st.button("🚀 Submit", type="primary", use_container_width=True)
        
        if submit_btn:
            if not question.strip():
                st.warning("⚠️ Please enter a question.")
            else:
                with st.spinner("🔄 Building / updating knowledge base..."):
                    doc_loader("data")
                
                with st.spinner("🧭 Routing your question..."):
                    known_students = get_known_students()
                    route = detect_route(question, known_students)
                
                with st.spinner("Retrieving relevant documents..."):
                    docs = retriever(
                        question=question,
                        student=route.student,
                        intent=route.intent,
                        known_students=known_students,
                    )
                
                with st.spinner("Generating answer..."):
                    answer = generator(docs, question)

                st.text_area("Answer:", value=answer, height=250)

    # ----------------------------
    # TAB 2: Add Student
    # ----------------------------
    with tab_add:
        st.markdown("### Add a new student to the database or update student information")
        st.info("📝 Fill in the student's name and upload **.txt or .pdf** files. They will be stored under `data/students/<StudentID>/` as .txt.")

        student_name = st.text_input("👤 Student name", placeholder="e.g., Lucas Almeida")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            cv_file = st.file_uploader("📄 Upload CV (.txt or .pdf)", type=["txt", "pdf"], key="cv_uploader")
        with col2:
            essay_file = st.file_uploader("📝 Upload admission essay (.txt or .pdf)", type=["txt", "pdf"],
                                          key="essay_uploader")
        with col3:
            rec_file = st.file_uploader("✉️ Upload recommendation letter (.txt or .pdf)", type=["txt", "pdf"],
                                        key="rec_uploader")

        if st.button("💾 Save Student", use_container_width=True):
            if not student_name.strip():
                st.error("❌ Please enter a student name.")
            elif not any([cv_file, essay_file, rec_file]):
                st.error("❌ Please upload at least one file for this student.")
            else:
                student_id, folder, success = save_student_files(
                    student_name=student_name,
                    cv_file=cv_file,
                    essay_file=essay_file,
                    rec_file=rec_file,
                )

                if not success:
                    st.error("❌ There was a problem processing one of the files. "
                             "Make sure they are valid .txt or .pdf files.")
                else:
                    st.success(
                        f"✅ Student **{student_name}** saved as folder `{student_id}` in `{folder}`.\n\n"
                        "You can now go to **Ask Questions** and query this student."
                    )
                    doc_loader("data", force_reload=True)
    # ----------------------------
    # TAB 3: Interview Audio (upload or record + transcribe)
    # ----------------------------
    with tab_interview:
        st.markdown("### 🎙️ Interview Audio")
        st.info(
            "You can either upload an existing audio file of a student interview, "
            "or record a new one directly in the browser. "
            "The app will transcribe it and save both the audio and the transcript "
            "under that student's folder in `data/students/<StudentID>/`."
        )

        # 1. Select existing student or type a new one (shared for both flows)
        known_students = get_known_students()
        existing_display_names = [name.replace("_", " ").title() for name in known_students]
        existing_display_names_with_none = ["(None)"] + existing_display_names

        col1, col2 = st.columns(2)
        with col1:
            selected_existing = st.selectbox(
                "👨‍🎓 Select existing student (optional)",
                existing_display_names_with_none,
            )
        with col2:
            new_student_name = st.text_input(
                "Or enter a new student name",
                placeholder="e.g., Maria Gomez",
            )

        # Resolve final student name
        chosen_student_name = None
        if new_student_name.strip():
            chosen_student_name = new_student_name.strip()
        elif selected_existing != "(None)":
            chosen_student_name = selected_existing

        # ----------------------------------------
        # A) Upload existing audio
        # ----------------------------------------
        with st.expander("📂 Upload existing interview audio", expanded=True):
            audio_file = st.file_uploader(
                "🎧 Upload interview audio file",
                type=["wav", "mp3", "m4a", "ogg"],
                key="upload_audio_file",
            )

            if st.button("🚀 Transcribe and save uploaded interview", type="primary", key="transcribe_upload"):
                if chosen_student_name is None:
                    st.warning("⚠️ Please select or enter a student name first.")
                elif audio_file is None:
                    st.warning("⚠️ Please upload an audio file.")
                else:
                    with st.spinner("🔊 Transcribing uploaded audio..."):
                        transcript_text = transcribe_audio_file(audio_file, language=None)

                    if not transcript_text.strip():
                        st.error("❌ Transcription failed or returned empty text.")
                    else:
                        student_id, audio_path, transcript_path = save_interview_audio_and_transcript(
                            chosen_student_name, audio_file, transcript_text
                        )

                        st.success(
                            f"✅ Interview saved for student ID `{student_id}`.\n\n"
                            f"- Audio: `{os.path.basename(audio_path)}`\n"
                            f"- Transcript: `{os.path.basename(transcript_path)}`"
                        )
                        doc_loader("data", force_reload=True)

                        st.markdown("#### 📝 Transcript preview (uploaded)")
                        st.text_area(
                            "",
                            value=transcript_text,
                            height=300,
                            label_visibility="collapsed",
                            key="uploaded_transcript_preview",
                        )

                        st.info(
                            "This transcript will be picked up automatically the next "
                            "time the knowledge base is loaded (e.g., when you ask a question)."
                        )

        # ----------------------------------------
        # B) Record a new interview
        # ----------------------------------------
        with st.expander("🎙️ Record a new interview", expanded=False):
            st.markdown(
                "Click the button below to start/stop recording using your microphone. "
                "Once you're happy with the recording, you can transcribe and save it "
                "for the selected student."
            )

            recorded_audio = audio_recorder(
                text="Click to start / stop recording",
                recording_color="#e3342f",  # red-ish while recording
                neutral_color="#4b5563",  # gray when idle
                icon_name="microphone",
                icon_size="2x",
            )

            if recorded_audio is not None:
                st.markdown("#### 🔊 Recorded audio preview")
                st.audio(recorded_audio, format="audio/wav")

                if st.button("🚀 Transcribe and save recorded interview", type="primary", key="transcribe_recorded"):
                    if chosen_student_name is None:
                        st.warning("⚠️ Please select or enter a student name first.")
                    else:
                        # Wrap the raw bytes in a file-like object that mimics an UploadedFile
                        recorded_file = io.BytesIO(recorded_audio)
                        recorded_file.name = "recorded_interview.wav"

                        with st.spinner("🔊 Transcribing recorded audio..."):
                            transcript_text = transcribe_audio_file(recorded_file, language=None)

                        if not transcript_text.strip():
                            st.error("❌ Transcription failed or returned empty text.")
                        else:
                            # We can reuse the same helper to save audio + transcript
                            student_id, audio_path, transcript_path = save_interview_audio_and_transcript(
                                chosen_student_name, recorded_file, transcript_text
                            )

                            st.success(
                                f"✅ Recorded interview saved for student ID `{student_id}`.\n\n"
                                f"- Audio: `{os.path.basename(audio_path)}`\n"
                                f"- Transcript: `{os.path.basename(transcript_path)}`"
                            )
                            doc_loader("data", force_reload=True)

                            st.markdown("#### 📝 Transcript preview (recorded)")
                            st.text_area(
                                "",
                                value=transcript_text,
                                height=300,
                                label_visibility="collapsed",
                                key="recorded_transcript_preview",
                            )

                            st.info(
                                "This transcript will be picked up automatically the next "
                                "time the knowledge base is loaded (e.g., when you ask a question)."
                            )

    # ----------------------------
    # TAB 4: Student Fit Test
    # ----------------------------
    with tab_fit:
        st.markdown("### Test Student Fit for University")
        st.info("🎯 Evaluate how well a student aligns with university values, grades, and program requirements.")
        
        with st.spinner("📚 Loading students..."):
            known_students = get_known_students()
        
        if not known_students:
            st.warning("⚠️ No students found in the database.")
        else:
            student_display_names = [name.replace("_", " ").title() for name in known_students]
            selected_student = st.selectbox("👨‍🎓 Select a student to evaluate:", student_display_names)
            
            if st.button("🔍 Evaluate Fit", use_container_width=True):
                with st.spinner("⚙️ Analyzing student profile..."):
                    student_id = _student_name_to_id(selected_student)
                    fit_question = (
                        "Evaluate how well this student fits the university. "
                        "Consider their grades, alignment of goals and values with the university, "
                        "and relevance of their experience to their chosen degree. "
                        "Classify the fit as 'bad fit', 'medium fit', or 'good fit'. "
                        "Provide a summary of their profile and explain the rating."
                    )
                    
                    docs = retriever(
                        question=fit_question,
                        student=student_id,
                        intent="mixed",
                        known_students=known_students,
                    )
                    
                    fit_prompt = """You are an admissions expert. 
Given the following student documents and university information, evaluate the student's fit for the university.

CONTEXT:
{context}

INSTRUCTIONS:
- Assess grades, goals, values, and relevant experience.
- Classify the fit as 'bad fit', 'medium fit', or 'good fit'.
- Provide a concise summary of the student's profile.
- Explain clearly why you gave this rating.

Your answer should start with: "Fit: <bad fit/medium fit/good fit>"
Then provide the summary and explanation.
"""
                    context = "\n\n".join([doc.page_content for doc in docs])
                    from langchain.prompts import ChatPromptTemplate
                    from langchain_core.output_parsers import StrOutputParser
                    from langchain_community.chat_models import ChatOllama
                    
                    prompt = ChatPromptTemplate.from_template(fit_prompt)
                    llm = ChatOllama(model="llama3.1:8b", temperature=0)
                    chain = prompt | llm | StrOutputParser()
                    fit_answer = chain.invoke({"context": context})
                
                st.markdown("### 📊 Student Fit Evaluation")
                
                # Parse fit level and show with colors
                if "good fit" in fit_answer.lower():
                    st.success("✅ GOOD FIT")
                elif "medium fit" in fit_answer.lower():
                    st.warning("⚠️ MEDIUM FIT")
                else:
                    st.error("❌ BAD FIT")
                
                st.text_area("", value=fit_answer, height=300, label_visibility="collapsed")

if __name__ == "__main__":
    main()
