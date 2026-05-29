import os
import json
import xml.etree.ElementTree as ET
import requests

def get_raw_news():
    print("Hole aktuelle Schlagzeilen...")
    feeds = [
        "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml",
        "https://search.yahoo.com/mrss/archive/techcrunch"
    ]
    headlines = []
    for url in feeds:
        try:
            response = requests.get(url, timeout=10)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:12]:
                title = item.find('title').text
                desc = item.find('description').text if item.find('description') is not None else ""
                headlines.append(f"Titel: {title}\nInhalt: {desc}\n---")
        except Exception as e:
            print(f"Fehler bei Feed {url}: {e}")
    return "\n".join(headlines)

def generate_content_with_ai(raw_text):
    print("Rufe Gemini-KI für News und Lektion auf...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY fehlt in den Umgebungsvariablen!")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    Du bist Chefredakteur für ein minimalistisches Finanz-Dashboard. Erstelle News und ein tägliches 3-Minuten-Lernmodul.
    
    TEIL 1: AKTUELLE NEWS
    Hier sind Roh-Nachrichten:
    {raw_text}
    Erstelle daraus genau 5 knackige Meldungen (3x 'global' für Märkte/Makro, 2x 'vc' für Startups/Tech).
    
    TEIL 2: DAILY LEARNING (3-MINUTEN WISSEN)
    Wähle vollautomatisch ein rotierendes, hochrelevantes Thema aus einem dieser Bereiche:
    - Makroökonomische Zusammenhänge & Krisenhistorie (z.B. Stagflation, Dotcom-Blase, Bretton-Woods)
    - Corporate Finance & Valuation Basics (z.B. DCF-Ziele, WACC-Logik, Multiples, Leverage-Effekt)
    - Private Equity, Venture Capital & Asset Management (z.B. LBO-Struktur, Cap Table, Fonds-Strukturen, OTC-Derivate)
    - Auditing & Core Accounting (z.B. Grundprinzipien der Rechnungslegung, Going-Concern, Goodwill-Impairment)
    Wichtig: Keine Excel-Erklärungen. Erkläre die Theorie simpel, sauber strukturiert, professionell und ohne kryptische Text-Pfeile.
    
    Gib AUSSCHLIESSLICH ein reines JSON-Objekt zurück, ohne Markdown-Codeblöcke (kein ```json).
    Exakte Struktur:
    {{
        "global": [
            {{ "tag": "USA", "headline": "...", "summary": "..." }},
            {{ "tag": "ZINSEN", "headline": "...", "summary": "..." }},
            {{ "tag": "MARKT", "headline": "...", "summary": "..." }}
        ],
        "vc": [
            {{ "tag": "SAAS", "headline": "...", "summary": "..." }},
            {{ "tag": "FUNDING", "headline": "...", "summary": "..." }}
        ],
        "learning": {{
            "topic": "Ein griffiger, spannender Titel (z.B. Der Leverage-Effekt verständlich erklärt)",
            "category": "Die Kategorie (z.B. Corporate Finance)",
            "concept": "1-2 prägnante Sätze, was die Kernaussage/Ursache ist.",
            "details": "Ein kompakter, starker Absatz zur genauen Funktionsweise oder Historie.",
            "takeaway": "Das entscheidende Learning für die Praxis in 1-2 Sätzen."
        }}
    }}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    text_response = result['candidates'][0]['content']['parts'][0]['text']
    return text_response.strip()

if __name__ == "__main__":
    raw_data = get_raw_news()
    if raw_data:
        try:
            ai_json_text = generate_content_with_ai(raw_data)
            
            if ai_json_text.startswith("```"):
                ai_json_text = ai_json_text.split("```json")[-1].split("```")[0].strip()
                
            parsed_json = json.loads(ai_json_text)
            
            with open("news.json", "w", encoding="utf-8") as f:
                json.dump(parsed_json, f, ensure_ascii=False, indent=2)
            print("news.json erfolgreich aktualisiert!")
        except Exception as e:
            print(f"Fehler bei der JSON-Erstellung: {e}")
