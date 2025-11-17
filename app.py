import os
import streamlit as st

from doc_loader import doc_loader
from routing import get_known_students, detect_route
from retriever import retriever
from generator import generator
from decomposer import decompose_question
from styles import apply_custom_styles

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
    
    def _save_uploaded(uploaded_file, filename: str):
        if uploaded_file is None:
            return
        target_path = os.path.join(base_dir, filename)
        with open(target_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    _save_uploaded(cv_file, "cv.txt")
    _save_uploaded(essay_file, "admission_essay.txt")
    _save_uploaded(rec_file, "recommendation_1.txt")
    return student_id, base_dir

def main():
    # Header with icon
    st.markdown("<h1>AI Admissions Helper</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 2rem;'>Your intelligent assistant for university admissions</p>", unsafe_allow_html=True)

    tab_ask, tab_add, tab_fit = st.tabs(["💬 Ask Questions", "➕ Add Student", "📊 Student Fit Test"])

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
                
                sub_questions = decompose_question(question)
                if len(sub_questions) > 1:
                    with st.expander("📋 Decomposed Sub-Questions", expanded=True):
                        for sq in sub_questions:
                            st.markdown(f"- {sq}")
                
                answers = []
                progress_bar = st.progress(0)
                for i, sq in enumerate(sub_questions):
                    docs = retriever(
                        question=sq,
                        student=route.student,
                        intent=route.intent,
                        known_students=known_students,
                    )
                    ans = generator(docs, sq)
                    answers.append(ans)
                    progress_bar.progress((i + 1) / len(sub_questions))
                
                if len(answers) == 1:
                    final_answer = answers[0]
                else:
                    final_answer = "Combined answer:\n" + "\n\n".join(
                        [f"**Sub-question:** {sub_questions[i]}\n\n**Answer:** {answers[i]}" for i in range(len(answers))]
                    )
                
                st.markdown("### 💡 Answer")
                st.text_area("", value=final_answer, height=300, label_visibility="collapsed")

    # ----------------------------
    # TAB 2: Add Student
    # ----------------------------
    with tab_add:
        st.markdown("### Add a new student to the database")
        st.info("📝 Fill in the student's name and upload **.txt** files. They will be stored under `data/students/<StudentID>/`.")
        
        student_name = st.text_input("👤 Student name", placeholder="e.g., Lucas Almeida")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            cv_file = st.file_uploader("📄 Upload CV (.txt)", type=["txt"], key="cv_uploader")
        with col2:
            essay_file = st.file_uploader("📝 Upload admission essay (.txt)", type=["txt"], key="essay_uploader")
        with col3:
            rec_file = st.file_uploader("✉️ Upload recommendation letter (.txt)", type=["txt"], key="rec_uploader")
        
        if st.button("💾 Save Student", use_container_width=True):
            if not student_name.strip():
                st.error("❌ Please enter a student name.")
            elif not any([cv_file, essay_file, rec_file]):
                st.error("❌ Please upload at least one file for this student.")
            else:
                student_id, folder = save_student_files(
                    student_name=student_name,
                    cv_file=cv_file,
                    essay_file=essay_file,
                    rec_file=rec_file,
                )
                st.success(
                    f"✅ Student **{student_name}** saved as folder `{student_id}` in `{folder}`.\n\n"
                    "You can now go to **Ask Questions** and query this student."
                )

    # ----------------------------
    # TAB 3: Student Fit Test
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
