from sentence_transformers import SentenceTransformer
model = SentenceTransformer("moka-ai/m3e-base")
model.save("./models/m3e-base")