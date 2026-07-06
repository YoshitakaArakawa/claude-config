"""Dedupe contacts.csv on email. Usage: python dedupe.py in.csv out.csv"""
import csv
import sys


def dedupe(rows):
    seen = set()
    out = []
    for r in rows:
        key = r["email"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames
    kept = dedupe(rows)
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(kept)
    print(f"{len(rows)} rows in, {len(kept)} kept")


if __name__ == "__main__":
    main()
