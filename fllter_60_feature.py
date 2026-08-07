"""Loc file du lieu, chi giu lai cac feature co trong feature_names.json.

Cach dung:
    python fllter_60_feature.py
    python fllter_60_feature.py --input output_after_preprocess/10pkt.xlsx \
                               --output output_after_preprocess/10pkt_60_features.csv
    python fllter_60_feature.py --drop-label      # bo cot Label khoi file ket qua
"""

import argparse
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "output_after_preprocess"

DEFAULT_INPUT = OUT_DIR / "10pkt.xlsx"
DEFAULT_FEATURES = OUT_DIR / "feature_names.json"
DEFAULT_OUTPUT = OUT_DIR / "10pkt_60_features.csv"

LABEL_COL = "Label"


def read_table(path: Path) -> pd.DataFrame:
    """Doc file .xlsx/.xls hoac .csv."""
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def write_table(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        df.to_excel(path, index=False)
    else:
        df.to_csv(path, index=False)


def filter_features(
    df: pd.DataFrame, features: list[str], keep_label: bool = True
) -> pd.DataFrame:
    """Giu lai cac cot trong `features`, dung dung thu tu cua feature_names.json."""
    # Chuan hoa ten cot (bo khoang trang thua) de tranh lech ten khi doc file
    df = df.rename(columns=lambda c: str(c).strip())
    lookup = {c.strip().lower(): c for c in df.columns}

    selected, missing = [], []
    for feat in features:
        col = lookup.get(feat.strip().lower())
        if col is None:
            missing.append(feat)
        else:
            selected.append(col)

    if missing:
        raise KeyError(
            f"Thieu {len(missing)} feature trong file input: {missing}"
        )

    if keep_label and LABEL_COL in df.columns and LABEL_COL not in selected:
        selected.append(LABEL_COL)

    return df[selected]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Giu lai cac feature co trong feature_names.json"
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--drop-label",
        action="store_true",
        help="Khong giu cot Label trong file ket qua",
    )
    args = parser.parse_args()

    with open(args.features, encoding="utf-8") as f:
        features = json.load(f)

    df = read_table(args.input)
    print(f"Input : {args.input}  ->  {df.shape[0]} dong, {df.shape[1]} cot")

    filtered = filter_features(df, features, keep_label=not args.drop_label)

    dropped = [c for c in df.columns if c not in set(filtered.columns)]
    print(f"Da bo {len(dropped)} cot: {dropped}")

    write_table(filtered, args.output)
    print(
        f"Output: {args.output}  ->  {filtered.shape[0]} dong, "
        f"{filtered.shape[1]} cot ({len(features)} feature"
        f"{' + Label' if LABEL_COL in filtered.columns else ''})"
    )


if __name__ == "__main__":
    main()
