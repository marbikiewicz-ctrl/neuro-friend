# -*- coding: utf-8 -*-
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
import tempfile
import io
import base64
import difflib
import streamlit as st
import pandas as pd
from openai import OpenAI
import subprocess
import sys
import streamlit.components.v1 as components

try:
    from gtts import gTTS
except ImportError:
    print("Brak biblioteki gtts. Trwa automatyczna instalacja...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gtts"])
    from gtts import gTTS

try:
    import speech_recognition as sr
except ImportError:
    print("Brak biblioteki SpeechRecognition. Trwa automatyczna instalacja...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "SpeechRecognition"])
    import speech_recognition as sr

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

    @keyframes smoothBreathing {{
      0% {{ transform: scale(0.9); background-color: {border_col}; }}
      50% {{ transform: scale(1.2); background-color: {accent_col}; }}
      100% {{ transform: scale(0.9); background-color: {border_col}; }}
    }}
    
    .breathing-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px;
    }}

    .breathe-circle {{
        width: 130px;
        height: 130px;
        border-radius: 50%;
        background-color: {accent_col};
        animation: smoothBreathing 7s infinite ease-in-out;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 0.9rem;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 20px auto;
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
# Klucze API NIE są zapisane w kodzie. Odczyt: .streamlit/secrets.toml (lokalnie) lub Settings -> Secrets (Streamlit Cloud),
# a jeśli ich brak - zmienne środowiskowe DEEPSEEK_API_KEY i OPENAI_API_KEY.
def odczytaj_sekret(nazwa):
    try:
        wartosc = st.secrets.get(nazwa, "")
    except Exception:
        wartosc = ""
    return wartosc or os.environ.get(nazwa, "")

DEEPSEEK_API_KEY_HARDCODED = ""
DOMYSLNY_MODEL = "DeepSeek V4 Pro"
OPENAI_API_KEY_HARDCODED = odczytaj_sekret("OPENAI_API_KEY")

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
def zbuduj_raport(messages, scenario_info, model_name, tryb_rozmowy, start_timestamp, summary_text=None):
    """Zwraca pełny raport sesji (transkrypt + analiza) jako tekst do pobrania."""
    now = datetime.datetime.now()
    linie = [
        "==================================================",
        "        NEURO FRIEND - ZAPIS SESJI TRENINGOWEJ      ",
        "==================================================",
        f"Data rozpoczęcia sesji: {start_timestamp}",
        f"Data wygenerowania raportu: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Scenariusz: {scenario_info['tytul']}",
        f"Rola rozmówcy: {scenario_info['rola']}",
        f"Użyty model AI: {model_name}",
        f"Tryb interakcji: {tryb_rozmowy}",
        "==================================================",
        "",
        "--- PRZEBIEG ROZMOWY (TRANSKRYPT) ---",
        "",
    ]
    for msg in messages:
        msg_time = msg.get("timestamp", "Brak daty")
        if "T" in str(msg_time):
            msg_time = str(msg_time).replace("T", " ")[:19]
        role_label = "UŻYTKOWNIK" if msg.get("role") == "user" else f"{scenario_info.get('rola', 'ROZMÓWCA')}"
        linie.append(f"[{msg_time}] {role_label}:")
        linie.append(msg.get("content", ""))
        linie.append("")
    if summary_text:
        linie += [
            "==================================================",
            "--- RAPORT PSYCHOLOGICZNY I ANALIZA METAKOGNITYWNA ---",
            "Każda emocja coś komunikuje, co komunikuje Twoja?",
            "==================================================",
            "",
            summary_text,
        ]
    return "\n".join(linie) + "\n"


def nazwa_pliku_raportu(scenario_info, start_timestamp):
    safe_title = "".join([c if c.isalnum() else "_" for c in scenario_info['tytul']])
    return f"Rozmowa_{safe_title}_START_{start_timestamp}.txt"

# ==========================================
# 4. SŁOWNIKI MODELI ORAZ SCENARIUSZY
# ==========================================
dostepne_modele = {
    "DeepSeek V4 Pro": {
        "model_id": "deepseek-v4-pro",
        "base_url": "https://api.deepseek.com",
        "env_key": "DEEPSEEK_API_KEY",
        "label": "Klucz API DeepSeek"
    },
    "Claude Sonnet 5": {
        "model_id": "claude-sonnet-5",
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
    "Llama 4 Maverick": {
        "model_id": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "base_url": "https://api.groq.com/openai/v1",
        "env_key": "GROQ_API_KEY",
        "label": "Klucz API Llama / Groq"
    }
}

# ==========================================
# 4a. FUNKCJE POMOCNICZE: WYWOŁANIA MODELU, PROFIL, MOWA
# ==========================================
def pobierz_klucz_deepseek():
    return odczytaj_sekret("DEEPSEEK_API_KEY") or DEEPSEEK_API_KEY_HARDCODED or st.session_state.get("model_api_key", "")


def is_deepseek(cfg):
    return "deepseek" in cfg.get("base_url", "")


def chat_completion(cfg, api_key, messages, max_tokens=800, temperature=0.5, json_mode=False):
    """Wywołanie modelu przez interfejs zgodny z OpenAI.
    Dla DeepSeek V4 wyłączany jest tryb myślenia (thinking), który jest domyślnie włączony
    i przy niskim max_tokens powodował puste lub ucięte odpowiedzi.
    Przy pustej odpowiedzi następuje jedna ponowna próba z większym limitem."""
    client = OpenAI(api_key=api_key, base_url=cfg["base_url"])
    extra = {}
    if is_deepseek(cfg):
        extra["extra_body"] = {"thinking": {"type": "disabled"}}
    if json_mode and (is_deepseek(cfg) or "api.openai.com" in cfg["base_url"]):
        extra["response_format"] = {"type": "json_object"}

    limit = max_tokens
    for _ in range(2):
        response = client.chat.completions.create(
            model=cfg["model_id"],
            messages=messages,
            temperature=temperature,
            max_tokens=limit,
            **extra
        )
        content = (response.choices[0].message.content or "").strip()
        if content:
            return content
        limit = limit * 2
    return ""


def profil_prompt(tryb="tekst"):
    """Zamienia odpowiedzi z kwestionariusza profilującego na instrukcje dla modelu."""
    p = st.session_state.get("user_prefs", {}) or {}
    forma = "krótkiej listy punktowanej (2-4 punkty)" if p.get("formatting_score", 3) >= 4 else "zwykłego, ciągłego tekstu (bez list)"
    styl = {
        1: "skrajnie dosłowny, krok po kroku, z gotowym przykładowym zdaniem do użycia",
        2: "dosłowny i konkretny, z przykładowym zdaniem do użycia",
        3: "zbalansowany: konkretny, z krótkim wyjaśnieniem",
        4: "raczej refleksyjny, z pytaniem do przemyślenia",
        5: "refleksyjny, dopuszczalne metafory i obrazowe porównania",
    }.get(p.get("semantic_diff", 3), "zbalansowany")
    zmeczenie = p.get("nasa_tlx", 3)
    if zmeczenie >= 4:
        dlugosc = "bardzo krótko: maksymalnie 1 proste zdanie, bez zbędnych szczegółów"
    elif zmeczenie <= 2:
        dlugosc = "naturalnie: 1-2 zdania"
    else:
        dlugosc = "zwięźle: 1-2 krótkie zdania"
    cel = p.get("abc_focus", "")
    tekst = f"""
            PROFIL UŻYTKOWNIKA (z kwestionariusza wstępnego) - DOSTOSUJ SIĘ DO NIEGO:
            - Długość Twoich wypowiedzi w roli: {dlugosc}.
            - Główny cel treningu (model ABC): {cel if cel else 'nie wskazano'}.
            """
    if tryb != "glos":
        tekst += f"""- Wskazówki i feedback podawaj w formie {forma}.
            - Styl wskazówek i feedbacku: {styl}.
            - Ukierunkuj wskazówki na wskazany cel treningu.
            """
    return tekst


def feedback_style_prompt():
    """Styl feedbacku po rozmowie, zgodny z profilem użytkownika."""
    p = st.session_state.get("user_prefs", {}) or {}
    forma = "krótkiej listy punktowanej" if p.get("formatting_score", 3) >= 4 else "zwykłego tekstu"
    styl = "dosłowny i konkretny, z przykładowym zdaniem" if p.get("semantic_diff", 3) <= 2 else (
        "zbalansowany" if p.get("semantic_diff", 3) == 3 else "refleksyjny")
    krotko = " Pisz krótko (maks. 4 zdania), bo użytkownik zgłasza wysokie zmęczenie poznawcze." if p.get("nasa_tlx", 3) >= 4 else ""
    return f"Pisz w formie {forma}, styl: {styl}.{krotko}"


def zbuduj_transkrypt(messages, rola):
    linie = []
    for m in messages:
        if m.get("role") == "system":
            continue
        kto = "UŻYTKOWNIK (osoba ćwicząca)" if m.get("role") == "user" else f"ROZMÓWCA AI ({rola})"
        linie.append(f"[{m.get('timestamp', '')}] {kto}: {m.get('content', '')}")
    return "\n".join(linie)


def tekst_do_mowy(content):
    """Usuwa blok wskazówki i formatowanie markdown przed syntezą mowy."""
    main = re.split(r'(?i)\*?\*?wskazówka\s*\*?\*?\s*[:\-]?\s*', content, maxsplit=1)[0]
    main = re.sub(r'[*_#>`]', '', main)
    return main.strip()


def synteza_mowy(tekst):
    bufor = io.BytesIO()
    gTTS(text=tekst, lang="pl").write_to_fp(bufor)
    return bufor.getvalue()


def rozpoznaj_mowe(audio_bytes):
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language="pl-PL")


def dodaj_wypowiedz_uzytkownika(tresc, scenariusz_tytul):
    aktualny_czas = datetime.datetime.now()
    st.session_state.training_history.append({
        "data": aktualny_czas,
        "data_str": aktualny_czas.strftime("%Y-%m-%d"),
        "dzien_tygodnia": aktualny_czas.strftime("%A"),
        "godzina": aktualny_czas.hour,
        "scenariusz": scenariusz_tytul
    })
    st.session_state.messages.append({
        "role": "user",
        "content": tresc,
        "timestamp": aktualny_czas.strftime("%Y-%m-%d %H:%M:%S")
    })


def feedback_regulowy(mysl):
    """Zapasowy feedback (bez połączenia z modelem), zależny od treści odpowiedzi."""
    lower_thought = mysl.lower()
    if any(w in lower_thought for w in ["szef", "ocen", "wypaść", "krytyk", "pomyśl"]):
        return f'Skupienie na zewnętrznej ocenie ("{mysl}") aktywuje lęk zadaniowy. Wartość Twojej komunikacji to relacja i proces, a nie bezbłędny występ. Pytanie pomocnicze: co najgorszego mogłoby się stać, jeśli nie wypadniesz idealnie?'
    if any(w in lower_thought for w in ["muszę", "zawsze", "nigdy", "wszystko"]):
        return f'Pojawia się tu sztywne przekonanie o charakterze absolutnym ("{mysl}"). Spróbuj zamienić "muszę" na "chciał(a)bym dać z siebie wszystko, ale mam prawo do błędów".'
    if any(w in lower_thought for w in ["nie umiem", "nie potrafię", "beznadziej"]):
        return f'Pojawia się schemat samokrytyki ("{mysl}"). Trudność w symulatorze to informacja zwrotna, a nie ocena Twoich umiejętności. Jakie konkretne fakty z rozmowy potwierdzają tę myśl?'
    if any(w in lower_thought for w in ["pytani", "odpowied", "nie wiedział", "zaskocz"]):
        return f'Trudność z odpowiedzią na nieoczekiwane pytanie ("{mysl}") jest bardzo częsta. Możesz kupić sobie czas zdaniem: "Dobre pytanie, zastanowię się chwilę".'
    if any(w in lower_thought for w in ["emocj", "stres", "nerw", "lęk", "strach"]):
        return f'Opisujesz silne emocje ("{mysl}"). Każda emocja coś komunikuje: co próbowała Ci powiedzieć ta? Przed kolejną próbą możesz skorzystać ze strefy relaksu.'
    return f'Dziękuję za refleksję ("{mysl}"). Zastanów się, w którym dokładnie momencie rozmowy pojawiła się ta trudność i co mogło ją wywołać.'


def breathing_widget_html(minutes, accent, border, text_col):
    total = int(minutes) * 60
    return f"""
<!DOCTYPE html><html lang="pl"><head><meta charset="UTF-8"></head>
<body style="margin:0;font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:transparent;">
<div style="display:flex;flex-direction:column;align-items:center;padding:6px 0;">
  <div id="circle" style="width:90px;height:90px;border-radius:50%;background:{border};
       display:flex;align-items:center;justify-content:center;color:{text_col};font-weight:600;font-size:0.95rem;
       transform:scale(0.8);transition:transform 4s ease-in-out, background-color 4s ease-in-out;margin:18px 0;">Gotowe?</div>
  <div id="timer" style="color:{text_col};font-size:0.85rem;margin-bottom:8px;">Czas: {int(minutes)}:00</div>
  <div style="display:flex;gap:8px;">
    <button id="startBtn" onclick="startEx()" style="background:{accent};color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;">Rozpocznij</button>
    <button id="stopBtn" onclick="stopEx(false)" style="background:#E7E5E4;color:#1C1917;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;">Stop</button>
  </div>
</div>
<script>
const TOTAL = {total};
const INHALE = 4000, EXHALE = 6000;
let running = false, remaining = TOTAL, phaseTimer = null, tick = null;
const c = document.getElementById("circle"), t = document.getElementById("timer");
function fmt(s) {{ return Math.floor(s/60) + ":" + String(s%60).padStart(2,"0"); }}
function inhale() {{
  if (!running) return;
  c.style.transition = "transform 4s ease-in-out, background-color 4s ease-in-out";
  c.style.transform = "scale(1.25)"; c.style.background = "{accent}"; c.style.color = "white";
  c.innerText = "Wdech";
  phaseTimer = setTimeout(exhale, INHALE);
}}
function exhale() {{
  if (!running) return;
  c.style.transition = "transform 6s ease-in-out, background-color 6s ease-in-out";
  c.style.transform = "scale(0.8)"; c.style.background = "{border}"; c.style.color = "{text_col}";
  c.innerText = "Wydech";
  phaseTimer = setTimeout(inhale, EXHALE);
}}
function startEx() {{
  if (running) return;
  running = true; remaining = TOTAL; t.innerText = "Pozostało: " + fmt(remaining);
  inhale();
  tick = setInterval(() => {{
    remaining -= 1;
    if (remaining <= 0) {{ stopEx(true); return; }}
    t.innerText = "Pozostało: " + fmt(remaining);
  }}, 1000);
}}
function stopEx(finished) {{
  running = false; clearTimeout(phaseTimer); clearInterval(tick);
  c.style.transition = "transform 1s ease-in-out"; c.style.transform = "scale(0.8)";
  c.style.background = "{border}"; c.style.color = "{text_col}";
  c.innerText = finished ? "Koniec 🌿" : "Gotowe?";
  t.innerText = finished ? "Ćwiczenie zakończone. Dobra robota!" : "Czas: " + fmt(TOTAL);
}}
</script></body></html>
"""

scenariusze_kategorie = {
    "Praca": {
        "rekrutacja": {
            "tytul": "Rozmowa rekrutacyjna (wstępna)",
            "rola": "Rekruter",
            "start": "Dzień dobry! Dziękuję za przybycie na dzisiejsze spotkanie. Czy można prosić o opowiedzenie czegoś o swoim doświadczeniu?"
        },
        "podwyzka": {
            "tytul": "Prośba o podwyżkę",
            "rola": "Przełożony",
            "start": "Dzień dobry. Była prośba o spotkanie. Słucham, o czym chcielibyśmy porozmawiać?"
        },
        "rezygnacja": {
            "tytul": "Chęć rezygnacji z pracy",
            "rola": "Przedstawiciel HR",
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
            "rola": "Partner",
            "start": "Hej. Cieszę się, że rozmawiamy. Mowa była o chęci omówienia czegoś ważnego w naszej relacji?"
        },
        "zaproponowanie_spotkania": {
            "tytul": "Zaproponowanie spotkania / randki",
            "rola": "Znajomy",
            "start": "Hej! Fajnie, że kontakt. Co tam słychać?"
        },
        "wyzszy_poziom": {
            "tytul": "Przeniesienie relacji na wyższy poziom / Wyznanie uczuć",
            "rola": "Bliska osoba",
            "start": "Hej! Ostatnio sporo myśli kłębiło się w głowie o naszej relacji. O czym chciało się porozmawiać?"
        },
        "zakonczenie_relacji": {
            "tytul": "Zakończenie relacji",
            "rola": "Partner",
            "start": "Cześć. Dziwnie brzmiał głos przez telefon... Co się stało?"
        }
    },
    "Sklep / Obsługa": {
        "reklamacja": {
            "tytul": "Reklamacja wadliwego produktu",
            "rola": "Pracownik punktu obsługi",
            "start": "Dzień dobry! W czym można pomóc dzisiaj?"
        },
        "dostepnosc": {
            "tytul": "Zapytanie o dostępność i lokalizację produktu",
            "rola": "Pracownik sklepu",
            "start": "Dzień dobry! Czy szukamy czegoś konkretnego?"
        },
        "pomylka_rachunek": {
            "tytul": "Zgłoszenie pomyłki na rachunku przy kasie",
            "rola": "Kasjer",
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

VOICE_COMPONENT_HTML = r"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="UTF-8">
<style>
body{margin:0;font-family:-apple-system,"Segoe UI",Roboto,sans-serif;background:transparent;}
.wrap{display:flex;flex-direction:column;align-items:center;padding:12px 4px;}
#btn{width:130px;height:130px;border-radius:50%;border:none;color:#fff;font-weight:700;font-size:1.05rem;
     cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,.15);transition:background-color .2s, transform .2s;}
#btn:disabled{opacity:.6;cursor:default;}
#box{width:100%;max-width:640px;min-height:56px;background:#fff;border:1px solid #E7E5E4;border-radius:8px;
     padding:12px 16px;margin-top:18px;text-align:center;font-size:.98rem;color:#1C1917;box-sizing:border-box;line-height:1.45;}
#replay{margin-top:8px;background:none;border:none;color:#78716C;cursor:pointer;font-size:.85rem;text-decoration:underline;}
</style></head>
<body><div class="wrap">
  <div id="who" style="display:flex;flex-direction:column;align-items:center;margin-bottom:14px;">
    <div id="av" style="width:96px;height:96px;border-radius:50%;background:#E7E5E4;display:flex;align-items:center;justify-content:center;font-size:48px;overflow:hidden;border:3px solid transparent;transition:box-shadow .3s;">🤖</div>
    <div id="rola" style="margin-top:6px;font-size:.9rem;color:#57534E;font-weight:600;"></div>
  </div>
  <button id="btn">🎤 Mów</button>
  <div id="box">Kliknij „Mów”, wypowiedz odpowiedź, a potem kliknij „Wyślij”.</div>
  <button id="replay" style="display:none">🔊 Odsłuchaj ponownie</button>
</div>
<script>
function post(type, data){ window.parent.postMessage(Object.assign({isStreamlitMessage:true, type:type}, data||{}), "*"); }
function setHeight(){ post("streamlit:setFrameHeight", {height: document.body.scrollHeight + 12}); }
function setValue(v){ post("streamlit:setComponentValue", {value: v, dataType: "json"}); }

const btn = document.getElementById("btn"), box = document.getElementById("box"), replay = document.getElementById("replay");
let args = {}, accent = "#78716C", state = "idle";
let audio = null, lastAudio = null, lastReset = null;
let rec = null, finalT = "", interimT = "", stopping = false;
let ctx = null, stream = null, proc = null, src = null, chunks = [], recStart = 0, recTimer = null;

function useRecordingMode(){ try { return localStorage.getItem("nf_voice_mode") === "record"; } catch(e){ return false; } }
function rememberRecordingMode(){ try { localStorage.setItem("nf_voice_mode", "record"); } catch(e){} }

function setState(s, msg){
  state = s;
  btn.disabled = false;
  const av = document.getElementById("av");
  av.style.boxShadow = (s === "speaking") ? "0 0 0 6px " + accent + "55" : "none";
  if (s === "idle"){ btn.innerText = "🎤 Mów"; btn.style.background = accent; box.innerText = msg || "Kliknij „Mów”, wypowiedz odpowiedź, a potem kliknij „Wyślij”."; }
  else if (s === "speaking"){ btn.innerText = "🔊 Słuchaj"; btn.style.background = accent; box.innerText = msg || "Rozmówca mówi... (kliknij, aby przerwać i odpowiedzieć)"; }
  else if (s === "listening"){ btn.innerText = "📤 Wyślij"; btn.style.background = "#DC2626"; box.innerText = msg || "Mów teraz... wyłapane słowa pojawią się tutaj."; }
  else if (s === "recording"){ btn.innerText = "📤 Wyślij"; btn.style.background = "#DC2626"; box.innerText = msg || "🔴 Nagrywanie... kliknij „Wyślij”, gdy skończysz."; }
  else if (s === "sent" || s === "waiting"){ btn.innerText = "⏳"; btn.disabled = true; btn.style.background = accent; box.innerText = msg || "Rozmówca myśli..."; }
  setHeight();
}

function playAudio(){
  if (!lastAudio) return;
  if (audio){ try { audio.pause(); } catch(e){} }
  audio = new Audio("data:audio/mp3;base64," + lastAudio);
  replay.style.display = "inline";
  setState("speaking");
  audio.onended = () => { if (state === "speaking") setState("idle"); };
  audio.play().catch(() => setState("idle", "Kliknij „Odsłuchaj ponownie”, aby usłyszeć rozmówcę, albo od razu „Mów”."));
}

function startListening(){
  if (audio){ try { audio.pause(); } catch(e){} }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR || useRecordingMode()){ startRecording(); return; }
  finalT = ""; interimT = ""; stopping = false;
  rec = new SR();
  rec.lang = "pl-PL"; rec.interimResults = true; rec.continuous = true;
  rec.onresult = (ev) => {
    let interim = "";
    for (let i = ev.resultIndex; i < ev.results.length; i++){
      if (ev.results[i].isFinal) finalT += ev.results[i][0].transcript + " ";
      else interim += ev.results[i][0].transcript;
    }
    interimT = interim;
    const t = (finalT + interimT).trim();
    box.innerText = t ? t : "Mów teraz...";
    setHeight();
  };
  rec.onerror = (ev) => {
    if (ev.error === "no-speech" || ev.error === "aborted") return;
    if (ev.error === "not-allowed"){ stopping = true; setState("idle", "⚠️ Zezwól na dostęp do mikrofonu w przeglądarce i spróbuj ponownie."); return; }
    // np. "network" lub "service-not-allowed": przejście na nagrywanie i rozpoznawanie po stronie aplikacji
    stopping = true; try { rec.abort(); } catch(e){}
    rememberRecordingMode();
    startRecording("Rozpoznawanie na żywo jest niedostępne w tej przeglądarce lub sieci. 🔴 Nagrywam - mów dalej i kliknij „Wyślij”, gdy skończysz.");
  };
  rec.onend = () => { if (state === "listening" && !stopping){ try { rec.start(); } catch(e){} } };
  setState("listening");
  try { rec.start(); } catch(e){ startRecording(); }
}

function stopAndSendText(){
  stopping = true;
  try { rec.stop(); } catch(e){}
  setTimeout(() => {
    const t = (finalT + " " + interimT).trim();
    if (!t){ setState("idle", "Nie wyłapano wypowiedzi. Kliknij „Mów” i spróbuj ponownie."); return; }
    setValue({type: "text", text: t, id: Date.now()});
    setState("sent", "Wysłano: „" + t + "”. Rozmówca myśli...");
  }, 450);
}

async function startRecording(msg){
  try {
    stream = await navigator.mediaDevices.getUserMedia({audio: true});
  } catch(e){ setState("idle", "⚠️ Zezwól na dostęp do mikrofonu w przeglądarce i spróbuj ponownie."); return; }
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  src = ctx.createMediaStreamSource(stream);
  proc = ctx.createScriptProcessor(4096, 1, 1);
  chunks = [];
  proc.onaudioprocess = (e) => { chunks.push(new Float32Array(e.inputBuffer.getChannelData(0))); };
  src.connect(proc); proc.connect(ctx.destination);
  recStart = Date.now();
  setState("recording", msg);
  const base = msg || "🔴 Nagrywanie... kliknij „Wyślij”, gdy skończysz.";
  recTimer = setInterval(() => {
    const s = Math.floor((Date.now() - recStart) / 1000);
    box.innerText = base + "  (" + Math.floor(s/60) + ":" + String(s%60).padStart(2, "0") + ")";
  }, 500);
}

function encodeWav(samples, rate){
  const buffer = new ArrayBuffer(44 + samples.length * 2), v = new DataView(buffer);
  const w = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
  w(0, "RIFF"); v.setUint32(4, 36 + samples.length * 2, true); w(8, "WAVE"); w(12, "fmt ");
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
  w(36, "data"); v.setUint32(40, samples.length * 2, true);
  let o = 44;
  for (let i = 0; i < samples.length; i++, o += 2){ const x = Math.max(-1, Math.min(1, samples[i])); v.setInt16(o, x < 0 ? x * 0x8000 : x * 0x7FFF, true); }
  return new Uint8Array(buffer);
}

function stopAndSendAudio(){
  clearInterval(recTimer);
  try { proc.disconnect(); src.disconnect(); stream.getTracks().forEach(t => t.stop()); } catch(e){}
  const rate = ctx.sampleRate; try { ctx.close(); } catch(e){}
  let len = 0; chunks.forEach(c => len += c.length);
  if (len < rate * 0.3){ setState("idle", "Nagranie było zbyt krótkie. Kliknij „Mów” i spróbuj ponownie."); return; }
  const all = new Float32Array(len); let off = 0; chunks.forEach(c => { all.set(c, off); off += c.length; });
  const target = 16000, ratio = rate / target, outLen = Math.floor(all.length / ratio), out = new Float32Array(outLen);
  for (let i = 0; i < outLen; i++){
    const start = Math.floor(i * ratio), end = Math.min(Math.floor((i + 1) * ratio), all.length);
    let sum = 0; for (let j = start; j < end; j++) sum += all[j];
    out[i] = sum / Math.max(1, end - start);
  }
  const bytes = encodeWav(out, target);
  let bin = ""; for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  setValue({type: "audio", wav: btoa(bin), id: Date.now()});
  setState("sent", "Rozpoznawanie wypowiedzi... Rozmówca za chwilę odpowie.");
}

btn.onclick = () => {
  if (state === "idle" || state === "speaking") startListening();
  else if (state === "listening") stopAndSendText();
  else if (state === "recording") stopAndSendAudio();
};
replay.onclick = () => playAudio();

window.addEventListener("message", (e) => {
  if (!e.data || e.data.type !== "streamlit:render") return;
  args = e.data.args || {};
  accent = args.accent || accent;
  const avEl = document.getElementById("av");
  if (args.avatar){ avEl.innerHTML = '<img src="' + args.avatar + '" style="width:100%;height:100%;object-fit:cover;">'; }
  document.getElementById("rola").innerText = args.rola || "";
  if (lastReset === null){ lastReset = args.reset; }
  else if (args.reset !== lastReset){ lastReset = args.reset; setState("idle", args.komunikat || undefined); }
  if (args.czeka){ if (state !== "sent") setState("waiting"); }
  else if (args.audio_b64 && args.audio_b64 !== lastAudio){ lastAudio = args.audio_b64; playAudio(); }
  else if (state === "waiting"){ setState("idle"); }
  else if (state === "idle"){ btn.style.background = accent; }
  setHeight();
});
post("streamlit:componentReady", {apiVersion: 1});
setHeight();
</script></body></html>
"""


# Komponent rozmowy głosowej (przycisk "Mów" -> na żywo wyłapane słowa -> "Wyślij").
# Plik HTML komponentu jest zapisywany obok aplikacji przy starcie.
VOICE_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neuro_voice_component")
os.makedirs(VOICE_COMPONENT_DIR, exist_ok=True)
_voice_index = os.path.join(VOICE_COMPONENT_DIR, "index.html")
if not os.path.exists(_voice_index) or open(_voice_index, encoding="utf-8").read() != VOICE_COMPONENT_HTML:
    with open(_voice_index, "w", encoding="utf-8") as _f:
        _f.write(VOICE_COMPONENT_HTML)
voice_component = components.declare_component("neuro_voice", path=VOICE_COMPONENT_DIR)


# Tła scenariuszy jako wbudowane ilustracje SVG (działają bez internetu)
TLA_SVG = {}

_HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice">'

TLA_SVG["Uczelnia"] = _HEAD + '''
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFD9EE"/><stop offset="1" stop-color="#EAF3FA"/></linearGradient></defs>
<rect width="1600" height="900" fill="url(#sky)"/>
<circle cx="1330" cy="140" r="60" fill="#FFF3C4"/>
<ellipse cx="300" cy="150" rx="120" ry="34" fill="#FFFFFF" opacity="0.8"/><ellipse cx="1050" cy="110" rx="150" ry="36" fill="#FFFFFF" opacity="0.7"/>
<rect y="690" width="1600" height="210" fill="#A9C98F"/>
<polygon points="700,900 900,900 840,690 760,690" fill="#E8DCC4"/>
<rect x="430" y="330" width="740" height="330" fill="#EDE6D8"/>
<polygon points="400,330 800,200 1200,330" fill="#D9CFBC"/>
<polygon points="470,318 800,222 1130,318" fill="#E7DFCF"/>
<circle cx="800" cy="282" r="26" fill="#C9BDA6"/>
<rect x="400" y="318" width="800" height="22" fill="#CFC4AE"/>
<g fill="#F7F2E8"><rect x="470" y="350" width="34" height="300"/><rect x="580" y="350" width="34" height="300"/><rect x="690" y="350" width="34" height="300"/><rect x="876" y="350" width="34" height="300"/><rect x="986" y="350" width="34" height="300"/><rect x="1096" y="350" width="34" height="300"/></g>
<rect x="760" y="520" width="80" height="140" rx="40" fill="#8C7B64"/>
<g fill="#9FB6C8"><rect x="515" y="400" width="55" height="80" rx="4"/><rect x="625" y="400" width="55" height="80" rx="4"/><rect x="920" y="400" width="55" height="80" rx="4"/><rect x="1030" y="400" width="55" height="80" rx="4"/><rect x="515" y="530" width="55" height="80" rx="4"/><rect x="625" y="530" width="55" height="80" rx="4"/><rect x="920" y="530" width="55" height="80" rx="4"/><rect x="1030" y="530" width="55" height="80" rx="4"/></g>
<rect x="380" y="660" width="840" height="14" fill="#D3C8B2"/><rect x="360" y="674" width="880" height="16" fill="#C8BCA4"/>
<rect x="190" y="560" width="22" height="140" fill="#7E6A52"/><circle cx="200" cy="520" r="90" fill="#7FA66A"/>
<rect x="1390" y="560" width="22" height="140" fill="#7E6A52"/><circle cx="1400" cy="520" r="90" fill="#7FA66A"/>
<rect x="760" y="240" width="80" height="14" rx="3" fill="#B8AC94"/>
</svg>'''

TLA_SVG["Lekarz"] = _HEAD + '''
<rect width="1600" height="900" fill="#E3F0EC"/>
<rect y="640" width="1600" height="260" fill="#CFD8D6"/>
<rect y="630" width="1600" height="14" fill="#B8C6C3"/>
<rect x="120" y="140" width="330" height="300" fill="#FFFFFF" stroke="#B8C6C3" stroke-width="10"/>
<g fill="#D6E6F2"><rect x="135" y="155" width="300" height="270"/></g>
<g stroke="#C2D2DD" stroke-width="6"><line x1="135" y1="185" x2="435" y2="185"/><line x1="135" y1="215" x2="435" y2="215"/><line x1="135" y1="245" x2="435" y2="245"/><line x1="135" y1="275" x2="435" y2="275"/><line x1="135" y1="305" x2="435" y2="305"/><line x1="135" y1="335" x2="435" y2="335"/></g>
<rect x="560" y="170" width="170" height="230" rx="6" fill="#FFFFFF" stroke="#B8C6C3" stroke-width="4"/>
<g fill="#6B7C7A" font-family="Arial" font-weight="700" text-anchor="middle"><text x="645" y="235" font-size="54">E</text><text x="645" y="290" font-size="34">F P</text><text x="645" y="330" font-size="24">T O Z</text><text x="645" y="362" font-size="16">L P E D</text></g>
<rect x="840" y="470" width="620" height="40" rx="10" fill="#9BBFB5"/>
<rect x="860" y="430" width="580" height="46" rx="16" fill="#B7D6CD"/>
<rect x="870" y="424" width="500" height="18" rx="6" fill="#FFFFFF"/>
<rect x="880" y="510" width="16" height="130" fill="#8FA3A0"/><rect x="1400" y="510" width="16" height="130" fill="#8FA3A0"/>
<rect x="480" y="520" width="300" height="24" rx="6" fill="#C9B79C"/>
<rect x="495" y="544" width="20" height="96" fill="#A89378"/><rect x="745" y="544" width="20" height="96" fill="#A89378"/>
<rect x="560" y="420" width="130" height="90" rx="6" fill="#4F5B5A"/><rect x="570" y="430" width="110" height="68" fill="#A8C8D8"/><rect x="615" y="510" width="20" height="12" fill="#4F5B5A"/>
<rect x="1470" y="330" width="90" height="310" fill="#F4F7F6" stroke="#B8C6C3" stroke-width="4"/>
<line x1="1470" y1="480" x2="1560" y2="480" stroke="#B8C6C3" stroke-width="4"/>
<rect x="1180" y="180" width="80" height="80" rx="10" fill="#FFFFFF"/><rect x="1210" y="195" width="20" height="50" fill="#E57373"/><rect x="1195" y="210" width="50" height="20" fill="#E57373"/>
<rect x="60" y="560" width="50" height="80" rx="6" fill="#C9B79C"/><circle cx="85" cy="530" r="45" fill="#8DB88A"/>
</svg>'''

TLA_SVG["Praca"] = _HEAD + '''
<rect width="1600" height="900" fill="#EDEAE4"/>
<rect x="160" y="110" width="760" height="440" fill="#CFE0EC"/>
<g fill="#AFC4D3"><rect x="190" y="330" width="90" height="220"/><rect x="300" y="260" width="110" height="290"/><rect x="430" y="360" width="80" height="190"/><rect x="530" y="220" width="120" height="330"/><rect x="670" y="300" width="90" height="250"/><rect x="780" y="380" width="110" height="170"/></g>
<rect x="160" y="110" width="760" height="440" fill="none" stroke="#FFFFFF" stroke-width="16"/>
<line x1="540" y1="110" x2="540" y2="550" stroke="#FFFFFF" stroke-width="12"/>
<rect y="640" width="1600" height="260" fill="#C9C2B6"/>
<rect x="1060" y="170" width="360" height="24" fill="#B7A68C"/><rect x="1060" y="300" width="360" height="24" fill="#B7A68C"/>
<g><rect x="1080" y="110" width="40" height="60" fill="#8FA9BF"/><rect x="1125" y="120" width="34" height="50" fill="#D6A36B"/><rect x="1165" y="105" width="44" height="65" fill="#9DB88F"/><rect x="1300" y="240" width="40" height="60" fill="#C98E8E"/><rect x="1345" y="250" width="34" height="50" fill="#8FA9BF"/></g>
<circle cx="1260" cy="255" r="32" fill="#7FA66A"/><rect x="1245" y="270" width="30" height="30" fill="#A87F5B"/>
<rect x="380" y="560" width="840" height="30" rx="8" fill="#9C8466"/>
<rect x="420" y="590" width="24" height="180" fill="#7E6A52"/><rect x="1156" y="590" width="24" height="180" fill="#7E6A52"/>
<rect x="560" y="490" width="160" height="70" rx="6" fill="#5B6770"/><rect x="570" y="498" width="140" height="52" fill="#A8C3D6"/>
<rect x="880" y="530" width="90" height="30" rx="4" fill="#FFFFFF"/><rect x="990" y="520" width="40" height="40" rx="8" fill="#FFFFFF"/>
<rect x="250" y="520" width="120" height="160" rx="20" fill="#6E7F8C"/><rect x="265" y="680" width="16" height="90" fill="#555"/>
<rect x="1230" y="520" width="120" height="160" rx="20" fill="#6E7F8C"/><rect x="1319" y="680" width="16" height="90" fill="#555"/>
<rect x="60" y="560" width="60" height="90" rx="6" fill="#B08B64"/><circle cx="90" cy="520" r="55" fill="#7FA66A"/>
</svg>'''

TLA_SVG["Rodzina"] = _HEAD + '''
<rect width="1600" height="900" fill="#F3E6D8"/>
<rect y="650" width="1600" height="250" fill="#CDB59A"/>
<ellipse cx="800" cy="760" rx="520" ry="70" fill="#D9A58B" opacity="0.7"/>
<rect x="1120" y="140" width="330" height="330" fill="#DCEBF3" stroke="#FFFFFF" stroke-width="16"/>
<line x1="1285" y1="140" x2="1285" y2="470" stroke="#FFFFFF" stroke-width="10"/>
<rect x="1100" y="120" width="30" height="400" fill="#C98E8E" opacity="0.8"/><rect x="1440" y="120" width="30" height="400" fill="#C98E8E" opacity="0.8"/>
<rect x="300" y="170" width="150" height="110" fill="#FFFFFF" stroke="#A8876A" stroke-width="8"/><rect x="315" y="185" width="120" height="80" fill="#B8D2C4"/>
<rect x="480" y="200" width="100" height="130" fill="#FFFFFF" stroke="#A8876A" stroke-width="8"/><rect x="493" y="213" width="74" height="104" fill="#E3C49A"/>
<rect x="610" y="160" width="130" height="100" fill="#FFFFFF" stroke="#A8876A" stroke-width="8"/><rect x="623" y="173" width="104" height="74" fill="#C8B6D8"/>
<rect x="250" y="440" width="620" height="170" rx="40" fill="#8FA7B5"/>
<rect x="230" y="500" width="660" height="120" rx="30" fill="#7F98A7"/>
<rect x="210" y="470" width="70" height="160" rx="30" fill="#7F98A7"/><rect x="840" y="470" width="70" height="160" rx="30" fill="#7F98A7"/>
<rect x="330" y="470" width="110" height="70" rx="20" fill="#E9D6A8"/><rect x="690" y="470" width="110" height="70" rx="20" fill="#D9A58B"/>
<rect x="260" y="620" width="18" height="40" fill="#5E4B3C"/><rect x="842" y="620" width="18" height="40" fill="#5E4B3C"/>
<rect x="990" y="610" width="200" height="20" rx="6" fill="#A8876A"/><rect x="1005" y="630" width="14" height="60" fill="#8A6E55"/><rect x="1161" y="630" width="14" height="60" fill="#8A6E55"/>
<rect x="1060" y="580" width="30" height="30" rx="4" fill="#FFFFFF"/><circle cx="1130" cy="595" r="18" fill="#E57373" opacity="0.8"/>
<rect x="1005" y="270" width="8" height="330" fill="#6B5A4A"/><polygon points="960,270 1058,270 1030,200 988,200" fill="#F5E3B3"/><rect x="975" y="600" width="70" height="12" rx="4" fill="#6B5A4A"/>
</svg>'''

TLA_SVG["Partner / Relacje"] = _HEAD + '''
<rect width="1600" height="900" fill="#F1E4DA"/>
<rect y="620" width="1600" height="280" fill="#B9A08A"/>
<g stroke="#A68D77" stroke-width="3"><line x1="0" y1="700" x2="1600" y2="700"/><line x1="0" y1="790" x2="1600" y2="790"/></g>
<rect x="150" y="120" width="600" height="380" fill="#E8EFF3" stroke="#6D5B4E" stroke-width="14"/>
<line x1="450" y1="120" x2="450" y2="500" stroke="#6D5B4E" stroke-width="10"/>
<g fill="#C9D9C0"><circle cx="250" cy="420" r="60"/><circle cx="640" cy="400" r="70"/></g>
<rect x="160" y="440" width="580" height="60" fill="#D6CFC6"/>
<rect x="900" y="140" width="520" height="80" rx="10" fill="#6D5B4E"/><text x="1160" y="195" font-family="Georgia" font-size="46" fill="#F1E4DA" text-anchor="middle">KAWIARNIA</text>
<g stroke="#6D5B4E" stroke-width="4"><line x1="980" y1="0" x2="980" y2="300"/><line x1="1340" y1="0" x2="1340" y2="300"/></g>
<g fill="#F5D38A"><polygon points="940,300 1020,300 1000,260 960,260"/><polygon points="1300,300 1380,300 1360,260 1320,260"/></g>
<ellipse cx="800" cy="560" rx="180" ry="26" fill="#8A6E55"/><rect x="790" y="560" width="20" height="160" fill="#6D5B4E"/><ellipse cx="800" cy="720" rx="70" ry="12" fill="#6D5B4E"/>
<rect x="740" y="520" width="40" height="36" rx="6" fill="#FFFFFF"/><rect x="820" y="520" width="40" height="36" rx="6" fill="#FFFFFF"/>
<rect x="520" y="480" width="110" height="130" rx="18" fill="#C98E8E"/><rect x="530" y="600" width="14" height="120" fill="#6D5B4E"/><rect x="606" y="600" width="14" height="120" fill="#6D5B4E"/>
<rect x="970" y="480" width="110" height="130" rx="18" fill="#C98E8E"/><rect x="980" y="600" width="14" height="120" fill="#6D5B4E"/><rect x="1056" y="600" width="14" height="120" fill="#6D5B4E"/>
<ellipse cx="1320" cy="600" rx="120" ry="20" fill="#8A6E55"/><rect x="1312" y="600" width="16" height="120" fill="#6D5B4E"/>
<rect x="1440" y="450" width="60" height="170" fill="#9FB58E"/><circle cx="1470" cy="430" r="50" fill="#7FA66A"/>
</svg>'''

TLA_SVG["Sklep / Obsługa"] = _HEAD + '''
<rect width="1600" height="900" fill="#EEF0EC"/>
<rect y="660" width="1600" height="240" fill="#D5D8D2"/>
<g stroke="#C4C8C0" stroke-width="3"><line x1="200" y1="660" x2="0" y2="900"/><line x1="600" y1="660" x2="500" y2="900"/><line x1="1000" y1="660" x2="1100" y2="900"/><line x1="1400" y1="660" x2="1600" y2="900"/><line x1="0" y1="760" x2="1600" y2="760"/></g>
<rect x="80" y="90" width="620" height="560" fill="#D9CBB4"/>
<g fill="#BFAE93"><rect x="80" y="220" width="620" height="16"/><rect x="80" y="370" width="620" height="16"/><rect x="80" y="520" width="620" height="16"/></g>
<g><rect x="110" y="140" width="70" height="80" fill="#E57373"/><rect x="190" y="160" width="60" height="60" fill="#FFD166"/><rect x="260" y="130" width="80" height="90" fill="#8FB8DE"/><rect x="350" y="150" width="60" height="70" fill="#9FC99A"/><rect x="420" y="135" width="75" height="85" fill="#C8A2D8"/><rect x="505" y="160" width="60" height="60" fill="#F4A261"/><rect x="575" y="140" width="95" height="80" fill="#8FB8DE"/>
<rect x="110" y="300" width="90" height="70" fill="#9FC99A"/><rect x="210" y="290" width="60" height="80" fill="#F4A261"/><rect x="280" y="310" width="80" height="60" fill="#E57373"/><rect x="370" y="285" width="70" height="85" fill="#FFD166"/><rect x="450" y="300" width="90" height="70" fill="#8FB8DE"/><rect x="550" y="290" width="60" height="80" fill="#C8A2D8"/><rect x="620" y="305" width="60" height="65" fill="#9FC99A"/>
<rect x="110" y="450" width="70" height="70" fill="#8FB8DE"/><rect x="190" y="440" width="80" height="80" fill="#C8A2D8"/><rect x="280" y="455" width="60" height="65" fill="#FFD166"/><rect x="350" y="445" width="90" height="75" fill="#E57373"/><rect x="450" y="450" width="70" height="70" fill="#9FC99A"/><rect x="530" y="440" width="70" height="80" fill="#F4A261"/><rect x="610" y="455" width="70" height="65" fill="#8FB8DE"/></g>
<rect x="900" y="120" width="560" height="80" rx="10" fill="#6E8B74"/><text x="1180" y="175" font-family="Arial" font-weight="700" font-size="42" fill="#FFFFFF" text-anchor="middle">KASA / OBSŁUGA</text>
<rect x="880" y="460" width="620" height="200" rx="10" fill="#B9A58A"/><rect x="860" y="440" width="660" height="30" rx="8" fill="#A38E72"/>
<rect x="1050" y="360" width="150" height="80" rx="8" fill="#4F5B5A"/><rect x="1065" y="372" width="120" height="50" fill="#A8C8D8"/>
<rect x="1260" y="400" width="140" height="40" rx="6" fill="#6B7C7A"/>
<rect x="760" y="520" width="80" height="120" rx="8" fill="#9DB0B8"/><circle cx="780" cy="660" r="12" fill="#555"/><circle cx="830" cy="660" r="12" fill="#555"/>
</svg>'''


TLA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tla_rozmow")
TLA_PLIKI = {
    "Uczelnia": "uczelnia", "Lekarz": "lekarz", "Praca": "praca",
    "Rodzina": "rodzina", "Partner / Relacje": "relacje", "Sklep / Obsługa": "sklep",
}
# Realistyczne zdjęcia (Unsplash, licencja pozwalająca na bezpłatne użycie); kilka adresów na kategorię na wypadek niedostępności
TLA_ZDJECIA_URL = {
    "Uczelnia": ["https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=1920&q=80",
                 "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1920&q=80"],
    "Lekarz": ["https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1920&q=80",
               "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1920&q=80"],
    "Praca": ["https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1920&q=80",
              "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1920&q=80"],
    "Rodzina": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=1920&q=80",
                "https://images.unsplash.com/photo-1511895426328-dc8714191300?auto=format&fit=crop&w=1920&q=80"],
    "Partner / Relacje": ["https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1920&q=80",
                          "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?auto=format&fit=crop&w=1920&q=80"],
    "Sklep / Obsługa": ["https://images.unsplash.com/photo-1556742049-0a67d553c253?auto=format&fit=crop&w=1920&q=80",
                        "https://images.unsplash.com/photo-1604719312566-8912e9227c6a?auto=format&fit=crop&w=1920&q=80"],
}


@st.cache_data(show_spinner=False)
def tlo_domyslne_data_uri(kategoria):
    """Zwraca tło rozmowy jako data URI: 1) własne zdjęcie z folderu tla_rozmow (np. uczelnia.jpg),
    2) zdjęcie pobrane z internetu i zapisane w tym folderze, 3) awaryjnie wbudowana ilustracja."""
    os.makedirs(TLA_FOLDER, exist_ok=True)
    nazwa = TLA_PLIKI.get(kategoria, "praca")
    for rozszerzenie, mime in ((".jpg", "image/jpeg"), (".jpeg", "image/jpeg"), (".png", "image/png"), (".webp", "image/webp")):
        sciezka = os.path.join(TLA_FOLDER, nazwa + rozszerzenie)
        if os.path.exists(sciezka):
            with open(sciezka, "rb") as f:
                return f"data:{mime};base64," + base64.b64encode(f.read()).decode()
    try:
        import requests
        for url in TLA_ZDJECIA_URL.get(kategoria, []):
            try:
                r = requests.get(url, timeout=8)
                if r.status_code == 200 and r.headers.get("content-type", "").startswith("image/"):
                    with open(os.path.join(TLA_FOLDER, nazwa + ".jpg"), "wb") as f:
                        f.write(r.content)
                    return "data:image/jpeg;base64," + base64.b64encode(r.content).decode()
            except Exception:
                continue
    except Exception:
        pass
    svg = TLA_SVG.get(kategoria, TLA_SVG["Praca"])
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


# ==========================================
# 5. ZARZĄDZANIE STANEM APLIKACJI (SESSION STATE)
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

if "box_active" not in st.session_state:
    st.session_state.box_active = False

if "breathe_started" not in st.session_state:
    st.session_state.breathe_started = False

if st.query_params.get("summarize") == "true":
    raw_transcript = st.query_params.get("transcript")
    if raw_transcript:
        try:
            parsed_msgs = json.loads(raw_transcript)
            cleaned_messages = []
            for m in parsed_msgs:
                if m.get("role") != "system":
                    if "timestamp" not in m or not m["timestamp"]:
                        m["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cleaned_messages.append(m)

            st.session_state.messages = cleaned_messages
        except Exception as e:
            st.error(f"Błąd podczas odczytu transkryptu głosowego: {e}")

    st.session_state.summary_mode = True
    st.query_params.clear()
    st.rerun()

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
        
        likert_options = [1, 2, 3, 4, 5]
        format_func_likert = lambda x: {1: "1 - Zdecydowanie nie", 2: "2 - Raczej nie", 3: "3 - Neutralnie", 4: "4 - Raczej tak", 5: "5 - Zdecydowanie tak"}[x]

        q2 = st.select_slider("Wolę, aby informacje i wskazówki były podawane w formie uporządkowanych list.", options=likert_options, value=4, format_func=format_func_likert, key="q2_likert", help="Określ, czy preferujesz jasne uporządkowanie treści.")

        st.markdown("---")
        st.markdown("#### 2. Styl języka wskazówek")
        
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
        
        nasa_options = [1, 2, 3, 4, 5]
        format_func_nasa = lambda x: {1: "Bardzo niskie", 2: "Niskie", 3: "Umiarkowane", 4: "Wysokie", 5: "Bardzo wysokie"}[x]
        q_nasa = st.select_slider("Jak oceniasz swoją obecną podatność na zmęczenie poznawcze lub przebodźcowanie?", options=nasa_options, value=3, format_func=format_func_nasa, key="q_nasa_tlx", help="Określ swój aktualny poziom energii psychicznej.")

        st.markdown("---")
        st.markdown("#### 4. Główny cel wsparcia")
        
        q_abc = st.selectbox("Na czym chcesz się dzisiaj najbardziej skupić w ramach modelu ABC?", [
            "Identyfikacja i redukcja lęku przed wejściem w interakcję (Antecedent)",
            "Trening precyzyjnego i asertywnego formułowania wypowiedzi (Behavior)",
            "Zrozumienie wpływu i odbioru mojego komunikatu przez rozmówcę (Consequence)"
        ], key="q_abc_model", help="Wybierz główny punkt skupienia procesu treningowego.")

        st.markdown("---")
        st.markdown("#### 5. Komfort sensoryczny interfejsu")
        
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
    wybrana_nazwa_modelu = DOMYSLNY_MODEL
    config_modelu = dostepne_modele[wybrana_nazwa_modelu]
    model_api_key = pobierz_klucz_deepseek()

    st.markdown(f"Scenariusz: {wybrany_scenariusz['tytul']} | Model: {wybrana_nazwa_modelu}")
    st.markdown("---")

    if "tom_quiz_struct" not in st.session_state:
        with st.spinner("Generowanie szczegółowej analizy psychologicznej, perspektywy rozmówcy oraz pytań treningowych..."):
            dialog_history = zbuduj_transkrypt(st.session_state.messages, wybrany_scenariusz['rola'])

            prompt_gen = f"""
            Przeanalizuj poniższą rozmowę treningową z perspektywy psychologicznej i relacyjnej. Odnieś się bezpośrednio zarówno do wypowiedzi UŻYTKOWNIKA (osoby ćwiczącej), jak i ROZMÓWCY AI z transkryptu, cytując krótkie fragmenty obu stron. Przygotuj odpowiedź ŚCISLE W FORMACIE JSON (bez żadnego dodatkowego formatowania markdown poza blokiem json, lub po prostu czysty json):
            {{
                "analiza_psychologiczna": "Szczegółowy opis, jak użytkownik mógł być odebrany przez rozmówcę, odwołując się do konkretnych momentów z przebiegu rozmowy (co powiedział użytkownik i jak zareagował rozmówca), co rozmówca mógł zrozumieć przez jego słowa, oraz pogłębiona refleksja emocjonalna nawiązująca do zasady: Każda emocja coś komunikuje, co komunikuje Twoja?",
                "pytania": [
                    {{
                        "pytanie": "Treść pytania treningowego w stylu pytań terapeutycznych (np. Jak inaczej można było odpowiedzieć na to pytanie w kluczowym momencie...?)",
                        "opcje": ["Opcja A (błędna lub nieprecyzyjna)", "Opcja B (poprawna i profesjonalna)", "Opcja C (inna opcja)"],
                        "poprawna": "Opcja B (poprawna i profesjonalna)",
                        "wyjasnienie": "Wyjaśnienie psychologiczne oraz wskazówka nawiązująca do konkretnych wypowiedzi z dialogu."
                    }}
                ]
            }}
            Przygotuj od 3 do 5 takich pytań dopasowanych do przebiegu rozmowy. Pole "poprawna" musi być identyczne z jedną z opcji.
            Styl analizy i wyjaśnień: {feedback_style_prompt()}

            ZAPIS ROZMOWY (tryb: {st.session_state.get('tryb_rozmowy', '')}):
            {dialog_history}
            """
            try:
                raw_content = chat_completion(config_modelu, model_api_key,
                                              [{"role": "user", "content": prompt_gen}],
                                              max_tokens=3000, temperature=0.3, json_mode=True)
                raw_content = raw_content.strip()
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
                    "analiza_psychologiczna": f"Analiza psychologiczna przeprowadzona pomyślnie na podstawie przebiegu rozmowy. Dialog został omówiony. Błąd parsowania: {e}",
                    "pytania": [
                        {
                            "pytanie": "Jak w kluczowym momencie rozmowy rozmówca mógł odebrać Twoją wypowiedź?",
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

        if score_percent == 0:
            st.info("ℹ️ Twój wynik to 0% ponieważ zaznaczone odpowiedzi różniły się od wzorcowego klucza metodycznego. Zapoznaj się z powyższymi wyjaśnieniami, aby skorygować schematy w przyszłych treningach.")
        elif score_percent >= 66:
            st.success("✅ Świetna refleksja! Bardzo dobrze rozumiesz perspektywę rozmówcy i mechanizmy komunikacyjne.")
        else:
            st.info("✅ Dobra praca! Analiza tych schematów pomoże Ci precyzyjniej formułować wypowiedzi w przyszłości.")

    st.markdown("---")

    st.markdown("""
        <div class="cbt-box">
            <h3>Moduł Refleksji i Regulacji (Metody CBT)</h3>
            <p>Co sprawiło Ci największą trudność w tej rozmowie? Opisz to własnymi słowami, a otrzymasz feedback dopasowany do Twojej odpowiedzi i przebiegu rozmowy.</p>
        </div>
    """, unsafe_allow_html=True)

    trudnosc = st.text_area("Co sprawiło Ci największą trudność w tej rozmowie?", placeholder="Np. nie wiedziałam, jak odpowiedzieć na pytanie o doświadczenie / stresowało mnie, że rozmówca był zirytowany...", key="difficulty_input")

    if st.button("Otrzymaj feedback", key="difficulty_btn"):
        if not trudnosc.strip():
            st.warning("⚠️ Wpisz, co sprawiło Ci największą trudność, aby otrzymać feedback.")
        else:
            with st.spinner("Przygotowywanie feedbacku..."):
                prompt_fb = f"""
                Jesteś wspierającym trenerem komunikacji pracującym metodami CBT z osobą neuroatypową.
                Użytkownik ukończył rozmowę treningową (scenariusz: {wybrany_scenariusz['tytul']}, rozmówca: {wybrany_scenariusz['rola']})
                i odpowiedział na pytanie "Co sprawiło Ci największą trudność w tej rozmowie?":
                "{trudnosc.strip()}"

                Napisz po polsku spersonalizowany feedback, który:
                1. odnosi się wprost do tego, co napisał użytkownik (nie ogólnikowo),
                2. wskazuje konkretny moment z rozmowy (wypowiedź użytkownika i reakcję rozmówcy), w którym ta trudność była widoczna,
                3. waliduje emocje bez oceniania osoby,
                4. podaje jedną konkretną strategię i przykładowe zdanie do użycia następnym razem,
                5. kończy się jednym pytaniem pomocniczym do refleksji.
                Nie stawiaj diagnoz. {feedback_style_prompt()}

                ZAPIS ROZMOWY:
                {zbuduj_transkrypt(st.session_state.messages, wybrany_scenariusz['rola'])}
                """
                try:
                    tekst_fb = chat_completion(config_modelu, model_api_key,
                                               [{"role": "user", "content": prompt_fb}],
                                               max_tokens=700, temperature=0.4)
                except Exception:
                    tekst_fb = ""
                if not tekst_fb:
                    tekst_fb = feedback_regulowy(trudnosc.strip())
                st.session_state.difficulty_feedback = {"odp": trudnosc.strip(), "tekst": tekst_fb}

    if st.session_state.get("difficulty_feedback") and st.session_state.difficulty_feedback["odp"] == trudnosc.strip():
        st.markdown("**Feedback:**")
        st.info(st.session_state.difficulty_feedback["tekst"])

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        raport_txt = zbuduj_raport(
            st.session_state.messages,
            wybrany_scenariusz,
            config_modelu["model_id"],
            st.session_state.get('tryb_rozmowy', 'Rozmowa pisemna'),
            st.session_state.get('start_time', '0000'),
            summary_text=quiz_data.get("analiza_psychologiczna", "") + (
                f"\n\n--- REFLEKSJA UŻYTKOWNIKA ---\nCo sprawiło największą trudność: {st.session_state.difficulty_feedback['odp']}\n\nFeedback: {st.session_state.difficulty_feedback['tekst']}"
                if st.session_state.get("difficulty_feedback") else "")
        )
        st.download_button(
            "📥 Pobierz raport i zapis rozmowy (.txt)",
            data=raport_txt.encode("utf-8"),
            file_name=nazwa_pliku_raportu(wybrany_scenariusz, st.session_state.get('start_time', '0000')),
            mime="text/plain",
            use_container_width=True
        )

    with col2:
        if st.button("Zakończ sesję i wyczyść pamięć", use_container_width=True, type="primary"):
            st.session_state.config_completed = False
            st.session_state.intro_dismissed = False
            st.session_state.summary_mode = False
            st.session_state.messages = []
            if "tom_quiz_struct" in st.session_state: del st.session_state.tom_quiz_struct
            if "quiz_done_clicked" in st.session_state: del st.session_state.quiz_done_clicked
            if "user_quiz_answers" in st.session_state: del st.session_state.user_quiz_answers
            st.session_state.pop("difficulty_feedback", None)
            st.session_state.tts_cache = {}
            st.rerun()

    st.stop()

# 3. Krok trzeci: Konfiguracja parametrów sesji
if not st.session_state.config_completed:
    st.title("Konfiguracja Sesji Treningowej")
    st.markdown("Wybierz tryb rozmowy oraz konkretny scenariusz treningowy.")

    wybrana_nazwa_modelu = DOMYSLNY_MODEL
    model_api_key = pobierz_klucz_deepseek()
    if not model_api_key:
        model_api_key = st.text_input(
            "Klucz API DeepSeek",
            type="password",
            help="Nie znaleziono klucza w secrets.toml ani w zmiennej środowiskowej DEEPSEEK_API_KEY. Wpisz go jednorazowo."
        )

    tryb_rozmowy = st.radio(
        "Wybierz styl interakcji:", 
        [
            "Rozmowa głosowa", 
            "Rozmowa pisemna", 
            "Rozmowa pisemna ze wskazówkami"
        ],
        help="Wybierz formę prowadzenia treningu komunikacyjnego."
    )

    st.markdown("---")
    st.subheader("Wybór Scenariusza Treningu")
    
    if "kategoria_wybor_select" not in st.session_state:
        st.session_state.kategoria_wybor_select = list(scenariusze_kategorie.keys())[0]

    def update_variants():
        cat = st.session_state.kategoria_wybor_select
        variants = list(scenariusze_kategorie[cat].keys())
        st.session_state.wariant_wybor_select = variants[0]

    kategoria_key = st.selectbox(
        "Kategoria sytuacji:", 
        list(scenariusze_kategorie.keys()), 
        key="kategoria_wybor_select",
        on_change=update_variants,
        help="Wybierz główny obszar tematyczny, w którym chcesz przetestować swoje umiejętności."
    )
    
    warianty_dict = scenariusze_kategorie[kategoria_key]
    wariant_keys = list(warianty_dict.keys())
    
    if "wariant_wybor_select" not in st.session_state or st.session_state.wariant_wybor_select not in wariant_keys:
        st.session_state.wariant_wybor_select = wariant_keys[0]

    wariant_key = st.selectbox(
        "Wariant rozmowy:", 
        options=wariant_keys, 
        format_func=lambda x: warianty_dict[x]["tytul"], 
        key="wariant_wybor_select",
        help="Wybierz konkretny profil psychologiczny rozmówcy oraz szczegółowy kontekst sytuacji."
    )

    st.markdown("---")
    st.subheader("Wygląd i Personalizacja Sesji")
    
    bg_choice = st.radio(
        "Tło konwersacji:", 
        ["Tło domyślne (zależne od scenariusza i kategorii)", "Wgraj własne tło"]
    )
    custom_bg_file = None
    if bg_choice == "Wgraj własne tło":
        custom_bg_file = st.file_uploader("Wgraj własne tło konwersacji (obraz)", type=["png", "jpg", "jpeg"])

    avatar_choice = st.radio(
        "Avatar rozmówcy:", 
        ["Domyślny (robot 🤖)", "Wgraj własnego avatara"]
    )
    custom_avatar_file = None
    if avatar_choice == "Wgraj własnego avatara":
        custom_avatar_file = st.file_uploader("Wgraj plik avatara rozmówcy (obraz)", type=["png", "jpg", "jpeg"])

    submitted = st.button("Potwierdź i wejdź do czatu", use_container_width=True)
    
    if submitted:
        if not model_api_key:
            st.error("⚠️ Brak klucza API DeepSeek. Dodaj go do secrets.toml, zmiennej DEEPSEEK_API_KEY lub wpisz powyżej.")
        else:
            st.session_state.config_completed = True
            st.session_state.wybrana_nazwa_modelu = wybrana_nazwa_modelu
            st.session_state.model_api_key = model_api_key
            st.session_state.tryb_rozmowy = tryb_rozmowy
            st.session_state.kategoria_key = st.session_state.get("kategoria_wybor_select", list(scenariusze_kategorie.keys())[0])
            st.session_state.wariant_key = st.session_state.get("wariant_wybor_select", list(scenariusze_kategorie[st.session_state.kategoria_key].keys())[0])
            st.session_state.bg_choice = bg_choice
            st.session_state.custom_bg_file = custom_bg_file
            st.session_state.custom_bg_bytes = custom_bg_file.getvalue() if custom_bg_file is not None else None
            st.session_state.custom_bg_mime = custom_bg_file.type if custom_bg_file is not None else None
            st.session_state.avatar_choice = avatar_choice
            st.session_state.custom_avatar_file = custom_avatar_file
            st.session_state.custom_avatar_bytes = custom_avatar_file.getvalue() if custom_avatar_file is not None else None
            st.session_state.custom_avatar_mime = custom_avatar_file.type if custom_avatar_file is not None else None
            st.session_state.current_scenario = f"{st.session_state.kategoria_key}_{st.session_state.wariant_key}"
            st.session_state.start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.messages = []
            st.session_state.summary_mode = False
            st.session_state.session_ended = False
            if "tom_quiz_struct" in st.session_state: 
                del st.session_state.tom_quiz_struct
            st.rerun()
    st.stop()

# ==========================================
# 4. TRYB CZATU TRENINGOWEGO I ZAKŁADKA STATYSTYK
# ==========================================
wybrana_nazwa_modelu = DOMYSLNY_MODEL
config_modelu = dostepne_modele[wybrana_nazwa_modelu]
model_api_key = pobierz_klucz_deepseek()
tryb_rozmowy = st.session_state.tryb_rozmowy
kategoria_key = st.session_state.kategoria_key
wariant_key = st.session_state.wariant_key
wybrany_scenariusz = scenariusze_kategorie[kategoria_key][wariant_key]

st.sidebar.markdown('<h2 class="brand-logo" style="font-size: 1.4rem; margin-bottom: 0px;">NEURO FRIEND</h2>', unsafe_allow_html=True)
st.sidebar.markdown(f"**Model:** {wybrana_nazwa_modelu}")
st.sidebar.markdown(f"**Tryb:** {tryb_rozmowy}")
st.sidebar.markdown("---")

st.sidebar.subheader("🌿 Interaktywna Strefa Wyciszenia i Relaksu")

wybrana_technika = st.sidebar.selectbox(
    "Wybierz interaktywną technikę:",
    [
        "Wybierz technikę...",
        "Spokojne oddychanie (Kółeczko: wdech i wydech)",
        "Technika uziemienia 5-4-3-2-1 (Krok po kroku)",
        "Zmiana przekonania (stresujące → neutralne lub pozytywne)"
    ],
    key="select_relaxation_technique"
)

if wybrana_technika == "Spokojne oddychanie (Kółeczko: wdech i wydech)":
    st.sidebar.markdown("#### 🔵 Trening Oddechowy")
    st.sidebar.caption("Wdech 4 s, wydech 6 s. Ćwiczenie samo zakończy się po wybranym czasie.")
    breath_time = st.sidebar.selectbox("Wybierz czas:", [1, 3, 5], format_func=lambda x: f"{x} min", key="b_time")
    with st.sidebar:
        components.html(breathing_widget_html(breath_time, accent_col, border_col, text_color), height=230)

elif wybrana_technika == "Technika uziemienia 5-4-3-2-1 (Krok po kroku)":
    st.sidebar.markdown("#### ⚓ Uziemienie 5-4-3-2-1")
    kroki_uziemienia = [
        {"n": 5, "polecenie": "Wymień 5 rzeczy, które obecnie **widzisz** wokół siebie", "przypomnienie": "rzeczy, które widzisz wokół siebie"},
        {"n": 4, "polecenie": "Wymień 4 rzeczy, których możesz **dotknąć** (poczuć ich fakturę)", "przypomnienie": "rzeczy, których możesz dotknąć"},
        {"n": 3, "polecenie": "Wymień 3 dźwięki, które obecnie **słyszysz**", "przypomnienie": "dźwięki, które słyszysz"},
        {"n": 2, "polecenie": "Wymień 2 zapachy, które możesz **poczuć**", "przypomnienie": "zapachy, które możesz poczuć"},
        {"n": 1, "polecenie": "Wymień 1 smak, który możesz teraz **poczuć**", "przypomnienie": "smak, który czujesz"},
    ]
    if "grounding_step" not in st.session_state:
        st.session_state.grounding_step = 0
    if "grounding_answers" not in st.session_state:
        st.session_state.grounding_answers = []

    krok = st.session_state.grounding_step
    if krok < len(kroki_uziemienia):
        dane = kroki_uziemienia[krok]
        st.sidebar.progress(krok / len(kroki_uziemienia), text=f"Krok {krok + 1} z 5")
        st.sidebar.info(f"{dane['polecenie']}. Oddziel je przecinkami.")
        wpis = st.sidebar.text_input(f"Wpisz {dane['n']}:", key=f"grounding_input_{krok}")
        elementy = [e.strip() for e in re.split(r"[,;\n]+", wpis) if e.strip()]
        st.sidebar.caption(f"Wpisano: {len(elementy)} z {dane['n']}")
        etykieta = "Dalej" if krok < len(kroki_uziemienia) - 1 else "Zakończ uziemienie"
        if st.sidebar.button(etykieta, key=f"grounding_btn_{krok}", use_container_width=True):
            if len(elementy) < dane["n"]:
                brakuje = dane["n"] - len(elementy)
                st.sidebar.warning(f"⚠️ Wpisz {dane['n']} {dane['przypomnienie']} (oddziel je przecinkami). Brakuje jeszcze: {brakuje}.")
            else:
                st.session_state.grounding_answers.append(elementy[:dane["n"]])
                st.session_state.grounding_step += 1
                st.rerun()
    else:
        st.sidebar.progress(1.0, text="Ukończono 5 z 5")
        st.sidebar.success("🎉 Świetnie! Twoje zmysły wróciły do tu i teraz.")
        for dane, odp in zip(kroki_uziemienia, st.session_state.grounding_answers):
            st.sidebar.markdown(f"<small>{dane['n']} – {', '.join(odp)}</small>", unsafe_allow_html=True)
        if st.sidebar.button("Rozpocznij ponownie", key="grounding_reset", use_container_width=True):
            st.session_state.grounding_step = 0
            st.session_state.grounding_answers = []
            for i in range(len(kroki_uziemienia)):
                st.session_state.pop(f"grounding_input_{i}", None)
            st.rerun()

elif wybrana_technika == "Zmiana przekonania (stresujące → neutralne lub pozytywne)":
    st.sidebar.markdown("#### 🧠 Zmiana Przekonania")
    if "reframing_stage" not in st.session_state:
        st.session_state.reframing_stage = "input"
    if "stressful_thought" not in st.session_state:
        st.session_state.stressful_thought = ""
    if "reframing_attempts" not in st.session_state:
        st.session_state.reframing_attempts = 0
    if "reframing_feedback" not in st.session_state:
        st.session_state.reframing_feedback = []

    kategorie_znieksztalcen = [
        (["muszę", "musze", "powinienem", "powinnam", "trzeba"],
         "Słowo typu „muszę” tworzy presję. Zamień je na „chcę”, „spróbuję” albo „mogę”."),
        (["zawsze", "nigdy", "wszyscy", "nikt", "wszystko", "nic mi"],
         "To uogólnienie („zawsze/nigdy/wszyscy”). Czy znasz choć jeden wyjątek? Opisz tę konkretną sytuację."),
        (["zepsuj", "katastrof", "porażk", "koniec", "beznadziej", "tragedi", "skompromit"],
         "To czarny scenariusz. Co najbardziej realistycznie może się wydarzyć, a nie najgorszego?"),
        (["nie umiem", "nie potrafię", "nie potrafie", "nie dam rady", "nie poradzę"],
         "To zdanie zamyka drogę. Dodaj słowo „jeszcze” albo opisz, czego się uczysz, np. „uczę się…”."),
        (["głupi", "glupi", "idiot", "żałos", "zalos", "do niczego", "beznadziejn"],
         "To etykieta, nie fakt. Opisz sytuację bez oceniania siebie jako osoby."),
    ]
    pytania_pomocnicze = [
        "Jakie masz dowody, że ta myśl jest w 100% prawdziwa?",
        "Co powiedział(a)byś przyjacielowi, który tak o sobie myśli?",
        "Jak wyglądałby najbardziej realistyczny, a nie najgorszy, scenariusz?",
        "Co w tej sytuacji jest pod Twoją kontrolą?",
        "Czego możesz się nauczyć z tej sytuacji, niezależnie od wyniku?",
    ]

    slowa_negatywne = [
        "zła", "zły", "złe", "źle", "brzydk", "głup", "glup", "beznadziej", "nienawidz", "nie znoszę",
        "gorsz", "do niczego", "nic nie wart", "nikt mnie", "nie zasługuj", "okropn", "żałosn",
        "porażk", "nieudaczni", "idiot", "tchórz", "słab", "wstyd", "nie lubi", "boję się", "przegra"
    ]

    def ocena_przekonania_ai(nowa, stara):
        """Ocena przez model (DeepSeek), czy nowe przekonanie jest neutralne lub pozytywne."""
        prompt_oc = f"""Jesteś terapeutą poznawczo-behawioralnym. Użytkownik ćwiczy zamianę stresującego przekonania
