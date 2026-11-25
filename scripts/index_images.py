"""RAG step 2: store CLIP vectors in Postgres + pgvector and search them with SQL.

Start the database first:  docker compose up -d db
Then run:                  python scripts/index_images.py
"""
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from PIL import Image
from sentence_transformers import SentenceTransformer

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://rag:rag@localhost:5432/rag")
IMAGE_DIR = Path("eval/week2/images")

SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS refs (
    id        serial PRIMARY KEY,
    name      text UNIQUE NOT NULL,
    note      text,                     -- filled in step 3 (knowledge base)
    embedding vector(512) NOT NULL      -- CLIP ViT-B/32 gives 512 numbers
);
"""

# <=> is pgvector's cosine distance (0 = same direction). Similarity = 1 - distance.
SEARCH = """
SELECT name, 1 - (embedding <=> %(v)s) AS similarity
FROM refs
ORDER BY embedding <=> %(v)s
LIMIT %(k)s
"""


def search(conn, vector, k=3):
    return conn.execute(SEARCH, {"v": vector, "k": k}).fetchall()


def show(title, rows):
    print(f"\n{title}")
    for name, sim in rows:
        print(f"   {sim:.3f}  {name}")


def main():
    model = SentenceTransformer("clip-ViT-B-32")

    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute(SCHEMA)
        register_vector(conn)  # lets us pass numpy arrays as vectors

        # 1. Store: embed each image and save it (re-running updates, never duplicates)
        paths = sorted(IMAGE_DIR.glob("*.*"))
        vectors = model.encode([Image.open(p).convert("RGB") for p in paths], normalize_embeddings=True)
        for path, vec in zip(paths, vectors):
            conn.execute(
                "INSERT INTO refs (name, embedding) VALUES (%s, %s) "
                "ON CONFLICT (name) DO UPDATE SET embedding = EXCLUDED.embedding",
                (path.name, vec),
            )
        count = conn.execute("SELECT count(*) FROM refs").fetchone()[0]
        print(f"Stored {len(paths)} images. Table 'refs' now has {count} rows.")

        # 2. Search with text: the database does the ranking now, not Python
        for text in ["an oscilloscope screen with waveforms", "a table of test results"]:
            show(f"Text search: '{text}'", search(conn, model.encode(text, normalize_embeddings=True)))

        # 3. Search with an image: this is how RAG will find a reference for an uploaded photo
        query = IMAGE_DIR / "12_modem_pcb_dark_blurry.jpg"
        vec = model.encode(Image.open(query).convert("RGB"), normalize_embeddings=True)
        show(f"Image search: {query.name}", search(conn, vec))


if __name__ == "__main__":
    main()
