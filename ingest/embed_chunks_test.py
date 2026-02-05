from sentence_transformers import SentenceTransformer

import numpy as np

def main():
    # ladataan malli
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # testidata

    chunks = [
        "Fuel pump removal procedure",
        "brake system bleeding instructions",
        "Torque specifications for suspension bolts",
    ]

    # embedding
    emb = model.encode(chunks)

    # muunnetaan float32
    emb = emb.astype(np.float32)

    # varmennus
    print("emb type", type(emb))
    print("emb dtype", emb.dtype)
    print("emb shape", emb.shape)

if __name__ == "__main__":
    main()