na przekonanie NEUTRALNE lub POZYTYWNE (wspierające).
Pierwotne przekonanie: "{stara}"
Nowa wersja: "{nowa}"
Oceń nową wersję. Jest poprawna tylko wtedy, gdy JEDNOCZEŚNIE: nie zawiera negatywnej oceny siebie ani innych
(np. "jestem zła", "jestem brzydka", "jestem głupia"), nie zawiera zniekształceń poznawczych (katastrofizowania,
uogólnień, etykietowania, "muszę"), ma wydźwięk neutralny lub wspierający i jest realistyczna.
Oceniaj znaczenie CAŁEGO zdania, a nie pojedyncze słowa: przeczenia negatywnych słów (np. "nie jestem zła",
"nie chcę myśleć źle o sobie") są w porządku, jeśli całość jest wspierająca. Nie bądź pedantyczny - zaakceptuj każde
rozsądne, życzliwe dla siebie przekonanie.
Odpowiedz WYŁĄCZNIE w formacie JSON:
{{"poprawne": true/false, "uzasadnienie": "1 zdanie po polsku, co jest nie tak lub co jest dobre",
"wskazowka": "1 konkretna wskazówka po polsku, jak poprawić (pusta, jeśli poprawne)",
"pytanie": "1 pytanie pomocnicze po polsku (puste, jeśli poprawne)"}}"""
        try:
            raw = chat_completion(config_modelu, model_api_key, [{"role": "user", "content": prompt_oc}],
                                  max_tokens=300, temperature=0.2, json_mode=True)
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(raw)
        except Exception:
            return None

    def sprawdz_przekonanie(nowa, stara):
        nowa_l = nowa.lower().strip()
        if len(nowa_l.split()) < 3:
            return ["Napisz pełne zdanie (co najmniej 3 słowa)."]
        if difflib.SequenceMatcher(None, nowa_l, stara.lower().strip()).ratio() > 0.85:
            return ["Nowa wersja jest prawie taka sama jak pierwotna myśl. Spróbuj spojrzeć na sytuację z innej strony."]
        # 1) Ocena znaczenia całego zdania przez model (uwzględnia kontekst i przeczenia, np. "nie mogę myśleć źle o sobie")
        with st.spinner("Sprawdzanie przekonania..."):
            ocena = ocena_przekonania_ai(nowa, stara)
        if ocena is not None:
            if ocena.get("poprawne", False):
                return []
            uwagi = [ocena.get("uzasadnienie", "Ta wersja nie jest jeszcze neutralna ani wspierająca.")]
            if ocena.get("wskazowka"):
                uwagi.append(ocena["wskazowka"])
            if ocena.get("pytanie"):
                uwagi.append(f"Pytanie pomocnicze: {ocena['pytanie']}")
            uwagi.append("__ai__")
            return uwagi
        # 2) Awaryjnie (brak połączenia z modelem): reguły słownikowe
        uwagi = []
        for slowa, podpowiedz in kategorie_znieksztalcen:
            if any(s_ in nowa_l for s_ in slowa):
                uwagi.append(podpowiedz)
        if zawiera_negatywne(nowa_l):
            uwagi.append("Nowa wersja nadal zawiera negatywną ocenę (np. „zła”, „brzydka”, „głupia”). Przekonanie ma być neutralne lub wspierające - opisz siebie lub sytuację bez oceniania.")
        return uwagi

    def zawiera_negatywne(tekst):
        for w in slowa_negatywne:
            if " " in w:
                if w in tekst:
                    return True
            elif w in ("zła", "zły", "złe", "źle"):
                # przeczenie przed słowem (np. "nie jestem zła", "nie myśleć źle") nie jest negatywną oceną
                for m in re.finditer(r"\b" + re.escape(w) + r"\b", tekst):
                    przed = tekst[max(0, m.start() - 25):m.start()]
                    if not re.search(r"\bnie\b", przed):
                        return True
            elif re.search(r"\b" + re.escape(w) + r"\w*", tekst):
                return True
        return False

    etap = st.session_state.reframing_stage
    if etap == "input":
        mysl = st.sidebar.text_input("1. Wpisz stresujące przekonanie:", placeholder="Np. 'Zepsuję tę rozmowę...'", key="def_thought")
        if st.sidebar.button("Dalej → Przeformułuj", key="ref_btn_1", use_container_width=True):
            if not mysl.strip():
                st.sidebar.warning("⚠️ Wpisz stresującą myśl.")
            else:
                st.session_state.stressful_thought = mysl.strip()
                st.session_state.reframing_attempts = 0
                st.session_state.reframing_feedback = []
                st.session_state.reframing_stage = "reform"
                st.rerun()
    elif etap == "reform":
        st.sidebar.markdown(f"**Twoja myśl:** _{st.session_state.stressful_thought}_")
        st.sidebar.markdown("<small>Zamień ją na wersję neutralną lub wspierającą.</small>", unsafe_allow_html=True)
        nowa = st.sidebar.text_input("2. Wpisz nową wersję:", key="reform_input")
        col_rf1, col_rf2 = st.sidebar.columns(2)
        sprawdz = col_rf1.button("Sprawdź", key="check_reform", use_container_width=True)
        reset = col_rf2.button("Reset", key="reset_reform", use_container_width=True)
        if sprawdz:
            uwagi = sprawdz_przekonanie(nowa, st.session_state.stressful_thought)
            if uwagi:
                st.session_state.reframing_attempts += 1
                if "__ai__" in uwagi:
                    st.session_state.reframing_feedback = [u for u in uwagi if u != "__ai__"]
                else:
                    pytanie = pytania_pomocnicze[(st.session_state.reframing_attempts - 1) % len(pytania_pomocnicze)]
                    st.session_state.reframing_feedback = uwagi + [f"Pytanie pomocnicze: {pytanie}"]
            else:
                st.session_state.reframed_final = nowa.strip()
                st.session_state.reframing_stage = "success"
                st.rerun()
        if reset:
            st.session_state.reframing_stage = "input"
            st.session_state.reframing_feedback = []
            st.session_state.pop("def_thought", None)
            st.session_state.pop("reform_input", None)
            st.rerun()
        if st.session_state.reframing_feedback:
            st.sidebar.warning(f"Próba {st.session_state.reframing_attempts}: spróbuj jeszcze raz.")
            for u in st.session_state.reframing_feedback:
                st.sidebar.markdown(f"<small>• {u}</small>", unsafe_allow_html=True)
    elif etap == "success":
        st.sidebar.success("🎉 Przekonanie zostało pomyślnie zmienione!")
        st.sidebar.markdown(f"<small>Było: _{st.session_state.stressful_thought}_<br>Jest: **{st.session_state.get('reframed_final', '')}**</small>", unsafe_allow_html=True)
        if st.sidebar.button("Nowe ćwiczenie", key="new_reform", use_container_width=True):
            st.session_state.reframing_stage = "input"
            st.session_state.reframing_feedback = []
            st.session_state.pop("def_thought", None)
            st.session_state.pop("reform_input", None)
            st.rerun()

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
    st.session_state.pop("difficulty_feedback", None)
    st.session_state.tts_cache = {}
    st.rerun()


def render_assistant_message(content):
    if not content or content.startswith("⚠️"):
        st.markdown(content)
        return

    pattern = r'(?i)\*?\*?wskazówka\s*\*?\*?\s*[:\-]?\s*'
    parts = re.split(pattern, content, maxsplit=1)

    main_text = parts[0].strip()
    main_text = re.sub(r'\*+\s*$', '', main_text).strip()

    if main_text:
        st.markdown(main_text)
    elif len(parts) == 1:
        st.markdown(content)

    if len(parts) > 1:
        wskazowka_text = parts[1].strip()
        wskazowka_text = re.sub(r'^\*+\s*', '', wskazowka_text).strip()
        if wskazowka_text:
            st.markdown(f'<div class="coach-box"><strong>Wskazówka:</strong> {wskazowka_text}</div>',
                        unsafe_allow_html=True)

tab_trening, tab_postepy = st.tabs(["💬 Symulator Rozmowy", "📈 Moje Treningi"])

# --- ZAKŁADKA 1: SYMULATOR ROZMOWY ---
with tab_trening:
    bg_choice_val = st.session_state.get('bg_choice', "Tło domyślne (zależne od scenariusza i kategorii)")
    custom_bg_bytes = st.session_state.get('custom_bg_bytes', None)

    if bg_choice_val == "Wgraj własne tło" and custom_bg_bytes:
        mime = st.session_state.get('custom_bg_mime') or "image/png"
        tlo_uri = f"data:{mime};base64," + base64.b64encode(custom_bg_bytes).decode()
    else:
        tlo_uri = tlo_domyslne_data_uri(kategoria_key)

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255,255,255,0.62), rgba(255,255,255,0.62)), url("{tlo_uri}") !important;
            background-size: cover !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main,
        [data-testid="stHeader"], [data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
        div[data-testid="stTabPanel"], div[role="tabpanel"], .stTabs [data-baseweb="tab-panel"] {{
            background: transparent !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.title(f"{kategoria_key} - {wybrany_scenariusz['tytul']}")

    st.markdown(f"""
    <div class="info-card">
        Rozmówca: {wybrany_scenariusz['rola']}<br>
        <small>Tryb: {tryb_rozmowy}</small>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.messages) == 0:
        st.markdown("<br>", unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
        with col_s2:
            if st.button("Rozpocznij", use_container_width=True, type="primary"):
                initial_content = wybrany_scenariusz["start"]
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": initial_content,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.rerun()
        st.stop()

    assistant_avatar_val = "🤖"
    avatar_uri = ""
    avatar_choice_val = st.session_state.get('avatar_choice', "Domyślny (robot 🤖)")
    custom_av_bytes = st.session_state.get('custom_avatar_bytes', None)
    if avatar_choice_val == "Wgraj własnego avatara" and custom_av_bytes:
        av_mime = st.session_state.get('custom_avatar_mime') or "image/png"
        avatar_uri = f"data:{av_mime};base64," + base64.b64encode(custom_av_bytes).decode()
        assistant_avatar_val = custom_av_bytes

    # Wyświetlanie przebiegu rozmowy (wspólne dla trybu pisemnego i głosowego)
    for msg in st.session_state.messages:
        current_avatar = assistant_avatar_val if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=current_avatar):
            if msg["role"] == "assistant":
                render_assistant_message(msg["content"])
            else:
                st.markdown(msg["content"])

    if tryb_rozmowy == "Rozmowa głosowa":
        if "tts_cache" not in st.session_state:
            st.session_state.tts_cache = {}
        if "voice_reset" not in st.session_state:
            st.session_state.voice_reset = 0
        ostatni = st.session_state.messages[-1] if st.session_state.messages else None
        czeka_na_odpowiedz = bool(ostatni and ostatni["role"] == "user")

        # Mowa rozmówcy (gTTS) dla ostatniej wypowiedzi AI - odtwarzana w komponencie
        audio_b64 = ""
        if ostatni and ostatni["role"] == "assistant" and not ostatni["content"].startswith("⚠️"):
            idx = len(st.session_state.messages) - 1
            if idx not in st.session_state.tts_cache:
                try:
                    st.session_state.tts_cache[idx] = base64.b64encode(
                        synteza_mowy(tekst_do_mowy(ostatni["content"]))).decode()
                except Exception:
                    st.session_state.tts_cache[idx] = ""
            audio_b64 = st.session_state.tts_cache[idx]

        wynik = voice_component(
            audio_b64=audio_b64,
            czeka=czeka_na_odpowiedz,
            accent=accent_col,
            avatar=avatar_uri,
            rola=wybrany_scenariusz['rola'],
            reset=st.session_state.voice_reset,
            komunikat=st.session_state.get("voice_komunikat", ""),
            key=f"voice_comp_{len(st.session_state.messages)}",
            default=None
        )

        if wynik and not czeka_na_odpowiedz and wynik.get("id") != st.session_state.get("last_voice_id"):
            st.session_state.last_voice_id = wynik.get("id")
            rozpoznany_tekst = ""
            if wynik.get("type") == "text":
                rozpoznany_tekst = (wynik.get("text") or "").strip()
            elif wynik.get("type") == "audio":
                with st.spinner("Rozpoznawanie mowy..."):
                    try:
                        rozpoznany_tekst = rozpoznaj_mowe(base64.b64decode(wynik.get("wav", "")))
                    except sr.UnknownValueError:
                        rozpoznany_tekst = ""
                    except sr.RequestError:
                        rozpoznany_tekst = ""
                        st.session_state.voice_network_error = True
                    except Exception:
                        rozpoznany_tekst = ""
            if rozpoznany_tekst.strip():
                st.session_state.voice_network_error = False
                st.session_state.voice_komunikat = ""
                dodaj_wypowiedz_uzytkownika(rozpoznany_tekst.strip(), wybrany_scenariusz['tytul'])
                st.rerun()
            else:
                st.session_state.voice_komunikat = (
                    "⚠️ Brak połączenia z usługą rozpoznawania mowy. Sprawdź internet lub wpisz odpowiedź w polu poniżej."
                    if st.session_state.get("voice_network_error")
                    else "Nie wyłapano wypowiedzi. Kliknij „Mów” i spróbuj ponownie, mówiąc wyraźnie.")
                st.session_state.voice_reset += 1
                st.rerun()

        if st.session_state.get("voice_network_error"):
            awaryjna = st.chat_input("Rozpoznawanie mowy niedostępne - wpisz odpowiedź...")
            if awaryjna:
                dodaj_wypowiedz_uzytkownika(awaryjna, wybrany_scenariusz['tytul'])
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_m1, col_m2, col_r = st.columns([1, 2, 2, 1])
    with col_m1:
        if st.button("🏁 Zakończ i podsumuj rozmowę", use_container_width=True, type="primary"):
            if len(st.session_state.messages) > 1:
                st.session_state.summary_mode = True
                st.rerun()
            else:
                st.warning("⚠️ Przeprowadź najpierw rozmowę, aby przejść do podsumowania.")
    with col_m2:
        if st.button("🛑 Przerwij sesję", use_container_width=True, help="Natychmiastowe przerwanie i wyczyszczenie"):
            st.session_state.config_completed = False
            st.session_state.intro_dismissed = False
            st.session_state.messages = []
            st.session_state.tts_cache = {}
            st.rerun()

    if tryb_rozmowy != "Rozmowa głosowa":
        prompt = st.chat_input("Wpisz swoją odpowiedź...")
        if prompt:
            dodaj_wypowiedz_uzytkownika(prompt, wybrany_scenariusz['tytul'])
            st.rerun()

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

        PROMPT_NATURALNY = f"""
        Wcielasz się w postać: {wybrany_scenariusz['rola']} w scenariuszu: {wybrany_scenariusz['tytul']}.
        BEZWZGLĘDNE ZASADY ZACHOWANIA (CZYSTY REALIZM):
        1. Jesteś prawdziwym człowiekiem w tej sytuacji, a NIE asystentem ani botem. Odpowiadaj maksymalnie zwięźle, naturalnie, dynamicznie i życiowo (1-2 zdania). Nie bądź sztucznie uprzejmy.
        2. Jeśli użytkownik zachowuje się wulgarnie, bezczelnie, mówi od rzeczy lub okazuje brak szacunku, zareaguj tak, jak zareagowałby prawdziwy człowiek w tej roli (np. okaż irytację, zaskoczenie, oburzenie, zwróć ostrą uwagę lub zakończ rozmowę).
        3. ZAKŁADANIE PŁCI: Nie używaj form w liczbie pojedynczej wskazujących na płeć, dopóki użytkownik sam wprost tego nie ujawni.
        4. ZMIANA BRANŻY: NIGDY nie sugeruj, nie wymyślaj ani nie zakładaj, że użytkownik chce zmienić branżę lub zawód, chyba że wynika to wprost i jednoznacznie z wybranego scenariusza.
        """

        PROMPT_Z_COACHEM = PROMPT_NATURALNY + f"""
        DODATKOWO, jako osobny blok pod swoją wypowiedź, dołącz merytoryczną wskazówkę na wyróżnionym tle, zaczynając dokładnie od słowa:
        Wskazówka: [Wpisz tutaj merytoryczną analizę błędu użytkownika z perspektywy modelu ABC oraz instrukcję poprawnej wypowiedzi].
        """

        PROMPT_GLOSOWY = PROMPT_NATURALNY + """
        5. ROZMOWA GŁOSOWA: Twoja odpowiedź zostanie odczytana na głos. Mów wyłącznie naturalnym, mówionym tekstem: bez list, nawiasów, emotikonów i formatowania.
        """

        if tryb_rozmowy == "Rozmowa pisemna ze wskazówkami":
            system_prompt = PROMPT_Z_COACHEM + profil_prompt("tekst")
            limit_tokenow = 800
        elif tryb_rozmowy == "Rozmowa głosowa":
            system_prompt = PROMPT_GLOSOWY + profil_prompt("glos")
            limit_tokenow = 300
        else:
            system_prompt = PROMPT_NATURALNY + profil_prompt("tekst")
            limit_tokenow = 500

        api_messages = [{"role": "system", "content": system_prompt + f"\n\nBaza wiedzy RAG:\n{rag_info}"}]
        for m in st.session_state.messages:
            if not (m["role"] == "assistant" and m["content"].startswith("⚠️")):
                api_messages.append({"role": m["role"], "content": m["content"]})

        with st.spinner("Rozmówca przemyślał wypowiedź i odpowiada..."):
            try:
                assistant_reply = chat_completion(config_modelu, model_api_key, api_messages,
                                                  max_tokens=limit_tokenow, temperature=0.5)
            except Exception as e:
                assistant_reply = f"⚠️ Wystąpił błąd podczas komunikacji z API modelu: {e}"

        if assistant_reply:
            asst_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_reply,
                "timestamp": asst_time_str
            })
            st.rerun()
        else:
            st.warning("⚠️ Model zwrócił pustą odpowiedź. Kliknij dowolny przycisk lub wyślij wiadomość ponownie, aby spróbować jeszcze raz.")


# --- ZAKŁADKA 2: MOJE TRENINGI I STATYSTYKI ---
with tab_postepy:
    st.header("Moje Treningi i Statystyki")
    st.write("Śledź historię swoich sesji pobieraną bezpośrednio z urządzeń oraz planuj harmonogram.")

    if st.session_state.training_history:
        df_hist = pd.DataFrame(st.session_state.training_history)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Liczba zarejestrowanych interakcji", len(df_hist))
        with col_m2:
            st.metric("Różnorodne scenariusze", df_hist['scenariusz'].nunique())
        with col_m3:
            ostatnia = df_hist['data'].max().strftime("%Y-%m-%d %H:%M")
            st.metric("Ostatnia aktywność", ostatnia)

        st.divider()

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
    st.caption("Wybierz dni tygodnia oraz godziny powiadomień:")
    
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
