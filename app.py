import streamlit as st
from doc_loader import doc_loader
from retriever import retriever
from generator import generator


def main():
    st.title("AI Admissions Helper")

    question = st.text_input("Enter your question:")

    if st.button("Submit"):
        if question.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Build / update the Chroma DB (same as in main.py)
            doc_loader("data")

            # Retrieve docs and generate answer
            docs = retriever(question)
            answer = generator(docs, question)

            st.text_area("Answer:", value=answer, height=200)


if __name__ == "__main__":
    main()
