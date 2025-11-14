from doc_loader import doc_loader
from retriever import retriever
from generator import generator

def main():
    question = "What topic does anthony talk about in his essay?"

    doc_loader("data")
    docs = retriever(question)
    answer = generator(docs, question)

    print(answer)

if __name__ == "__main__":
    main()
