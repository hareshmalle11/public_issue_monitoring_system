from __future__ import annotations

import argparse
import json
import pickle
import re
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import (
    Bidirectional,
    Dense,
    Dropout,
    Embedding,
    Input,
    LSTM,
)
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = BASE_DIR / "grievance_dataset_70k_merged.csv"
DEFAULT_OUTPUT_DIR = BASE_DIR / "saved_model"

CATEGORY_CLASSES = [
    "Water",
    "Roads",
    "Electricity",
    "Sanitation",
    "Drainage",
    "Traffic",
    "Public Property",
    "Environment",
]

PRIORITY_CLASSES = ["Low", "Medium", "High"]


def clean_text(text: object) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    df = pd.read_csv(dataset_path)
    required_columns = {"complaint_text", "category", "priority"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Dataset is missing columns: {sorted(missing_columns)}")

    df = df.dropna(subset=["complaint_text", "category", "priority"]).copy()
    df["complaint_text"] = df["complaint_text"].map(clean_text)
    df["category"] = df["category"].astype(str).str.strip()
    df["priority"] = df["priority"].astype(str).str.strip()
    df = df[df["complaint_text"].str.len() > 0]

    return df


def fit_encoder(values: pd.Series, preferred_classes: list[str]) -> LabelEncoder:
    available_classes = list(dict.fromkeys(values.tolist()))
    ordered_classes = [label for label in preferred_classes if label in available_classes]
    ordered_classes.extend(label for label in sorted(available_classes) if label not in ordered_classes)

    encoder = LabelEncoder()
    encoder.classes_ = np.array(ordered_classes)
    return encoder


def build_model(
    vocab_size: int,
    max_length: int,
    embedding_dim: int,
    lstm_units: int,
    category_count: int,
    priority_count: int,
    dropout: float,
) -> Model:
    text_input = Input(shape=(max_length,), name="complaint_text")

    x = Embedding(
        input_dim=vocab_size,
        output_dim=embedding_dim,
        input_length=max_length,
        name="embedding",
    )(text_input)
    x = Bidirectional(LSTM(lstm_units), name="bi_lstm")(x)
    x = Dropout(dropout, name="dropout")(x)
    shared_features = Dense(64, activation="relu", name="shared_features")(x)

    category_output = Dense(
        category_count,
        activation="softmax",
        name="category_output",
    )(shared_features)
    priority_output = Dense(
        priority_count,
        activation="softmax",
        name="priority_output",
    )(shared_features)

    model = Model(
        inputs=text_input,
        outputs={
            "category_output": category_output,
            "priority_output": priority_output,
        },
        name="multi_task_grievance_bilstm",
    )

    model.compile(
        optimizer="adam",
        loss={
            "category_output": "sparse_categorical_crossentropy",
            "priority_output": "sparse_categorical_crossentropy",
        },
        metrics={
            "category_output": ["accuracy"],
            "priority_output": ["accuracy"],
        },
    )

    return model


def save_artifacts(
    output_dir: Path,
    tokenizer: Tokenizer,
    category_encoder: LabelEncoder,
    priority_encoder: LabelEncoder,
    config: dict[str, object],
    history: tf.keras.callbacks.History,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "tokenizer.json").write_text(tokenizer.to_json(), encoding="utf-8")

    with (output_dir / "category_label_encoder.pkl").open("wb") as file:
        pickle.dump(category_encoder, file)
    with (output_dir / "priority_label_encoder.pkl").open("wb") as file:
        pickle.dump(priority_encoder, file)

    label_mappings = {
        "category": {
            label: int(index) for index, label in enumerate(category_encoder.classes_)
        },
        "priority": {
            label: int(index) for index, label in enumerate(priority_encoder.classes_)
        },
    }
    (output_dir / "label_mappings.json").write_text(
        json.dumps(label_mappings, indent=2),
        encoding="utf-8",
    )
    (output_dir / "training_config.json").write_text(
        json.dumps(config, indent=2),
        encoding="utf-8",
    )

    pd.DataFrame(history.history).to_csv(output_dir / "training_history.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a multi-task Bi-LSTM for grievance category and priority."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--vocab-size", type=int, default=10000)
    parser.add_argument("--max-length", type=int, default=100)
    parser.add_argument("--embedding-dim", type=int, default=128)
    parser.add_argument("--lstm-units", type=int, default=128)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--validation-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_path = args.dataset.resolve()
    output_dir = args.output_dir.resolve()
    model_path = output_dir / "grievance_bilstm_multi_task.keras"

    print(f"Loading dataset: {dataset_path}")
    df = load_dataset(dataset_path)

    category_encoder = fit_encoder(df["category"], CATEGORY_CLASSES)
    priority_encoder = fit_encoder(df["priority"], PRIORITY_CLASSES)

    category_labels = category_encoder.transform(df["category"])
    priority_labels = priority_encoder.transform(df["priority"])
    stratify_labels = df["category"].astype(str) + "__" + df["priority"].astype(str)

    x_train_text, x_val_text, y_cat_train, y_cat_val, y_pri_train, y_pri_val = train_test_split(
        df["complaint_text"],
        category_labels,
        priority_labels,
        test_size=args.validation_size,
        random_state=args.random_state,
        stratify=stratify_labels,
    )

    tokenizer = Tokenizer(num_words=args.vocab_size, oov_token="<OOV>")
    tokenizer.fit_on_texts(x_train_text)

    x_train = pad_sequences(
        tokenizer.texts_to_sequences(x_train_text),
        maxlen=args.max_length,
        padding="post",
        truncating="post",
    )
    x_val = pad_sequences(
        tokenizer.texts_to_sequences(x_val_text),
        maxlen=args.max_length,
        padding="post",
        truncating="post",
    )

    model = build_model(
        vocab_size=args.vocab_size,
        max_length=args.max_length,
        embedding_dim=args.embedding_dim,
        lstm_units=args.lstm_units,
        category_count=len(category_encoder.classes_),
        priority_count=len(priority_encoder.classes_),
        dropout=args.dropout,
    )
    model.summary()

    output_dir.mkdir(parents=True, exist_ok=True)
    callbacks = [
        ModelCheckpoint(
            filepath=model_path,
            monitor="val_loss",
            save_best_only=True,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    history = model.fit(
        x_train,
        {
            "category_output": y_cat_train,
            "priority_output": y_pri_train,
        },
        validation_data=(
            x_val,
            {
                "category_output": y_cat_val,
                "priority_output": y_pri_val,
            },
        ),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
    )

    model.save(model_path)

    config = {
        "dataset": str(dataset_path),
        "model_path": str(model_path),
        "rows": int(len(df)),
        "vocab_size": args.vocab_size,
        "max_length": args.max_length,
        "embedding_dim": args.embedding_dim,
        "lstm_units": args.lstm_units,
        "dropout": args.dropout,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "category_classes": category_encoder.classes_.tolist(),
        "priority_classes": priority_encoder.classes_.tolist(),
    }
    save_artifacts(output_dir, tokenizer, category_encoder, priority_encoder, config, history)

    print(f"Saved model to: {model_path}")
    print(f"Saved tokenizer, label encoders, mappings, and history to: {output_dir}")


if __name__ == "__main__":
    main()
