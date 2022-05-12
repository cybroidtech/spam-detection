import json
from multiprocessing.spawn import spawn_main
import pathlib
from typing import Optional
from fastapi import FastAPI
from keras.models import load_model
from keras_preprocessing.text import tokenizer_from_json
from keras_preprocessing.sequence import pad_sequences

app = FastAPI(
    version="1.0.0",
    title="DrexSpam",
    description="An Artificial Intelligence based Spam detector API using machine learning",
)

BASE_DIR = pathlib.Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR.parent / "models"
SPAM_MODEL_DIR = MODEL_DIR / "spam"
SPAM_MODEL_PATH = SPAM_MODEL_DIR / "spam-model.h5"
SPAM_TOKENIZER_PATH = SPAM_MODEL_DIR / "spam-classifer-tokenizer.json"
SPAM_METADATA_PATH = SPAM_MODEL_DIR / "spam-classifer-metadata.json"

SPAM_MODEL = None
SPAM_TOKENIZER = None
SPAM_METADATA = {}
LEGEND_INVERTED = {}

@app.on_event("startup")
def on_startup():
    global SPAM_MODEL, SPAM_TOKENIZER, SPAM_METADATA, LEGEND_INVERTED
    # Load model
    if SPAM_MODEL_PATH.exists():
        SPAM_MODEL = load_model(SPAM_MODEL_PATH)
    if SPAM_TOKENIZER_PATH.exists():
        t_json = SPAM_TOKENIZER_PATH.read_text()
        SPAM_TOKENIZER = tokenizer_from_json(t_json)
    if SPAM_METADATA_PATH.exists():
        SPAM_METADATA = json.loads(SPAM_METADATA_PATH.read_text())
        LEGEND_INVERTED = SPAM_METADATA["labels_legend_inverted"]

def predict(query: str):
    sequences = SPAM_TOKENIZER.texts_to_sequences([query])
    maxlen = SPAM_METADATA.get("max_sequence") or 280
    x_input = pad_sequences(sequences, maxlen=280)
    preds_array = SPAM_MODEL.predict(x_input)
    return {}


@app.get("/")
def read_index(q: Optional[str] = None):
    global SPAM_MODEL, SPAM_METADATA
    query = q or "Hello world"
    print(SPAM_MODEL)
    return {"query": query, **SPAM_METADATA}
