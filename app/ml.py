from dataclasses import dataclass
import json
import numpy as np
from pathlib import Path
from typing import Any, List, Optional
from importlib_metadata import metadata
from keras.models import load_model
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import tokenizer_from_json

from app.encoders import NumpyEncoder, encode_to_json


@dataclass
class SpamModel:
    """Drex Machine Learning Spam Classifier Model"""

    model_path: Path
    metadata_path: Optional[Path] = None
    tokenizer_path: Optional[Path] = None

    model = None
    tokenizer = None
    metadata = None

    def __post_init__(self):
        if self.model_path.exists():
            self.model = load_model(self.model_path)
        if self.tokenizer_path:
            if self.tokenizer_path.exists():
                if self.is_json(self.tokenizer_path):
                    tokenizer_text = self.tokenizer_path.read_text()
                    self.tokenizer = tokenizer_from_json(tokenizer_text)
        if self.metadata_path:
            if self.metadata_path.exists():
                if self.is_json(self.metadata_path):
                    metadata_text = self.metadata_path.read_text()
                    self.metadata = json.loads(metadata_text)

    def get_model(self):
        if not self.model:
            raise Exception("Model not loaded")
        return self.model

    def get_tokenizer(self):
        if not self.tokenizer:
            raise Exception("Tokenizer not loaded")
        return self.tokenizer

    def get_metadata(self):
        if not self.metadata:
            raise Exception("Metadata not loaded")
        return self.metadata

    def get_sequences_from_text(self, texts: List[str]):
        tokenizer = self.get_tokenizer()
        sequences = tokenizer.texts_to_sequences(texts)
        return sequences

    def get_input_from_sequences(self, sequences: List[Any]):
        metadata = self.get_metadata()
        maxlen = metadata.get("max_sequence") or 280
        x_input = pad_sequences(sequences, maxlen)
        return x_input

    def get_label_legend_inverted(self):
        metadata = self.get_metadata()
        legend = metadata.get("labels_legend_inverted") or {}
        if len(legend.keys()) != 2:
            raise Exception("Legend invalid")
        return legend

    def get_label_pred(self, index: int, val):
        label_legend_inverted = self.get_label_legend_inverted()
        labeled_pred = {
            "label": label_legend_inverted[str(index)],
            "confidence": val,
        }
        return labeled_pred

    def get_top_label_pred(self, preds):
        top_index = np.argmax(preds)
        top_pred = self.get_label_pred(top_index, preds[top_index])
        return top_pred

    def is_json(self, path: Path):
        if path.name.endswith(".json"):
            return True
        return False

    def predict_text(self, query: str, include_top=True, encode_json=True):
        model = self.get_model()
        sequences = self.get_sequences_from_text([query])
        x_input = self.get_input_from_sequences(sequences)
        preds_array = model.predict(x_input)[0]
        preds = [self.get_label_pred(i, x) for i, x in enumerate(list(preds_array))]
        results = {"predictions": preds}
        if include_top:
            results["top"] = self.get_top_label_pred(preds_array)
        if encode_json:
            results = encode_to_json(results)
        return results
