import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

def llm_mode_label(llm_mode: str) -> str:
    m = (llm_mode or "").strip().lower()
    if m == "ollama":
        return "Vastaus tuli: LLM (Ollama)"
    if m == "fallback":
        return "Vastaus tuli: fallback (LLM epäonnistui, käytetään kontekstia)"
    return "Vastaus tuli: konteksti (ei LLM)"

st.set_page_config(
    page_title="AI-projektiautoavustaja",
    page_icon="🚗",
    layout="wide",
)

st.title("AI-projektiautoavustaja")
st.subheader("Kysy yksi kysymys")

question = st.text_input(
    "Kysymys",
    placeholder="Esim. Mikä osa sopii tähän moottoriin",
    key="question_input",
)

ask = st.button("Kysy", key="ask_button")

if ask:
    if not question.strip():
        st.warning("Kirjoita kysymys.")
    else:
        with st.spinner("Haetaan vastausta"):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": question},
                    timeout=10,
                )
                resp.raise_for_status()

                try:
                    data = resp.json()
                except ValueError:
                    st.error("Backend palautti virheellisen vastauksen.")
                    st.stop()

                answer = data.get("answer", "")
                sources = data.get("sources", [])
                llm_mode = data.get("llm_mode", "off")

                st.subheader("Vastaus")
                st.caption(llm_mode_label(llm_mode))

                if llm_mode == "fallback":
                    err = (data.get("error") or "").strip()
                    if err:
                        st.caption(f"Syy: {err}")

                st.write(answer if answer else "Ei vastausta.")

                st.subheader("Lähteet")
                if not sources:
                    st.markdown("- Ei lähteitä.")
                else:
                    for i, s in enumerate(sources, start=1):
                        source = (s.get("source") or "").strip()
                        ref = (s.get("ref") or "").strip()
                        page = s.get("page", None)
                        score = s.get("score", None)
                        snippet = (s.get("snippet") or "").strip()

                        src_label = source if source else "unknown"
                        page_label = f", sivu {page}" if page is not None else ""
                        score_label = f", score {float(score):.3f}" if isinstance(score, (int, float)) else ""

                        snippet_short = snippet[:160].strip()
                        if snippet and len(snippet) > 160:
                            snippet_short += "..."

                        st.markdown(f"- [{i}] {src_label}{page_label}{score_label}")
                        if ref:
                            st.markdown(f" - ref: `{ref}`")
                        if snippet_short:
                            st.markdown(f" - {snippet_short}")

            except requests.exceptions.Timeout:
                st.error("Backend ei vastannut 10 sekunnissa.")
            except requests.exceptions.ConnectionError:
                st.error("Backend ei ole käynnissä. Käynnistä backend ja yritä uudelleen.")
            except requests.exceptions.HTTPError:
                st.error(f"Backend palautti virheen. HTTP {resp.status_code}.")
            except requests.exceptions.RequestException:
                st.error("Yhteys backend-palveluun epäonnistui.")

with st.sidebar:
    st.header("Valikko")
    page = st.radio(
        "Sivu",
        ["Etusivu", "Kuvat", "Ostoslista", "PDF-haku", "Lokit"],
        index=0,
        key="page_select",
    )

if page == "Etusivu":
    st.subheader("Status")
    st.success("Sovellus käynnissä.")
    st.write("Seuraavaksi lisäät sivujen sisällöt ja backend-logiikan.")

elif page == "Kuvat":
    st.subheader("Kuvat")
    st.info("Tähän tulee kuvien selaus ja tagit.")
    st.file_uploader(
        "Lataa kuva",
        type=["jpg", "jpeg", "png", "webp"],
        key="image_upload",
    )

elif page == "Ostoslista":
    st.subheader("Ostoslista")

    with st.form("add_part_form"):
        date = st.text_input("Päivä (YYYY-MM-DD)")
        part = st.text_input("Osa")
        cost = st.number_input("Hinta", min_value=0.0)
        notes = st.text_input("Huomio")
        submitted = st.form_submit_button("Lisää")

        if submitted:
            try:
                requests.post(
                    f"{BACKEND_URL}/parts",
                    json={
                        "date": date,
                        "part": part,
                        "cost": cost,
                        "notes": notes,
                    },
                )
                st.success("Lisätty.")
            except:
                st.error("Lisäys epäonnistui.")

    try:
        resp = requests.get(f"{BACKEND_URL}/parts")
        items = resp.json().get("items", [])

        for item in items:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(
                    f"{item['date']} | {item['part']} | {item['cost']} € | {item['notes']}"
                )
            with col2:
                if st.button("Poista", key=f"del_{item['id']}"):
                    requests.delete(f"{BACKEND_URL}/parts/{item['id']}")
                    st.experimental_rerun()

    except:
        st.error("Ostoslistaa ei voitu hakea.")
        
elif page == "PDF-haku":
    st.subheader("PDF-haku")

    query = st.text_input("Hae käsikirjasta", key="pdf_search")
    if st.button("Hae", key="pdf_search_button"):
        if not query.strip():
            st.warning("Kirjoita hakulause.")
        else:
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/pdf/search",
                    json={"query": query},
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])

                if not results:
                    st.info("Ei osumia.")
                else:
                    for i, r in enumerate(results, start=1):
                        st.markdown(f"### [{i}] {r['source']}")
                        st.write(f"ref: {r['ref']}")
                        st.write(f"score: {r['score']:.3f}")
                        st.write(r["snippet"])
                        st.divider()

            except requests.RequestException:
                st.error("PDF-haku epäonnistui.")

elif page == "Lokit":
    st.subheader("Lokit")
    st.info("Tähän tulee ajolokit ja virheet.")
    st.code("No logs yet.", language="text")
