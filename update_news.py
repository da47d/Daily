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
            for item in root.findall('.//item')[:15]:
                title = item.find('title').text
                desc = item.find('description').text if item.find('description') is not None else ""
                headlines.append(f"Titel: {title}\nInhalt: {desc}\n---")
        except Exception as e:
            print(f"Fehler bei Feed {url}: {e}")
    return "\n".join(headlines)

def generate_content_with_ai(raw_text):
    print("Rufe Gemini für gefilterte News und Finanz-Lektion auf...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY fehlt!")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    Du bist Chefredakteur für ein minimalistisches Finanz- und Business-Dashboard.
    Hier sind rohe Nachrichtenmeldungen:
    {raw_text}
    
    Erstelle daraus ein sauberes JSON-Paket nach folgenden strengen Regeln:

    KATEGORIE 'global' (Genau 3 Meldungen):
    - Hier landen alle makroökonomischen, geldpolitischen und weltpolitischen Themen.
    - WICHTIG: Politische Konflikte, Unfälle, Katastrophen oder Drohneneinschläge gehören AUSSCHLIESSLICH hierhin! Niemals in VC.

    KATEGORIE 'vc' (Genau 2 Meldungen):
    - Hier landen NUR echte Startup-News, Risikokapital (Venture Capital), Tech-Investments, KI-SaaS-Tools oder M&A-Deals.
    - Keine allgemeine Weltpolitik hier abspeichern!

    KATEGORIE 'learning':
    Generiere eine lehrreiche, leicht verständliche 3-Minuten-Theorie-Lektion für Studenten. Rotiere täglich durch folgende Gebiete:
    - Makro & Krisen (z.B. Funktionsweise Inflation, Goldstandard, Finanzkrise 2008)
    - Corporate Finance & Valuation (z.B. DCF-Verfahren, Multiples, Leverage-Effekt, WACC)
    - Private Equity & Asset Management (z.B. LBO-Deals, OTC-Derivate, Funktionsweise Investmentfonds)
    - Auditing & Accounting (z.B. Going-Concern-Prinzip, HGB vs. IFRS Grundlagen, Bilanzposten-Prüfung)
    - WICHTIG: Keine Programmiercodes, keine Excel-Formeln. Reiner, stark strukturierter, professioneller Text.

    Antworte NUR mit reinem JSON-Code. Verwende keine Markdown-Formatierung (keine ```json am Anfang oder Ende).

    Exakte Struktur:
    {{
        "global": [
            {{ "tag": "MARKT/POLITIK", "headline": "Griffige Schlagzeile", "summary": "Kurze, präzise Zusammenfassung." }},
            {{ "tag": "MARKT/POLITIK", "headline": "...", "summary": "..." }},
            {{ "tag": "MARKT/POLITIK", "headline": "...", "summary": "..." }}
        ],
        "vc": [
            {{ "tag": "TECH/STARTUP", "headline": "Startup Schlagzeile", "summary": "Zusammenfassung des Investments/Tools." }},
            {{ "tag": "TECH/STARTUP", "headline": "...", "summary": "..." }}
        ],
        "learning": {{
            "topic": "Ein starker Titel für die heutige Lektion",
            "category": "Die Fach-Kategorie",
            "concept": "Die Kernaussage in 1-2 Sätzen.",
            "details": "Die genaue theoretische Funktionsweise oder historische Einordnung (1 kompakter Absatz).",
            "takeaway": "Das wichtigste Learning für die Praxis (1-2 Sätze)."
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
            print("news.json wurde erfolgreich im neuen Kombi-Format gespeichert!")
        except Exception as e:
            print(f"Fehler bei der JSON-Erstellung: {e}")
