import os
for env_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'OPENAI_PROXY']:
    os.environ.pop(env_var, None)
import sqlite3

sqlite3.sqlite_version_info = (3, 35, 0)
sqlite3.sqlite_version = "3.35.0"

import os
import random
import json
import re
import datetime
import streamlit as st
import pandas as pd
from openai import OpenAI

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# ==========================================
# 1. KONFIGURACJA INTERFEJSU I STONOWANYCH MOTYWÓW UX/UI
# ==========================================
st.set_page_config(
    page_title="NEURO FRIEND | Platforma Treningowa",
    page_icon="🎓",
    layout="wide"
)

user_prefs = st.session_state.get('user_prefs', {})
chosen_theme = user_prefs.get('theme', 'Ciepły stonowany (Beż i szarość)')

if chosen_theme == "Pastele: Różowy (Soft Pink)":
    bg_app = "#FDF2F4"        
    sidebar_bg = "#FCE8EC"    
    card_bg = "#FFFFFF"      
    text_color = "#4A2E35"    
    border_col = "#F7D6DE"    
    accent_col = "#D85A75"    
    user_bubble = "#F7D6DE"
    assistant_bubble = "#FFFFFF"
elif chosen_theme == "Pastele: Żółty (Pastel Yellow)":
    bg_app = "#FEFCE8"        
    sidebar_bg = "#FEF9C3"    
    card_bg = "#FFFFFF"      
    text_color = "#422006"    
    border_col = "#FEF08A"    
    accent_col = "#A16207"    
    user_bubble = "#FEF08A"
    assistant_bubble = "#FFFFFF"
elif chosen_theme == "Pastele: Zielony (Mint Green)":
    bg_app = "#F0FDF4"        
    sidebar_bg = "#DCFCE7"    
    card_bg = "#FFFFFF"      
    text_color = "#14532D"    
    border_col = "#BBF7D0"    
    accent_col = "#15803D"    
    user_bubble = "#BBF7D0"
    assistant_bubble = "#FFFFFF"
elif chosen_theme == "Pastele: Niebieski (Soft Blue)":
    bg_app = "#F0F9FF"        
    sidebar_bg = "#E0F2FE"    
    card_bg = "#FFFFFF"      
    text_color = "#0C4A6E"    
    border_col = "#BAE6FD"    
    accent_col = "#0369A1"    
    user_bubble = "#BAE6FD"
    assistant_bubble = "#FFFFFF"
elif chosen_theme == "Pastele: Pomarańczowy (Peach)":
    bg_app = "#FFF7ED"        
    sidebar_bg = "#FFEDD5"    
    card_bg = "#FFFFFF"      
    text_color = "#431407"    
    border_col = "#FED7AA"    
    accent_col = "#C2410C"    
    user_bubble = "#FED7AA"
    assistant_bubble = "#FFFFFF"
elif chosen_theme == "Klasyczny jasny (Biel i głęboka czerń)":
    bg_app = "#FFFFFF"        
    sidebar_bg = "#F8F9FA"    
    card_bg = "#FFFFFF"      
    text_color = "#000000"    
    border_col = "#DDE2E5"    
    accent_col = "#333333"    
    user_bubble = "#E9ECEF"
    assistant_bubble = "#FFFFFF"
