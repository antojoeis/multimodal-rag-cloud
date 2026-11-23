"""RAG step 1: turn images and text into vectors with CLIP and compare them.

Run on the test PC:  python scripts/embed_demo.py
Needs: pip install torch --index-url https://download.pytorch.org/whl/cpu
       pip install sentence-transformers
"""
from pathlib import Path

from PIL import Image
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("clip-ViT-B-32")  # downloads ~600 MB the first time

# 1. Embed every test image
paths = sorted(Path("eval/week2/images").glob("*.*"))
images = [Image.open(p).convert("RGB") for p in paths]
img_vecs = model.encode(images, convert_to_tensor=True, normalize_embeddings=True)
print(f"{len(paths)} images -> each is {img_vecs.shape[1]} numbers")
print("first 5 numbers of", paths[0].name, ":", [round(x, 3) for x in img_vecs[0][:5].tolist()])

# 2. Embed some text descriptions
texts = [
    "an oscilloscope screen with waveforms",
    "a close-up of a computer chip with printed text",
    "an empty power connector",
    "a table of test results",
    "a dark, blurry photo of a circuit board",
]
txt_vecs = model.encode(texts, convert_to_tensor=True, normalize_embeddings=True)

# 3. Compare: for each text, which images are closest?
scores = util.cos_sim(txt_vecs, img_vecs)
for i, text in enumerate(texts):
    print(f"\n'{text}'")
    for j in scores[i].argsort(descending=True)[:3]:
        print(f"   {scores[i][j]:.3f}  {paths[j].name}")

# 4. Image vs image: which test image is most similar to each one?
img_scores = util.cos_sim(img_vecs, img_vecs)
print("\nMost similar other image:")
for i, p in enumerate(paths):
    img_scores[i][i] = -1  # ignore itself
    j = int(img_scores[i].argmax())
    print(f"   {p.name:<32} -> {paths[j].name:<32} {img_scores[i][j]:.3f}")
