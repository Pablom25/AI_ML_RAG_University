import os
import whisper

def main():
    base_dir = os.path.dirname(__file__)
    model_dir = os.path.join(base_dir, "whisper_models")
    os.makedirs(model_dir, exist_ok=True)

    # Use the smallest model: "tiny"
    print("Downloading Whisper 'tiny' model into:", model_dir)
    _ = whisper.load_model("tiny", download_root=model_dir)
    print("Done. Model is stored in:", model_dir)

if __name__ == "__main__":
    main()
