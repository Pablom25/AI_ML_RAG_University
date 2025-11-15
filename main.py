from doc_loader import doc_loader
from routing import detect_route, get_known_students
from retriever import retriever
from generator import generator

def main():
    question = "Does Sofia Martinez's admission essay relate to the university values?"

    doc_loader("data")
    known_students = get_known_students()
    route = detect_route(question, known_students)
    print("Route: ", route)
    docs = retriever(question, route.student, route.intent, known_students)
    print("Docs: ", docs)
    answer = generator(docs, question)
    print("\n Answer: \n", answer)

if __name__ == "__main__":
    main()
