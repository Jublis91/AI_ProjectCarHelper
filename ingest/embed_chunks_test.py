"""Quick sanity check for sentence transformer embeddings."""

from sentence_transformers import SentenceTransformer

import numpy as np

def main():
    """Run a simple embedding flow and print shape/type info."""
    # Load the sentence-transformer model once for reuse.
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Example input sentences used to verify embeddings.
    chunks = [
        "Fuel pump removal procedure",
        "brake system bleeding instructions",
        "Torque specifications for suspension bolts",
    ]

    # Produce embeddings from the input text.
    emb = model.encode(chunks)

    # Convert to float32 to match storage/serialization expectations.
    emb = emb.astype(np.float32)

    # Simple verification output for shape and dtype.
    print("emb type", type(emb))
    print("emb dtype", emb.dtype)
    print("emb shape", emb.shape)

if __name__ == "__main__":
    main()
