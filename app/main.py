import pathlib
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from app.config import get_settings
from app.db import get_session

from app.ml import SpamModel
from app.models import SpamInference

from cassandra.cqlengine.management import sync_table
from cassandra.query import SimpleStatement

from app.schema import Query

app = FastAPI(
    version="1.0.0",
    title="DrexSpam",
    description="An Artificial Intelligence based Spam detector API using machine learning",
)

SETTINGS = get_settings()

BASE_DIR = pathlib.Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR.parent / "models"
SPAM_MODEL_DIR = MODEL_DIR / "spam"
SPAM_MODEL_PATH = SPAM_MODEL_DIR / "spam-model.h5"
SPAM_TOKENIZER_PATH = SPAM_MODEL_DIR / "spam-classifer-tokenizer.json"
SPAM_METADATA_PATH = SPAM_MODEL_DIR / "spam-classifer-metadata.json"

SPAM_MODEL = None
DB_SESSION = None
SPAM_INFERENCE = SpamInference

@app.on_event("startup")
def on_startup():
    global SPAM_MODEL, DB_SESSION
    SPAM_MODEL = SpamModel(
        model_path = SPAM_MODEL_PATH,
        tokenizer_path = SPAM_TOKENIZER_PATH,
        metadata_path= SPAM_METADATA_PATH,
    )
    DB_SESSION = get_session()
    sync_table(SPAM_INFERENCE)

@app.get("/")
def read_index(q: Optional[str] = None):
    return {"hello": "world"}

@app.post("/")
def create_infercence(q: Query):
    global SPAM_MODEL
    query = q.query or "Hello world"
    preds_dict = SPAM_MODEL.predict_text(query)
    top = preds_dict.get("top")
    data = {"query": query, **top}
    obj = SPAM_INFERENCE.objects.create(**data)
    return obj

@app.get("/inferences")
def get_inferences():
    q = SPAM_INFERENCE.objects.all()
    return list(q)

@app.get("/inferences/{my_uuid}")
def get_inference_detail(my_uuid):
    obj = SPAM_INFERENCE.objects.get(uuid=my_uuid)
    return obj 

def fetch_row(statement: SimpleStatement, fetch_size: int, session=None):
    statement.fetch_size = fetch_size
    result_set = session.execute(statement)
    has_pages = result_set.has_more_pages
    yield "uuid,label,confidence,query,model_version\n"
    while has_pages:
        for row in result_set.current_rows:
            yield f"{row['uuid']},{row['label']},{row['confidence']},{row['query']},{row['model_version']}\n"
        has_pages = result_set.has_more_pages
        result_set = session.execute(statement, paging_state=result_set.paging_state)

@app.get("/dataset")
def export_inferences():
    global DB_SESSION
    cql_query = "SELECT * FROM spam_inferences.spam_inference LIMIT 10000"
    # rows = DB_SESSION.execute(cql_query)
    statement = SimpleStatement(cql_query)
    return StreamingResponse(fetch_row(statement, 25, DB_SESSION))

