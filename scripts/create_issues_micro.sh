#!/usr/bin/env bash
set -euo pipefail

gh repo view >/dev/null

create_issue () {
  local title="$1"
  local body="$2"
  local labels="$3"
  gh issue create --title "$title" --body "$body" --label "$labels"
}

# 00 Setup, repo hygiene

create_issue \
"Repo: Lisää peruskansiorakenne" \
"Tavoite
- Perusrunko olemassa.

Tehtävät
- Luo kansiot: data, db, ingest, backend, ui, scripts

Valmis kun
- Kaikki kansiot löytyy reposta" \
"type:setup,prio:P0"

create_issue \
"Repo: Lisää .gitkeep tyhjiin kansioihin" \
"Tavoite
- Tyhjät kansiot pysyy versionhallinnassa.

Tehtävät
- Lisää .gitkeep kansioihin, joissa ei ole vielä tiedostoja

Valmis kun
- git status näyttää uudet .gitkeep tiedostot" \
"type:setup,prio:P0"

create_issue \
"Repo: Lisää .gitignore venv ja python cache" \
"Tavoite
- Et committaa ympäristöä tai cachea.

Tehtävät
- Lisää .gitignore:
  - venv/
  - __pycache__/
  - *.pyc

Valmis kun
- venv ei näy git statusissa" \
"type:setup,prio:P0"

create_issue \
"Repo: Lisää .gitignore sqlite ja local data" \
"Tavoite
- Et committaa db:tä tai paikallista ingest outputtia.