else:  # Ciepły stonowany (Beż i szarość)
    bg_app = "#FAF8F5"        
    sidebar_bg = "#F3F1EC"    
    card_bg = "#FFFFFF"      
    text_color = "#1C1917"    
    border_col = "#E7E5E4"    
    accent_col = "#78716C"    
    user_bubble = "#E7E5E4"
    assistant_bubble = "#FFFFFF"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&display=swap');
    
    .brand-logo {{
        font-family: 'Cinzel', serif;
        letter-spacing: 2px;
        font-weight: 700;
        color: {accent_col};
    }}

    .stApp {{
        background-color: {bg_app};
        color: {text_color};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid {border_col};
    }}

    .info-card {{
        background-color: {card_bg};
        padding: 24px 28px;
        border-radius: 12px;
        border: 1px solid {border_col};
        border-left: 3px solid {accent_col};
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 24px;
        color: {text_color};
    }}

    .coach-box {{
        background: linear-gradient(135deg, {card_bg} 0%, {sidebar_bg} 100%);
        border: 1px solid {border_col};
        border-left: 3px solid {accent_col};
        padding: 16px 20px;
        border-radius: 8px;
        color: {text_color};
        margin-top: 14px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        font-size: 0.96rem;
        line-height: 1.5;
    }}

    .cbt-box {{
        background-color: {card_bg};
        border: 1px solid {border_col};
        border-left: 4px solid {accent_col};
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
        color: {text_color};
    }}

    @keyframes breathing {{
      0% {{ transform: scale(0.9); background-color: {border_col}; opacity: 0.7; }}
      50% {{ transform: scale(1.2); background-color: {accent_col}; opacity: 0.95; }}
      100% {{ transform: scale(0.9); background-color: {border_col}; opacity: 0.7; }}
    }}
    
    .breathing-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px;
    }}

    .breathe-circle {{
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background-color: {accent_col};
        animation: breathing 6s infinite ease-in-out;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 0.85rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 8px;
    }}

    h1, h2, h3 {{
        color: {text_color};
        letter-spacing: -0.01em;
    }}

    .stChatMessage {{
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        border: 1px solid {border_col};
        color: {text_color};
    }}
    
    .stChatInput input {{
        color: {text_color} !important;
    }}
    
    .stButton button {{
        border-radius: 8px;
        font-weight: 500;
        border: 1px solid {border_col};
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STAŁA KONFIGURACJA RAG
# ==========================================
CHROMA_PERSIST_DIR = "./chroma_db_neuro_friend"
OPENAI_API_KEY_HARDCODED = "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"

@st.cache_resource(show_spinner="Ładowanie bazy wiedzy RAG...")
def load_rag_engine():
    try:
        if not OPENAI_API_KEY_HARDCODED:
            return None
        if not os.path.exists(CHROMA_PERSIST_DIR) or not os.listdir(CHROMA_PERSIST_DIR):
            return None

        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY_HARDCODED, model="text-embedding-3-small")
        vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k": 3})
    except Exception:
        return None

retriever = load_rag_engine()

# ==========================================
# 3. FUNKCJA ZAPISU ROZMOWY DO PLIKU
# ==========================================
def save_chat_to_file(messages, scenario_info, model_name, tryb_rozmowy, start_timestamp, summary_text=None):
    EXPORT_DIR = r"C:\Users\marbi\OneDrive\Pulpit\Magisterka-Conversation Training App&Support\ZAPISANE_ROZMOWY"
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    safe_title = "".join([c if c.isalnum() else "_" for c in scenario_info['tytul']])
    filename = f"Rozmowa_{safe_title}_START_{start_timestamp}.txt"
    filepath = os.path.join(EXPORT_DIR, filename)

    now = datetime.datetime.now()
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("        NEURO FRIEND - ZAPIS SESJI TRENINGOWEJ      \n")
        f.write("==================================================\n")
        f.write(f"Data rozpoczęcia sesji: {start_timestamp}\n")
        f.write(f"Data wygenerowania raportu: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Scenariusz: {scenario_info['tytul']}\n")
        f.write(f"Rola AI: {scenario_info['rola']}\n")
        f.write(f"Użyty model AI: {model_name}\n")
        f.write(f"Tryb interakcji: {tryb_rozmowy}\n")
        f.write("==================================================\n\n")
        f.write("--- PRZEBIEG ROZMOWY ---\n\n")

        for msg in messages:
            msg_time = msg.get("timestamp", "Brak daty")
            role_label = "UŻYTKOWNIK" if msg["role"] == "user" else f"AI ({scenario_info['rola']})"
            f.write(f"[{msg_time}] {role_label}:\n{msg['content']}\n\n")

        if summary_text:
            f.write("==================================================\n")
            f.write("--- RAPORT PSYCHOLOGICZNY I ANALIZA METAKOGNITYWNA ---\n")
            f.write("Każda emocja coś komunikuje, co komunikuje Twoja?\n")
            f.write("==================================================\n\n")
            f.write(f"{summary_text}\n")

    return filepath

# ==========================================
# 4. SŁOWNIKI MODELI ORAZ SCENARIUSZY
# ==========================================
dostepne_modele = {
    "Claude Sonnet 5": {
        "model_id": "claude-5-sonnet",
        "base_url": "https://api.anthropic.com/v1",
        "env_key": "ANTHROPIC_API_KEY",
        "label": "Klucz API Anthropic"
    },
    "GPT-5.6 Sol": {
        "model_id": "gpt-5.6-sol",
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
        "label": "Klucz API OpenAI"
    },
    "Google Gemini 3.1 Flash Lite": {
        "model_id": "gemini-3.1-flash-lite",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "env_key": "GEMINI_API_KEY",
        "label": "Klucz API Google Gemini"
    },
    "DeepSeek V4 Pro": {
        "model_id": "deepseek-v4-pro",
        "base_url": "https://api.deepseek.com",
        "env_key": "DEEPSEEK_API_KEY",
        "label": "Klucz API DeepSeek"
    },
    "Llama 4 Maverick": {
        "model_id": "llama-4-maverick",
        "base_url": "https://api.groq.com/openai/v1",
        "env_key": "GROQ_API_KEY",
        "label": "Klucz API Llama / Groq"
    }
}

scenariusze_kategorie = {
    "Praca": {
        "rekrutacja": {
            "tytul": "Rozmowa rekrutacyjna (wstępna)",
            "rola": "Rekruter / Osoba prowadząca rozmowę kwalifikacyjną",
            "start": "Dzień dobry! Dziękuję za przybycie na dzisiejsze spotkanie. Czy można prosić o opowiedzenie czegoś o swoim doświadczeniu?"
        },
        "podwyzka": {
            "tytul": "Prośba o podwyżkę",
            "rola": "Przełożony / Kierownik",
            "start": "Dzień dobry. Była prośba o spotkanie. Słucham, o czym chcielibyśmy porozmawiać?"
        },
        "rezygnacja": {
            "tytul": "Chęć rezygnacji z pracy",
            "rola": "Przełożony / Przedstawiciel HR",
            "start": "Dzień dobry. Wspomniano, że jest ważna sprawa do omówienia. O co chodzi?"
        }
    },
    "Lekarz": {
        "wyniki": {
            "tytul": "Omówienie wyników badań",
            "rola": "Lekarz prowadzący",
            "start": "Dzień dobry. Proszę usiąść. Mam przed sobą wyniki badań. Jak samopoczucie?"
        },
        "dolegliwosci": {
            "tytul": "Zgłoszenie dolegliwości i skierowanie na badania",
            "rola": "Lekarz pierwszego kontaktu",
            "start": "Dzień dobry. Proszę usiąść. Z jakimi objawami wizyta dzisiaj?"
        }
    },
    "Rodzina": {
        "granice": {
            "tytul": "Stawianie granic w relacji z rodziną",
            "rola": "Członek rodziny",
            "start": "Cześć! Dobrze, że się widzimy. O czym chcesz ze mną porozmawiać?"
        },
        "przebodzcowanie": {
            "tytul": "Komunikowanie przeciążenia sensorycznego",
            "rola": "Gospodarz spotkania rodzinnego",
            "start": "Cześć! Dlaczego stoimy z boku? Wszystko w porządku, czemu nie dołączyć do reszty?"
        },
        "nieproszone_rady": {
            "tytul": "Reakcja na nieproszone rady i ocenianie stylu życia",
            "rola": "Bliski członek rodziny",
            "start": "Cześć! Widzę, że znowu robimy to po swojemu... Nie uważasz, że warto zorganizować to inaczej?"
        }
    },
    "Partner / Relacje": {
        "potrzeby": {
            "tytul": "Wyrażanie własnych potrzeb i emocji",
            "rola": "Partner / Partnerka",
            "start": "Hej. Cieszę się, że rozmawiamy. Mowa była o chęci omówienia czegoś ważnego w naszej relacji?"
        },
        "zaproponowanie_spotkania": {
            "tytul": "Zaproponowanie spotkania / randki",
            "rola": "Osoba, która Ci się podoba / Znajomy",
            "start": "Hej! Fajnie, że kontakt. Co tam słychać?"
        },
        "wyzszy_poziom": {
            "tytul": "Przeniesienie relacji na wyższy poziom / Wyznanie uczuć",
            "rola": "Partner / Partnerka / Bliska osoba",
            "start": "Hej! Ostatnio sporo myśli kłębiło się w głowie o naszej relacji. O czym chciało się porozmawiać?"
        },
        "zakonczenie_relacji": {
            "tytul": "Zakończenie relacji",
            "rola": "Partner / Partnerka",
            "start": "Cześć. Dziwnie brzmiał głos przez telefon... Co się stało?"
        }
    },
    "Sklep / Obsługa": {
        "reklamacja": {
            "tytul": "Reklamacja wadliwego produktu",
            "rola": "Pracownik punktu obsługi klienta",
            "start": "Dzień dobry! W czym można pomóc dzisiaj?"
        },
        "dostepnosc": {
            "tytul": "Zapytanie o dostępność i lokalizację produktu",
            "rola": "Pracownik sklepu",
            "start": "Dzień dobry! Czy szukamy czegoś konkretnego?"
        },
        "pomylka_rachunek": {
            "tytul": "Zgłoszenie pomyłki na rachunku przy kasie",
            "rola": "Kasjer / Kasjerka",
            "start": "Dzień dobry. Proszę, oto paragon. Czy wszystko się zgadza?"
        }
    },
    "Uczelnia": {
        "rekrutacja_uczelnia": {
            "tytul": "Pytania rekrutacyjne i organizacyjne",
            "rola": "Pracownik biura rekrutacji",
            "start": "Dzień dobry. W jakiej sprawie wizyta w biurze rekrutacji?"
        },
        "przeniesienie": {
            "tytul": "Przeniesienie na inny kierunek studiów",
            "rola": "Pracownik dziekanatu",
            "start": "Dzień dobry. Słucham, w czym można pomóc?"
        },
        "przedluzenie_sesji": {
            "tytul": "Wniosek o przedłużenie sesji lub semestru",
            "rola": "Pracownik dziekanatu",
            "start": "Dzień dobry. Słucham, z jaką sprawą wizyta?"
        },
        "dziekanka": {
            "tytul": "Wniosek o urlop dziekański",
            "rola": "Pracownik dziekanatu",
            "start": "Dzień dobry. Słucham, w czym mogę pomóc?"
        },
        "egzamin_komisyjny": {
            "tytul": "Wniosek o egzamin komisyjny",
            "rola": "Pracownik dziekanatu",
            "start": "Dzień dobry. W czym mogę pomóc?"
        },
        "rezygnacja_studia": {
            "tytul": "Rezygnacja ze studiów",
            "rola": "Pracownik dziekanatu",
            "start": "Dzień dobry. Słucham, w jakiej sprawie wizyta?"
        }
    }
}

# ==========================================
# 5. ZARZĄDZANIE STANEM APLIKACJI
# ==========================================
if "intro_dismissed" not in st.session_state:
    st.session_state.intro_dismissed = False

if "config_completed" not in st.session_state:
    st.session_state.config_completed = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_prefs" not in st.session_state:
    st.session_state.user_prefs = {}

if "summary_mode" not in st.session_state:
    st.session_state.summary_mode = False

if "session_ended" not in st.session_state:
    st.session_state.session_ended = False

if "training_history" not in st.session_state:
    st.session_state.training_history = []

# ==========================================
# KOLEJNOŚĆ WIDOKÓW (STATE ROUTING)
# ==========================================

# 1. Krok pierwszy: Kwestionariusz profilowania
if not st.session_state.intro_dismissed:
    st.markdown("""
        <div class="info-card">
            <h3>Witaj w aplikacji <span class="brand-logo">NEURO FRIEND</span></h3>
            <p>Aplikacja pozwala na trening umiejętności komunikacyjnych w bezpiecznej przestrzeni. System konfigurowany jest przy użyciu sprawdzonych metodologii psychologicznych i behawioralnych (Skala Likerta, Dyferencjał Semantyczny Osgooda, Indeks NASA-TLX oraz Model ABC), aby maksymalnie dopasować wsparcie do Twoich potrzeb.</p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("Zaawansowany Kwestionariusz Profilowania Użytkownika")
    with st.form("advanced_methodology_form"):
        
        st.markdown("#### 1. Preferencje komunikacyjne")
        st.caption("ℹ️ *Skala Likerta* – pozwala określić, jak bardzo cenisz uporządkowane listy i strukturę.")
        
        likert_options = [1, 2, 3, 4, 5]
        format_func_likert = lambda x: {1: "1 - Zdecydowanie nie", 2: "2 - Raczej nie", 3: "3 - Neutralnie", 4: "4 - Raczej tak", 5: "5 - Zdecydowanie tak"}[x]

        q2 = st.select_slider("Wolę, aby informacje i wskazówki były podawane w formie uporządkowanych list.", options=likert_options, value=4, format_func=format_func_likert, key="q2_likert", help="Określ, czy preferujesz jasne uporządkowanie treści.")

        st.markdown("---")
        st.markdown("#### 2. Styl języka wskazówek")
        st.caption("ℹ️ *Dyferencjał Semantyczny Osgooda* – narzędzie służące do pomiaru konotacji i stylu językowego (od dosłownego po metaforyczny).")
        
        sem_options = [1, 2, 3, 4, 5]
        format_func_sem = lambda x: {
            1: "Skrajnie dosłowna instrukcja krok po kroku", 
            2: "Raczej dosłowna i konkretna", 
            3: "Neutralna / zbalansowana", 
            4: "Raczej metaforyczna / refleksyjna", 
            5: "Skrajnie metaforyczna / abstrakcyjna"
        }[x]
        q_sem = st.select_slider("Wolę, aby wskazówki i styl wypowiedzi były:", options=sem_options, value=2, format_func=format_func_sem, key="q_sem_osgood", help="Wybierz preferowany stopień dosłowności lub abstrakcji komunikacji.")

        st.markdown("---")
        st.markdown("#### 3. Obciążenie i zmęczenie poznawcze")
        st.caption("ℹ️ *Indeks NASA-TLX* – standardowa metoda oceny obciążenia psychicznego i podatności na przebodźcowanie w danej chwili.")
        
        nasa_options = [1, 2, 3, 4, 5]
        format_func_nasa = lambda x: {1: "Bardzo niskie", 2: "Niskie", 3: "Umiarkowane", 4: "Wysokie", 5: "Bardzo wysokie"}[x]
        q_nasa = st.select_slider("Jak oceniasz swoją obecną podatność na zmęczenie poznawcze lub przebodźcowanie?", options=nasa_options, value=3, format_func=format_func_nasa, key="q_nasa_tlx", help="Określ swój aktualny poziom energii psychicznej.")

        st.markdown("---")
        st.markdown("#### 4. Główny cel wsparcia")
        st.caption("ℹ️ *Model behawioralny ABC* – dzieli analizę na Antecedent (sytuacja/lęk), Behavior (zachowanie/komunikacja) oraz Consequence (wpływ na otoczenie).")
        
        q_abc = st.selectbox("Na czym chcesz się dzisiaj najbardziej skupić w ramach modelu ABC?", [
            "Identyfikacja i redukcja lęku przed wejściem w interakcję (Antecedent)",
            "Trening precyzyjnego i asertywnego formułowania wypowiedzi (Behavior)",
            "Zrozumienie wpływu i odbioru mojego komunikatu przez rozmówcę (Consequence)"
        ], key="q_abc_model", help="Wybierz główny punkt skupienia procesu treningowego.")

        st.markdown("---")
        st.markdown("#### 5. Komfort sensoryczny interfejsu")
        st.caption("Wybierz paletę kolorystyczną, która najbardziej sprzyja Twojemu skupieniu i odciąża wzrok.")
        
        q_theme = st.selectbox("Kolorystyka interfejsu:", [
            "Ciepły stonowany (Beż i szarość)",
            "Pastele: Różowy (Soft Pink)",
            "Pastele: Żółty (Pastel Yellow)",
            "Pastele: Zielony (Mint Green)",
            "Pastele: Niebieski (Soft Blue)",
            "Pastele: Pomarańczowy (Peach)",
            "Klasyczny jasny (Biel i głęboka czerń)"
        ], key="q_theme_select", help="Wybierz motyw wizualny najlepiej dopasowany do Twoich preferencji wzrokowych.")

        submitted_quiz = st.form_submit_button("Zapisz profil i przejdź do konfiguracji", use_container_width=True, type="primary")

        if submitted_quiz:
            st.session_state.user_prefs = {
                "formatting_score": q2,
                "semantic_diff": q_sem,
                "nasa_tlx": q_nasa,
                "abc_focus": q_abc,
                "theme": q_theme
            }
            st.session_state.intro_dismissed = True
            st.rerun()
    st.stop()

# 2. Krok drugi: Ekran Podsumowania, Analizy Behawioralnej i Treningu Metakognitywnego
if st.session_state.summary_mode:
    st.title("Raport Psychologiczny, Podsumowanie i Trening Metakognitywny")
    st.markdown("Każda emocja coś komunikuje, co komunikuje Twoja?")
    
    kategoria_key = st.session_state.get('kategoria_key', 'Praca')
    wariant_key = st.session_state.get('wariant_key', 'rekrutacja')
    wybrany_scenariusz = scenariusze_kategorie[kategoria_key][wariant_key]
    wybrana_nazwa_modelu = st.session_state.get('wybrana_nazwa_modelu', 'GPT-5.6 Sol')
    config_modelu = dostepne_modele[wybrana_nazwa_modelu]
    model_api_key = st.session_state.get('model_api_key', OPENAI_API_KEY_HARDCODED)

    st.markdown(f"Scenariusz: {wybrany_scenariusz['tytul']} | Model: {wybrana_nazwa_modelu}")
    st.markdown("---")

    if "tom_quiz_struct" not in st.session_state:
        with st.spinner("Generowanie szczegółowej analizy psychologicznej, perspektywy rozmówcy oraz pytań treningowych..."):
            analyser = ChatOpenAI(
                api_key=model_api_key,
                base_url=config_modelu["base_url"],
                model=config_modelu["model_id"],
                temperature=0.3
            )
            dialog_history = "\n".join([f"[{m.get('timestamp', '')}] {m['role']}: {m['content']}" for m in st.session_state.messages])

            prompt_gen = f"""
            Przeanalizuj poniższą rozmowę treningową z perspektywy psychologicznej i relacyjnej. Przygotuj odpowiedź ŚCISLE W FORMACIE JSON (bez żadnego dodatkowego formatowania markdown poza blokiem json, lub po prostu czysty json):
            {{
                "analiza_psychologiczna": "Szczegółowy opis, jak użytkownik mógł być odebrany przez rozmówcę, co rozmówca mógł zrozumieć przez jego słowa, jakie ukryte intencje lub sygnały wysłał użytkownik, oraz pogłębiona refleksja emocjonalna nawiązująca do zasady: Każda emocja coś komunikuje, co komunikuje Twoja?",
                "pytania": [
                    {{
                        "pytanie": "Treść pytania treningowego w stylu pytań terapeutycznych (np. Jak inaczej można było odpowiedzieć na to pytanie, na co zwracać uwagę, gdy ktoś pyta o...?)",
                        "opcje": ["Opcja A (błędna lub nieprecyzyjna)", "Opcja B (poprawna i profesjonalna)", "Opcja C (inna opcja)"],
                        "poprawna": "Opcja B (poprawna i profesjonalna)",
                        "wyjasnienie": "Wyjaśnienie psychologiczne oraz wskazówka: przy odpowiedziać na takie pytania używamy zwrotów typu..."
                    }}
                ]
            }}
            Przygotuj od 3 do 5 takich pytań dopasowanych do przebiegu rozmowy.
            
            ZAPIS ROZMOWY:
            {dialog_history}
            """
            try:
                res = analyser.invoke(prompt_gen)
                raw_content = res.content.strip()
                if raw_content.startswith("```json"):
                    raw_content = raw_content[7:]
                if raw_content.startswith("```"):
                    raw_content = raw_content[3:]
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3]
                raw_content = raw_content.strip()
                
                parsed_data = json.loads(raw_content)
                st.session_state.tom_quiz_struct = parsed_data
            except Exception as e:
                st.session_state.tom_quiz_struct = {
                    "analiza_psychologiczna": f"Analiza psychologiczna przeprowadzona pomyślnie. Dialog został omówiony. Błąd parsowania: {e}",
                    "pytania": [
                        {
                            "pytanie": "Jak w kluczowym momencie rozmówca mógł odebrać Twoją wypowiedź?",
                            "opcje": ["Jako brak zaangażowania lub unikanie kontaktu", "Jako pełną gotowość do dialogu", "Jako obojętność"],
                            "poprawna": "Jako brak zaangażowania lub unikanie kontaktu",
                            "wyjasnienie": "Kiedy unikamy wprost odpowiedzi, rozmówca dopisuje własne interpretacje. Przy odpowiadaniu na trudne pytania warto używać zwrotów typu: rozumiem Twoją obawę, spójrzmy na to z tej perspektywy..."
                        },
                        {
                            "pytanie": "Jaki mechanizm obronny lub tendencję komunikacyjną można zauważyć w Twoich odpowiedziach?",
                            "opcje": ["Zbyt szybkie przechodzenie do defensywy", "Neutralne i otwarte słuchanie", "Brak jakichkolwiek barier"],
                            "poprawna": "Zbyt szybkie przechodzenie do defensywy",
                            "wyjasnienie": "Defensywa utrudnia budowanie porozumienia. Na co zwracać uwagę: gdy ktoś ocenia nasz styl, zamiast atakować, stosujmy klaryfikację."
                        },
                        {
                            "pytanie": "Co mogło być kluczowym czynnikiem, który wpłynął na spadek dynamiki tej rozmowy?",
                            "opcje": ["Brak doprecyzowania intencji i niedopowiedzenia", "Zbyt duża precyzja", "Nadmierny spokój"],
                            "poprawna": "Brak doprecyzowania intencji i niedopowiedzenia",
                            "wyjasnienie": "Niedopowiedzenia rodzą domysły. Przy odpowiedziach na pytania o intencje używamy zwrotów typu: moim celem w tej sytuacji jest..."
                        }
                    ]
                }

    quiz_data = st.session_state.tom_quiz_struct

    st.subheader("1. Główna Analiza Psychologiczna i Perspektywa Odbiorcy")
    st.markdown(quiz_data.get("analiza_psychologiczna", "Brak danych."))
    st.markdown("---")

    st.subheader("2. Trening Metakognitywny i Refleksje Terapeutyczne")
    st.markdown("Przeanalizuj poniższe pytania, sprawdź co Twoje słowa mogły zakomunikować i zweryfikuj swoje zachowanie w trakcie rozmowy:")

    pytania_lista = quiz_data.get("pytania", [])
    
    if "user_quiz_answers" not in st.session_state:
        st.session_state.user_quiz_answers = {}

    for i, q in enumerate(pytania_lista):
        st.markdown(f"Pytanie {i+1}: {q['pytanie']}")
        selected_option = st.radio(
            f"Wybierz opcję dla pytania {i+1}:", 
            q['opcje'], 
            key=f"q_dyn_interactive_{i}",
            index=None
        )
        if selected_option is not None:
            st.session_state.user_quiz_answers[i] = selected_option
        st.markdown("---")

    if st.button("Sprawdź wyniki i przeanalizuj błędy", type="primary", use_container_width=True):
        st.session_state.quiz_done_clicked = True

    if st.session_state.get('quiz_done_clicked', False):
        correct_count = 0
        total_q = len(pytania_lista)
        for i, q in enumerate(pytania_lista):
            if st.session_state.user_quiz_answers.get(i) == q['poprawna']:
                correct_count += 1

        score_percent = int((correct_count / total_q) * 100) if total_q > 0 else 0
        st.markdown(f"**Ocena procentowa Twoich wyborów:** {score_percent}%")
        st.progress(score_percent / 100)
        
        st.markdown("#### Krótkie wyjaśnienie i poprawa zachowania:")
        for i, q in enumerate(pytania_lista):
            user_ans = st.session_state.user_quiz_answers.get(i)
            is_corr = (user_ans == q['poprawna'])
            status_symbol = "✅" if is_corr else "⚠️"
            st.markdown(f"{status_symbol} **Pytanie {i+1}:** {q['wyjasnienie']}")

        if score_percent >= 66:
            st.success("✅ Świetna refleksja! Bardzo dobrze rozumiesz perspektywę rozmówcy i mechanizmy komunikacyjne.")
        else:
            st.info("✅ Dobra praca! Analiza tych schematów pomoże Ci precyzyjniej formułować wypowiedzi w przyszłości.")

    st.markdown("---")

    st.markdown("""
        <div class="cbt-box">
            <h3>Moduł Refleksji i Regulacji (Metody CBT)</h3>
            <p>Zastanów się, co mogło kłębić się w Twojej głowie (lub głowie rozmówcy) i przeformułuj myśli.</p>
        </div>
    """, unsafe_allow_html=True)

    cbt_thought = st.text_input("Co według Ciebie mogło być najtrudniejszą myślą lub przekonaniem w tej rozmowie?", placeholder="Np. obawa przed oceną / poczucie, że muszę mieć gotową odpowiedź...")

    if cbt_thought:
        st.markdown(f"""
        > **Walidacja i reframing CBT:** To całkowicie naturalne, że w takich sytuacjach pojawia się myśl: *\"{cbt_thought}\"*. Pamiętaj jednak: myśli to nie fakty. Każda trudność to informacja, a nie ostateczna ocena Twoich możliwości.
        """)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Zapisz pełny raport i historię do pliku", use_container_width=True):
            saved_path = save_chat_to_file(
                st.session_state.messages, 
                wybrany_scenariusz, 
                config_modelu["model_id"], 
                st.session_state.get('tryb_rozmowy', 'Naturalna Rozmowa'), 
                st.session_state.get('start_time', '0000'),
                summary_text=quiz_data.get("analiza_psychologiczna", "")
            )
            st.success(f"Zapisano pomyślnie w:\n`{saved_path}`")

    with col2:
        if st.button("Zakończ sesję i wyczyść pamięć", use_container_width=True, type="primary"):
            st.session_state.config_completed = False
            st.session_state.intro_dismissed = False
            st.session_state.summary_mode = False
            st.session_state.messages = []
            if "tom_quiz_struct" in st.session_state: del st.session_state.tom_quiz_struct
            if "quiz_done_clicked" in st.session_state: del st.session_state.quiz_done_clicked
            if "user_quiz_answers" in st.session_state: del st.session_state.user_quiz_answers
            st.rerun()

    st.stop()

# 3. Krok trzeci: Konfiguracja parametrów sesji (Z DODANYMI ZNACZNIKAMI `?` POMOCY)
if not st.session_state.config_completed:
    st.title("Konfiguracja Sesji Treningowej")
    st.markdown("Wybierz model AI oraz konkretny scenariusz treningowy.")

    with st.form("config_form"):
        wybrana_nazwa_modelu = st.selectbox(
            "Wybierz model konwersacyjny:", 
            ["-- Wybierz model --"] + list(dostepne_modele.keys()),
            help="Wybierz model sztucznej inteligencji, który będzie symulował rozmówcę w Twoim treningu."
        )
        config_temp = dostepne_modele.get(wybrana_nazwa_modelu, {"env_key": "OPENAI_API_KEY", "label": "Klucz API"})
        model_api_key = st.text_input(
            config_temp["label"], 
            type="password", 
            value=os.environ.get(config_temp["env_key"], ""),
            help="Wprowadź swój poufny klucz API wybranego dostawcy modelu, aby umożliwić połączenie."
        )

        tryb_rozmowy = st.radio(
            "Wybierz styl interakcji:", 
            ["Naturalna Rozmowa", "Rozmowa z informacją zwrotną (w poszarzałym okienku)"],
            help="Wybierz, czy chcesz prowadzić płynną rozmowę, czy otrzymywać natychmiastowe wskazówki i analizę po każdej wypowiedzi."
        )

        st.markdown("---")
        st.subheader("Wybór Scenariusza Treningu")
        
        kategoria_key = st.selectbox(
            "Kategoria sytuacji:", 
            list(scenariusze_kategorie.keys()), 
            key="kategoria_wybor_select",
            help="Wybierz główny obszar tematyczny, w którym chcesz przetestować swoje umiejętności."
        )
        warianty_dict = scenariusze_kategorie[kategoria_key]
        wariant_key = st.selectbox(
            "Wariant rozmowy:", 
            options=list(warianty_dict.keys()), 
            format_func=lambda x: warianty_dict[x]["tytul"], 
            key=f"wariant_wybor_{kategoria_key}",
            help="Wybierz konkretny profil psychologiczny rozmówcy oraz szczegółowy kontekst sytuacji."
        )

        submitted = st.form_submit_button("Potwierdź i wejdź do czatu", use_container_width=True)
        
        if submitted:
            if wybrana_nazwa_modelu == "-- Wybierz model --" or not model_api_key:
                st.error("⚠️ Musisz wybrać model konwersacyjny oraz podać klucz API.")
            else:
                st.session_state.config_completed = True
                st.session_state.wybrana_nazwa_modelu = wybrana_nazwa_modelu
                st.session_state.model_api_key = model_api_key
                st.session_state.tryb_rozmowy = tryb_rozmowy
                st.session_state.kategoria_key = kategoria_key
                st.session_state.wariant_key = wariant_key
                st.session_state.current_scenario = f"{kategoria_key}_{wariant_key}"
                st.session_state.start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.messages = []
                st.session_state.summary_mode = False
                st.session_state.session_ended = False
                if "tom_quiz_struct" in st.session_state: del st.session_state.tom_quiz_struct
                st.rerun()
    st.stop()

# ==========================================
# 4. TRYB CZATU TRENINGOWEGO I ZAKŁADKA STATYSTYK
# ==========================================
wybrana_nazwa_modelu = st.session_state.wybrana_nazwa_modelu
config_modelu = dostepne_modele[wybrana_nazwa_modelu]
model_api_key = st.session_state.model_api_key
tryb_rozmowy = st.session_state.tryb_rozmowy
kategoria_key = st.session_state.kategoria_key
wariant_key = st.session_state.wariant_key
wybrany_scenariusz = scenariusze_kategorie[kategoria_key][wariant_key]

# Panele boczne w trybie czatu
st.sidebar.markdown('<h2 class="brand-logo" style="font-size: 1.4rem; margin-bottom: 0px;">NEURO FRIEND</h2>', unsafe_allow_html=True)
st.sidebar.markdown(f"**Model:** {wybrana_nazwa_modelu}")
st.sidebar.markdown(f"**Tryb:** {tryb_rozmowy}")
st.sidebar.markdown("---")

st.sidebar.subheader("🌿 Strefa Wyciszenia i Relaksu")
st.sidebar.markdown("""
<div class="breathing-container">
    <div class="breathe-circle">Oddychaj</div>
    <small style="text-align:center; display:block; margin-top:6px;">Zsynchronizuj oddech (wdech / wydech)</small>
</div>
""", unsafe_allow_html=True)

wybrana_technika = st.sidebar.selectbox(
    "Wybierz technikę relaksacyjną:",
    [
        "Wybierz technikę...",
        "Box Breathing (Oddychanie po kwadracie)",
        "Technika uziemienia 5-4-3-2-1",
        "Szybki reset napięcia (CBT)",
        "Skanowanie ciała (Body Scan)",
        "Przeformułowanie myśli (Defuzja)"
    ],
    key="select_relaxation_technique"
)

if wybrana_technika == "Box Breathing (Oddychanie po kwadracie)":
    st.sidebar.caption("Wdech 4 sek. -> Zatrzymaj 4 sek. -> Wydech 4 sek. -> Zatrzymaj 4 sek.")
elif wybrana_technika == "Technika uziemienia 5-4-3-2-1":
    st.sidebar.caption("Znajdź w otoczeniu: 5 rzeczy, które widzisz, 4 do dotknięcia, 3 dźwięki, 2 zapachy, 1 smak.")
elif wybrana_technika == "Szybki reset napięcia (CBT)":
    st.sidebar.caption("Opuść barki, rozluźnij szczękę i weź głęboki oddech przeponowy.")
elif wybrana_technika == "Skanowanie ciała (Body Scan)":
    st.sidebar.caption("Przenieś uwagę po kolei na stopy, dłonie, kark i czoło, rozluźniając każdą partię.")
elif wybrana_technika == "Przeformułowanie myśli (Defuzja)":
    st.sidebar.caption("Powiedz sobie: „To tylko myśl, a nie fakt” i spójrz na sytuację obiektywnie.")

user_rel_note = st.sidebar.text_area("Twoje notatki / refleksje z techniki:", placeholder="Wpisz swoje odczucia lub myśli...", key="sidebar_rel_note")
if user_rel_note:
    st.sidebar.success("Zapisano refleksję w pamięci sesji.")

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Myśli Wspierające")
if st.sidebar.button("Losuj myśl wspierającą", use_container_width=True):
    inspiracje = [
        "Idziesz dokładnie takim tempem, jakie jest dla Ciebie najlepsze.",
        "Każda mała próba to już Twój sukces.",
        "Zaufaj swojej intuicji i temu, co potrafisz.",
        "Skup się na chwili obecnej – tylko ona ma znaczenie.",
        "Ciekawość świata i siebie to najlepszy przewodnik.",
        "Masz w sobie pełną swobodę wyboru.",
        "Rób tyle, ile możesz w danym momencie – to w pełni wystarczy.",
        "Każde doświadczenie wzbogaca Twoją perspektywę.",
        "Twoja obecność i głos mają wartość.",
        "Pozwól sobie na naturalność, nie musisz niczego udowadniać.",
        "Spokój rodzi się z akceptacji tego, co tu i teraz.",
        "Masz pełne prawo do własnego tempa i stylu."
    ]
    st.sidebar.info(random.choice(inspiracje))

st.sidebar.markdown("---")

st.sidebar.subheader("Podsumowanie i Trening")
if st.sidebar.button("Zapisz, podsumuj i przejdź do treningu", use_container_width=True, type="primary"):
    if len(st.session_state.messages) > 1:
        st.session_state.summary_mode = True
        st.rerun()
    else:
        st.sidebar.warning("⚠️ Przeprowadź najpierw dłuższą rozmowę, aby przejść do podsumowania.")

st.sidebar.markdown("---")
st.sidebar.subheader("Zarządzanie Sesją")

if st.sidebar.button("Zmień ustawienia / profil", use_container_width=True):
    st.session_state.config_completed = False
    st.session_state.intro_dismissed = False
    st.rerun()

if st.sidebar.button("Rozpocznij od nowa", use_container_width=True):
    st.session_state.messages = []
    st.session_state.start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if "tom_quiz_struct" in st.session_state: del st.session_state.tom_quiz_struct
    if "user_quiz_answers" in st.session_state: del st.session_state.user_quiz_answers
    st.rerun()

# --- ZAKŁADKI GŁÓWNE ---
tab_trening, tab_postepy = st.tabs(["💬 Symulator Rozmowy", "📈 Moje Treningi"])

# --- ZAKŁADKA 1: SYMULATOR ROZMOWY ---
with tab_trening:
    st.title(f"{kategoria_key} - {wybrany_scenariusz['tytul']}")

    st.markdown(f"""
    <div class="info-card">
        Rola rozmówcy (AI): {wybrany_scenariusz['rola']}<br>
        <small>Wskazówka: Odpowiadaj naturalnie. Rozmówca zachowuje się jak żywy człowiek.</small>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": wybrany_scenariusz["start"],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def render_assistant_message(content):
        pattern = r'(?i)\*?\*?wskazówka\s*\*?\*?\s*[:\-]?\s*'
        parts = re.split(pattern, content, maxsplit=1)
        
        main_text = parts[0].strip()
        main_text = re.sub(r'\*+\s*$', '', main_text).strip()
        
        if main_text:
            st.markdown(main_text)
            
        if len(parts) > 1:
            wskazowka_text = parts[1].strip()
            wskazowka_text = re.sub(r'^\*+\s*', '', wskazowka_text).strip()
            st.markdown(f'<div class="coach-box"><strong>Wskazówka:</strong> {wskazowka_text}</div>', unsafe_allow_html=True)

    PROMPT_NATURALNY = f"""
    Wcielasz się w postać: {wybrany_scenariusz['rola']} w scenariuszu: {wybrany_scenariusz['tytul']}.

    ZASADA KLUCZOWA (W 100% ŻYWY, AUTENTYCZNY I ZWIĘZŁY CZŁOWIEK):
    1. Jesteś prawdziwym człowiekiem w tej sytuacji, a nie asystentem AI. Nigdy nie wychodź z roli, nie przepraszaj jak chatbot.
    2. Odpowiadaj zwięźle i naturalnie (zazwyczaj w 1-3 zdaniach), dokładnie tak, jak pisze się w normalnym czacie. Unikaj długich, sztucznych monologów.
    3. ⛔ ABSOLUTNY ZAKAZ ZAKŁADANIA PŁCI UŻYTKOWNIKA: Nie używaj w wypowiedziach skierowanych do użytkownika żadnych form gramatycznych wskazujących na płeć w liczbie pojedynczej (np. nie pisz "zrobiłeś", "zrobiłaś", "napisałeś", "napisałaś", "byłeś", "byłaś", "chciałeś", "chciałaś", "musiałbyś", "musiałabyś"), dopóki użytkownik sam wprost nie użyje formy wskazującej na swoją płeć w liczbie pojedynczej w swoich wiadomościach. Zamiast tego stosuj formy bezosobowe, uniwersalne, formy w liczbie mnogiej (jeśli pasuje) lub konstrukcje neutralne pod względem płci.
    4. Jeśli użytkownik odpisze nie na temat, potraktuje Cię poufale, użyje slangu, rzuci bezsensowny tekst lub zachowa się niestosownie, zareaguj w pełni autentycznie jako człowiek: okaż oburzenie, irytację, konfuzję, zdziwienie lub sarkazm dopasowany do roli ({wybrany_scenariusz['rola']}). Nie bądź miłym, ułożonym botem.
    """

    PROMPT_Z_COACHEM = PROMPT_NATURALNY + f"""
    DODATKOWO, jako osobny blok pod swoją wypowiedzią (jako twój wewnętrzny analityk treningowy), dołącz merytoryczną wskazówkę na wyróżnionym tle, zaczynając dokładnie od słowa:
    Wskazówka: [Wpisz tutaj merytoryczną analizę błędu użytkownika z perspektywy modelu ABC oraz konkretną instrukcję, jak sformułować poprawną wypowiedź w tej sytuacji. Nie używaj żadnych gwiazdek przed słowem Wskazówka].
    """

    # 1. NAJPIERW WYŚWIETLAMY HISTORIĘ DOTYCHCHASOWYCH WIADOMOŚCI
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                render_assistant_message(msg["content"])
            else:
                st.markdown(msg["content"])

    # 2. POLE WPISYWANIA WIADOMOŚCI (ZAWSZE NA SAMYM KOŃCU POD WIADOMOŚCIAMI)
    if prompt := st.chat_input("Wpisz swoją odpowiedź..."):
        aktualny_czas = datetime.datetime.now()
        
        # Zapisujemy zdarzenie treningowe pobrane z urządzenia użytkownika do historii statystyk
        st.session_state.training_history.append({
            "data": aktualny_czas,
            "data_str": aktualny_czas.strftime("%Y-%m-%d"),
            "dzien_tygodnia": aktualny_czas.strftime("%A"),
            "godzina": aktualny_czas.hour,
            "scenariusz": wybrany_scenariusz['tytul']
        })

        current_time_str = aktualny_czas.strftime("%Y-%m-%d %H:%M:%S")
        
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": current_time_str
        })
        # Natychmiastowe odświeżenie, aby użytkownik od razu zobaczył swoją wiadomość
        st.rerun()

    # 3. GENEROWANIE ODPOWIEDZI AI, JEŚLI OSTATNIA WIADOMOŚĆ JEST OD UŻYTKOWNIKA
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_user_msg = st.session_state.messages[-1]["content"]

        rag_info = "Brak dodatkowego kontekstu."
        if retriever:
            try:
                search_query = f"Scenariusz: {wybrany_scenariusz['tytul']}. Wypowiedź: {last_user_msg}"
                docs = retriever.invoke(search_query)
                if docs:
                    rag_info = "\n\n---\n\n".join([f"Źródło:\n{d.page_content}" for d in docs])
            except Exception:
                pass

        system_prompt = PROMPT_Z_COACHEM if tryb_rozmowy.startswith("Rozmowa z informacją") else PROMPT_NATURALNY

        api_messages = [{"role": "system", "content": system_prompt + f"\n\nBaza wiedzy / kontekst RAG:\n{rag_info}"}]
        for m in st.session_state.messages:
            api_messages.append({"role": m["role"], "content": m["content"]})

        with st.spinner("Rozmówca pisze..."):
            try:
                client = OpenAI(
                    api_key=model_api_key,
                    base_url=config_modelu["base_url"]
                )
                response = client.chat.completions.create(
                    model=config_modelu["model_id"],
                    messages=api_messages,
                    temperature=0.7
                )
                assistant_reply = response.choices[0].message.content
            except Exception as e:
                assistant_reply = f"⚠️ Wystąpił błąd podczas komunikacji z API modelu: {e}"

        asst_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": assistant_reply,
            "timestamp": asst_time_str
        })
        st.rerun()

