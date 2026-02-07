# AI Project Car Helper, MVP

AI-projektiautoavustaja: FastAPI-backend + Streamlit-käyttöliittymä. Data pysyy lokaalissa SQLite-tietokannassa ja vastaukset tulevat ainoastaan omista lähteistä (PDF-manuaali + osalista).

## Esivaatimukset

- Python 3.10+
- Git
- Windows: Git Bash tai PowerShell

## Kehitysympäristön asennus

Siirry projektikansioon ja luo virtuaaliympäristö:

```bash
python -m venv .venv
source .venv/bin/activate
```

Asenna riippuvuudet:

```bash
pip install -r requirements.txt
```

## Data ja kansiorakenne

Projektin tarvitsemat tiedostot:

- `data/s13servicemanual.pdf` (huoltomanuaali PDF)
- `data/parts.csv` (osalista CSV, sarakkeet: `date,part,cost,notes`)

SQLite-tietokanta luodaan automaattisesti tiedostoon `db/app.sqlite`.

## Ingest-pipeline (manuaali + osalista)

### 1) Renderöi PDF-sivut PNG-kuviksi

```bash
python ingest/ingest_manual.py
```

Output: `db/cache/pages/manual_page_{n}.png`

### 2) OCR kuvista manuaaliteksti tietokantaan

```bash
python ingest/ocr_manual_pages.py
```

Tämä kirjoittaa OCR-tekstin tauluun `manual_pages`.

### 3) Chunkit + embeddingit manuaalista

```bash
python ingest/ingest_manual_to_db.py
```

Tämä luo `chunks`-tauluun tekstiä ja embeddingit RAGia varten.

### 4) Osalistan ingest

```bash
python ingest/ingest_parts.py
```

Tämä täyttää `parts`-taulun CSV:stä.

## Backend

Käynnistä FastAPI (portti 8000):

```bash
uvicorn backend.main:app --reload --port 8000
```

Tarkistus: `GET http://localhost:8000/health`

## UI

Käynnistä Streamlit:

```bash
streamlit run ui/app.py
```

UI odottaa backendin osoitteessa `http://localhost:8000`.