Tehtävät
- Lisää .gitignore:
  - db/*.sqlite
  - db/*.db

Valmis kun
- db/app.sqlite ei näy git statusissa" \
"type:setup,prio:P0"

create_issue \
"Repo: Lisää requirements.txt tyhjä runko" \
"Tavoite
- Riippuvuuksille on paikka.

Tehtävät
- Lisää requirements.txt tiedosto

Valmis kun
- requirements.txt löytyy repon juuressa" \
"type:setup,prio:P0"

create_issue \
"Deps: Lisää FastAPI ja Uvicorn requirementsiin" \
"Tavoite
- Backend käynnistyy myöhemmin.

Tehtävät
- Lisää requirements.txt:
  - fastapi
  - uvicorn[standard]

Valmis kun
- pip install ei valita puuttuvista" \
"type:setup,prio:P0"

create_issue \
"Deps: Lisää Streamlit ja Requests requirementsiin" \
"Tavoite
- UI pystyy kutsumaan backendia.

Tehtävät
- Lisää requirements.txt:
  - streamlit
  - requests

Valmis kun
- pip install asentaa streamlitin" \
"type:setup,prio:P0"

create_issue \
"Deps: Lisää pypdf requirementsiin" \
"Tavoite
- PDF voidaan lukea.

Tehtävät
- Lisää requirements.txt:
  - pypdf

Valmis kun
- pip install asentaa pypdf:n" \
"type:setup,prio:P0"

create_issue \
"Deps: Lisää sentence-transformers ja numpy requirementsiin" \
"Tavoite
- Vektorointi onnistuu.

Tehtävät
- Lisää requirements.txt:
  - sentence-transformers
  - numpy

Valmis kun
- pip install asentaa mallikirjaston" \
"type:setup,prio:P0"

create_issue \
"Deps: Lisää pandas requirementsiin" \
"Tavoite
- CSV osalista voidaan lukea.

Tehtävät
- Lisää requirements.txt:
  - pandas

Valmis kun
- pip install asentaa pandas" \
"type:setup,prio:P0"

create_issue \
"Docs: Lisää README asennus ja ajokomennot, placeholder" \
"Tavoite
- Yksi paikka mistä näkee miten ajetaan.

Tehtävät
- Lisää README.md jossa:
  - venv luonti
  - pip install
  - ingest komennot placeholderina
  - backend ja ui komennot placeholderina

Valmis kun
- README.md löytyy ja sisältää komennot" \
"type:setup,prio:P1"

# 10 DB micro

create_issue \
"DB: Lisää backend/store.py tiedosto" \
"Tavoite
- Tietokantakerrokselle oma moduuli.

Tehtävät
- Luo backend/store.py

Valmis kun
- Tiedosto on repossa" \
"type:backend,prio:P0"

create_issue \
"DB: Implementoi DB_PATH ja connect()" \
"Tavoite
- Yksi sqlite tiedosto ja yhteysfunktio.

Tehtävät
- DB_PATH: db/app.sqlite
- connect(): luo kansio, avaa yhteys, WAL päälle

Valmis kun
- python import backend.store ei kaadu" \
"type:backend,prio:P0"

create_issue \
"DB: Implementoi init_db() ja taulu chunks" \
"Tavoite
- chunks taulu on olemassa.

Tehtävät
- CREATE TABLE chunks: source, ref, text, embedding

Valmis kun
- init_db() luo taulun ilman virhettä" \
"type:backend,prio:P0"

create_issue \
"DB: Lisää parts taulu init_db():hen" \
"Tavoite
- parts taulu on olemassa.

Tehtävät
- CREATE TABLE parts: date, part, cost, notes

Valmis kun
- init_db() luo parts taulun" \
"type:backend,prio:P0"

create_issue \
"DB: Lisää indexit chunks ja parts" \
"Tavoite
- Perushaut nopeutuu.

Tehtävät
- idx_chunks_source
- idx_parts_part
- idx_parts_date

Valmis kun
- init_db() ajaa indexit ilman virhettä" \
"type:backend,prio:P1"

# 20 RAG util micro

create_issue \
"RAG: Lisää backend/rag.py tiedosto" \
"Tavoite
- RAG util erilliseksi.

Tehtävät
- Luo backend/rag.py

Valmis kun
- Import onnistuu" \
"type:backend,prio:P0"

create_issue \
"RAG: Lisää chunk_text perusversio" \
"Tavoite
- Teksti pilkotaan.

Tehtävät
- chunk_size 900
- overlap 150
- trimmaa whitespace

Valmis kun
- chunk_text palauttaa listan stringejä" \
"type:backend,prio:P0"

create_issue \
"RAG: Lisää cosine_top_k" \
"Tavoite
- Top-k osumat numpylla.

Tehtävät
- Normalisoi vektorit
- Palauta idx ja scores

Valmis kun
- Sama vektori antaa score suurimman" \
"type:backend,prio:P0"

create_issue \
"RAG: Lisää Hit dataluokka" \
"Tavoite
- Hakutuloksille selkeä rakenne.

Tehtävät
- dataclass Hit: text, source, ref, score

Valmis kun
- Hit voidaan luoda ja käyttää" \
"type:backend,prio:P1"

# 30 Ingest manual micro

create_issue \
"Ingest manual: Lisää ingest/ingest_manual.py tiedosto" \
"Tavoite
- Käsikirjan ingestille oma skripti.

Tehtävät
- Luo tiedosto

Valmis kun
- python ingest/ingest_manual.py käynnistyy (vaikka heti exit)" \
"type:ingest,prio:P0"

create_issue \
"Ingest manual: Lue PDF sivut pypdf:llä" \
"Tavoite
- Saat sivutekstit ulos.

Tehtävät
- PdfReader(data/manual.pdf)
- Loop pages, extract_text()

Valmis kun
- Skripti tulostaa sivumäärän" \
"type:ingest,prio:P0"

create_issue \
"Ingest manual: Pilko yhden sivun teksti chunkeiksi" \
"Tavoite
- chunk_text käytössä PDF:lle.

Tehtävät
- Kutsu chunk_text(page_text)

Valmis kun
- Skripti tulostaa chunk määrän per sivu" \
"type:ingest,prio:P0"

create_issue \
"Ingest manual: Lataa embedding malli" \
"Tavoite
- SentenceTransformer käytössä.

Tehtävät
- Lataa all-MiniLM-L6-v2

Valmis kun
- Malli latautuu ilman virhettä" \
"type:ingest,prio:P0"

create_issue \
"Ingest manual: Luo embeddaukset chunkeille" \
"Tavoite
- Saat float32 vektorit.

Tehtävät
- model.encode(chunks)
- astype float32

Valmis kun
- emb shape näkyy logissa" \
"type:ingest,prio:P0"

create_issue \
"Ingest manual: Tallenna manual chunkit sqlite chunks-tauluun" \
"Tavoite
- Käsikirja siirtyy DB:hen.

Tehtävät
- init_db()
- DELETE vanhat source=manual
- INSERT jokainen chunk embedding blobina
- ref = manual.pdf s. X

Valmis kun
- SELECT COUNT(*) WHERE source=manual > 0" \
"type:ingest,prio:P0"

# 40 Ingest notes micro

create_issue \
"Ingest notes: Lisää ingest/ingest_notes.py tiedosto" \
"Tavoite
- Muistiinpanot ingestattavissa.

Tehtävät
- Luo tiedosto

Valmis kun
- Skripti käynnistyy" \
"type:ingest,prio:P0"

create_issue \
"Ingest notes: Lue notes.md ja chunkkaa" \
"Tavoite
- notes.md pilkotaan.

Tehtävät
- read_text utf-8
- chunk_text

Valmis kun
- tulostaa chunk määrän" \
"type:ingest,prio:P0"

create_issue \
"Ingest notes: Embed ja tallenna sqliteen" \
"Tavoite
- notes siirtyy chunks-tauluun.

Tehtävät
- DELETE source=notes
- INSERT chunkit ref=notes.md

Valmis kun
- SELECT COUNT(*) source=notes > 0" \
"type:ingest,prio:P0"

# 50 Ingest parts micro

create_issue \
"Ingest parts: Lisää ingest/ingest_parts.py tiedosto" \
"Tavoite
- Osalistan ingestille oma skripti.

Tehtävät
- Luo tiedosto

Valmis kun
- Skripti käynnistyy" \
"type:ingest,prio:P0"

create_issue \
"Ingest parts: Lue parts.csv pandasilla" \
"Tavoite
- CSV sisään.

Tehtävät
- pd.read_csv(data/parts.csv)

Valmis kun
- Skripti tulostaa rivimäärän" \
"type:ingest,prio:P0"

create_issue \
"Ingest parts: Varmista sarakkeet date part cost notes" \
"Tavoite
- Skeema vakio.

Tehtävät
- Jos puuttuu, luo tyhjänä

Valmis kun
- Skripti tulostaa lopulliset sarakkeet" \
"type:ingest,prio:P0"

create_issue \
"Ingest parts: Tyhjennä parts taulu ja insert rivit" \
"Tavoite
- parts taulu täyttyy.

Tehtävät
- DELETE FROM parts
- INSERT kaikki rivit joissa part ei tyhjä
- cost muunnos float tai NULL

Valmis kun
- SELECT COUNT(*) FROM parts vastaa odotusta" \
"type:ingest,prio:P0"

create_issue \
"Ingest parts: Muodosta parts_text rivit" \
"Tavoite
- RAG saa tekstimuotoisen osalistan.

Tehtävät
- Format: Päivä, Osa, Hinta, Huomio
- Yhteen stringiin

Valmis kun
- Tekstissä on vähintään 1 rivi" \
"type:ingest,prio:P0"

create_issue \
"Ingest parts: Chunkkaa parts_text" \
"Tavoite
- parts_text pilkotaan.

Tehtävät
- chunk_text(parts_text)

Valmis kun
- chunks määrä tulostuu" \
"type:ingest,prio:P0"

create_issue \
"Ingest parts: Embed parts_text chunkit" \
"Tavoite
- Vektorit valmiiksi.

Tehtävät
- model.encode(chunks)
- float32

Valmis kun
- ensimmäinen embedding dim tulostuu" \
"type:ingest,prio:P0"

create_issue \
"Ingest parts: Tallenna parts_text chunkit chunks-tauluun" \
"Tavoite
- Haku osalistasta RAG:illa toimii.

Tehtävät
- DELETE source=parts_text
- INSERT chunkit ref=parts.csv

Valmis kun
- SELECT COUNT(*) WHERE source=parts_text > 0" \
"type:ingest,prio:P0"

# 60 Backend micro

create_issue \
"Backend: Lisää backend/main.py tiedosto" \
"Tavoite
- FastAPI entrypoint.

Tehtävät
- Luo tiedosto

Valmis kun
- uvicorn import ei kaadu" \
"type:backend,prio:P0"

create_issue \
"Backend: Lisää FastAPI app ja /health" \
"Tavoite
- Perusendpoint ylös.

Tehtävät
- GET /health palauttaa ok true

Valmis kun
- curl /health toimii" \
"type:backend,prio:P0"

create_issue \
"Backend: Lisää startup hook init_db()" \
"Tavoite
- DB luodaan automaattisesti.

Tehtävät
- startup event
- init_db()

Valmis kun
- /health toimii tyhjällä db:llä" \
"type:backend,prio:P0"

create_issue \
"Backend: Lisää malli lataus startupissa" \
"Tavoite
- Sama embedding malli käytössä haussa.

Tehtävät
- SentenceTransformer all-MiniLM-L6-v2

Valmis kun
- backend käynnistyy ja lataa mallin" \
"type:backend,prio:P0"

create_issue \
"Backend: Lisää chunkien lataus sqlite -> numpy" \
"Tavoite
- Vaste nopea.

Tehtävät
- SELECT source, ref, text, embedding FROM chunks
- np.frombuffer float32
- vstack matriisiksi

Valmis kun
- /health raportoi chunks määrän" \
"type:backend,prio:P0"

create_issue \
"Backend: Lisää /ask request malli (pydantic)" \
"Tavoite
- JSON input vakio.

Tehtävät
- AskIn: question, top_k default 5

Valmis kun
- FastAPI docs näyttää mallin" \
"type:backend,prio:P0"

create_issue \
"Backend: Lisää /ask endpoint stub palauttaa placeholder" \
"Tavoite
- Endpoint olemassa ennen logiikkaa.

Tehtävät
- POST /ask palauttaa {answer:'', sources:[]}

Valmis kun
- curl POST /ask toimii" \
"type:backend,prio:P0"

create_issue \
"Backend: /ask RAG haku ja sources listaus" \
"Tavoite
- Kysymys hakee top-k chunkit.

Tehtävät
- Encode question
- cosine_top_k
- sources: source, ref, score
- answer: näytä 1 relevantti ote

Valmis kun
- sources ei ole tyhjä ingestin jälkeen" \
"type:backend,prio:P0"

# 70 Rules micro

create_issue \
"Rules: Lisää backend/rules.py tiedosto" \
"Tavoite
- Osalistalogiikka erikseen.

Tehtävät
- Luo tiedosto

Valmis kun
- Import toimii" \
"type:backend,prio:P0"

create_issue \
"Rules: Lisää _load_parts_df()" \
"Tavoite
- parts data dataframeksi.

Tehtävät
- SELECT parts taulusta
- lisää part_lc sarake

Valmis kun
- Funktio palauttaa df jossa part_lc on olemassa" \
"type:backend,prio:P0"

create_issue \
"Rules: Lisää regex tunnistus kysymykselle summaa kustannukset" \
"Tavoite
- Tunnistat 'Paljonko X on maksanut yhteensä'.

Tehtävät
- Regex ja target capture

Valmis kun
- Unit print testillä target löytyy" \
"type:backend,prio:P0"

create_issue \
"Rules: Implementoi kustannusten summaan vastaus" \
"Tavoite
- Palautat tarkan summan.

Tehtävät
- contains target
- sum cost
- osumien määrä

Valmis kun
- palauttaa eurot ja osumat" \
"type:backend,prio:P0"

create_issue \
"Rules: Regex tunnistus 'Milloin viimeksi X vaihdettiin'" \
"Tavoite
- Tunnistat last-date kysymyksen.

Tehtävät
- Regex ja target capture

Valmis kun
- target löytyy testissä" \
"type:backend,prio:P0"

create_issue \
"Rules: Implementoi viimeisin päivämäärä vastaus" \
"Tavoite
- Palautat viimeisimmän date-arvon.

Tehtävät
- suodata date tyhjät
- max date

Valmis kun
- palauttaa päivämäärän tai kertoo että puuttuu" \
"type:backend,prio:P0"

create_issue \
"Rules: Regex tunnistus 'Onko X vaihdettu aiemmin'" \
"Tavoite
- Tunnistat yes/no kysymyksen.

Tehtävät
- Regex ja target capture

Valmis kun
- target löytyy testissä" \
"type:backend,prio:P0"

create_issue \
"Rules: Implementoi vaihdettu aiemmin vastaus" \
"Tavoite
- Palautat kyllä/ei ja osumat.

Tehtävät
- osumien count
- viimeisin date

Valmis kun
- palauttaa kyllä tai ei ja viimeisin date" \
"type:backend,prio:P0"

create_issue \
"Backend: Kytke rules /ask endpointtiin" \
"Tavoite
- Osalistakysymykset ohittaa RAG:in.

Tehtävät
- try_rules(question)
- jos palauttaa dict, palauta se suoraan

Valmis kun
- kustannus ja last-date kysymykset ei tarvitse sources=manual" \
"type:backend,prio:P0"

# 80 UI micro

create_issue \
"UI: Lisää ui/app.py tiedosto" \
"Tavoite
- Streamlit entrypoint.

Tehtävät
- Luo tiedosto

Valmis kun
- streamlit run ui/app.py käynnistyy" \
"type:ui,prio:P0"

create_issue \
"UI: Lisää tekstikenttä ja Kysy nappi" \
"Tavoite
- Yksi kysymys syöte.

Tehtävät
- st.text_input
- st.button

Valmis kun
- UI näyttää kentän ja napin" \
"type:ui,prio:P0"

create_issue \
"UI: Lisää backend kutsu /ask" \
"Tavoite
- UI saa vastauksen backendistä.

Tehtävät
- requests.post /ask
- timeout 10

Valmis kun
- UI näyttää answer tekstin" \
"type:ui,prio:P0"

create_issue \
"UI: Renderöi sources listana" \
"Tavoite
- Näytät lähteen ja scoret.

Tehtävät
- loop sources
- näytä source, ref, score

Valmis kun
- sources näkyy UI:ssa" \
"type:ui,prio:P0"

create_issue \
"UI: Lisää virheilmoitus jos backend ei vastaa" \
"Tavoite
- Ei tracebackia käyttäjälle.

Tehtävät
- try except requests
- st.error selkeällä viestillä

Valmis kun
- backend pois päältä, UI kertoo tilanteen" \
"type:ui,prio:P1"

# 90 QA micro

create_issue \
"QA: Lisää scripts/smoke_test.sh tiedosto" \
"Tavoite
- Testiskriptille paikka.

Tehtävät
- Luo tiedosto ja tee ajettavaksi

Valmis kun
- bash scripts/smoke_test.sh käynnistyy" \
"type:qa,prio:P0"

create_issue \
"QA: Smoke test kutsuu /health" \
"Tavoite
- Varmistat backendin olevan ylhäällä.

Tehtävät
- curl /health
- jos ei 200, exit 1

Valmis kun
- skripti kaatuu jos backend ei ole käynnissä" \
"type:qa,prio:P0"

create_issue \
"QA: Smoke test mittaa yhden /ask kyselyn ajan" \
"Tavoite
- Latenssin mittaus.

Tehtävät
- mittaa curl time_total
- tulosta sekunteina

Valmis kun
- skripti tulostaa time_total" \
"type:qa,prio:P0"

create_issue \
"QA: Lisää 4 MVP kysymystä smoke testiin" \
"Tavoite
- Sama setti aina.

Tehtävät
- aja /ask neljällä kysymyksellä
- tulosta vastauksen pituus ja sources count

Valmis kun
- skripti suorittaa 4 kysymystä" \
"type:qa,prio:P0"

create_issue \
"QA: Assert sources ei tyhjä RAG kysymyksissä" \
"Tavoite
- Et saa 'yleistä' vastausta.

Tehtävät
- kahdessa RAG-kysymyksessä tarkista sources count > 0
- jos 0, exit 1

Valmis kun
- skripti failaa jos sources tyhjä" \
"type:qa,prio:P0"

echo "OK. Micro-issuet luotu."