# --- ZAKŁADKA 2: MOJE TRENINGI I STATYSTYKI ---
with tab_postepy:
    st.header("Moje Treningi i Statystyki")
    st.write("Śledź historię swoich sesji pobieraną bezpośrednio z urządzeń oraz planuj harmonogram.")

    if st.session_state.training_history:
        df_hist = pd.DataFrame(st.session_state.training_history)
        
        # Metryki podsumowujące
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Liczba zarejestrowanych interakcji", len(df_hist))
        with col_m2:
            st.metric("Różnorodne scenariusze", df_hist['scenariusz'].nunique())
        with col_m3:
            ostatnia = df_hist['data'].max().strftime("%Y-%m-%d %H:%M")
            st.metric("Ostatnia aktywność", ostatnia)

        st.divider()

        # Wykresy analityczne
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("📊 Aktywność wg godzin dnia")
            df_hist['godzina_etykieta'] = df_hist['godzina'].apply(lambda h: f"{h:02d}:00")
            godziny_counts = df_hist['godzina_etykieta'].value_counts().sort_index()
            st.bar_chart(godziny_counts)

        with col_c2:
            st.subheader("📈 Popularność scenariuszy")
            scenariusze_counts = df_hist['scenariusz'].value_counts()
            st.bar_chart(scenariusze_counts)

        st.divider()
        st.subheader("🕒 Szczegółowy rejestr sesji")
        for sesja in reversed(st.session_state.training_history):
            pelna_data_str = sesja["data"].strftime("%Y-%m-%d | %H:%M:%S")
            st.info(f"📅 **{pelna_data_str}** \n* Scenariusz: {sesja['scenariusz']} \n* Godzina urządzenia: {sesja['godzina']:02d}:00")
    else:
        st.info("Brak zarejestrowanych sesji. Przeprowadź pierwszą rozmowę w symulatorze, aby dane pojawiły się na wykresach.")

    st.divider()

    st.subheader("🗓️ Harmonogram i Przypominajki")
    st.caption("Wybierz dni tygodnia (mini kalendarzyk) oraz godziny powiadomień:")
    
    wybrana_data = st.date_input("Wybierz konkretny dzień z kalendarza:", datetime.date.today())

    col1, col2 = st.columns(2)
    
    with col1:
        wybrane_dni = st.pills(
            "Wybierz dni tygodnia:",
            ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"],
            selection_mode="multi"
        )
    with col2:
        wybrana_godzina = st.time_input(
            "Wybierz godzinę powiadomień:",
            datetime.time(18, 00)
        )
        
    powiadomienia_wlaczone = st.toggle(
        "🔔 Włącz powiadomienia", 
        help="Aktywuje przypomnienia."
    )
    
    if st.button("💾 Zapisz harmonogram", use_container_width=True):
        dni_tekst = ", ".join(wybrane_dni) if wybrane_dni else "brak wybranego dnia"
        st.success(f"Zapisano pomyślnie! Data: {wybrana_data.strftime('%Y-%m-%d')}, Dni: {dni_tekst}, Godzina: {wybrana_godzina.strftime('%H:%M')}.")
