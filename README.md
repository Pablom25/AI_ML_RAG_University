This is a RAG solution for a university

# Set up

To get everything set-up run the following code on your terminal. You must have python 3.12 and Ollama in your computer.

```
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
ollama pull llama3.1:8b
ollama pull mxbai-embed-large
brew install ffmpeg
```

# Run the Streamlit app

From the project root (same folder as app.py) with the virtual environment activated:
```
python -m streamlit run app.py
```
