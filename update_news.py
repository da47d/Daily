import os
import json
import xml.etree.ElementTree as ET
import requests

def get_raw_news():
    print("Hole aktuelle Schlagzeilen aus erweiterten Quellen...")
    feeds = [
        "[https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml](https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml)",
        "[https://www.nzz.ch/wirtschaft.rss](https://www.nzz.ch/wirtschaft.rss)",
        "[https://www.n-tv.de/ticker/rss](https://www.n-tv.de/ticker/rss)",
        "[https://techcrunch.com/feed/](https://techcrunch.com/feed/)"
    ]
    headlines = []
    for url in feeds:
        try:
            response = requests.get(url, timeout=10)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:12]:
                title = item.find('title').text if item.find('title') is not None else ""
                desc = item.find('description').text if item.find('description') is not None else ""
                headlines.append(f"Titel: {title}\nInhalt: {desc}\n---")
        except Exception as e:
            print(f"Fehler bei Feed {url}: {e}")
    return "\n".join(headlines)

def generate_content_with_ai(raw_text):
    print("Rufe Gemini für die neuen Kategorien und die praxisnahe Finance-Matrix auf...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY fehlt!")
        
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=){api_key}"
    
    prompt = f"""
    Du bist Chefredakteur für ein minimalistisches, hochgradig personalisiertes Dashboard eines Finance-Studenten.
    Hier sind die aktuellen rohen Nachrichtenmeldungen des Tages:
    {raw_text}
    
    Deine Aufgabe ist es, diese Meldungen zu filtern, drastisch zu kürzen (maximal 2 prägnante Sätze pro Zusammenfassung) und strikt in die folgenden 4 Kategorien zu sortieren. 
    Lösche irrelevante Meldungen eiskalt.

    ---
    
    1. KATEGORIE 'politics' (Genau 2 Meldungen):
       - Fokus: Geopolitische Großereignisse und weltweite Politik, die direkten Einfluss auf die Stimmung an den globalen Märkten haben (z.B. Wahlen, internationale Konflikte, Sanktionen, wichtige Handelszölle).

    2. KATEGORIE 'macro' (Genau 2 Meldungen):
       - Fokus: Harte wirtschaftliche Fakten. Makroökonomische Trends, Zinsentscheidungen von EZB/Fed, Inflationsdaten, große M&A-Deals, Private Equity Übernahmen und Konjunkturprognosen.

    3. KATEGORIE 'buzz' (Genau 2 Meldungen):
       - Fokus: Top Stories. Wichtige globale Ereignisse, über die man im Alltag spricht und die Schlagzeilen außerhalb der reinen Wirtschaftswelt dominieren (z.B. Technologie-Meilensteine, große Sport-Events wie Entwicklungen nach dem Champions-League-Finale, spektakuläre Produkt-Launches). Keine Boulevard-Gerüchte, sondern echte Top-Schlagzeilen.

    4. KATEGORIE 'vc' (Genau 2 Meldungen):
       - Fokus: Startups & Venture Capital. Wichtige Tech-Finanzierungsrunden (ab Series A), neue VC-Fonds, bahnbrechende Tech-Prototypen oder Gründer-Storys.

    ---

    5. KATEGORIE 'learning' (Tägliches 3-Minuten-Wissen):
       Generiere eine lehrreiche, extrem gut verständliche Theorie-Lektion, um die "Finance-Sprache" und das Marktgeschehen zu entschlüsseln. 
       Wähle eigenständig EIN spezifisches Thema aus einem dieser vier rotierenden Gebiete:
       
       - Finanz-Dechiffrierung: Abkürzungen und Produktbezeichnungen zerlegen (z.B. ETF-Namenszusätze wie Core, IMI, Acc vs. Dist, UCITS, Swap/Physisch; Startup-Slang wie SaaS, B2B, ARR, Burn Rate, Churn; M&A-Unterschiede wie Strategic vs. Financial Buyer).
       - Historische Finanzereignisse & Krisen: Meilensteine kurz erklärt (z.B. Das Black-Swan-Konzept, die Tulpenmanie 1637, das Bretton-Woods-System, der Kern der Dotcom-Blase oder Lehman-Pleite 2008).
       - Finanzprodukte verständlich erklärt: Logische Funktionsweise komplexer Instrumente (z.B. Derivate über den Ernte-Vergleich, Optionen vs. Optionsscheine, Arbeitsweise von Hedgefonds, Ablauf eines Short Squeeze).
       - Tech & VC Deal-Decoder: Vertragliche und finanzielle Strukturierung von Deals (z.B. Cap-Table-Logik bei einer Down Round, Pre-Money vs. Post-Money Bewertung, Bedeutung von Vesting für Gründer, Asset Deal vs. Share Deal).

       STRIKTE VERBOTENE THEMEN (BANNED LIST):
       Generiere unter gar keinen Umständen etwas zu: "DCF-Verfahren" / "Discounted Cash Flow", "EBITDA", "Leverage-Effekt" oder den absoluten Grundlagen. Diese Themen sind gesperrt! Konzentriere dich auf die logische Mechanik, keine mathematischen Formeln, keine Programmiercodes, keine Excel-Formeln.

    ---

    Exakte JSON-Struktur, die du befüllen musst:
    {{
        "politics": [
            {{ "tag": "POLITIK & GLOBAL", "headline": "Schlagzeile", "summary": "Maximal zwei Sätze." }},
            {{ "tag": "POLITIK & GLOBAL", "headline": "...", "summary": "..." }}
        ],
        "macro": [
            {{ "tag": "MACRO ECONOMY", "headline": "Schlagzeile", "summary": "Maximal zwei Sätze." }},
            {{ "tag": "MACRO ECONOMY", "headline": "...", "summary": "..." }}
        ],
        "buzz": [
            {{ "tag": "TOP STORIES", "headline": "Schlagzeile", "summary": "Maximal zwei Sätze." }},
            {{ "tag": "TOP STORIES", "headline": "...", "summary": "..." }}
        ],
        "vc": [
            {{ "tag": "STARTUPS & VC", "headline": "Schlagzeile", "summary": "Maximal zwei Sätze." }},
            {{ "tag": "STARTUPS & VC", "headline": "...", "summary": "..." }}
        ],
        "learning": {{
            "topic": "Titel der Lektion",
            "category": "Die Fach-Kategorie",
            "concept": "Die Kernaussage in 1-2 Sätzen.",
            "details": "Die genaue logische Funktionsweise und Relevanz für die Praxis (1 kompakter Absatz).",
            "takeaway": "Das wichtigste Learning für die Praxis oder Interviews (1-2 Sätze)."
        }}
    }}
    """
    
    # Hier zwingen wir die API über die Config zu sauberem JSON ohne Backticks:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    text_response = result['candidates'][0]['content']['parts'][0]['text']
    return text_response.strip()

if __name__ == "__main__":
    raw_data = get_raw_news()
    if raw_data:
        ai_json_text = generate_content_with_ai(raw_data)
        
        # Dank responseMimeType ist der Text jetzt IMMER direkt valides JSON!
        parsed_json = json.loads(ai_json_text)
        
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=2)
        print("news.json wurde erfolgreich gespeichert!")
