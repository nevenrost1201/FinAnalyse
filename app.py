#!/usr/bin/env python3
"""
FinAnalyse - Pro (Streamlit) - Neo-Broker-Design (Indigo/Violett)
=================================================================
Dashboard (Markt-Suche + Indizes mit Mini-Charts) + Einzelanalyse
+ Mein Depot (Ist-Wert, XIRR, Depot-Backtest) + Charts/Prognose
+ Makro-Faktoren + Watchlist + Sprachwahl + Begriffe + Templates
+ Investment-Memo + Portfolio-Backtest + Free/Plus/Pro.

ANALYSE- UND BILDUNGS-TOOL. KEINE ANLAGEBERATUNG.

Start:
    pip install streamlit yfinance pandas numpy
    streamlit run app.py
"""

import os
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None


# ============================================================
#  SPRACHE
# ============================================================
TR = {
    "title": {"de": "FinAnalyse", "en": "FinAnalyse"},
    "subtitle": {"de": "Fundamentalanalyse - schnell, strukturiert, nachpruefbar",
                 "en": "Fundamental analysis - fast, structured, verifiable"},
    "dashboard": {"de": "Dashboard", "en": "Dashboard"},
    "single": {"de": "Einzelanalyse", "en": "Single Analysis"},
    "mein_depot": {"de": "Mein Depot", "en": "My Portfolio"},
    "portfolio": {"de": "Portfolio & Backtest", "en": "Portfolio & Backtest"},
    "pricing": {"de": "Preise & Plus", "en": "Pricing & Plus"},
    "rechtliches": {"de": "Rechtliches", "en": "Legal"},
    "lernen": {"de": "Lernen", "en": "Learn"},
    "krypto": {"de": "Krypto", "en": "Crypto"},
    "rechner": {"de": "Rechner", "en": "Calculators"},
    "analyze": {"de": "Analysieren", "en": "Analyze"},
    "ticker_in": {"de": "Ticker suchen / eingeben", "en": "Search / enter ticker"},
    "popular": {"de": "oder beliebt waehlen", "en": "or pick popular"},
    "overview": {"de": "Unternehmens-Ueberblick", "en": "Company Overview"},
    "macro": {"de": "Annahmen anpassen: Wachstum & Makro-Faktoren", "en": "Adjust assumptions: growth & macro"},
    "growth": {"de": "Erwartetes EPS-Wachstum p.a. (%)", "en": "Expected EPS growth p.a. (%)"},
    "eff_growth": {"de": "Effektives Wachstum (nach Makro)", "en": "Effective growth (after macro)"},
    "quality": {"de": "Quality-Score", "en": "Quality Score"},
    "value": {"de": "Value-Score (wachstumsber.)", "en": "Value Score (growth-adj.)"},
    "verdict": {"de": "FAZIT", "en": "VERDICT"},
    "tab_eval": {"de": "Auswertung", "en": "Evaluation"},
    "tab_hist": {"de": "Kennzahlen & Diagramme", "en": "Metrics & Charts"},
    "tab_chart": {"de": "Chart & Prognose", "en": "Chart & Projection"},
    "tab_qual": {"de": "Qualitativ (Templates)", "en": "Qualitative (Templates)"},
    "tab_summary": {"de": "Zusammenfassung", "en": "Summary"},
    "tab_raw": {"de": "Rohdaten", "en": "Raw Data"},
    "tab_check": {"de": "Gegenpruefen", "en": "Verify"},
    "add_wl": {"de": "Zur Watchlist", "en": "Add to watchlist"},
    "watchlist": {"de": "Watchlist", "en": "Watchlist"},
    "glossary": {"de": "Begriffserklaerungen", "en": "Glossary"},
    "howto": {"de": "So funktioniert's", "en": "How it works"},
    "completeness": {"de": "Vollstaendigkeit der Analyse", "en": "Analysis completeness"},
    "download_memo": {"de": "Investment-Memo herunterladen (.md)", "en": "Download investment memo (.md)"},
    "start_capital": {"de": "Startkapital (EUR)", "en": "Starting capital (EUR)"},
    "plan": {"de": "Dein Plan", "en": "Your plan"},
    "market_today": {"de": "Markt heute", "en": "Market today"},
    "market_search": {"de": "Beliebigen Wert suchen (Ticker)", "en": "Search any asset (ticker)"},
    "your_wl": {"de": "Deine Watchlist", "en": "Your watchlist"},
    "pf_snapshot": {"de": "Portfolio-Snapshot", "en": "Portfolio snapshot"},
}
def t(k):
    lang = st.session_state.get("lang", "de")
    return TR.get(k, {}).get(lang, k)

NAV = ["dash", "single", "depot", "portfolio", "lernen", "krypto", "rechner", "pricing", "legal"]
NAV_KEY = {"dash": "dashboard", "single": "single", "depot": "mein_depot",
           "portfolio": "portfolio", "lernen": "lernen", "krypto": "krypto", "rechner": "rechner",
           "pricing": "pricing", "legal": "rechtliches"}
def nav_label(k): return t(NAV_KEY[k])

def goto_analyze(tk):
    st.session_state["nav"] = "single"
    st.session_state["pending_ticker"] = tk

def goto_single():
    st.session_state["nav"] = "single"

def goto_legal():
    st.session_state["nav"] = "legal"

def accept_consent():
    st.session_state["consent_ok"] = True

def dismiss_onboarding():
    st.session_state["onboard_dismissed"] = True

# Gefuehrte Erst-Tour: mehrstufige Erklaerung, ueberspringbar
TOUR = [
    ("Willkommen bei FinAnalyse",
     "Diese App hilft dir, Aktien strukturiert nach Fundamentaldaten zu pruefen, dein Depot zu verstehen und Schritt "
     "fuer Schritt dazuzulernen. Wichtig vorab: Es ist ein Bildungs- und Analyse-Tool und gibt KEINE Anlageberatung. "
     "In den naechsten Schritten zeige ich dir kurz, was wo zu finden ist."),
    ("Dashboard",
     "Dein Startpunkt: aktuelle Marktdaten mit Mini-Charts, deine Watchlist mit Live-Scores, ein Snapshot deines "
     "getesteten Portfolios und - mit hinterlegtem Schluessel - aktuelle News zu deinen Depot-Positionen."),
    ("Einzelanalyse",
     "Gib einen Ticker ein und bekomme in Sekunden Quality-Score, Value/PEG und ein Fazit. Dazu Tabs fuer qualitative "
     "Vorlagen (Moat, Risiken), zum Gegenpruefen der Zahlen und ein herunterladbares Investment-Memo."),
    ("Mein Depot",
     "Trage deine echten Positionen ein: exakter Depotwert, geldgewichtete Rendite (XIRR), ein Backtest deiner "
     "Mischung, die Wertentwicklung seit Kauf und eine Klumpenrisiko-Uebersicht nach Anlageklasse."),
    ("Portfolio & Backtest",
     "Teste eine Aktien-Mischung historisch: Rendite p.a., Sharpe-Ratio und maximaler Drawdown - plus eine "
     "begruendete Szenario-Prognose fuer die Zukunft."),
    ("Lernen",
     "27 Lektionen vom Anfaenger bis zum eigenstaendigen Analysieren - jede mit einem kleinen Test (5-10 Fragen). "
     "Optional beantwortet dir ein KI-Tutor deine Fragen."),
    ("Rechner",
     "Die wichtigsten Werkzeuge fuer Privatanleger: Sparplan/Zinseszins, Notgroschen, Kosten-Effekt, "
     "Steuer-Schaetzer (Deutschland), Entnahme/4%-Regel und Positionsgroesse."),
    ("Los geht's!",
     "Oben links wechselst du jederzeit zwischen den Bereichen. Denk dran: alle Ergebnisse sind ohne Gewaehr und "
     "keine Anlageberatung. Viel Erfolg beim Lernen und Analysieren!"),
]

def onboard_next():
    s = st.session_state.get("onboard_step", 0) + 1
    if s >= len(TOUR):
        st.session_state["tour_done"] = True
    else:
        st.session_state["onboard_step"] = s

def onboard_skip():
    st.session_state["tour_done"] = True


# ============================================================
#  RECHTSTEXTE (Kurzfassungen fuer die App; Muster)
# ============================================================
LEGAL_DISCLAIMER = """**Haftungsausschluss**

FinAnalyse ist ein **Bildungs- und Analysewerkzeug** und stellt KEINE Anlageberatung, Anlageempfehlung oder
Aufforderung zum Kauf/Verkauf dar. Es findet keine Eignungs- oder Angemessenheitspruefung statt. Alle Inhalte,
Kennzahlen, Scores und Beispiel-Allokationen sind allgemeine Informationen und nicht auf deine persoenliche
Situation zugeschnitten.

Markt- und Fundamentaldaten stammen von Dritten (u.a. Yahoo Finance) und werden ohne Gewaehr bereitgestellt;
sie koennen fehlerhaft oder verzoegert sein. Investitionen in Wertpapiere, ETFs und besonders Kryptowerte koennen
zum **Totalverlust** fuehren. Vergangene Wertentwicklung ist kein verlaesslicher Indikator fuer die Zukunft.
KI-Texte koennen Fehler enthalten. Entscheidungen triffst du eigenverantwortlich; ziehe bei Bedarf eine
zugelassene Beratung hinzu."""

LEGAL_AGB = """**Nutzungsbedingungen (Kurzfassung)**

- **Anbieter:** [Name / Firma], [Anschrift], [E-Mail].
- **Leistung:** Informations-, Bildungs- und Berechnungswerkzeug. Der Anbieter ist kein Finanzdienstleistungs-
institut und erbringt keine Anlageberatung, -vermittlung oder Portfolioverwaltung; keine personalisierten
Empfehlungen zu konkreten Finanzinstrumenten.
- **Nutzerpflichten:** eigenverantwortliche Nutzung, keine rechtswidrigen Inhalte, keine missbraeuchliche Nutzung.
- **Verfuegbarkeit/Gewaehr:** keine Garantie auf staendige Verfuegbarkeit; Daten ohne Gewaehr.
- **Haftung:** unbeschraenkt bei Vorsatz/grober Fahrlaessigkeit und bei Leben/Koerper/Gesundheit; sonst nur bei
Verletzung wesentlicher Pflichten, begrenzt auf den vorhersehbaren Schaden. Keine Haftung fuer Anlageentscheidungen.
- **Kostenpflichtige Plaene (falls aktiv):** [Preise, Laufzeit, Kuendigung, 14-taegiges Widerrufsrecht].
- **Recht:** es gilt deutsches Recht; Gerichtsstand [Ort], soweit zulaessig."""

LEGAL_IMPRESSUM = """**Impressum (Paragraph 5 DDG)**

[Vorname Nachname / Firmenname]
[Strasse Hausnummer]
[PLZ Ort], [Land]

Kontakt: [E-Mail], [Telefon optional]
Vertretungsberechtigt / Inhaber: [Name]
USt-IdNr. (falls vorhanden): [DE...]
Verantwortlich i.S.v. Paragraph 18 Abs. 2 MStV: [Name, Anschrift]

EU-Streitschlichtung: https://ec.europa.eu/consumers/odr - zur Teilnahme an einem Verbraucherschlichtungsverfahren
sind wir nicht verpflichtet und grundsaetzlich nicht bereit."""

LEGAL_DATENSCHUTZ = """**Datenschutz (Eckpunkte, DSGVO)**

- **Verantwortlicher:** [Name / Firma], [Anschrift], [E-Mail].
- **Daten:** Server-Logs (Betrieb/Sicherheit, Art. 6 (1) f); Konto-Daten falls Login (Art. 6 (1) b); Cookies/Tracking
nur mit Einwilligung (Art. 6 (1) a).
- **Hinweis:** Deine Eingaben (Watchlist, Depot, Notizen) werden im Prototyp nur waehrend der Sitzung gehalten und
NICHT dauerhaft gespeichert. Mit Login + Datenbank ist dieser Punkt anzupassen.
- **Drittanbieter:** Hosting [Provider], Marktdaten (Yahoo Finance), optional KI (OpenAI), Zahlung [Stripe] - je AVV
und ggf. Drittlandtransfer (USA, Standardvertragsklauseln).
- **Cookies (TDDDG):** technisch Notwendiges ohne Einwilligung; sonst Consent-Banner.
- **Deine Rechte:** Auskunft, Berichtigung, Loeschung, Einschraenkung, Datenuebertragbarkeit, Widerspruch, Widerruf
sowie Beschwerde bei einer Aufsichtsbehoerde. Kontakt: [E-Mail]."""


# ============================================================
#  LERN-CURRICULUM: Fundamentalanalyse von 0 auf
# ============================================================
LESSONS = [
    {
        "key": 'was',
        "title": 'Was ist Fundamentalanalyse?',
        "body": 'Beim Investieren kaufst du keinen zappelnden Kurs auf einem Bildschirm, sondern einen echten Anteil an einem Unternehmen - mit Mitarbeitern, Marken, Produkten und Gewinnen. Fundamentalanalyse ist die Disziplin, dieses Geschaeft zu verstehen und zu bewerten, statt auf Kursmuster zu wetten. Vier Leitfragen stehen im Zentrum: Verdient die Firma Geld (Profitabilitaet)? Waechst sie nachhaltig (Wachstum)? Ist sie solide finanziert (Bilanz)? Und ist der Preis dafuer fair (Bewertung)? Der boersengehandelte Kurs ist nur die Tagesmeinung des Marktes - eine Mischung aus Fakten, Erwartungen, Angst und Gier. Die Fundamentaldaten sind die langsamere Realitaet dahinter. Benjamin Graham, der Begruender, brachte es auf ein Bild: Kurzfristig ist die Boerse eine Abstimmungsmaschine (Stimmung), langfristig eine Waage (echter Wert). Genau die Luecke zwischen Stimmung und Wert ist deine Chance - wird ein gutes Unternehmen voruebergehend zu billig gehandelt, kannst du es guenstig einsammeln. Diese App fuehrt dich Schritt fuer Schritt durch die vier Fragen, vom ersten Blick auf die Kennzahlen bis zur fertigen Investment-These. Wichtig: Fundamentalanalyse ist kein Werkzeug fuer schnelle Trades, sondern fuer geduldiges Investieren ueber Jahre - und reine Bildung, keine Anlageberatung.',
        "faustregel": 'Erst das Unternehmen verstehen, dann auf den Preis schauen - nie umgekehrt.',
        "quizzes": [
            {"q": 'Was kaufst du laut Fundamentalanalyse beim Investieren?', "options": ['Einen Anteil an einem echten Unternehmen', 'Ein kurzfristiges Kursmuster', 'Eine Wette auf die Stimmung'], "correct": 0, "explain": 'Du erwirbst einen Anteil am Geschaeft, nicht am Chart.'},
            {"q": 'Welche vier Leitfragen stehen im Zentrum?', "options": ['Profitabilitaet, Wachstum, Bilanz, Bewertung', 'Chart, Volumen, RSI, MACD', 'Marke, Logo, Werbung, CEO'], "correct": 0, "explain": 'Verdient sie, waechst sie, ist sie solide, ist der Preis fair?'},
            {"q": 'Was ist die Boerse laut Graham langfristig?', "options": ['Eine Waage (echter Wert)', 'Eine Abstimmungsmaschine (Stimmung)', 'Ein Wuerfel'], "correct": 0, "explain": 'Kurzfristig Stimmung, langfristig wiegt sie den echten Wert.'},
            {"q": 'Was ist der Aktienkurs kurzfristig?', "options": ['Die Tagesmeinung des Marktes', 'Der exakte innere Wert', 'Eine garantierte Rendite'], "correct": 0, "explain": 'Eine Mischung aus Fakten, Erwartungen, Angst und Gier.'},
            {"q": 'Wofuer ist Fundamentalanalyse gedacht?', "options": ['Geduldiges Investieren ueber Jahre', 'Sekundenschnelles Daytrading', 'Gluecksspiel'], "correct": 0, "explain": 'Sie zielt auf langfristige Substanz, nicht auf schnelle Trades.'},
            {"q": 'Worin liegt laut Lektion deine Chance?', "options": ['In der Luecke zwischen Stimmung und Wert', 'In Insiderwissen', 'In Hebelprodukten'], "correct": 0, "explain": 'Wenn Stimmung und echter Wert auseinanderlaufen, entsteht die Gelegenheit.'},
        ],
        "quiz": {"q": 'Was kaufst du laut Fundamentalanalyse beim Investieren?', "options": ['Einen Anteil an einem echten Unternehmen', 'Ein kurzfristiges Kursmuster', 'Eine Wette auf die Stimmung'], "correct": 0, "explain": 'Du erwirbst einen Anteil am Geschaeft, nicht am Chart.'},
    },
    {
        "key": 'abschluesse',
        "title": 'Die 3 Zahlenwerke',
        "body": "Jede boersennotierte Firma veroeffentlicht regelmaessig drei zentrale Berichte - sie sind die Rohstoffe jeder Analyse. Die **GuV** (Gewinn- und Verlustrechnung) zeigt ueber einen Zeitraum: Umsatz minus aller Kosten ergibt den Gewinn. Sie ist wie ein Kontoauszug der Geschaeftstaetigkeit und beantwortet 'Wie viel hat die Firma verdient?'. Die **Bilanz** ist dagegen ein Foto zu einem Stichtag: Auf der einen Seite steht, was die Firma besitzt (Vermoegen - Maschinen, Vorraete, Cash), auf der anderen, wie das finanziert ist (Eigenkapital der Aktionaere und Schulden). Sie beantwortet 'Wie solide steht die Firma da?'. Der **Cashflow** schliesslich zeigt, wie viel echtes Geld tatsaechlich rein- und rausgeflossen ist, getrennt nach operativem, investivem und finanzierendem Bereich. Warum drei Berichte? Weil Gewinn (GuV) und Geld (Cashflow) nicht dasselbe sind: Eine Firma kann auf dem Papier Gewinn ausweisen und trotzdem kein Cash haben - etwa weil Kunden noch nicht gezahlt haben oder hohe Investitionen anstehen. Erst das Zusammenspiel aller drei ergibt ein ehrliches Bild und deckt Widersprueche auf. Saemtliche Kennzahlen dieser App - Margen, Renditen, Verschuldung, Bewertung - werden aus genau diesen drei Werken berechnet. Wer sie grob lesen kann, versteht jede Analyse besser und merkt sofort, wenn etwas nicht zusammenpasst.",
        "faustregel": 'GuV = Ertrag, Bilanz = Substanz, Cashflow = echtes Geld.',
        "quizzes": [
            {"q": 'Welcher Bericht zeigt, wie viel echtes Geld fliesst?', "options": ['Cashflow', 'GuV', 'Bilanz'], "correct": 0, "explain": 'Buchgewinn ist nicht automatisch Geld in der Kasse.'},
            {"q": 'Was zeigt die Bilanz?', "options": ['Vermoegen und Schulden zu einem Stichtag', 'Den Gewinn ueber ein Jahr', 'Den Aktienkurs'], "correct": 0, "explain": 'Ein Foto des Vermoegens zu einem Stichtag.'},
            {"q": 'Was beschreibt die GuV?', "options": ['Umsatz minus Kosten = Gewinn ueber einen Zeitraum', 'Den Kontostand heute', 'Die Dividende'], "correct": 0, "explain": 'Wie ein Kontoauszug der Geschaeftstaetigkeit.'},
            {"q": 'Warum reicht der ausgewiesene Gewinn allein nicht?', "options": ['Gewinn auf dem Papier ist nicht automatisch Cash', 'Gewinn ist immer falsch', 'Gewinn zeigt die Schulden'], "correct": 0, "explain": 'Kunden koennen noch nicht gezahlt haben - dann fehlt das Geld trotz Gewinn.'},
            {"q": 'Woraus berechnet die App ihre Kennzahlen?', "options": ['Aus diesen drei Berichten', 'Aus der Foren-Stimmung', 'Aus dem Chart'], "correct": 0, "explain": 'GuV, Bilanz und Cashflow sind die Rohstoffe jeder Analyse.'},
            {"q": 'Die Bilanz ist wie ...?', "options": ['Ein Foto zu einem Stichtag', 'Ein Film ueber ein Jahr', 'Eine Wettervorhersage'], "correct": 0, "explain": 'Ein Momentaufnahme, kein Zeitraum.'},
        ],
        "quiz": {"q": 'Welcher Bericht zeigt, wie viel echtes Geld fliesst?', "options": ['Cashflow', 'GuV', 'Bilanz'], "correct": 0, "explain": 'Buchgewinn ist nicht automatisch Geld in der Kasse.'},
    },
    {
        "key": 'margen',
        "title": 'Profitabilitaet: Margen',
        "body": 'Eine Marge beantwortet die einfache Frage: Wie viel von einem Euro Umsatz bleibt am Ende als Gewinn uebrig? Man liest sie von oben nach unten durch die GuV. Die **Bruttomarge** bleibt nach den direkten Herstellkosten (Material, Produktion) - sie zeigt die rohe Preissetzungsmacht: Software erreicht oft 70-85%, Markenartikler 40-60%, der Einzelhandel nur 20-35%. Die **EBIT-Marge** (operative Marge) bleibt nach allen laufenden Kosten wie Vertrieb, Verwaltung und Forschung - sie zeigt, wie effizient das Kerngeschaeft wirklich arbeitet. Die **Nettomarge** ganz unten beruecksichtigt zusaetzlich Zinsen und Steuern und zeigt, was am Ende fuer die Aktionaere uebrig bleibt. Entscheidend sind zwei Dinge: die Hoehe UND die Stabilitaet ueber die Jahre. Eine Firma mit konstant 25% EBIT-Marge ueber zehn Jahre ist meist staerker als eine, die zwischen 5% und 35% schwankt - Stabilitaet deutet auf einen Wettbewerbsvorteil und Preissetzungsmacht hin. Steigende Margen koennen Skaleneffekte oder eine staerker werdende Marktposition signalisieren; dauerhaft fallende Margen sind ein Warnsignal fuer Preisdruck oder steigende Kosten. Ganz wichtig: Vergleiche Margen immer nur innerhalb derselben Branche. Ein Supermarkt mit 4% Nettomarge kann ein hervorragendes Geschaeft sein, ein Softwarehaus mit 4% dagegen ein schwaches - die strukturellen Margenniveaus unterscheiden sich von Branche zu Branche gewaltig.',
        "faustregel": 'Hohe UND stabile Margen schlagen hohe, aber schwankende.',
        "quizzes": [
            {"q": 'Was signalisiert eine hohe Bruttomarge?', "options": ['Preissetzungsmacht', 'Hohe Schulden', 'Niedrige Steuern'], "correct": 0, "explain": 'Wer Preise durchsetzt, hat meist einen Vorteil.'},
            {"q": 'Welche Marge steht ganz unten (nach Steuern und Zinsen)?', "options": ['Nettomarge', 'Bruttomarge', 'EBIT-Marge'], "correct": 0, "explain": 'Die Nettomarge ist das, was fuer Aktionaere bleibt.'},
            {"q": 'Was ist neben der Hoehe der Marge entscheidend?', "options": ['Die Stabilitaet ueber die Jahre', 'Die Farbe des Logos', 'Der Boersenplatz'], "correct": 0, "explain": 'Stabile Margen deuten auf einen Wettbewerbsvorteil hin.'},
            {"q": 'Wie vergleicht man Margen sinnvoll?', "options": ['Nur innerhalb derselben Branche', 'Quer ueber alle Branchen', 'Mit dem Goldpreis'], "correct": 0, "explain": 'Branchen haben strukturell sehr unterschiedliche Margenniveaus.'},
            {"q": 'Welche Marge bleibt nach allen operativen Kosten?', "options": ['EBIT-Marge', 'Bruttomarge', 'Nettomarge'], "correct": 0, "explain": 'Die operative (EBIT-)Marge nach Vertrieb, Verwaltung, F&E.'},
            {"q": 'Ein Supermarkt mit 4% Nettomarge ist ...?', "options": ['Branchenueblich und evtl. ein gutes Geschaeft', 'Automatisch schlecht', 'Pleite'], "correct": 0, "explain": 'Im Handel sind niedrige Margen normal.'},
        ],
        "quiz": {"q": 'Was signalisiert eine hohe Bruttomarge?', "options": ['Preissetzungsmacht', 'Hohe Schulden', 'Niedrige Steuern'], "correct": 0, "explain": 'Wer Preise durchsetzt, hat meist einen Vorteil.'},
    },
    {
        "key": 'rendite',
        "title": 'Kapitalrendite: ROE & ROCE',
        "body": 'Margen sagen, wie profitabel der Umsatz ist - Kapitalrenditen sagen, wie effizient die Firma das eingesetzte Kapital in Gewinn verwandelt. Das ist oft die wichtigere Frage, denn ein Unternehmen, das aus 100 Euro Kapital 20 Euro Gewinn macht, ist eine bessere Geldmaschine als eines, das dafuer 1000 Euro binden muss. **ROE** (Return on Equity) = Gewinn geteilt durch Eigenkapital, also die Rendite auf das Geld der Aktionaere. **ROCE** bzw. ROIC = operativer Gewinn geteilt durch das gesamte eingesetzte Kapital (Eigenkapital plus zinstragende Schulden) - das ist fairer, weil es Schulden mitzaehlt. Werte dauerhaft ueber rund 15% gelten als gut, ueber 20% als exzellent. Der entscheidende Vergleich: Liegt die Kapitalrendite ueber den **Kapitalkosten** der Firma? Nur dann schafft sie echten Wert. Achte auf eine haeufige Falle: Ein sehr hohes ROE kann kuenstlich durch hohe Verschuldung oder massive Aktienrueckkaeufe (die das Eigenkapital verkleinern) entstehen - die Firma sieht dann profitabler aus, als sie operativ ist. Deshalb immer ROE gegen ROCE pruefen: Klaffen sie weit auseinander, steckt meist viel Schuldenhebel dahinter. Hohe, ueber viele Jahre stabile Kapitalrenditen sind eines der staerksten Qualitaetsmerkmale ueberhaupt - sie sind oft ein Indiz fuer einen echten Wettbewerbsvorteil, weil normale Konkurrenz solche Ueberrenditen sonst wegkonkurrieren wuerde.',
        "faustregel": 'ROCE > 15% = das Unternehmen verzinst Kapital stark.',
        "quizzes": [
            {"q": 'Warum ROE mit ROCE gegenpruefen?', "options": ['ROE ignoriert Schulden und Rueckkaeufe', 'ROCE ist immer hoeher', 'Beide sind identisch'], "correct": 0, "explain": 'Hohe Verschuldung kann das ROE aufblaehen.'},
            {"q": 'Was misst ROCE bzw. ROIC?', "options": ['Rendite auf das gesamte eingesetzte Kapital', 'Nur den Aktienkurs', 'Die Dividende'], "correct": 0, "explain": 'Inklusive Schulden - daher fairer als das ROE.'},
            {"q": 'Ab welchem Wert gilt die Kapitalrendite grob als gut?', "options": ['Ueber rund 15%', 'Ueber 2%', 'Unter 0%'], "correct": 0, "explain": 'Ueber 20% gilt als exzellent.'},
            {"q": 'Wann schafft eine Firma echten Wert?', "options": ['Wenn die Kapitalrendite ueber den Kapitalkosten liegt', 'Immer', 'Nie'], "correct": 0, "explain": 'Nur oberhalb der Kapitalkosten entsteht Mehrwert.'},
            {"q": 'Wodurch kann ein ROE kuenstlich hoch wirken?', "options": ['Durch hohe Verschuldung oder Rueckkaeufe', 'Durch niedrige Steuern', 'Durch viele Mitarbeiter'], "correct": 0, "explain": 'Beides verkleinert das Eigenkapital im Nenner.'},
            {"q": 'Hohe, stabile Kapitalrenditen deuten oft auf ...?', "options": ['Einen Wettbewerbsvorteil', 'Bilanzbetrug', 'Zufall'], "correct": 0, "explain": 'Sonst wuerde Konkurrenz die Ueberrenditen wegkonkurrieren.'},
        ],
        "quiz": {"q": 'Warum ROE mit ROCE gegenpruefen?', "options": ['ROE ignoriert Schulden und Rueckkaeufe', 'ROCE ist immer hoeher', 'Beide sind identisch'], "correct": 0, "explain": 'Hohe Verschuldung kann das ROE aufblaehen.'},
    },
    {
        "key": 'wachstum',
        "title": 'Wachstum (CAGR)',
        "body": 'Wachstum ist der Motor langfristiger Kursgewinne - aber nur die richtige Art von Wachstum. Die **CAGR** (durchschnittliche jaehrliche Wachstumsrate) glaettet einzelne Ausreisser und zeigt das Tempo ueber mehrere Jahre. Die App schaut auf drei Ebenen: **Umsatz-Wachstum** (waechst die Nachfrage?), **Gewinn- bzw. EPS-Wachstum** (kommt das Wachstum auch unten an?) und **FCF-Wachstum** (entsteht echtes Geld?). Ideal ist, wenn Gewinn und Cashflow mindestens so schnell wachsen wie der Umsatz - dann skaliert das Geschaeft profitabel. Waechst der Umsatz, aber der Gewinn nicht mit, kauft die Firma ihr Wachstum womoeglich zu teuer ein. Zwei klassische Fallen: Erstens der **Basiseffekt** - startest du die Messung in einem Krisen-Tiefjahr, sieht die Wachstumsrate kuenstlich spektakulaer aus; schau deshalb ueber einen vollen Zyklus von 5-10 Jahren. Zweitens **unprofitables Wachstum** - Umsatz um jeden Preis, finanziert durch staendig neue Schulden oder neue Aktien, vernichtet eher Wert, als ihn zu schaffen. Frage dich auch, ob das Wachstum **organisch** (aus eigener Kraft) oder durch teure Zukaeufe entsteht - organisches Wachstum ist meist hochwertiger und nachhaltiger. Und denke daran, dass kein Baum in den Himmel waechst: Sehr hohe Raten verlangsamen sich mit zunehmender Groesse fast immer, und Prognosen, die zweistelliges Wachstum auf Jahrzehnte fortschreiben, sollten dich skeptisch machen. Gesundes Wachstum ist stetig, profitabel und durch einen echten, dauerhaften Markttrend gedeckt.',
        "faustregel": 'Profitables, stetiges Wachstum schlaegt schnelles, aber verlustreiches.',
        "quizzes": [
            {"q": 'Worauf bei der CAGR achten?', "options": ['Startjahr - Ausreisser verzerren', 'Nur auf den letzten Tag', 'Auf den Aktienkurs'], "correct": 0, "explain": 'Ein Tief- oder Hochpunkt als Start verzerrt die Rate stark.'},
            {"q": 'Welches Wachstum ist am hochwertigsten?', "options": ['Profitables, organisches Wachstum', 'Umsatz um jeden Preis', 'Wachstum nur durch Schulden'], "correct": 0, "explain": 'Profitabel und aus eigener Kraft ist am nachhaltigsten.'},
            {"q": 'Welche drei Ebenen schaut die App an?', "options": ['Umsatz, Gewinn/EPS, FCF', 'Kurs, Volumen, RSI', 'Marke, Werbung, PR'], "correct": 0, "explain": 'Idealerweise wachsen Gewinn und Cash mit dem Umsatz.'},
            {"q": 'Was bedeutet der Basiseffekt?', "options": ['Start im Tiefjahr laesst Wachstum kuenstlich hoch wirken', 'Wachstum ist immer echt', 'FCF ist egal'], "correct": 0, "explain": 'Deshalb ueber einen vollen Zyklus von 5-10 Jahren schauen.'},
            {"q": 'Was heisst organisches Wachstum?', "options": ['Aus eigener Kraft, nicht durch Zukaeufe', 'Nur durch Uebernahmen', 'Durch neue Aktien'], "correct": 0, "explain": 'Organisch ist meist hochwertiger als zugekauft.'},
            {"q": 'Sehr hohe Wachstumsraten ...?', "options": ['Verlangsamen sich mit der Groesse fast immer', 'Halten ewig an', 'Sind garantiert'], "correct": 0, "explain": 'Kein Baum waechst in den Himmel.'},
        ],
        "quiz": {"q": 'Worauf bei der CAGR achten?', "options": ['Startjahr - Ausreisser verzerren', 'Nur auf den letzten Tag', 'Auf den Aktienkurs'], "correct": 0, "explain": 'Ein Tief- oder Hochpunkt als Start verzerrt die Rate stark.'},
    },
    {
        "key": 'bilanz',
        "title": 'Bilanz-Gesundheit & Schulden',
        "body": 'Schulden sind nicht per se schlecht - klug eingesetzt koennen sie die Rendite hebeln. Zu viel davon macht eine Firma aber verwundbar, besonders wenn Zinsen steigen oder das Geschaeft einbricht. Die wichtigste Kennzahl ist **Net Debt/EBITDA**: Sie zeigt, wie viele Jahre operativer Gewinn (EBITDA) noetig waeren, um die Nettoschulden (Schulden minus Cash) zu tilgen. Unter 1 ist sehr stark, 1-3 normal, ueber 3 wird es heikel und ueber 4-5 gefaehrlich - vor allem in zyklischen Branchen. Die **Current Ratio** (kurzfristiges Vermoegen geteilt durch kurzfristige Verbindlichkeiten) prueft, ob die Firma ihre Rechnungen der naechsten zwoelf Monate problemlos bezahlen kann; Werte ueber 1 sind beruhigend. Der **Zinsdeckungsgrad** (EBIT geteilt durch Zinsaufwand) zeigt, wie locker die Firma ihre Zinsen aus dem operativen Gewinn stemmt - je hoeher, desto sicherer. Wichtig ist der Kontext: Ein stabiler Versorger mit planbaren Einnahmen vertraegt mehr Schulden als ein schwankungsanfaelliger Zykliker. Achte auch auf versteckte Verpflichtungen wie Pensionslasten, Leasingverbindlichkeiten oder kurzfristig faellige Anleihen, die in Krisen refinanziert werden muessen. Eine solide Bilanz ist wie ein dickes Polster: Sie laesst eine Firma Krisen ueberstehen, in denen schwaecher finanzierte Konkurrenten kapitulieren - und ermoeglicht es sogar, antizyklisch zu investieren, wenn andere ums Ueberleben kaempfen. Bilanzstaerke ist unspektakulaer, entscheidet aber oft ueber Untergang oder Fortbestand.',
        "faustregel": 'Net Debt/EBITDA < 3 - darueber wird es heikel.',
        "quizzes": [
            {"q": 'Was bedeutet Net Debt/EBITDA = 4?', "options": ['Eher hohe Verschuldung', 'Sehr solide', 'Kein Aussagewert'], "correct": 0, "explain": 'Ueber 3 gilt als riskant.'},
            {"q": 'Was prueft die Current Ratio?', "options": ['Ob kurzfristige Rechnungen gedeckt sind', 'Den Gewinn', 'Den Kurs'], "correct": 0, "explain": 'Kurzfristiges Vermoegen gegen kurzfristige Schulden.'},
            {"q": 'Was zeigt der Zinsdeckungsgrad?', "options": ['Wie locker Zinsen aus dem Gewinn gestemmt werden', 'Die Dividende', 'Den Umsatz'], "correct": 0, "explain": 'EBIT geteilt durch Zinsaufwand - je hoeher, desto sicherer.'},
            {"q": 'Wer vertraegt mehr Schulden?', "options": ['Ein stabiler Versorger', 'Ein schwankungsanfaelliger Zykliker', 'Ein Start-up'], "correct": 0, "explain": 'Planbare Einnahmen tragen mehr Verschuldung.'},
            {"q": 'Net Debt/EBITDA unter 1 ist ...?', "options": ['Sehr stark', 'Gefaehrlich', 'Verboten'], "correct": 0, "explain": 'Die Firma koennte ihre Schulden fast aus einem Jahr tilgen.'},
            {"q": 'Wozu dient eine solide Bilanz?', "options": ['Krisen ueberstehen', 'Den Kurs zu garantieren', 'Steuern zu sparen'], "correct": 0, "explain": 'Sie ist das Polster, das schwaechere Konkurrenten nicht haben.'},
        ],
        "quiz": {"q": 'Was bedeutet Net Debt/EBITDA = 4?', "options": ['Eher hohe Verschuldung', 'Sehr solide', 'Kein Aussagewert'], "correct": 0, "explain": 'Ueber 3 gilt als riskant.'},
    },
    {
        "key": 'cashflow',
        "title": 'Cashflow & FCF-Conversion',
        "body": "'Gewinn ist eine Meinung, Cash ist ein Fakt' - dieser Satz erklaert, warum erfahrene Investoren oft zuerst auf den Cashflow schauen. Der **operative Cashflow** ist das Geld aus dem laufenden Geschaeft. Zieht man davon die noetigen Investitionen (CapEx) ab, bleibt der **Free Cash Flow (FCF)** - das wirklich freie Geld, mit dem die Firma Dividenden zahlen, Schulden tilgen, Aktien zurueckkaufen oder Zukaeufe finanzieren kann, ohne sich neu zu verschulden. FCF ist die Lebensader eines Unternehmens. Die Kennzahl **FCF-Conversion** (FCF geteilt durch Buchgewinn) zeigt, wie viel des in der GuV ausgewiesenen Gewinns tatsaechlich als Cash ankommt. Werte um oder ueber 90-100% sind exzellent und ein Zeichen ehrlicher, hochwertiger Gewinne. Liegt die Conversion ueber Jahre deutlich darunter, ist Vorsicht geboten: Der Gewinn existiert dann vor allem auf dem Papier - etwa weil er in unbezahlten Forderungen, wachsenden Lagern oder aggressiven Buchungen steckt. Genau hier verstecken sich viele Bilanzskandale, denn ausgewiesener Gewinn laesst sich leichter schoenrechnen als echtes Cash auf dem Konto. Achte zudem auf den Unterschied zwischen **Erhaltungs-CapEx** (noetig, um den Betrieb am Laufen zu halten) und **Wachstums-CapEx** (freiwillige Investition in die Zukunft): Eine Firma, die nur wegen hoher Wachstumsinvestitionen gerade wenig FCF zeigt, kann attraktiver sein als eine mit stagnierendem Geschaeft und scheinbar hohem FCF. Cash luegt am seltensten - deshalb ist es oft der ehrlichste Blick auf die Qualitaet.",
        "faustregel": 'Cash schlaegt Buchgewinn - FCF-Conversion > 90% ist top.',
        "quizzes": [
            {"q": 'Was misst die FCF-Conversion?', "options": ['Wie viel Gewinn als echtes Cash ankommt', 'Die Dividendenhoehe', 'Den Aktienkurs'], "correct": 0, "explain": 'Sie zeigt die Cash-Qualitaet des Gewinns.'},
            {"q": 'Was ist Free Cash Flow?', "options": ['Geld nach den noetigen Investitionen', 'Der Umsatz', 'Das Eigenkapital'], "correct": 0, "explain": 'Daraus zahlt die Firma Dividenden, Schulden und Rueckkaeufe.'},
            {"q": 'Eine FCF-Conversion ueber 90% ist ...?', "options": ['Exzellent', 'Ein Warnsignal', 'Egal'], "correct": 0, "explain": 'Zeichen ehrlicher, hochwertiger Gewinne.'},
            {"q": 'Niedrige Conversion ueber viele Jahre?', "options": ['Warnsignal - Gewinn nur auf dem Papier', 'Immer gut', 'Bedeutet hohe Dividende'], "correct": 0, "explain": 'Der Gewinn steckt dann oft in Forderungen oder Lagern.'},
            {"q": 'Welche Investition ist eher freiwillig?', "options": ['Wachstums-CapEx', 'Erhaltungs-CapEx', 'Keine von beiden'], "correct": 0, "explain": 'Erhaltungs-CapEx haelt nur den Betrieb am Laufen.'},
            {"q": 'Warum schauen Profis oft zuerst auf Cash?', "options": ['Cash laesst sich schwerer schoenrechnen als Gewinn', 'Cash ist unwichtig', 'Gewinn gibt es nicht'], "correct": 0, "explain": 'Cash ist der ehrlichste Blick auf die Qualitaet.'},
        ],
        "quiz": {"q": 'Was misst die FCF-Conversion?', "options": ['Wie viel Gewinn als echtes Cash ankommt', 'Die Dividendenhoehe', 'Den Aktienkurs'], "correct": 0, "explain": 'Sie zeigt die Cash-Qualitaet des Gewinns.'},
    },
    {
        "key": 'bewertung',
        "title": 'Bewertung: KGV & EV/EBITDA',
        "body": 'Ein gutes Unternehmen ist noch kein gutes Investment - es kommt auf den Preis an. Bewertungskennzahlen setzen den Kurs ins Verhaeltnis zum Geschaeft. Das bekannteste ist das **KGV** (Kurs-Gewinn-Verhaeltnis) = Aktienkurs geteilt durch Gewinn je Aktie. Ein KGV von 15 bedeutet grob, dass du fuer die Aktie rund 15 Jahresgewinne auf einmal bezahlst - oder umgekehrt eine Gewinnrendite von rund 6,7% erzielst (1 geteilt durch 15). Je niedriger, desto optisch guenstiger. Das KGV hat aber Schwaechen: Es ignoriert Schulden und laesst sich durch Sondereffekte verzerren. Deshalb nutzen Profis zusaetzlich **EV/EBITDA**: Der Enterprise Value (Marktwert plus Nettoschulden) wird ins Verhaeltnis zum operativen Gewinn vor Abschreibungen gesetzt. Das macht Firmen mit unterschiedlicher Verschuldung vergleichbar und ist daher fuer Branchenvergleiche oft fairer. Weitere nuetzliche Multiples sind das **KUV** (Kurs-Umsatz, brauchbar fuer noch unprofitable Wachstumsfirmen) und das **KBV** (Kurs-Buchwert, relevant bei Banken und Versicherern). Die wichtigste Warnung: Ein niedriges KGV ist nicht automatisch ein Schnaeppchen. Oft ist eine Aktie aus gutem Grund billig - schrumpfendes Geschaeft, strukturelle Probleme, drohende Disruption oder ein Bilanzrisiko. Das nennt man eine **Value Trap**, eine Bewertungsfalle. Guenstig ist nur dann wirklich guenstig, wenn die Qualitaet des Unternehmens stimmt und die niedrige Bewertung nicht ein berechtigtes Misstrauen des Marktes widerspiegelt. Bewertung ist deshalb immer die zweite Frage - erst Qualitaet, dann Preis.',
        "faustregel": 'Ein niedriges KGV ist nur guenstig, wenn die Qualitaet stimmt.',
        "quizzes": [
            {"q": 'Ein KGV von 15 bedeutet ungefaehr ...?', "options": ['15 Jahresgewinne als Preis', '15 Euro Dividende', '15% Wachstum'], "correct": 0, "explain": 'Du zahlst rund 15 Jahresgewinne fuer die Aktie.'},
            {"q": 'Warum ist EV/EBITDA oft fairer?', "options": ['Es beruecksichtigt zusaetzlich Schulden', 'Es ignoriert alles', 'Es ist immer hoeher'], "correct": 0, "explain": 'Macht Firmen mit unterschiedlicher Verschuldung vergleichbar.'},
            {"q": 'Was ist eine Value Trap?', "options": ['Optisch billig, aber zu Recht', 'Eine teure Wachstumsaktie', 'Eine Dividende'], "correct": 0, "explain": 'Guenstig wegen echter struktureller Probleme.'},
            {"q": 'Ein niedriges KGV ist nur guenstig, wenn ...?', "options": ['Die Qualitaet stimmt', 'Immer', 'Nie'], "correct": 0, "explain": 'Sonst ist es oft eine Value Trap.'},
            {"q": 'Wofuer ist das KUV (Kurs-Umsatz) brauchbar?', "options": ['Fuer noch unprofitable Wachstumsfirmen', 'Fuer Banken', 'Fuer Gold'], "correct": 0, "explain": 'Wenn es noch keinen Gewinn fuer ein KGV gibt.'},
            {"q": 'Bewertung ist ...?', "options": ['Die zweite Frage nach der Qualitaet', 'Die einzige Frage', 'Egal'], "correct": 0, "explain": 'Erst Qualitaet, dann Preis.'},
        ],
        "quiz": {"q": 'Ein KGV von 15 bedeutet ungefaehr ...?', "options": ['15 Jahresgewinne als Preis', '15 Euro Dividende', '15% Wachstum'], "correct": 0, "explain": 'Du zahlst rund 15 Jahresgewinne fuer die Aktie.'},
    },
    {
        "key": 'peg',
        "title": 'Die KGV-Falle & PEG',
        "body": "Das KGV allein fuehrt zu einem haeufigen Denkfehler: Eine Aktie mit KGV 30 wirkt teuer, eine mit KGV 10 billig. Doch das ignoriert das Wachstum voellig. Eine Firma, die ihren Gewinn jaehrlich um 25% steigert, ist mit KGV 30 womoeglich guenstiger als eine stagnierende Firma mit KGV 10 - denn die Wachstumsfirma 'waechst in ihre Bewertung hinein'. Genau das loest das **PEG-Verhaeltnis** (Price/Earnings-to-Growth): KGV geteilt durch die erwartete prozentuale Gewinnwachstumsrate. Die Faustregel von Peter Lynch: PEG unter 1 ist wachstumsbereinigt guenstig, um 1 fair bewertet, ueber 2 teuer. Ein Beispiel: KGV 30 bei 30% Wachstum ergibt ein PEG von 1,0 - fair. KGV 10 bei nur 5% Wachstum ergibt ein PEG von 2,0 - trotz niedrigem KGV also teuer. So kannst du einen langsam wachsenden Versorger fair mit einem schnellen Tech-Wert vergleichen, ohne dich vom absoluten KGV taeuschen zu lassen. Deshalb gewichtet diese App den PEG bewusst stark. Kenne aber die Grenzen: Das PEG steht und faellt mit der Wachstums-Schaetzung, und Wachstum laesst sich nicht ewig fortschreiben - irgendwann verlangsamt sich jede Firma. Sehr hohe, gerade aktuelle Wachstumsraten sind selten nachhaltig, weshalb ein optisch niedriges PEG bei einer Hype-Aktie truegen kann. Nutze das PEG als nuetzliche Bruecke zwischen Preis und Wachstum - als wertvollen Hinweis, nicht als alleinige Wahrheit.",
        "faustregel": 'PEG < 1 = du zahlst wenig pro Prozent Wachstum.',
        "quizzes": [
            {"q": 'Warum reicht das KGV allein nicht?', "options": ['Es ignoriert das Wachstum', 'Es ist immer falsch', 'Es zeigt Schulden'], "correct": 0, "explain": 'Erst das Wachstum (PEG) macht teure Wachstumswerte vergleichbar.'},
            {"q": 'Ein PEG unter 1 bedeutet ...?', "options": ['Wachstumsbereinigt guenstig', 'Teuer', 'Hohe Schulden'], "correct": 0, "explain": 'Du zahlst wenig pro Prozent Wachstum.'},
            {"q": 'KGV 30 bei 30% Wachstum ergibt welches PEG?', "options": ['1,0 (fair)', '30', '0,1'], "correct": 0, "explain": '30 geteilt durch 30 = 1,0.'},
            {"q": 'KGV 10 bei 5% Wachstum ergibt welches PEG?', "options": ['2,0 (teuer)', '0,5', '1,0'], "correct": 0, "explain": '10 geteilt durch 5 = 2,0 - trotz niedrigem KGV teuer.'},
            {"q": 'Womit steht und faellt das PEG?', "options": ['Mit der Wachstums-Schaetzung', 'Mit dem Logo', 'Mit dem Boersenplatz'], "correct": 0, "explain": 'Falsche Wachstumsannahme = falsches PEG.'},
            {"q": 'Wer hat die PEG-Faustregel bekannt gemacht?', "options": ['Peter Lynch', 'Niemand', 'Ein Roboter'], "correct": 0, "explain": 'Lynch nutzte PEG < 1 als Orientierung.'},
        ],
        "quiz": {"q": 'Warum reicht das KGV allein nicht?', "options": ['Es ignoriert das Wachstum', 'Es ist immer falsch', 'Es zeigt Schulden'], "correct": 0, "explain": 'Erst das Wachstum (PEG) macht teure Wachstumswerte vergleichbar.'},
    },
    {
        "key": 'moat',
        "title": 'Qualitaet & Moat',
        "body": "Alle bisherigen Kennzahlen beschreiben die Vergangenheit. Die entscheidende Frage fuer die Zukunft lautet: Kann die Firma ihre hohen Margen und Renditen auch in zehn Jahren noch verteidigen? Genau das beantwortet der **Moat** (englisch fuer Burggraben) - ein Begriff, den Warren Buffett gepraegt hat. Ein Moat ist ein dauerhafter, struktureller Wettbewerbsvorteil, der Konkurrenten fernhaelt und es der Firma erlaubt, ueber Jahre ueberdurchschnittlich zu verdienen. Ohne Moat lockt jede hohe Marge sofort Nachahmer an, die die Preise so lange druecken, bis kaum noch Gewinn uebrig bleibt - so funktioniert Wettbewerb normalerweise. Typische Quellen eines Moats sind starke Marken (Apple kann Premiumpreise durchsetzen), Netzwerkeffekte (Visa wird mit jedem Nutzer wertvoller), Kostenvorteile durch Groesse (Amazon), hohe Wechselkosten (ein Unternehmen wechselt nicht mal eben seine Microsoft- oder SAP-Software) oder Patente und Lizenzen. Dazu kommt der menschliche Faktor: ehrliches, faehiges Management, das das Kapital klug einsetzt. Diese qualitativen Punkte stehen in keiner Tabelle - du musst sie selbst beurteilen, indem du Geschaeftsberichte liest und das Geschaeftsmodell wirklich verstehst. Die App liefert dir dafuer strukturierte Vorlagen im Tab 'Qualitativ'. Frage immer auch, ob der Graben breiter oder schmaler wird: Ein Moat, der gerade von neuer Technologie oder veraenderten Kundengewohnheiten angegriffen wird, ist weniger wert, als die Vergangenheitszahlen vermuten lassen. Merke: Die Zahlen filtern die Kandidaten, aber der Moat entscheidet, ob aus einem guten Jahr ein gutes Jahrzehnt wird.",
        "faustregel": 'Ohne Moat sind hohe Margen selten von Dauer.',
        "quizzes": [
            {"q": 'Was ist ein Moat?', "options": ['Ein dauerhafter Wettbewerbsvorteil', 'Ein kurzfristiger Kursanstieg', 'Eine Dividende'], "correct": 0, "explain": 'Der Burggraben schuetzt Gewinne langfristig.'},
            {"q": 'Was passiert ohne Moat mit hohen Margen?', "options": ['Nachahmer druecken sie weg', 'Sie steigen ewig', 'Nichts'], "correct": 0, "explain": 'Wettbewerb erodiert ungeschuetzte Margen.'},
            {"q": 'Welche Firma ist ein Beispiel fuer Netzwerkeffekte?', "options": ['Visa', 'Ein Bergwerk', 'Ein Baecker'], "correct": 0, "explain": 'Mehr Nutzer machen das Netz wertvoller.'},
            {"q": 'Wo bewertest du die qualitativen Moat-Punkte?', "options": ['Selbst, mit den App-Vorlagen', 'Gar nicht', 'Per Zufall'], "correct": 0, "explain": 'Sie stehen in keiner Tabelle.'},
            {"q": 'Was entscheidet ueber die Zukunft?', "options": ['Der Moat', 'Der gestrige Kurs', 'Das Wetter'], "correct": 0, "explain": 'Zahlen sind Vergangenheit, der Moat die Zukunft.'},
            {"q": 'Ein gerade angegriffener Moat ist ...?', "options": ['Weniger wert als die alten Zahlen zeigen', 'Mehr wert', 'Egal'], "correct": 0, "explain": 'Disruption kann den Vorteil schnell aushoehlen.'},
        ],
        "quiz": {"q": 'Was ist ein Moat?', "options": ['Ein dauerhafter Wettbewerbsvorteil', 'Ein kurzfristiger Kursanstieg', 'Eine Dividende'], "correct": 0, "explain": 'Der Burggraben schuetzt Gewinne langfristig.'},
    },
    {
        "key": 'sbc',
        "title": 'Aktienzahl & Verwaesserung',
        "body": "Der Gewinn je Aktie (EPS) ist ein Bruch: Gesamtgewinn geteilt durch Anzahl der Aktien. Er kann also steigen, weil der Zaehler (Gewinn) waechst - oder weil der Nenner (Aktienzahl) sinkt. Beides sieht in der Kennzahl gleich aus, ist wirtschaftlich aber sehr unterschiedlich. Viele Firmen **verwaessern** ihre Aktionaere, indem sie laufend neue Aktien ausgeben, am haeufigsten als **aktienbasierte Verguetung** (Stock-Based Compensation, SBC) fuer Mitarbeiter und Management. Das ist ein realer Kostenblock - die Firma bezahlt mit Eigentumsanteilen statt mit Cash -, aber das beliebte 'adjusted' oder 'non-GAAP'-Ergebnis blendet ihn gerne aus und laesst die Profitabilitaet schoener aussehen, als sie ist. Der Effekt fuer dich: Mit jeder neuen Aktie schrumpft dein prozentualer Anteil am Unternehmen, selbst wenn der Gesamtgewinn waechst. Umgekehrt erhoehen **Aktienrueckkaeufe** deinen Anteil - dieselbe Firma gehoert dann weniger Eigentuemern, dein Stueck vom Kuchen wird groesser. Deshalb lohnt der Blick auf die **ausstehenden Aktien ueber 5-10 Jahre**: Eine sinkende Aktienzahl ist Rueckenwind fuer den Aktionaer, eine stark steigende ein chronischer Gegenwind. Pruefe besonders bei wachstumsstarken Tech-Firmen, wie hoch die SBC im Verhaeltnis zu Umsatz und Cashflow ist - manchmal frisst sie einen Grossteil des scheinbaren Gewinns auf. Und denke daran: Ein Rueckkaufprogramm schafft nur dann Wert, wenn die Aktie zum Rueckkaufzeitpunkt nicht ohnehin ueberteuert war - sonst verbrennt das Management Geld der Aktionaere.",
        "faustregel": 'Sinkende Aktienzahl ist Rueckenwind, steigende ist Gegenwind fuer den Aktionaer.',
        "quizzes": [
            {"q": 'Was bedeutet eine stark steigende Aktienzahl fuer dich?', "options": ['Verwaesserung deines Anteils', 'Garantiert hoehere Dividende', 'Keine Schulden mehr'], "correct": 0, "explain": 'Dein Stueck vom Kuchen wird kleiner.'},
            {"q": 'Was ist SBC?', "options": ['Aktienbasierte Verguetung', 'Eine Steuer', 'Eine Dividende'], "correct": 0, "explain": 'Stock-Based Compensation - Bezahlung mit Aktien.'},
            {"q": 'Was bewirken Aktienrueckkaeufe?', "options": ['Dein Anteil steigt', 'Dein Anteil sinkt', 'Nichts'], "correct": 0, "explain": 'Weniger Aktien = groesserer Anteil je Aktie.'},
            {"q": 'Wodurch kann das EPS steigen?', "options": ['Durch mehr Gewinn ODER weniger Aktien', 'Nur durch mehr Aktien', 'Nur durch Werbung'], "correct": 0, "explain": 'EPS = Gewinn geteilt durch Aktienzahl.'},
            {"q": 'Worauf beim Rueckkauf achten?', "options": ['Nicht zu ueberhoehten Kursen', 'Immer kaufen', 'Nie kaufen'], "correct": 0, "explain": 'Teure Rueckkaeufe verbrennen Aktionaersgeld.'},
            {"q": "Was blendet das 'adjusted'-Ergebnis oft aus?", "options": ['Die SBC-Kosten', 'Den Umsatz', 'Die Steuern'], "correct": 0, "explain": 'Dadurch wirkt die Profitabilitaet schoener.'},
        ],
        "quiz": {"q": 'Was bedeutet eine stark steigende Aktienzahl fuer dich?', "options": ['Verwaesserung deines Anteils', 'Garantiert hoehere Dividende', 'Keine Schulden mehr'], "correct": 0, "explain": 'Dein Stueck vom Kuchen wird kleiner.'},
    },
    {
        "key": 'dividenden',
        "title": 'Dividenden & Rueckkaeufe',
        "body": 'Wenn eine Firma Gewinn erwirtschaftet, hat das Management vier Moeglichkeiten: ins eigene Geschaeft reinvestieren, Schulden tilgen, eine Dividende zahlen oder eigene Aktien zurueckkaufen. Wie es sich entscheidet, sagt viel ueber die Qualitaet. Eine **Dividende** ist Bargeld, das direkt auf dein Konto fliesst - attraktiv fuer planbares Einkommen, aber nicht automatisch ein Qualitaetszeichen. Entscheidend ist die **Ausschuettungsquote** (Payout Ratio): der Anteil des Gewinns (besser noch des Free Cash Flow), der als Dividende ausgezahlt wird. Liegt sie nachhaltig unter etwa 60%, bleibt genug fuer Investitionen und ein Puffer fuer schlechte Jahre. Zahlt eine Firma dagegen mehr aus, als sie verdient, finanziert sie die Dividende aus der Substanz oder mit Schulden - das geht selten lange gut und endet oft in einer Dividendenkuerzung, die den Kurs zusaetzlich abstuerzen laesst. Eine sehr hohe **Dividendenrendite** von z.B. 9% ist deshalb oft kein Geschenk, sondern ein Warnsignal: Sie ist meist nur deshalb so hoch, weil der Kurs aus gutem Grund eingebrochen ist - die **Dividendenfalle**. **Aktienrueckkaeufe** sind die steuerlich oft effizientere Alternative: Sie erhoehen deinen Anteil und steigern den Gewinn je Aktie - aber nur, wenn das Management nicht zu ueberhoehten Kursen zurueckkauft. Am aussagekraeftigsten ist eine lange Historie stetig steigender Dividenden bei gleichzeitig wachsendem Gewinn: Das zeigt ein verlaessliches Geschaeft und ein aktionaersfreundliches, diszipliniertes Management.',
        "faustregel": 'Payout-Quote unter ~60% und ein wachsender Gewinn machen Dividenden nachhaltig.',
        "quizzes": [
            {"q": 'Bei 9% Dividendenrendite was zuerst pruefen?', "options": ['Ob die Ausschuettung aus dem Gewinn gedeckt ist', 'Ob der CEO sympathisch ist', 'Den Kurs von gestern'], "correct": 0, "explain": 'Sehr hohe Renditen sind oft ein Warnsignal.'},
            {"q": 'Was ist die Payout Ratio?', "options": ['Anteil des Gewinns, der als Dividende ausgezahlt wird', 'Der Kurs', 'Eine Steuer'], "correct": 0, "explain": 'Ueber 100% ist die Dividende nicht gedeckt.'},
            {"q": 'Wann ist eine Dividende nachhaltig?', "options": ['Payout unter ~60% und Gewinn waechst', 'Payout ueber 150%', 'Egal'], "correct": 0, "explain": 'Dann bleibt Puffer fuer schlechte Jahre.'},
            {"q": 'Eine sehr hohe Dividendenrendite ist oft ...?', "options": ['Ein Warnsignal (Dividendenfalle)', 'Ein Qualitaetssiegel', 'Garantiert'], "correct": 0, "explain": 'Meist nur hoch, weil der Kurs eingebrochen ist.'},
            {"q": 'Rueckkaeufe sind sinnvoll, wenn ...?', "options": ['Die Aktie nicht ueberteuert ist', 'Immer', 'Nie'], "correct": 0, "explain": 'Sonst zahlt das Management zu viel.'},
            {"q": 'Was ist das beste Zeichen?', "options": ['Lange Historie steigender Dividenden bei wachsendem Gewinn', 'Einmalige Sonderdividende', 'Hohe Schulden'], "correct": 0, "explain": 'Zeigt ein verlaessliches, aktionaersfreundliches Geschaeft.'},
        ],
        "quiz": {"q": 'Bei 9% Dividendenrendite was zuerst pruefen?', "options": ['Ob die Ausschuettung aus dem Gewinn gedeckt ist', 'Ob der CEO sympathisch ist', 'Den Kurs von gestern'], "correct": 0, "explain": 'Sehr hohe Renditen sind oft ein Warnsignal.'},
    },
    {
        "key": 'moat_typen',
        "title": 'Die 5 Burggraben-Typen',
        "body": 'Ein Moat ist nichts Vages - er laesst sich in fuenf konkrete Typen einteilen (eine Systematik von Morningstar). Wenn du bei einer Aktie keinen dieser Typen klar benennen kannst, gibt es vermutlich keinen echten Burggraben. Erstens **immaterielle Werte**: Marken, Patente und Lizenzen. Coca-Cola kann allein wegen der Marke hoehere Preise verlangen; ein Pharmakonzern ist durch Patente fuer Jahre vor Nachahmern geschuetzt. Zweitens **Wechselkosten**: Wenn der Wechsel zur Konkurrenz teuer, riskant oder muehsam ist, bleiben Kunden auch bei Preiserhoehungen - eine Bank wechselt nicht mal eben ihre Kernsoftware, ein Konzern nicht mal eben sein ERP-System. Drittens der **Netzwerkeffekt**: Jeder neue Nutzer macht das Produkt fuer alle anderen wertvoller. Visa und Mastercard profitieren davon, dass mehr Karteninhaber mehr Haendler anziehen und umgekehrt; Buchungs- und Handelsplattformen funktionieren genauso. Viertens **Kostenvorteile**: Eine Firma produziert dauerhaft guenstiger als alle anderen - durch Groesse, ueberlegene Prozesse oder Standortvorteile (Amazon, Costco). Fuenftens **effiziente Skalierung**: In manchen Maerkten ist nur Platz fuer wenige Anbieter, etwa bei Pipelines, Bahnstrecken oder regionalen Versorgern - neue Konkurrenz lohnt sich schlicht nicht. Pruefe bei jeder Position: Welcher Typ liegt vor, wie breit ist der Graben, und vor allem - wird er in zehn Jahren breiter oder schmaler? Ein wachsender Moat ist Gold wert; ein schrumpfender ist ein Grund, vorsichtig zu werden, egal wie gut die letzten Zahlen aussahen.',
        "faustregel": 'Benenne den Moat-Typ konkret - kannst du es nicht, gibt es vielleicht keinen.',
        "quizzes": [
            {"q": 'Visa profitiert vor allem von welchem Moat?', "options": ['Netzwerkeffekt', 'Patenten auf Geldscheine', 'Niedriger Dividende'], "correct": 0, "explain": 'Mehr Karten und Haendler machen das Netz wertvoller.'},
            {"q": 'Coca-Cola hat vor allem welchen Moat?', "options": ['Immaterielle Werte / Marke', 'Netzwerkeffekt', 'Kostenvorteil'], "correct": 0, "explain": 'Die Marke erlaubt Premiumpreise.'},
            {"q": 'SAP- oder Bank-Software steht fuer welchen Moat?', "options": ['Wechselkosten', 'Patente', 'Marke'], "correct": 0, "explain": 'Ein Wechsel ist teuer und riskant.'},
            {"q": 'Amazon und Costco stehen fuer welchen Moat?', "options": ['Kostenvorteil', 'Marke', 'Patente'], "correct": 0, "explain": 'Sie produzieren bzw. liefern dauerhaft guenstiger.'},
            {"q": 'Pipelines und Bahnstrecken sind ein Beispiel fuer ...?', "options": ['Effiziente Skalierung', 'Marke', 'Wechselkosten'], "correct": 0, "explain": 'Der Markt traegt nur wenige Anbieter.'},
            {"q": 'Wenn du keinen Moat-Typ benennen kannst ...?', "options": ['Gibt es vermutlich keinen Moat', 'Ist der Moat riesig', 'Egal'], "correct": 0, "explain": 'Ein echter Burggraben laesst sich konkret benennen.'},
        ],
        "quiz": {"q": 'Visa profitiert vor allem von welchem Moat?', "options": ['Netzwerkeffekt', 'Patenten auf Geldscheine', 'Niedriger Dividende'], "correct": 0, "explain": 'Mehr Karten und Haendler machen das Netz wertvoller.'},
    },
    {
        "key": 'management',
        "title": 'Management & Kapitalallokation',
        "body": 'Ueber Jahrzehnte entscheidet vor allem eine Sache ueber deine Rendite: wie das Management mit jedem verdienten Euro umgeht. Das nennt man **Kapitalallokation**, und sie ist die Kernaufgabe jedes CEO. Es gibt fuenf Hebel: ins Kerngeschaeft reinvestieren, Uebernahmen taetigen, Schulden tilgen, Dividenden zahlen oder Aktien zurueckkaufen. Gute Kapitalallokatoren handeln mit der Disziplin eines Investors: Sie stecken Geld dorthin, wo die Rendite auf das eingesetzte Kapital (**ROIC**) am hoechsten ist, kaufen eigene Aktien nur zurueck, wenn sie guenstig sind, und widerstehen der Versuchung teurer Prestige-Uebernahmen, die oft Wert vernichten. Worauf du achten kannst: Schreibt das Management ehrlich auch ueber Fehler und schwache Jahre, oder gibt es nur Erfolgsmeldungen? Hat das Fuehrungsteam nennenswert **eigenes Geld** in der Aktie (Skin in the Game)? Wurden frueher gegebene Versprechen tatsaechlich eingehalten - vergleiche dazu alte Geschaeftsberichte mit dem, was spaeter wirklich eintrat. Ist die Verguetung an sinnvolle, langfristige Kennzahlen wie ROIC und FCF je Aktie gekoppelt, oder nur an kurzfristigen Umsatz und Aktienkurs? Der **ROIC** im Verhaeltnis zu den Kapitalkosten ist der objektivste Beleg fuer gute Kapitalallokation: Verdient die Firma dauerhaft mehr auf ihr Kapital, als dieses kostet, schafft sie echten Wert; liegt sie darunter, vernichtet Wachstum sogar Wert. Gutes Management ist schwer zu quantifizieren, aber ueber lange Zeitraeume schlaegt kluge Kapitalallokation fast jede kurzfristige Quartals-Story.',
        "faustregel": 'Folge dem Geld: gute Kapitalallokation schlaegt langfristig jede Quartals-Story.',
        "quizzes": [
            {"q": 'Was beschreibt Kapitalallokation?', "options": ['Wie das Management verdiente Gewinne einsetzt', 'Den Aktienkurs', 'Die Mitarbeiterzahl'], "correct": 0, "explain": 'Reinvestieren, tilgen, ausschuetten oder zurueckkaufen.'},
            {"q": "Was bedeutet 'Skin in the Game'?", "options": ['Das Management haelt selbst Aktien', 'Der CEO ist beliebt', 'Die Firma hat Schulden'], "correct": 0, "explain": 'Eigenes Geld im Spiel schafft gleiche Interessen.'},
            {"q": 'Was ist der objektivste Beleg fuer gute Kapitalallokation?', "options": ['ROIC dauerhaft ueber den Kapitalkosten', 'Hoher Umsatz', 'Ein grosses Logo'], "correct": 0, "explain": 'Nur darueber entsteht echter Wert.'},
            {"q": 'Gute Manager kaufen eigene Aktien zurueck, wenn ...?', "options": ['Sie guenstig sind', 'Immer', 'Nie'], "correct": 0, "explain": 'Teure Rueckkaeufe vernichten Wert.'},
            {"q": 'Worauf bei der Verguetung achten?', "options": ['Kopplung an langfristige Kennzahlen', 'Nur an den Quartalskurs', 'Egal'], "correct": 0, "explain": 'Sinnvoll sind ROIC und FCF, nicht nur Umsatz.'},
            {"q": 'Was ist ein Warnzeichen?', "options": ['Teure Prestige-Uebernahmen', 'Ehrliche Fehlerkommunikation', 'Hoher ROIC'], "correct": 0, "explain": 'Solche Deals vernichten oft Wert.'},
        ],
        "quiz": {"q": 'Was beschreibt Kapitalallokation?', "options": ['Wie das Management verdiente Gewinne einsetzt', 'Den Aktienkurs', 'Die Mitarbeiterzahl'], "correct": 0, "explain": 'Reinvestieren, tilgen, ausschuetten oder zurueckkaufen.'},
    },
    {
        "key": 'dcf',
        "title": 'Innerer Wert & DCF',
        "body": "Was ist eine Aktie eigentlich 'wirklich wert', unabhaengig vom Tageskurs? Die theoretisch sauberste Antwort liefert der **innere Wert**: die Summe aller zukuenftigen freien Cashflows, die das Unternehmen je erwirtschaften wird, abgezinst auf heute. Genau das berechnet ein **DCF** (Discounted Cash Flow). Abgezinst wird, weil ein Euro in zehn Jahren weniger wert ist als ein Euro heute - wegen entgangener Zinsen und Risiko. Drei Annahmen treiben jeden DCF: erstens das erwartete Wachstum der Cashflows, zweitens der **Abzinssatz** (die Rendite, die du fuer dein Risiko verlangst, oft 8-10%), drittens der **Endwert** (Terminal Value), der den Grossteil des Ergebnisses ausmacht und annimmt, wie die Firma nach der Detailprognose weiterwaechst. Das Problem: Schon kleine Aenderungen dieser Annahmen veraendern das Ergebnis dramatisch - ein DCF taeuscht eine Praezision vor, die er nicht besitzt. Deshalb behandeln erfahrene Investoren ihn nicht als Wahrsage-Maschine, sondern als **Denkrahmen**. Besonders nuetzlich ist die Umkehrung (Reverse DCF): Statt einen Wert auszurechnen, fragst du, welches Wachstum der heutige Kurs bereits einpreist. Wenn der Markt z.B. 15% Wachstum ueber zwei Jahrzehnte voraussetzen muss, damit der Preis aufgeht, ist das eine sehr hohe Huerde - ein klarer Hinweis, dass viel Optimismus eingebaut ist. Rechne immer mehrere Szenarien (konservativ, basis, optimistisch), arbeite mit vorsichtigen Annahmen und verlange am Ende einen Sicherheitspuffer auf dein Ergebnis, statt dich auf eine einzige Punktlandung zu verlassen.",
        "faustregel": 'Ein DCF liefert keine Wahrheit, sondern zeigt, welche Erwartungen im Kurs stecken.',
        "quizzes": [
            {"q": 'Worauf reagiert ein DCF besonders empfindlich?', "options": ['Auf die Annahmen zu Wachstum und Abzinssatz', 'Auf den Wochentag', 'Auf die Logofarbe'], "correct": 0, "explain": 'Kleine Aenderungen veraendern das Ergebnis stark.'},
            {"q": 'Was ist der innere Wert?', "options": ['Summe abgezinster kuenftiger Cashflows', 'Der gestrige Kurs', 'Die Dividende'], "correct": 0, "explain": 'Alle kuenftigen Free Cashflows auf heute abgezinst.'},
            {"q": 'Warum wird abgezinst?', "options": ['Ein Euro heute ist mehr wert als spaeter', 'Aus Spass', 'Wegen der Steuer'], "correct": 0, "explain": 'Wegen entgangener Zinsen und Risiko.'},
            {"q": 'Was ist ein Reverse-DCF?', "options": ['Man prueft, welches Wachstum der Kurs einpreist', 'Eine Rueckbuchung', 'Ein Chart'], "correct": 0, "explain": 'Zeigt, wie hoch die Markterwartung schon ist.'},
            {"q": 'Wie behandelt man einen DCF am besten?', "options": ['Als Denkrahmen, nicht als exakte Wahrheit', 'Als Garantie', 'Als Glaskugel'], "correct": 0, "explain": 'Er taeuscht eine Praezision vor, die er nicht hat.'},
            {"q": 'Welcher Teil macht oft den Grossteil des Werts aus?', "options": ['Der Endwert (Terminal Value)', 'Das erste Jahr', 'Die Dividende'], "correct": 0, "explain": 'Deshalb ist die Endwert-Annahme so heikel.'},
        ],
        "quiz": {"q": 'Worauf reagiert ein DCF besonders empfindlich?', "options": ['Auf die Annahmen zu Wachstum und Abzinssatz', 'Auf den Wochentag', 'Auf die Logofarbe'], "correct": 0, "explain": 'Kleine Aenderungen veraendern das Ergebnis stark.'},
    },
    {
        "key": 'peer',
        "title": 'Peer-Vergleich & Multiples im Kontext',
        "body": "Eine Bewertungskennzahl fuer sich genommen ist fast bedeutungslos - ein KGV von 22 ist weder gut noch schlecht, bis du einen Vergleichsmassstab hast. Aussagekraft entsteht erst im **Vergleich**, und zwar in zwei Richtungen. Erstens der **Peer-Vergleich**: Stelle die Firma neben echte Wettbewerber derselben Branche mit aehnlichem Geschaeftsmodell und vergleiche KGV, EV/EBITDA, Margen, Wachstum und Verschuldung nebeneinander in einer Tabelle. So siehst du, ob die Aktie relativ zu ihrer Konkurrenz teuer oder guenstig ist. Wichtig: Ein hoeheres Multiple ist voellig gerechtfertigt, wenn die Firma besser ist - hoehere Margen, schnelleres Wachstum, staerkerer Moat, geringeres Risiko. Eine pauschale Aussage 'teuer' ohne Qualitaetsvergleich ist wertlos. Niemals quer ueber Branchen vergleichen: Ein Softwarehaus hat strukturell ein hoeheres KGV als ein Autobauer, weil es kapitalleichter, margenstaerker und besser skalierbar ist - das ist kein Bewertungsfehler, sondern Oekonomie. Zweitens der **historische Vergleich**: Wo handelt die Aktie heute relativ zu ihrem eigenen 5- oder 10-Jahres-Durchschnitt? Notiert sie deutlich unter ihrem ueblichen Bewertungsniveau, lohnt die Frage, ob der Markt uebertrieben pessimistisch ist - oder ob sich das Geschaeft fundamental verschlechtert hat und die niedrigere Bewertung berechtigt ist. Beide Vergleiche zusammen helfen dir, 'optisch teuer' von 'zu Recht hoeher bewertet' und 'optisch billig' von einer echten Value Trap zu unterscheiden. Kontext schlaegt absolute Zahlen - eine Kennzahl ohne Vergleichsrahmen ist nur eine Zahl.",
        "faustregel": 'Multiples vergleichst du nur mit echten Peers und der eigenen Historie - nie quer ueber Branchen.',
        "quizzes": [
            {"q": 'Womit vergleichst du das KGV sinnvoll?', "options": ['Mit Peers und der eigenen Historie', 'Mit einer Zufallsaktie', 'Mit dem Goldpreis'], "correct": 0, "explain": 'Nur echte Vergleiche liefern einen Massstab.'},
            {"q": 'Ein hoeheres Multiple ist gerechtfertigt, wenn ...?', "options": ['Qualitaet, Wachstum oder Margen besser sind', 'Nie', 'Immer'], "correct": 0, "explain": 'Bessere Firmen duerfen teurer sein.'},
            {"q": 'Darf man Multiples quer ueber Branchen vergleichen?', "options": ['Nein, das ist ein Fehler', 'Ja, immer', 'Nur bei Banken'], "correct": 0, "explain": 'Branchen haben strukturell andere Niveaus.'},
            {"q": 'Warum hat Software ein hoeheres KGV als ein Autobauer?', "options": ['Kapitalleichter, margenstaerker, skalierbar', 'Reiner Zufall', 'Wegen Werbung'], "correct": 0, "explain": 'Das ist Oekonomie, kein Bewertungsfehler.'},
            {"q": 'Was zeigt der historische Vergleich?', "options": ['Ob die Aktie ueber/unter ihrem Schnitt handelt', 'Den CEO', 'Die Steuer'], "correct": 0, "explain": 'Gegen den eigenen 5-10-Jahres-Schnitt.'},
            {"q": 'Eine Kennzahl ohne Vergleich ist ...?', "options": ['Nur eine Zahl', 'Eine Garantie', 'Ein Kaufsignal'], "correct": 0, "explain": 'Erst der Kontext macht sie aussagekraeftig.'},
        ],
        "quiz": {"q": 'Womit vergleichst du das KGV sinnvoll?', "options": ['Mit Peers und der eigenen Historie', 'Mit einer Zufallsaktie', 'Mit dem Goldpreis'], "correct": 0, "explain": 'Nur echte Vergleiche liefern einen Massstab.'},
    },
    {
        "key": 'sektor',
        "title": 'Sektor-Spezifika',
        "body": 'Es gibt keine universelle Checkliste, die fuer jede Branche gleich gut funktioniert - die entscheidenden Werttreiber unterscheiden sich fundamental. Bei **Banken und Versicherern** zaehlen klassische Margen wenig; relevant sind Eigenkapitalquote (etwa die Kernkapitalquote), die Qualitaet des Kreditbuchs, die Risikovorsorge und die Zinsmarge - bewertet wird oft ueber das KBV (Kurs-Buchwert) statt das KGV. Bei **Software- und SaaS-Firmen** ist der ausgewiesene Gewinn in der Wachstumsphase oft niedrig oder negativ, obwohl das Geschaeft kerngesund ist - wichtiger sind wiederkehrende Umsaetze (ARR), die Netto-Umsatzbindung (behalten und vergroessern Kunden ihre Vertraege?), die Bruttomarge und der Free Cash Flow. Bei **Zyklikern** (Autobauer, Chemie, Rohstoffe, Stahl) lauert die gefaehrlichste Falle: Genau am Gewinngipfel des Konjunkturzyklus wirkt das KGV optisch niedrig - bricht der Gewinn dann ein, schnellt das KGV hoch und der Kurs faellt; hier hilft eher ein Blick auf normalisierte Gewinne ueber einen ganzen Zyklus. **Versorger und REITs** leben von stabilen, planbaren Cashflows, vertragen hoehere Verschuldung und werden ueber Cashflow-Groessen wie FFO und die Dividendendeckung beurteilt. **Rohstofffoerderer** haengen vom Rohstoffpreis ab, den niemand verlaesslich prognostizieren kann - ihre Gewinne sind kaum planbar. Die Lehre: Verstehe erst das Geschaeftsmodell und die Branchenlogik, und waehle dann die Kennzahlen, die in DIESEM Sektor wirklich den Wert treiben. Eine Kennzahl mechanisch ueber alle Branchen zu legen, fuehrt zu teuren Fehlschluessen.',
        "faustregel": 'Erst die Branche verstehen, dann die richtigen Kennzahlen waehlen.',
        "quizzes": [
            {"q": 'Warum ist ein niedriges KGV bei Zyklikern oft eine Falle?', "options": ['Der Gewinn steht am Hoch und faellt bald', 'Zykliker haben keine Gewinne', 'Das KGV ist verboten'], "correct": 0, "explain": 'Am Gewinngipfel wirkt das KGV optisch niedrig.'},
            {"q": 'Banken bewertet man oft ueber ...?', "options": ['Das KBV (Kurs-Buchwert)', 'Das KUV', 'Den Goldpreis'], "correct": 0, "explain": 'Klassische Margen passen hier schlecht.'},
            {"q": 'Bei SaaS-Firmen ist wichtiger als der Buchgewinn ...?', "options": ['Wiederkehrende Umsaetze und FCF', 'Das Logo', 'Die Dividende'], "correct": 0, "explain": 'ARR und Cashflow zeigen die Substanz.'},
            {"q": 'Versorger und REITs leben von ...?', "options": ['Stabilen, planbaren Cashflows', 'Hohem Risiko', 'Krypto'], "correct": 0, "explain": 'Daher vertragen sie auch mehr Schulden.'},
            {"q": 'Was treibt Rohstofffoerderer vor allem?', "options": ['Der Rohstoffpreis', 'Die Marke', 'Patente'], "correct": 0, "explain": 'Den kann niemand verlaesslich prognostizieren.'},
            {"q": 'Welche Frage kommt vor der Kennzahl?', "options": ['Welche Zahlen treiben in dieser Branche den Wert', 'Wie ist der Kurs heute', 'Wer ist CEO'], "correct": 0, "explain": 'Erst das Geschaeftsmodell verstehen.'},
        ],
        "quiz": {"q": 'Warum ist ein niedriges KGV bei Zyklikern oft eine Falle?', "options": ['Der Gewinn steht am Hoch und faellt bald', 'Zykliker haben keine Gewinne', 'Das KGV ist verboten'], "correct": 0, "explain": 'Am Gewinngipfel wirkt das KGV optisch niedrig.'},
    },
    {
        "key": 'mos',
        "title": 'Sicherheitsmarge (Margin of Safety)',
        "body": 'Jede Analyse - auch eine sehr sorgfaeltige - beruht auf Annahmen ueber eine unsichere Zukunft. Du kannst dich irren, die Welt kann sich aendern, oder schlicht Pech eintreten. Die Antwort auf diese Unsicherheit ist das vielleicht wichtigste Prinzip des Value Investing, gepraegt von Benjamin Graham: die **Sicherheitsmarge** (Margin of Safety). Sie ist der Abstand zwischen deinem geschaetzten inneren Wert und dem Preis, den du tatsaechlich bezahlst. Schaetzt du den fairen Wert einer Aktie auf 100 Euro und kaufst sie fuer 70, hast du 30% Puffer - Raum fuer Schaetzfehler, ein schwaecheres Geschaeftsjahr oder unerwartete Rueckschlaege, ohne gleich Geld zu verlieren. Je unsicherer das Geschaeft (junges Unternehmen, volatile Branche, schwer prognostizierbare Zukunft), desto groesser sollte die geforderte Marge sein; bei sehr stabilen, vorhersehbaren Firmen darf sie kleiner ausfallen. Die Sicherheitsmarge schuetzt nicht vor jedem Verlust, aber sie verschiebt die Wahrscheinlichkeiten klar zu deinen Gunsten und sorgt dafuer, dass ein einzelner Fehler dich nicht ruiniert. Sie hat eine wichtige praktische Konsequenz: **Geduld**. Oft ist eine gute Firma fair oder zu teuer bewertet - dann musst du warten, bis der Markt sie dir mit ausreichendem Abschlag anbietet, was meist in Phasen allgemeiner Angst geschieht. Eine grossartige Firma zu einem ueberhoehten Preis kann ein schlechtes Investment sein; eine gute Firma mit grosser Sicherheitsmarge ist oft das bessere. Lieber auf den richtigen Preis warten, als einer Aktie hinterherzulaufen - der Preis, den du zahlst, bestimmt einen Grossteil deiner spaeteren Rendite.',
        "faustregel": 'Kaufe deutlich unter deinem geschaetzten Wert - der Puffer verzeiht Fehler.',
        "quizzes": [
            {"q": 'Was ist die Sicherheitsmarge?', "options": ['Der Abstand zwischen innerem Wert und gezahltem Preis', 'Die Dividende', 'Die Brokergebuehr'], "correct": 0, "explain": 'Der Puffer fuer Fehler und Pech.'},
            {"q": 'Wert 100 EUR, Preis 70 EUR - wie viel Puffer?', "options": ['30%', '0%', '70%'], "correct": 0, "explain": '30 EUR Abschlag auf den geschaetzten Wert.'},
            {"q": 'Je unsicherer das Geschaeft ...?', "options": ['Desto groesser sollte die Marge sein', 'Desto kleiner', 'Egal'], "correct": 0, "explain": 'Mehr Unsicherheit verlangt mehr Puffer.'},
            {"q": 'Wer praegte das Prinzip der Sicherheitsmarge?', "options": ['Benjamin Graham', 'Niemand', 'Ein Bot'], "correct": 0, "explain": 'Der Begruender des Value Investing.'},
            {"q": 'Was ist die praktische Konsequenz?', "options": ['Geduld - auf den richtigen Preis warten', 'Schnell kaufen', 'Nie kaufen'], "correct": 0, "explain": 'Oft muss man auf einen Abschlag warten.'},
            {"q": 'Eine grossartige Firma zu ueberhoehtem Preis ...?', "options": ['Kann ein schlechtes Investment sein', 'Ist immer gut', 'Ist risikolos'], "correct": 0, "explain": 'Der Einstandspreis bestimmt einen Grossteil der Rendite.'},
        ],
        "quiz": {"q": 'Was ist die Sicherheitsmarge?', "options": ['Der Abstand zwischen innerem Wert und gezahltem Preis', 'Die Dividende', 'Die Brokergebuehr'], "correct": 0, "explain": 'Der Puffer fuer Fehler und Pech.'},
    },
    {
        "key": 'bias',
        "title": 'Psychologie & typische Fehler',
        "body": "Die groesste Renditebremse sitzt selten in der Bilanz - sie sitzt im eigenen Kopf. Die Verhaltensoekonomie hat eine Reihe systematischer Denkfehler dokumentiert, die Anleger immer wieder Geld kosten. Der **Bestaetigungsfehler** (Confirmation Bias): Hast du eine Aktie erst einmal ins Herz geschlossen, suchst du unbewusst nur noch Argumente, die deine These stuetzen, und blendest Gegenargumente aus. Die **Verlustaversion**: Verluste schmerzen psychologisch etwa doppelt so stark, wie gleich grosse Gewinne erfreuen - die Folge ist, dass viele Verlierer-Positionen viel zu lange gehalten ('das kommt schon wieder') und Gewinner zu frueh verkauft werden. Der **Herdentrieb**: Steigt eine Aktie und alle reden darueber, wird Kaufen verlockend - oft genau dann, wenn sie am teuersten ist (FOMO, die Angst, etwas zu verpassen). Der **Recency Bias**: Die juengste Kursentwicklung wird unbewusst in die Zukunft verlaengert, in Boomphasen zu optimistisch, in Crashs zu pessimistisch. Dazu kommen der **Ankereffekt** (man klammert sich an den frueheren Kaufpreis) und **Selbstueberschaetzung** nach ein paar Gewinnen. Die wirksamsten Gegenmittel sind Prozesse, keine guten Vorsaetze: Schreibe vor jedem Kauf deine **These und konkrete Verkaufsgruende** auf und definiere ausdruecklich, welche Entwicklung dich widerlegen wuerde (ein 'Pre-Mortem'). Pruefe das Unternehmen, nicht den Kurs. Fuehre ein Entscheidungs-Tagebuch, um spaeter ehrlich zu sehen, ob deine Annahmen stimmten. Das von dieser App erzeugte Investment-Memo zwingt dich genau zu dieser Disziplin - es macht aus einer Bauchentscheidung eine nachpruefbare These, die du spaeter ueberpruefen kannst.",
        "faustregel": 'Schreib deine These vorab auf - das schuetzt vor Bauchentscheidungen im Stress.',
        "quizzes": [
            {"q": 'Was ist der Bestaetigungsfehler?', "options": ['Man sucht nur Infos, die die eigene Meinung stuetzen', 'Man rechnet immer falsch', 'Man kauft nur teuer'], "correct": 0, "explain": 'Gegenargumente werden ausgeblendet.'},
            {"q": 'Wozu fuehrt Verlustaversion oft?', "options": ['Verlierer zu lange halten', 'Gewinner zu lange halten', 'Nichts'], "correct": 0, "explain": 'Verluste schmerzen staerker, als Gewinne erfreuen.'},
            {"q": 'Was beschreibt Herdentrieb / FOMO?', "options": ['Kaufen, weil alle kaufen', 'Verkaufen aus Vernunft', 'Sparen'], "correct": 0, "explain": 'Oft genau am teuersten Punkt.'},
            {"q": 'Was ist der Recency Bias?', "options": ['Die juengste Kursbewegung in die Zukunft fortschreiben', 'Alte Daten zu nutzen ist immer richtig', 'Zufall'], "correct": 0, "explain": 'Boom wirkt zu optimistisch, Crash zu pessimistisch.'},
            {"q": 'Was ist das beste Gegenmittel?', "options": ['These und Verkaufsgruende vorab aufschreiben', 'Reines Bauchgefuehl', 'Forenposts'], "correct": 0, "explain": 'Prozesse schlagen gute Vorsaetze.'},
            {"q": 'Was zwingt dich zur Disziplin?', "options": ['Das Investment-Memo', 'Der Chart', 'Werbung'], "correct": 0, "explain": 'Es macht aus dem Bauch eine nachpruefbare These.'},
        ],
        "quiz": {"q": 'Was ist der Bestaetigungsfehler?', "options": ['Man sucht nur Infos, die die eigene Meinung stuetzen', 'Man rechnet immer falsch', 'Man kauft nur teuer'], "correct": 0, "explain": 'Gegenargumente werden ausgeblendet.'},
    },
    {
        "key": 'diversifikation',
        "title": 'Diversifikation & Positionsgroesse',
        "body": 'Selbst die sorgfaeltigste Einzelanalyse kann scheitern - durch Betrug, eine ploetzliche Disruption, einen Managementfehler oder schlicht Pech. Weil du die Zukunft nie sicher kennst, ist **Diversifikation** kein Eingestaendnis von Schwaeche, sondern intelligenter Umgang mit Unsicherheit: Du verteilst dein Kapital so, dass kein einzelnes Ereignis dein Depot ruinieren kann. Streuung wirkt auf mehreren Ebenen - ueber einzelne Aktien, ueber Branchen, ueber Laender und ueber Anlageklassen. Eng damit verbunden ist die **Positionsgroesse**: Wie viel Prozent deines Depots steckst du in eine einzelne Idee? Sie sollte sich nach zwei Faktoren richten - deiner Ueberzeugung UND dem Risiko. Eine spekulative, schwer einschaetzbare Position haelt man bewusst klein; eine hochwertige Firma mit grosser Sicherheitsmarge darf groesser ausfallen. Viele Anleger legen vorab eine Obergrenze fest (etwa maximal 5-10% pro Einzelwert), damit ein Totalausfall verkraftbar bleibt. Ein haeufiger Trugschluss ist die **Schein-Diversifikation**: Zehn verschiedene Tech-Aktien sind kaum Streuung, weil sie stark **korreliert** sind - faellt der Sektor, fallen sie fast alle gemeinsam. Echte Diversifikation kombiniert Werte, die nicht im Gleichschritt laufen. Es gibt aber auch ein Gegenargument (Buffett): Zu breite Streuung verwaessert deine besten Ideen und ist vor allem ein Schutz vor Unwissen - wer wirklich tief versteht, was er besitzt, braucht weniger davon. Der vernuenftige Mittelweg fuer die meisten Privatanleger: ausreichend streuen, um nicht ruiniert zu werden, aber fokussiert genug, dass gute Entscheidungen auch spuerbar wirken.',
        "faustregel": 'Streue ueber Branchen und begrenze jede Einzelposition - kein Einzelwert darf dich ruinieren.',
        "quizzes": [
            {"q": 'Warum sind zehn Tech-Aktien keine echte Diversifikation?', "options": ['Sie sind stark korreliert und fallen gemeinsam', 'Es sind zu wenige', 'Tech ist verboten'], "correct": 0, "explain": 'Faellt der Sektor, faellt fast alles zugleich.'},
            {"q": 'Wonach richtet sich die Positionsgroesse?', "options": ['Nach Ueberzeugung UND Risiko', 'Nur nach Bauchgefuehl', 'Nur nach dem Kurs'], "correct": 0, "explain": 'Spekulatives klein, Hochwertiges darf groesser sein.'},
            {"q": 'Diversifikation ist vor allem ...?', "options": ['Intelligenter Umgang mit Unsicherheit', 'Ein Zeichen von Schwaeche', 'Glueck'], "correct": 0, "explain": 'Kein Einzelereignis soll dich ruinieren.'},
            {"q": 'Welche Obergrenze pro Einzelwert ist ueblich?', "options": ['Etwa 5-10%', '90%', '0%'], "correct": 0, "explain": 'Damit ein Totalausfall verkraftbar bleibt.'},
            {"q": 'Was ist Buffetts Gegenargument?', "options": ['Zu breite Streuung verwaessert die besten Ideen', 'Streuung ist nutzlos', 'Nie streuen'], "correct": 0, "explain": 'Wer tief versteht, braucht weniger Streuung.'},
            {"q": 'Was ist ein vernuenftiger Mittelweg?', "options": ['Streuen, aber fokussiert genug', 'Alles auf eine Aktie', '200 Aktien'], "correct": 0, "explain": 'Gute Entscheidungen sollen spuerbar wirken.'},
        ],
        "quiz": {"q": 'Warum sind zehn Tech-Aktien keine echte Diversifikation?', "options": ['Sie sind stark korreliert und fallen gemeinsam', 'Es sind zu wenige', 'Tech ist verboten'], "correct": 0, "explain": 'Faellt der Sektor, faellt fast alles zugleich.'},
    },
    {
        "key": 'anlageklassen',
        "title": 'Portfolio: Anlageklassen & Asset-Allokation',
        "body": "Ein Portfolio ist mehr als eine Liste von Lieblingsaktien - es ist eine bewusste Mischung von Anlageklassen mit unterschiedlichem Charakter. Die wichtigsten: **Aktien** bieten langfristig die hoechste erwartete Rendite, schwanken aber stark und koennen in Krisen die Haelfte ihres Werts verlieren. **Anleihen** (Staats- und Unternehmensanleihen) liefern planbare Zinsen, schwanken weniger und wirken oft als Stabilisator, bringen dafuer geringere Renditen. **Bargeld und Tagesgeld** geben Sicherheit und Liquiditaet - wichtig fuer Notfaelle und um in Krisen handlungsfaehig zu bleiben -, verlieren aber durch Inflation real an Wert. **Rohstoffe und Gold** werfen keinen Cashflow ab, koennen aber als Inflationsschutz und Krisenversicherung dienen. **Immobilien** (direkt oder ueber REITs) verbinden laufende Ertraege mit Inflationsschutz. **Krypto** ist hochspekulativ und extrem volatil. Der zentrale Begriff ist die **Asset-Allokation** - die prozentuale Aufteilung auf diese Klassen. Klassische Studien deuten darauf hin, dass die Allokation den groessten Teil der Schwankungen des langfristigen Ergebnisses erklaert, oft mehr als die Auswahl einzelner Titel. Die richtige Mischung haengt von deinem **Anlagehorizont** (wann brauchst du das Geld?) und deiner **Risikotragfaehigkeit** ab - sowohl finanziell als auch emotional, also wie viel Schwankung du aushaeltst, ohne in Panik zu verkaufen. Eine alte Faustformel lautete '110 minus Lebensalter = Aktienquote', heute eher als grober Anhaltspunkt denn als feste Regel zu verstehen. Wichtig: Das ist Bildung, keine Empfehlung fuer deine konkrete Quote - die haengt allein von deiner persoenlichen Lage ab und sollte gut ueberlegt sein.",
        "faustregel": 'Die Aufteilung auf Anlageklassen praegt dein Ergebnis staerker als die einzelne Aktienwahl.',
        "quizzes": [
            {"q": 'Was beschreibt die Asset-Allokation?', "options": ['Die Aufteilung des Geldes auf Anlageklassen', 'Einen Aktienkurs', 'Die Ordergebuehr'], "correct": 0, "explain": 'Aktien, Anleihen, Cash, Rohstoffe - wie du sie mischst.'},
            {"q": 'Welche Klasse ist am sichersten/liquidesten?', "options": ['Bargeld / Tagesgeld', 'Aktien', 'Krypto'], "correct": 0, "explain": 'Dafuer verliert es real durch Inflation.'},
            {"q": 'Wovon haengt die richtige Mischung ab?', "options": ['Vom Horizont und der Risikotragfaehigkeit', 'Vom Wetter', 'Vom Logo'], "correct": 0, "explain": 'Je laenger und gelassener, desto mehr Aktien tragbar.'},
            {"q": 'Was erklaert laut Studien viel vom langfristigen Ergebnis?', "options": ['Die Allokation', 'Die Aktienauswahl allein', 'Glueck'], "correct": 0, "explain": 'Oft mehr als die Auswahl einzelner Titel.'},
            {"q": 'Was liefert Gold?', "options": ['Keinen Cashflow, evtl. Inflationsschutz', 'Garantierte Zinsen', 'Eine Dividende'], "correct": 0, "explain": 'Es wirft keinen laufenden Ertrag ab.'},
            {"q": 'Risikotragfaehigkeit ist ...?', "options": ['Finanziell UND emotional', 'Nur finanziell', 'Egal'], "correct": 0, "explain": 'Auch: Wie viel Schwankung haeltst du aus, ohne zu verkaufen?'},
        ],
        "quiz": {"q": 'Was beschreibt die Asset-Allokation?', "options": ['Die Aufteilung des Geldes auf Anlageklassen', 'Einen Aktienkurs', 'Die Ordergebuehr'], "correct": 0, "explain": 'Aktien, Anleihen, Cash, Rohstoffe - wie du sie mischst.'},
    },
    {
        "key": 'instrumente',
        "title": 'Portfolio: Finanzinstrumente im Ueberblick',
        "body": 'Ein neutraler Ueberblick, welche Bausteine es gibt - ausdruecklich keine Empfehlung, was du nutzen solltest. Eine **Aktie** ist ein Eigentumsanteil an einer Firma; du partizipierst an Kurs und Dividende, traegst aber das volle unternehmerische Risiko bis zum Totalverlust bei Insolvenz. Ein **ETF** (boersengehandelter Indexfonds) buendelt viele Wertpapiere in einem Produkt und bildet meist passiv einen Index nach - so erreichst du mit einem einzigen Kauf breite Streuung zu niedrigen Kosten. Ein klassischer **aktiver Fonds** verfolgt dasselbe Buendelungsprinzip, versucht aber, den Markt durch Auswahl zu schlagen, und kostet mehr. Eine **Anleihe** ist ein Kredit, den du einem Staat oder Unternehmen gibst; du erhaeltst Zinsen, das Hauptrisiko ist der Zahlungsausfall des Schuldners sowie Kursverluste bei steigenden Zinsen. **Derivate** - dazu zaehlen Optionen, Futures, Zertifikate, Optionsscheine und CFDs - sind abgeleitete Produkte, deren Wert von einem Basiswert abhaengt. Sie sind oft **gehebelt**: Schon kleine Bewegungen des Basiswerts fuehren zu grossen Gewinnen oder Verlusten, und bei manchen (etwa CFDs oder Futures) kannst du sogar mehr verlieren als deinen Einsatz oder Nachschuss leisten muessen. Sie sind komplex, haben oft versteckte Kosten und sind fuer Einsteiger in aller Regel ungeeignet. **Krypto-Assets** sind hochvolatil, stark spekulativ und regulatorisch noch jung. Die Grundregel ueber alle Produkte hinweg: Je komplexer und je staerker gehebelt ein Produkt ist, desto groesser das Risiko - und desto wichtiger, dass du es vollstaendig verstehst, bevor es ueberhaupt in Frage kommt. Was du nicht in einem einzigen Satz erklaeren kannst, solltest du nicht kaufen.',
        "faustregel": 'Investiere nie in ein Produkt, das du nicht in einem Satz erklaeren kannst - besonders bei Hebel.',
        "quizzes": [
            {"q": 'Was ist typisch fuer gehebelte Derivate?', "options": ['Verluste koennen vervielfacht werden', 'Sie sind risikolos', 'Sie zahlen garantierte Zinsen'], "correct": 0, "explain": 'Hebel verstaerkt Gewinne UND Verluste.'},
            {"q": 'Was ist ein ETF?', "options": ['Ein Korb vieler Wertpapiere, meist passiv', 'Eine Einzelaktie', 'Eine Anleihe'], "correct": 0, "explain": 'Breite Streuung in einem Produkt.'},
            {"q": 'Was ist eine Anleihe?', "options": ['Ein Kredit an Staat oder Firma', 'Ein Firmenanteil', 'Ein Derivat'], "correct": 0, "explain": 'Du bekommst Zinsen.'},
            {"q": 'Was ist das Hauptrisiko einer Aktie?', "options": ['Totalverlust bei Insolvenz', 'Garantierter Gewinn', 'Kein Risiko'], "correct": 0, "explain": 'Du traegst das volle Unternehmerrisiko.'},
            {"q": 'Bei manchen Derivaten (CFDs/Futures) gilt ...?', "options": ['Mehr als der Einsatz ist verlierbar', 'Nie ein Verlust', 'Immer Gewinn'], "correct": 0, "explain": 'Teils Nachschusspflicht ueber den Einsatz hinaus.'},
            {"q": 'Was ist die Grundregel?', "options": ['Nichts kaufen, was man nicht erklaeren kann', 'Alles kaufen', 'Nur mit Hebel'], "correct": 0, "explain": 'Besonders bei komplexen, gehebelten Produkten.'},
        ],
        "quiz": {"q": 'Was ist typisch fuer gehebelte Derivate?', "options": ['Verluste koennen vervielfacht werden', 'Sie sind risikolos', 'Sie zahlen garantierte Zinsen'], "correct": 0, "explain": 'Hebel verstaerkt Gewinne UND Verluste.'},
    },
    {
        "key": 'etf_aktiv',
        "title": 'Portfolio: ETF & Fonds - passiv vs. aktiv',
        "body": 'Eine der grundlegendsten Weichenstellungen fuer Privatanleger lautet: selbst auswaehlen oder den Markt einfach abbilden? **Passive ETFs** bilden einen Index nach - etwa einen breiten Welt-Index mit Tausenden Firmen aus vielen Laendern. Sie sind guenstig (oft 0,1-0,3% laufende Kosten pro Jahr), transparent, breit gestreut und erfordern kein Stockpicking. **Aktive Fonds** dagegen werden von einem Manager gesteuert, der versucht, durch Auswahl besser als der Markt zu sein. Das Problem: Die ueberwiegende Mehrheit der aktiven Fonds schafft es ueber lange Zeitraeume nach Kosten nicht, ihren Vergleichsindex zu schlagen - die hoeheren Gebuehren fressen den Vorsprung auf, und die wenigen Gewinner sind im Voraus kaum zu identifizieren. Das spricht fuer viele Anleger fuer einen breiten Index-ETF als Fundament. Fundamentalanalyse und ETFs sind dabei kein Widerspruch, sondern lassen sich kombinieren: Beim **Kern-Satellit-Ansatz** bildet ein breiter, guenstiger ETF den stabilen **Kern** des Depots, waehrend einzelne, selbst gruendlich analysierte Aktien als **Satelliten** gezielt ergaenzt werden - dort, wo du wirklich eine Ueberzeugung hast. So verbindest du die Sicherheit breiter Streuung mit der Chance der eigenen Analyse. Worauf du bei ETFs achten solltest: die **TER** (Gesamtkostenquote), die Fondsgroesse und Liquiditaet (sehr kleine ETFs koennen geschlossen werden), die Replikationsmethode (physisch vs. synthetisch) und ob er **ausschuettend** (zahlt Dividenden aus) oder **thesaurierend** (legt sie automatisch wieder an) ist. Welche Mischung zu dir passt, haengt von deiner Zeit, deinem Wissen und deiner Risikoneigung ab - die App liefert dir das Wissen und die Werkzeuge, die Entscheidung bleibt deine.',
        "faustregel": 'Ein breiter, guenstiger ETF als Kern - selbst analysierte Aktien als bewusste Ergaenzung.',
        "quizzes": [
            {"q": 'Was bedeutet ein passiver ETF?', "options": ['Er bildet einen Index nach', 'Ein Manager handelt taeglich', 'Er ist verlustfrei'], "correct": 0, "explain": 'Er folgt einem Index, statt aktiv auszuwaehlen.'},
            {"q": 'Schlagen aktive Fonds den Markt langfristig?', "options": ['Die Mehrheit nicht (nach Kosten)', 'Immer', 'Garantiert'], "correct": 0, "explain": 'Die hoeheren Gebuehren fressen den Vorsprung.'},
            {"q": 'Was ist der Kern-Satellit-Ansatz?', "options": ['Breiter ETF als Kern, Einzelaktien als Satelliten', 'Nur Hebelprodukte', 'Nur Krypto'], "correct": 0, "explain": 'Sicherheit der Streuung plus eigene Analyse.'},
            {"q": "Was bedeutet 'thesaurierend'?", "options": ['Ertraege werden automatisch wieder angelegt', 'Ertraege werden ausgezahlt', 'Ertraege verfallen'], "correct": 0, "explain": 'Gegenteil von ausschuettend.'},
            {"q": 'Worauf bei ETFs achten?', "options": ['TER, Groesse, Replikationsmethode', 'Logo', 'CEO'], "correct": 0, "explain": 'Auch ausschuettend vs. thesaurierend.'},
            {"q": 'Was ist ein Vorteil passiver ETFs?', "options": ['Guenstig und breit gestreut', 'Teuer', 'Riskant durch Hebel'], "correct": 0, "explain": 'Oft 0,1-0,3% laufende Kosten.'},
        ],
        "quiz": {"q": 'Was bedeutet ein passiver ETF?', "options": ['Er bildet einen Index nach', 'Ein Manager handelt taeglich', 'Er ist verlustfrei'], "correct": 0, "explain": 'Er folgt einem Index, statt aktiv auszuwaehlen.'},
    },
    {
        "key": 'kosten_steuern',
        "title": 'Portfolio: Kosten, Gebuehren & Steuern',
        "body": 'Kosten sind einer der wenigen Faktoren, die du fast vollstaendig kontrollieren kannst - und sie wirken ueber Jahrzehnte wie ein staendiger Gegenwind durch den Zinseszinseffekt. Ein Beispiel verdeutlicht es: Bei 7% Bruttorendite ueber 30 Jahre macht es einen gewaltigen Unterschied, ob jaehrlich 0,2% oder 1,5% an Kosten abgehen - am Ende koennen das Zehntausende Euro sein. Achte deshalb auf mehrere Kostenarten: **Ordergebuehren und Spreads** beim Kauf und Verkauf (haeufiges Traden summiert sich schnell), die **laufenden Kosten (TER)** von Fonds und ETFs sowie eventuelle **Depotgebuehren**. Guenstige Broker und kostenarme Index-Produkte sind hier ein direkter, fast sicherer Renditevorteil. Beim Thema **Steuern** hier nur das allgemeine Prinzip (kein Steuerberatungs-Rat und ohne Gewaehr): In Deutschland faellt auf Kursgewinne und Ausschuettungen in der Regel die **Abgeltungsteuer** von 25% plus Solidaritaetszuschlag und gegebenenfalls Kirchensteuer an, also rund 26-28%. Es gibt einen jaehrlichen **Sparer-Pauschbetrag** (Freibetrag), bis zu dem Kapitalertraege steuerfrei bleiben - ueber einen Freistellungsauftrag bei der Bank nutzbar. Bei thesaurierenden Fonds greift die **Vorabpauschale**, eine Art jaehrliche Mindestbesteuerung auf nicht ausgeschuettete Gewinne. Steuerstundung ist ein unterschaetzter Vorteil: Wer selten verkauft, laesst Gewinne unversteuert weiterarbeiten und profitiert laenger vom Zinseszins. Deine konkrete Situation - Freibetraege, Verlustverrechnung, auslaendische Quellensteuer - klaerst du am besten mit einem Steuerberater. Die Kernbotschaft bleibt: Am Ende zaehlt die **Nettorendite** nach Kosten und Steuern, nicht die schoene Bruttorendite auf dem Werbeprospekt.',
        "faustregel": 'Niedrige Kosten sind eine der wenigen fast sicheren Renditequellen.',
        "quizzes": [
            {"q": 'Warum sind laufende Kosten so wichtig?', "options": ['Sie schmaelern die Rendite ueber viele Jahre', 'Einmalig und egal', 'Sie erhoehen die Dividende'], "correct": 0, "explain": 'Durch Zinseszins kostet schon 1% p.a. viel.'},
            {"q": 'Wie hoch ist die Abgeltungsteuer in DE grob?', "options": ['25% plus Soli (rund 26-28%)', '50%', '0%'], "correct": 0, "explain": 'Plus ggf. Kirchensteuer.'},
            {"q": 'Was ist der Sparer-Pauschbetrag?', "options": ['Ein Steuerfreibetrag fuer Kapitalertraege', 'Eine Gebuehr', 'Ein Hebel'], "correct": 0, "explain": 'Per Freistellungsauftrag bei der Bank nutzbar.'},
            {"q": 'Was greift bei thesaurierenden Fonds?', "options": ['Die Vorabpauschale', 'Keine Steuer', 'Doppelte Steuer'], "correct": 0, "explain": 'Eine Art jaehrliche Mindestbesteuerung.'},
            {"q": 'Was ist ein Vorteil seltener Verkaeufe?', "options": ['Steuerstundung - Gewinne arbeiten weiter', 'Hoehere Gebuehren', 'Nichts'], "correct": 0, "explain": 'Laenger vom Zinseszins profitieren.'},
            {"q": 'Was zaehlt am Ende?', "options": ['Die Nettorendite nach Kosten und Steuern', 'Die Bruttorendite', 'Das Werbeversprechen'], "correct": 0, "explain": 'Netto, nicht brutto.'},
        ],
        "quiz": {"q": 'Warum sind laufende Kosten so wichtig?', "options": ['Sie schmaelern die Rendite ueber viele Jahre', 'Einmalig und egal', 'Sie erhoehen die Dividende'], "correct": 0, "explain": 'Durch Zinseszins kostet schon 1% p.a. viel.'},
    },
    {
        "key": 'sparplan',
        "title": 'Portfolio: Sparplan, Cost-Average & Horizont',
        "body": "Einer der groessten Vorteile von Privatanlegern ist Zeit - und ein **Sparplan** macht sie systematisch nutzbar. Dabei investierst du regelmaessig (z.B. monatlich) einen festen Betrag, unabhaengig vom aktuellen Kursniveau. Der **Cost-Average-Effekt** (Durchschnittskosteneffekt) sorgt dafuer, dass du bei niedrigen Kursen automatisch mehr Anteile kaufst und bei hohen Kursen weniger - das glaettet deinen Einstiegspreis und nimmt die Emotion aus der Frage 'Ist jetzt der richtige Zeitpunkt?'. Genau diese Frage fuehrt naemlich zu den teuersten Fehlern: Der Versuch, Tief- und Hochpunkte zu erwischen (**Market Timing**), schadet den meisten Anlegern eher, weil die staerksten Boersentage oft direkt nach den schlimmsten kommen - wer dann nicht investiert ist, verpasst die Erholung. Das gefluegelte Wort dazu: 'Time in the market beats timing the market'. Der zweite Schluesselbegriff ist der **Anlagehorizont**. Geld, das du in ein bis zwei Jahren sicher brauchst (Notgroschen, geplante Anschaffungen), gehoert nicht in schwankende Aktien, sondern auf ein sicheres Konto - bei kurzem Horizont kann ein Crash dich zum Verkauf im falschen Moment zwingen. Je laenger dein Horizont, desto besser kannst du Schwankungen aussitzen und desto staerker wirkt der **Zinseszins**: Reinvestierte Ertraege erwirtschaften selbst wieder Ertraege, was ueber Jahrzehnte exponentiell wirkt und den groessten Teil des Endvermoegens ausmachen kann. Trenne deshalb klar zwischen kurzfristig benoetigtem Geld und langfristigem Anlagekapital - und bleib dann diszipliniert dabei, gerade in turbulenten Phasen, in denen das Aufgeben am verlockendsten erscheint.",
        "faustregel": 'Regelmaessig investieren und dranbleiben schlaegt das Erraten des perfekten Zeitpunkts.',
        "quizzes": [
            {"q": 'Was bewirkt ein regelmaessiger Sparplan?', "options": ['Cost-Average glaettet den Einstiegspreis', 'Garantiert Gewinne', 'Vermeidet jede Steuer'], "correct": 0, "explain": 'Feste Betraege kaufen mal mehr, mal weniger Anteile.'},
            {"q": 'Was bringt Market Timing den meisten Anlegern?', "options": ['Es schadet eher', 'Es funktioniert immer', 'Es ist risikolos'], "correct": 0, "explain": 'Die besten Tage folgen oft direkt auf die schlimmsten.'},
            {"q": 'Wohin gehoert Geld, das du in 1-2 Jahren brauchst?', "options": ['Nicht in schwankende Aktien', 'In Hebelprodukte', 'In Krypto'], "correct": 0, "explain": 'Bei kurzem Horizont droht der Notverkauf.'},
            {"q": 'Je laenger der Anlagehorizont ...?', "options": ['Desto staerker wirkt der Zinseszins', 'Desto schlechter', 'Egal'], "correct": 0, "explain": 'Ertraege erwirtschaften selbst wieder Ertraege.'},
            {"q": "Was meint 'Time in the market beats timing the market'?", "options": ['Dranbleiben schlaegt das Erraten des Zeitpunkts', 'Schnell raus', 'Nie investieren'], "correct": 0, "explain": 'Dauerhaftes Investiertsein hat historisch besser funktioniert.'},
            {"q": 'Was sollte klar getrennt sein?', "options": ['Notgroschen und langfristiges Anlagegeld', 'Nichts', 'Aktien und ETFs nie zusammen'], "correct": 0, "explain": 'Verschiedene Toepfe fuer verschiedene Zwecke.'},
        ],
        "quiz": {"q": 'Was bewirkt ein regelmaessiger Sparplan?', "options": ['Cost-Average glaettet den Einstiegspreis', 'Garantiert Gewinne', 'Vermeidet jede Steuer'], "correct": 0, "explain": 'Feste Betraege kaufen mal mehr, mal weniger Anteile.'},
    },
    {
        "key": 'portfolio_pflege',
        "title": 'Portfolio: Rebalancing & Risiko steuern',
        "body": 'Ein gutes Portfolio braucht Pflege, aber kein staendiges Herumdoktern - die Kunst liegt zwischen Vernachlaessigung und Hyperaktivitaet. Mit der Zeit verschieben sich die Gewichte von selbst: Gut gelaufene Positionen oder Anlageklassen werden immer groesser und dominieren irgendwann dein Depot - oft genau die, die zuletzt am teuersten geworden sind. **Rebalancing** bringt die Gewichte regelbasiert wieder naeher an deine Zielallokation, typischerweise einmal jaehrlich oder wenn eine Position eine vorher festgelegte Bandbreite verlaesst (etwa mehr als 5 Prozentpunkte ueber Ziel). Das wirkt automatisch antizyklisch und diszipliniert: Du reduzierst tendenziell, was teuer geworden ist, und stockst auf, was guenstig ist - das genaue Gegenteil des emotionalen Herdenverhaltens. Gleichzeitig begrenzt es **Klumpenrisiken**, also die Gefahr, dass eine einzelne Aktie oder Branche unbemerkt zum Schwergewicht wird, das dein ganzes Depot dominiert. Beachte, dass Verkaeufe Steuern und Gebuehren ausloesen koennen - in Sparplaenen laesst sich Rebalancing oft eleganter ueber die Verteilung neuer Einzahlungen erreichen, ohne etwas zu verkaufen. Genauso wichtig wie das mechanische Rebalancing ist die laufende **These-Pruefung**: Stimmt der urspruengliche Grund, warum du eine Aktie besitzt, noch? Hat sich der Moat, die Wettbewerbslage oder das Management verschlechtert? Reagiere auf solche fundamentalen Veraenderungen - nicht auf den taeglichen Kurslaerm. Lege vorab fest, wie gross eine Einzelposition maximal werden darf und wie viel Gesamtschwankung du aushaeltst. Die Rebalancing-Funktion dieser App ist dabei ausdruecklich ein neutrales **Rechenwerkzeug**, das nur auf deine eigenen Vorgaben rechnet - sie ist keine Anlageberatung und gibt keine Kauf- oder Verkaufsempfehlung.',
        "faustregel": 'Selten, regelbasiert rebalancieren - These pruefen statt auf Kurse reagieren.',
        "quizzes": [
            {"q": 'Was ist das Ziel von Rebalancing?', "options": ['Das Portfolio wieder an die Zielgewichtung annaehern', 'Moeglichst oft traden', 'Die beste Aktie finden'], "correct": 0, "explain": 'Es fuehrt die Gewichte zurueck ans Ziel.'},
            {"q": 'Wie wirkt Rebalancing?', "options": ['Antizyklisch - teuer reduzieren, guenstig aufstocken', 'Prozyklisch', 'Rein zufaellig'], "correct": 0, "explain": 'Das Gegenteil des Herdenverhaltens.'},
            {"q": 'Wie oft rebalanciert man typischerweise?', "options": ['Selten, z.B. einmal jaehrlich', 'Taeglich', 'Nie'], "correct": 0, "explain": 'Oder bei Verlassen einer Bandbreite.'},
            {"q": 'Was begrenzt Rebalancing?', "options": ['Klumpenrisiken', 'Die Rendite', 'Die Dividende'], "correct": 0, "explain": 'Keine Einzelposition soll alles dominieren.'},
            {"q": 'Worauf solltest du reagieren?', "options": ['Auf fundamentale Veraenderungen, nicht den Tageskurs', 'Auf jeden Tick', 'Auf Forenposts'], "correct": 0, "explain": 'Pruefe, ob die These noch stimmt.'},
            {"q": 'Was ist die Rebalancing-Funktion der App?', "options": ['Ein neutrales Rechenwerkzeug', 'Anlageberatung', 'Ein Kaufsignal'], "correct": 0, "explain": 'Sie rechnet nur auf deine eigenen Vorgaben.'},
        ],
        "quiz": {"q": 'Was ist das Ziel von Rebalancing?', "options": ['Das Portfolio wieder an die Zielgewichtung annaehern', 'Moeglichst oft traden', 'Die beste Aktie finden'], "correct": 0, "explain": 'Es fuehrt die Gewichte zurueck ans Ziel.'},
    },
    {
        "key": 'anwenden',
        "title": 'So liest du die App & analysierst selbst',
        "body": 'Jetzt fuegt sich alles zusammen - hier ist der praktische Workflow von der ersten Eingabe bis zur fertigen Entscheidung. Schritt 1: Gib in der **Einzelanalyse** den Ticker einer Firma ein, die du verstehst oder verstehen willst. Schritt 2: Lies den **Quality-Score** - er buendelt Profitabilitaet (Margen), Kapitalrendite (ROE/ROCE), Bilanzgesundheit und Wachstum zu einem schnellen Qualitaetsurteil. Ein hoher Score heisst: starke Geldmaschine, solide finanziert, waechst gesund. Schritt 3: Pruefe **PEG und Value-Score** - ist der Preis im Verhaeltnis zu Qualitaet und Wachstum fair, oder zahlst du zu viel? Schritt 4: Das **Fazit** verdichtet beides zu einer ersten Einordnung (etwa attraktiv / fair / Vorsicht) - aber es ist ein Ausgangspunkt, kein Endurteil. Schritt 5: Wechsle in den Tab **Qualitativ** und arbeite die Vorlagen durch - benenne den Moat-Typ konkret, liste die groessten Risiken und denke in Szenarien (was, wenn die These nicht aufgeht?). Diese Punkte stehen in keiner Tabelle und entscheiden trotzdem ueber den langfristigen Erfolg. Schritt 6: Im Tab **Gegenpruefen** kontrollierst du auffaellige oder zu schoene Kennzahlen gegen den Original-Geschaeftsbericht - Yahoo-Daten sind praktisch, aber nicht audit-grade, und Fehler oder Sondereffekte kommen vor. Schritt 7: Erzeuge das **Investment-Memo** - es zwingt dich, deine These, deine Annahmen und deine Verkaufsgruende schriftlich festzuhalten, dein bester Schutz vor spaeteren Bauchentscheidungen. Die Gesamtlogik in einem Satz: Der Score filtert die Kandidaten, das Qualitative entscheidet ueber Investieren oder nicht, und das Gegenpruefen schuetzt vor Fehlinformation. Wenn der Score gut ist, der Moat verstanden, der Preis fair (mit Sicherheitsmarge) und die Risiken tragbar sind, dann steht deine These auf einem soliden Fundament. Und vergiss nie: Das alles ist ein Bildungs- und Analysewerkzeug, das dich zu eigenen, informierten Entscheidungen befaehigen soll - keine Anlageberatung.',
        "faustregel": 'Score filtert, Qualitatives entscheidet, Gegenpruefen schuetzt.',
        "quizzes": [
            {"q": 'Was tust du bei auffaelligen Kennzahlen?', "options": ['Gegen den Geschaeftsbericht pruefen', 'Ignorieren', 'Sofort kaufen'], "correct": 0, "explain": 'Yahoo-Daten sind nicht audit-grade.'},
            {"q": 'Was buendelt der Quality-Score?', "options": ['Profitabilitaet, Kapitalrendite, Bilanz, Wachstum', 'Nur den Kurs', 'Foren-Stimmung'], "correct": 0, "explain": 'Ein schnelles Qualitaetsurteil auf einen Blick.'},
            {"q": 'Wozu dient das Investment-Memo?', "options": ['These und Verkaufsgruende festhalten', 'Werbung', 'Steuer sparen'], "correct": 0, "explain": 'Schutz vor spaeteren Bauchentscheidungen.'},
            {"q": 'Wie lautet die Reihenfolge der Logik?', "options": ['Score filtert, Qualitatives entscheidet, Gegenpruefen schuetzt', 'Reiner Zufall', 'Nur der Kurs zaehlt'], "correct": 0, "explain": 'Erst filtern, dann verstehen, dann absichern.'},
            {"q": 'Wann steht deine These auf solidem Fundament?', "options": ['Score gut + Moat + fairer Preis + tragbare Risiken', 'Nur bei hohem Kurs', 'Nie'], "correct": 0, "explain": 'Alle vier Bausteine zusammen.'},
            {"q": 'Was ist die App letztlich?', "options": ['Ein Bildungs- und Analysewerkzeug, keine Anlageberatung', 'Ein Broker', 'Eine Bank'], "correct": 0, "explain": 'Sie befaehigt zu eigenen, informierten Entscheidungen.'},
        ],
        "quiz": {"q": 'Was tust du bei auffaelligen Kennzahlen?', "options": ['Gegen den Geschaeftsbericht pruefen', 'Ignorieren', 'Sofort kaufen'], "correct": 0, "explain": 'Yahoo-Daten sind nicht audit-grade.'},
    },
]


# ============================================================
#  KRYPTO-WISSEN: Grundbegriffe + Coin-Portraits (reine Bildung)
# ============================================================
CRYPTO_BASICS = [
    ("Was ist eine Blockchain?",
     "Eine Blockchain ist ein gemeinsames, fortlaufendes Kassenbuch, das gleichzeitig auf vielen Computern weltweit "
     "gefuehrt wird. Jede Transaktion wird in 'Bloecken' gebuendelt und unveraenderbar an die Kette davor gehaengt. "
     "Weil alle Teilnehmer dieselbe Kopie haben und Aenderungen kryptografisch abgesichert sind, braucht es keine "
     "zentrale Stelle (Bank), der man vertrauen muss - das Netzwerk selbst sichert die Wahrheit."),
    ("Wallet & Boerse",
     "Eine **Wallet** verwahrt deine Krypto-Schluessel - genauer den privaten Schluessel, der den Zugriff auf deine "
     "Coins kontrolliert. 'Not your keys, not your coins': Wer den Schluessel nicht selbst haelt (sondern nur auf einer "
     "Boerse liegen hat), ist vom Anbieter abhaengig. Eine **Boerse** (Exchange) ist der Marktplatz zum Kaufen und "
     "Verkaufen. Hardware-Wallets (Offline-Geraete) gelten als sicherste Aufbewahrung. Verlierst du Schluessel bzw. "
     "Seed-Phrase, ist das Guthaben unwiederbringlich weg."),
    ("Proof of Work vs. Proof of Stake",
     "Beides sind Verfahren, mit denen sich ein Netzwerk ohne zentrale Stelle auf den gueltigen Stand einigt. "
     "**Proof of Work** (Bitcoin): Rechner loesen energieintensive Aufgaben ('Mining') - sehr sicher, aber stromhungrig. "
     "**Proof of Stake** (Ethereum seit 2022, Solana, Cardano u.a.): Teilnehmer hinterlegen Coins als Pfand ('Staking') "
     "und werden ausgelost, Bloecke zu bestaetigen - viel energieeffizienter, aber tendenziell etwas zentralisierter."),
    ("Marktkapitalisierung & Volatilitaet",
     "Die **Marktkapitalisierung** = Kurs x Anzahl der Coins zeigt die Groesse eines Projekts (Bitcoin und Ethereum sind "
     "die groessten). Kleine Coins koennen extrem steigen, aber auch komplett wertlos werden. **Volatilitaet** ist die "
     "Schwankungsbreite - bei Krypto extrem: Verluste von 50-80% in Baerenmaerkten sind normal. Anders als Aktien haben "
     "die meisten Coins keinen Cashflow; ihr Wert beruht auf Angebot/Nachfrage, Nutzen und Vertrauen."),
    ("Regulierung, Steuern & Sicherheit",
     "Krypto wird zunehmend reguliert: In der EU schafft die **MiCA**-Verordnung einheitliche Regeln fuer Anbieter und "
     "Stablecoins. Steuerlich sind private Veraeusserungsgewinne in Deutschland nach ueber 1 Jahr Haltedauer oft "
     "steuerfrei (ohne Gewaehr - Steuerberater fragen). Vorsicht vor Betrug: unrealistische Renditeversprechen, "
     "Phishing, gefaelschte Apps und 'Pump and Dump'. Grundregel: nur regulierte Anbieter, eigene Schluessel sichern, "
     "gesund misstrauisch bleiben."),
]

CRYPTO_INFO = [
    {"key": "btc", "name": "Bitcoin", "symbol": "BTC", "kategorie": "Wertspeicher / digitales Gold",
     "fakten": "Start 2009 - Schoepfer: Satoshi Nakamoto (pseudonym) - Konsens: Proof of Work - Max. Angebot: 21 Mio.",
     "risiko": "Extrem volatil, kein Cashflow, Totalverlust moeglich; Wert beruht allein auf Angebot/Nachfrage und Vertrauen.",
     "body": "Bitcoin ist die erste und groesste Kryptowaehrung, 2009 von der pseudonymen Person bzw. Gruppe Satoshi "
             "Nakamoto gestartet - kurz nach der Finanzkrise als Gegenentwurf zum Vertrauen in Banken und Zentralbanken. "
             "Die Idee: digitales Geld ohne Mittelsmann, abgesichert ueber ein weltweit verteiltes Netzwerk (Blockchain). "
             "Neue Bitcoin entstehen durch **Mining** (Proof of Work): Rechner loesen kryptografische Aufgaben und sichern "
             "dafuer das Netz - das verbraucht viel Energie. Das Angebot ist hart auf **21 Millionen** Stueck begrenzt, "
             "und etwa alle vier Jahre halbiert sich die Ausgabe neuer Coins (**Halving**) - diese Knappheit ist der Kern "
             "der 'digitales Gold'-Erzaehlung als Wertspeicher und moeglicher Inflationsschutz. Bitcoin ist bewusst kein "
             "Smart-Contract-System wie Ethereum; sein Zweck ist schlicht: Werte halten und uebertragen. Kritisch sind die "
             "hohe Volatilitaet (Schwankungen von 50%+ sind normal), der Energieverbrauch, die fehlende Cashflow-Basis "
             "(anders als eine Aktie produziert Bitcoin keine Gewinne) und regulatorische Unsicherheit. Ein "
             "hochspekulatives Asset, kein sicherer Hafen im klassischen Sinn."},
    {"key": "eth", "name": "Ethereum", "symbol": "ETH", "kategorie": "Smart-Contract-Plattform",
     "fakten": "Start 2015 - Schoepfer: Vitalik Buterin u.a. - Konsens: Proof of Stake (seit 2022) - kein fixes Maximalangebot.",
     "risiko": "Hochvolatil; Smart-Contract- und Hack-Risiken; starke Konkurrenz; Gebuehren bei Ueberlastung.",
     "body": "Ethereum, 2015 von Vitalik Buterin und Mitstreitern gestartet, erweiterte die Blockchain-Idee von reinem "
             "Geld zu einem **programmierbaren Weltcomputer**. Auf Ethereum laufen **Smart Contracts** - selbst "
             "ausfuehrende Programme - und darauf Tausende Anwendungen (dApps): dezentrale Finanzdienste (DeFi: Tauschen, "
             "Verleihen, Zinsen ohne Bank), NFTs, Spiele, Stablecoins. Die Waehrung **Ether (ETH)** bezahlt die "
             "Rechenleistung im Netz ('Gas-Gebuehren'). 2022 wechselte Ethereum mit 'The Merge' von Proof of Work auf "
             "**Proof of Stake**: Statt Mining sichern nun Validatoren das Netz, indem sie ETH hinterlegen (staken) - das "
             "senkte den Energieverbrauch um ueber 99%. Ethereum ist die mit Abstand wichtigste Plattform fuer das "
             "gesamte Krypto-Oekosystem, weshalb ETH oft als Infrastruktur-Wette gilt. Schwaechen: zeitweise hohe "
             "Gebuehren bei Ueberlastung (dagegen helfen 'Layer-2'-Netze wie Arbitrum/Optimism), starke Konkurrenz "
             "(Solana u.a.) sowie Komplexitaet und Smart-Contract-Risiken - Programmierfehler oder Hacks koennen Gelder "
             "vernichten. Wie alle Kryptos hochvolatil und spekulativ."},
    {"key": "usdt", "name": "Tether", "symbol": "USDT", "kategorie": "Stablecoin (an US-Dollar gekoppelt)",
     "fakten": "Start 2014 - Emittent: Tether Ltd. - Typ: an USD gebundener Stablecoin - Deckung umstritten.",
     "risiko": "Deckungs- und Emittentenrisiko; Bindung kann brechen ('de-peg'); kein staatlich garantiertes Geld.",
     "body": "Tether (USDT) ist der groesste **Stablecoin** - eine Kryptowaehrung, deren Kurs an den US-Dollar gekoppelt "
             "ist (1 USDT soll rund 1 USD wert sein). Stablecoins sind das 'Bargeld' der Kryptowelt: Anleger parken damit "
             "Werte zwischen Trades, ohne in Euro/Dollar zurueckzuwechseln, und nutzen sie als Recheneinheit auf Boersen "
             "und in DeFi. Die Stabilitaet soll durch **Reserven** gedeckt sein - Tether gibt an, jeden USDT mit Dollar, "
             "Staatsanleihen und aehnlichen Werten zu hinterlegen. Genau hier liegt die jahrelange Kritik: Transparenz und "
             "Pruefung dieser Reserven waren wiederholt umstritten, es gab Strafzahlungen wegen irrefuehrender Angaben. "
             "Faellt das Vertrauen in die Deckung, kann ein Stablecoin seine Bindung verlieren ('de-peggen') - beim "
             "Algorithmus-Stablecoin TerraUSD geschah das 2022 katastrophal. USDT ist also KEIN risikofreier "
             "Dollar-Ersatz, sondern traegt ein Emittenten- und Deckungsrisiko. In der EU regelt die MiCA-Verordnung "
             "Stablecoins inzwischen strenger."},
    {"key": "bnb", "name": "BNB", "symbol": "BNB", "kategorie": "Exchange-/Plattform-Token",
     "fakten": "Start 2017 - Hinter: Binance - Nutzen: Gebuehren-Rabatt + Treibstoff der BNB Chain - regelmaessige Burns.",
     "risiko": "Stark abhaengig von einem Unternehmen (Binance) und dessen Regulierung; eher zentralisiert.",
     "body": "BNB (frueher 'Binance Coin') ist der Token der weltgroessten Krypto-Boerse Binance und der zugehoerigen "
             "Blockchain (BNB Chain). Ursprung 2017 als Rabatt-Token: Wer mit BNB Handelsgebuehren auf Binance zahlte, "
             "bekam Nachlass. Daraus wurde ein breites Plattform-Token, das die BNB Chain antreibt - eine schnelle, "
             "guenstige Smart-Contract-Kette, die als Ethereum-Alternative viele Anwendungen beherbergt. Binance "
             "verringert das Angebot regelmaessig durch 'Coin Burns' (Vernichtung von Token), was den Wert stuetzen soll. "
             "Der grosse Vorbehalt: BNB ist eng an das Schicksal eines einzelnen, stark regulierten Unternehmens "
             "gebunden. Binance und sein Gruender hatten erhebliche rechtliche Auseinandersetzungen (u.a. eine "
             "Milliarden-Einigung mit US-Behoerden 2023). Regulatorischer Druck auf Binance trifft BNB direkt. Zudem ist "
             "die BNB Chain staerker zentralisiert als Ethereum. Wie alle Kryptos hochspekulativ und volatil."},
    {"key": "sol", "name": "Solana", "symbol": "SOL", "kategorie": "Hochleistungs-Smart-Contract-Plattform",
     "fakten": "Start 2020 - Schoepfer: Anatoly Yakovenko - Konsens: Proof of History + Proof of Stake - sehr schnell/guenstig.",
     "risiko": "Netzwerk-Ausfaelle in der Vergangenheit; staerkere Zentralisierung; hohe Volatilitaet.",
     "body": "Solana, 2020 gestartet, ist eine Smart-Contract-Plattform wie Ethereum, aber auf **Geschwindigkeit und "
             "niedrige Gebuehren** getrimmt. Durch ein besonderes Verfahren ('Proof of History' kombiniert mit Proof of "
             "Stake) verarbeitet Solana sehr viele Transaktionen pro Sekunde zu Bruchteilen eines Cents - attraktiv fuer "
             "Handel, NFTs, Spiele und Zahlungen. Das machte Solana zu einem der wichtigsten Ethereum-Herausforderer. Die "
             "Kehrseite dieser Leistung war lange die Stabilitaet: Das Netz hatte mehrere komplette Ausfaelle, bei denen "
             "stundenlang nichts ging - ein ernstes Vertrauensproblem fuer ein Finanznetz. Solana gilt zudem als "
             "staerker zentralisiert (ein Validator erfordert teure Hardware). Ein schwerer Rueckschlag war die Naehe zur "
             "2022 kollabierten Boerse FTX, deren Pleite den SOL-Kurs einbrechen liess; das Projekt hat sich seither "
             "stark erholt. Hochvolatil und spekulativ wie der gesamte Sektor."},
    {"key": "xrp", "name": "XRP", "symbol": "XRP", "kategorie": "Zahlungs-/Banken-Token",
     "fakten": "Start 2012 - Hinter: Ripple Labs - Zweck: schnelle Bank-/Auslandszahlungen - nicht gemined.",
     "risiko": "Regulatorisch und juristisch stark belastet; relativ zentralisiert; hohe Volatilitaet.",
     "body": "XRP ist die Kryptowaehrung des XRP Ledgers, eng verbunden mit dem Unternehmen Ripple. Ziel ist es, "
             "**internationale Zahlungen** zwischen Banken und Finanzdienstleistern schnell und billig abzuwickeln - als "
             "Bruecke zwischen Waehrungen, die das langsame Korrespondenzbank-System (SWIFT) ersetzen soll. "
             "Transaktionen sind in Sekunden bestaetigt und kosten fast nichts. Anders als Bitcoin/Ethereum wird XRP "
             "nicht gemined; ein Grossteil wurde bei Start erzeugt und wird teils von Ripple gehalten - ein Kritikpunkt "
             "zur Zentralisierung. Praegend war ein langer **Rechtsstreit mit der US-Boersenaufsicht SEC** (ab 2020) um "
             "die Frage, ob XRP ein nicht registriertes Wertpapier ist; ein Teilurteil 2023 fiel teils zugunsten von "
             "Ripple aus und bewegte den Kurs stark. XRP zeigt exemplarisch, wie sehr Krypto-Werte von Regulierung und "
             "Gerichtsentscheidungen abhaengen. Hochspekulativ und volatil."},
    {"key": "ada", "name": "Cardano", "symbol": "ADA", "kategorie": "Forschungsbasierte Smart-Contract-Plattform",
     "fakten": "Start 2017 - Schoepfer: Charles Hoskinson - Konsens: Proof of Stake - forschungsgetrieben/peer-reviewed.",
     "risiko": "Langsame Entwicklung, bislang weniger Nutzung als die Konkurrenz; hohe Volatilitaet.",
     "body": "Cardano (Token: ADA), 2017 von Ethereum-Mitgruender Charles Hoskinson gestartet, ist eine "
             "Smart-Contract-Plattform mit einem besonderen Anspruch: **wissenschaftlich fundiert und besonders "
             "sorgfaeltig** entwickelt. Neue Funktionen werden vor der Einfuehrung in akademischen Papieren geprueft "
             "('peer-reviewed') und in Phasen ausgerollt. Cardano nutzt von Anfang an energiesparendes Proof of Stake. "
             "Befuerworter loben die Gruendlichkeit und den Fokus auf reale Anwendungen, u.a. Projekte in "
             "Entwicklungslaendern. Die Kehrseite: Dieser langsame, methodische Ansatz fuehrte dazu, dass Smart Contracts "
             "und ein lebendiges Anwendungs-Oekosystem erst spaet kamen - Kritiker werfen dem Projekt vor, "
             "technologisch viel zu versprechen, aber in der Nutzung (DeFi, Apps) hinter Ethereum und Solana "
             "zurueckzubleiben. ADA ist damit eine Wette darauf, dass sich Sorgfalt langfristig auszahlt. Hochvolatil "
             "und spekulativ."},
    {"key": "doge", "name": "Dogecoin", "symbol": "DOGE", "kategorie": "Meme-Coin",
     "fakten": "Start 2013 - Schoepfer: Billy Markus & Jackson Palmer (als Scherz) - Konsens: Proof of Work - kein Limit.",
     "risiko": "Wert fast nur durch Hype und prominente Aussagen; inflationaer; extrem spekulativ.",
     "body": "Dogecoin entstand 2013 als **Scherz** - benannt nach dem 'Doge'-Internet-Meme mit dem Shiba-Inu-Hund - und "
             "sollte die Krypto-Euphorie augenzwinkernd parodieren. Technisch ist es eine einfache Abspaltung von "
             "Litecoin/Bitcoin (Proof of Work). Anders als Bitcoin hat Dogecoin **kein Angebotslimit**: Jedes Jahr "
             "kommen feste Mengen neuer Coins hinzu, es ist also leicht inflationaer. Trotz - oder gerade wegen - seiner "
             "unernsten Herkunft entwickelte Dogecoin eine riesige, treue Community und wird fuer kleine Trinkgelder und "
             "Spenden genutzt. Beruehmt wurde es vor allem durch die Tweets von Elon Musk, die den Kurs mehrfach "
             "explodieren liessen. Genau das ist das Kernproblem: Dogecoins Wert beruht fast vollstaendig auf **Hype, "
             "Stimmung und prominenten Aussagen**, nicht auf Technologie oder Nutzen. Das Paradebeispiel fuer einen rein "
             "spekulativen, sentiment-getriebenen Meme-Coin - extrem volatil und mit hohem Totalverlustrisiko."},
    {"key": "dot", "name": "Polkadot", "symbol": "DOT", "kategorie": "Multi-Chain / Interoperabilitaet",
     "fakten": "Start 2020 - Schoepfer: Gavin Wood - Konsens: Proof of Stake - Fokus: vernetzte Blockchains.",
     "risiko": "Hohe Komplexitaet; starker Wettbewerb; Nutzung unter den Erwartungen; volatil.",
     "body": "Polkadot, 2020 von Ethereum-Mitgruender Gavin Wood gestartet, will ein grundlegendes Problem loesen: dass "
             "viele Blockchains wie **Inseln** nebeneinander existieren und schlecht miteinander reden. Polkadot ist ein "
             "'Netz von Blockchains': Eine zentrale 'Relay Chain' verbindet viele spezialisierte Einzelketten "
             "('Parachains'), die untereinander Daten und Werte austauschen koennen - das nennt man "
             "**Interoperabilitaet**. Projekte koennen so eine eigene, auf ihren Zweck zugeschnittene Blockchain bauen und "
             "trotzdem von der gemeinsamen Sicherheit profitieren. DOT dient zur Sicherung (Staking), zur Steuerung "
             "(Abstimmungen ueber Upgrades) und um Parachain-Plaetze zu ersteigern. Polkadot gilt technisch als "
             "ambitioniert, ist aber komplex und steht im Wettbewerb mit anderen Interoperabilitaets-Ansaetzen (Cosmos "
             "u.a.); die Nutzung blieb hinter den hohen Erwartungen zurueck. Hochvolatil und spekulativ."},
    {"key": "link", "name": "Chainlink", "symbol": "LINK", "kategorie": "Oracle-Netzwerk (Echtweltdaten)",
     "fakten": "Start 2017/2019 - Schoepfer: Sergey Nazarov u.a. - Zweck: Echtweltdaten fuer Smart Contracts (Oracle).",
     "risiko": "Token-Nutzen teils indirekt; Datenqualitaets- und Wettbewerbsrisiko; volatil.",
     "body": "Chainlink loest ein unsichtbares, aber entscheidendes Problem: Smart Contracts auf einer Blockchain kennen "
             "die Aussenwelt nicht - sie wissen von sich aus keinen Aktienkurs, kein Wetter, kein Ergebnis. Chainlink ist "
             "ein **Oracle-Netzwerk**: ein dezentrales System, das verlaessliche Echtweltdaten in Blockchains "
             "hineinspeist, damit Smart Contracts darauf reagieren koennen (etwa 'zahle aus, wenn Bitcoin ueber X "
             "steht'). Damit ist Chainlink kritische Infrastruktur fuer DeFi und viele Anwendungen - praktisch das "
             "Bindeglied zwischen Blockchains und realer Welt. Der Token LINK bezahlt die Datenanbieter ('Node "
             "Operators') und sichert das Netz. Chainlink arbeitet mit etablierten Finanzfirmen an der Anbindung "
             "traditioneller Maerkte (Tokenisierung). Risiken: Abhaengigkeit von der Datenqualitaet, Wettbewerb, und der "
             "Token-Nutzen ist teils indirekt. Wie alle Kryptos hochvolatil; der Wert haengt am Erfolg des gesamten "
             "Smart-Contract-Sektors."},
    {"key": "avax", "name": "Avalanche", "symbol": "AVAX", "kategorie": "Smart-Contract-Plattform",
     "fakten": "Start 2020 - Hinter: Ava Labs (Emin Guen Sirer) - Konsens: Proof of Stake - 'Subnets' fuer eigene Netze.",
     "risiko": "Sehr starker Plattform-Wettbewerb; Erfolg von Akzeptanz abhaengig; volatil.",
     "body": "Avalanche (Token: AVAX), 2020 gestartet, ist eine weitere schnelle Smart-Contract-Plattform und "
             "Ethereum-Alternative. Ihr Markenzeichen ist eine ungewoehnliche Architektur aus **drei zusammenarbeitenden "
             "Ketten** und vor allem die Moeglichkeit, eigene massgeschneiderte Netzwerke ('Subnets') zu bauen - "
             "interessant fuer Unternehmen und Spiele, die ihre eigene Blockchain mit eigenen Regeln wollen. Avalanche "
             "erreicht sehr schnelle Endgueltigkeit von Transaktionen (unter zwei Sekunden) und ist mit "
             "Ethereum-Werkzeugen kompatibel, was Entwicklern den Umstieg erleichtert. AVAX dient als Gebuehren-, "
             "Staking- und Steuerungs-Token. Avalanche steht im harten Wettbewerb der 'Ethereum-Killer' (Solana u.a.), "
             "in dem sich erst zeigen muss, welche Plattformen dauerhaft genug Nutzer und Anwendungen anziehen. "
             "Hochvolatil und spekulativ; der Erfolg haengt stark an der Akzeptanz durch Entwickler und Projekte."},
    {"key": "pol", "name": "Polygon", "symbol": "POL", "kategorie": "Ethereum-Skalierung (Layer-2)",
     "fakten": "Start 2017 - Hinter: Polygon Labs - Zweck: Ethereum guenstiger/schneller machen (Layer-2). Token frueher MATIC.",
     "risiko": "Starker Layer-2-Wettbewerb; Token-Nutzen abhaengig von Akzeptanz; volatil.",
     "body": "Polygon (frueher Token MATIC, inzwischen POL) ist kein Konkurrent zu Ethereum, sondern ein **Helfer**: eine "
             "Familie von Loesungen, die Ethereum schneller und guenstiger machen ('Skalierung', Layer-2). Statt "
             "Transaktionen teuer direkt auf Ethereum abzuwickeln, buendelt Polygon viele Transaktionen guenstig auf "
             "einer Nebenkette bzw. Technik und sichert das Ergebnis auf Ethereum ab. Nutzer zahlen dadurch Cent-Betraege "
             "statt teurer Gas-Gebuehren - weshalb viele grosse Marken (Zahlungsdienste, Spiele, Konsumgueter) Polygon "
             "fuer ihre Blockchain-Projekte gewaehlt haben. Polygon entwickelt stark in Richtung "
             "'Zero-Knowledge'-Technologie (zk), die als Zukunft der Skalierung gilt. Der Token zahlt Gebuehren und "
             "sichert das Netz. Risiken: Layer-2 ist ein dicht umkaempftes Feld (Arbitrum, Optimism, Base u.a.), und der "
             "Token-Nutzen haengt am Wettbewerb. Hochvolatil und spekulativ."},
    {"key": "ltc", "name": "Litecoin", "symbol": "LTC", "kategorie": "Zahlungs-Coin",
     "fakten": "Start 2011 - Schoepfer: Charlie Lee - Konsens: Proof of Work (Scrypt) - Max. 84 Mio.",
     "risiko": "Wenig Alleinstellung heute; abnehmende Relevanz moeglich; volatil.",
     "body": "Litecoin, 2011 vom frueheren Google-Ingenieur Charlie Lee gestartet, ist einer der aeltesten Altcoins und "
             "wurde als '**Silber zu Bitcoins Gold**' positioniert. Technisch ist es eine fast unveraenderte "
             "Bitcoin-Kopie mit ein paar Anpassungen: Bloecke entstehen viermal schneller (alle 2,5 statt 10 Minuten), "
             "das Maximalangebot ist mit 84 Millionen viermal groesser, und es nutzt einen anderen Mining-Algorithmus "
             "(Scrypt). Damit sollte Litecoin guenstige, schnelle Alltagszahlungen ermoeglichen. Litecoin gilt als "
             "solide, langlebig und unspektakulaer - es gab nie grosse Skandale, aber auch keine bahnbrechende "
             "Innovation. Genau das ist sein Problem: In einer Welt aus Smart-Contract-Plattformen, schnellen "
             "Stablecoins und Layer-2-Loesungen ist der urspruengliche Zweck 'schnelleres Bitcoin' weniger einzigartig "
             "geworden. LTC dient vielen als einfache, bewaehrte Zahlungs-Krypto. Hochvolatil wie der gesamte Sektor."},
    {"key": "xmr", "name": "Monero", "symbol": "XMR", "kategorie": "Privacy-Coin (anonym)",
     "fakten": "Start 2014 - Konsens: Proof of Work - Besonderheit: vollstaendige Privatsphaere (anonyme Transaktionen).",
     "risiko": "Regulatorisch besonders heikel (Auslistungen, Geldwaesche-Fokus); eingeschraenkte Handelbarkeit; volatil.",
     "body": "Monero (XMR) ist die bekannteste **Privacy-Kryptowaehrung**. Waehrend Bitcoin-Transaktionen oeffentlich und "
             "nachverfolgbar sind, verschleiert Monero durch eingebaute Technik (Ring-Signaturen, Stealth-Adressen, "
             "vertrauliche Betraege) standardmaessig Sender, Empfaenger und Betrag - Zahlungen sind also privat und nicht "
             "zuordenbar. Befuerworter sehen darin echtes digitales Bargeld und einen Schutz der finanziellen "
             "Privatsphaere in Zeiten zunehmender Ueberwachung. Genau diese Anonymitaet macht Monero aber regulatorisch "
             "hochproblematisch: Mehrere Boersen haben XMR ausgelistet, in der EU steht es im Fokus der "
             "Geldwaesche-Regulierung, und es wird mit illegalen Zahlungen in Verbindung gebracht. Fuer Privatanleger "
             "bedeutet das ein erhebliches Risiko, dass Handelbarkeit und Zugang weiter eingeschraenkt werden. "
             "Technologisch interessant, rechtlich besonders heikel - und wie alle Kryptos hochvolatil und spekulativ."},
]


# ============================================================
#  DESIGN (CSS) - Neo-Broker, Indigo/Violett, dark+light
# ============================================================
CSS = """
:root{
  --fa-primary:#6366f1;        /* Indigo */
  --fa-primary-d:#4f46e5;
  --fa-accent2:#8b5cf6;        /* Violett */
  --fa-muted:#7c87a0;
  --fa-border:rgba(130,135,165,.22);
  --fa-soft:rgba(130,135,170,.07);
  --fa-card:rgba(130,135,170,.045);
  --fa-shadow:0 1px 2px rgba(15,23,42,.04), 0 6px 22px rgba(15,23,42,.06);
  --fa-shadow-lg:0 12px 40px rgba(79,70,229,.16);
  --fa-green:#16a34a; --fa-green-bg:#dcfce7;
  --fa-amber:#b45309; --fa-amber-bg:#fef3c7;
  --fa-red:#dc2626;   --fa-red-bg:#fee2e2;
}
html, body, .stApp, [class*="css"]{
  font-family:"Inter",-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
}
.stApp{ font-size:15.5px; letter-spacing:.1px; }
.block-container{ padding-top:1.4rem; max-width:1180px; }
h1,h2,h3,h4{ letter-spacing:-.4px; font-weight:750; }
::selection{ background:rgba(99,102,241,.28); }
::-webkit-scrollbar{ width:11px; height:11px; }
::-webkit-scrollbar-thumb{ background:rgba(130,135,165,.40); border-radius:8px; border:3px solid transparent; background-clip:content-box; }
hr{ border:0; border-top:1px solid var(--fa-border); margin:1.2rem 0; }

[data-testid="stSidebar"]{ background:var(--fa-soft); border-right:1px solid var(--fa-border); }
[data-testid="stSidebar"] [role="radiogroup"] label{ border-radius:10px; padding:2px 8px; transition:background .15s ease; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover{ background:rgba(99,102,241,.08); }

[data-testid="stMetric"]{
  background:var(--fa-card); border:1px solid var(--fa-border);
  border-radius:16px; padding:16px 18px; box-shadow:var(--fa-shadow);
  transition:transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
[data-testid="stMetric"]:hover{ transform:translateY(-2px); border-color:var(--fa-primary); box-shadow:var(--fa-shadow-lg); }
[data-testid="stMetricValue"]{ font-weight:780; letter-spacing:-.4px; font-feature-settings:"tnum"; }
[data-testid="stMetricLabel"]{ color:var(--fa-muted); font-weight:600; text-transform:uppercase; font-size:.72rem; letter-spacing:.5px; }

.stButton>button, .stDownloadButton>button{
  border-radius:12px; font-weight:650; min-height:44px; border:1px solid var(--fa-border);
  transition:transform .12s ease, box-shadow .12s ease, border-color .12s ease, background .12s ease;
}
.stButton>button:hover, .stDownloadButton>button:hover{ transform:translateY(-1px); border-color:var(--fa-primary); box-shadow:var(--fa-shadow); }
.stButton>button:active, .stDownloadButton>button:active{ transform:translateY(0); }
.stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"],
[data-testid="baseButton-primary"], [data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,var(--fa-primary),var(--fa-accent2)); border:0; color:#fff;
  box-shadow:0 8px 22px rgba(99,102,241,.34);
}
.stButton>button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover{ box-shadow:0 12px 30px rgba(99,102,241,.46); }
button:focus-visible, a:focus-visible, [role="radio"]:focus-visible{ outline:3px solid var(--fa-primary); outline-offset:2px; }

.stTextInput input, .stNumberInput input, textarea,
.stTextInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"]{ border-radius:12px !important; }
.stTextInput div[data-baseweb="input"]:focus-within, .stSelectbox div[data-baseweb="select"]:focus-within{
  border-color:var(--fa-primary) !important; box-shadow:0 0 0 3px rgba(99,102,241,.16) !important; }

.stTabs [data-baseweb="tab-list"]{ gap:4px; border-bottom:1px solid var(--fa-border); }
.stTabs [data-baseweb="tab"]{ border-radius:10px 10px 0 0; padding:7px 16px; font-weight:600; }
.stTabs [data-baseweb="tab"]:hover{ background:rgba(99,102,241,.07); }
.stTabs [aria-selected="true"]{ color:var(--fa-primary) !important; }
.stTabs [data-baseweb="tab-highlight"]{ background:var(--fa-primary) !important; height:3px; border-radius:3px; }

.fa-hero{
  position:relative; overflow:hidden;
  background:linear-gradient(120deg,#4338ca 0%, #6d5efc 50%, #8b5cf6 100%);
  color:#fff; padding:30px 34px; border-radius:22px; margin-bottom:18px;
  box-shadow:0 20px 50px rgba(79,70,229,.34);
}
.fa-hero:after{ content:""; position:absolute; top:-45%; right:-8%; width:360px; height:360px;
  background:radial-gradient(circle, rgba(255,255,255,.18), rgba(255,255,255,0) 70%); pointer-events:none; }
.fa-hero h1{ color:#fff; margin:0; font-size:2rem; font-weight:850; letter-spacing:-.6px; }
.fa-hero .sub{ color:#eef0ff; opacity:.95; font-size:1rem; margin-top:5px; }
.fa-hero .tag{ display:inline-block; margin-top:14px; background:rgba(255,255,255,.16); color:#fff;
  padding:5px 15px; border-radius:999px; font-size:.78rem; font-weight:600;
  border:1px solid rgba(255,255,255,.25); }
.fa-onboard{ background:var(--fa-card); border:1px solid var(--fa-border); border-left:4px solid var(--fa-primary);
  border-radius:16px; padding:20px 24px; margin-bottom:6px; box-shadow:var(--fa-shadow); }
.fa-onboard h4{ margin:0 0 8px; font-weight:750; }
.fa-onboard ol{ margin:6px 0 0; padding-left:20px; line-height:1.9; }
.fa-pill{ display:inline-block; padding:3px 12px; border-radius:999px; font-size:.76rem; font-weight:700; letter-spacing:.2px; }
.fa-verdict{ border-radius:16px; padding:16px 20px; font-size:1.05rem; font-weight:750; margin:8px 0 4px; box-shadow:var(--fa-shadow); }
.fa-table{ width:100%; border-collapse:separate; border-spacing:0; font-size:.93rem;
  border:1px solid var(--fa-border); border-radius:14px; overflow:hidden; font-feature-settings:"tnum"; }
.fa-table th{ text-align:left; color:var(--fa-muted); font-weight:700; padding:10px 14px; background:var(--fa-soft);
  border-bottom:1px solid var(--fa-border); text-transform:uppercase; font-size:.68rem; letter-spacing:.7px; }
.fa-table td{ padding:11px 14px; border-bottom:1px solid var(--fa-border); }
.fa-table tbody tr:last-child td{ border-bottom:0; }
.fa-table tbody tr:hover td{ background:rgba(99,102,241,.05); }
.fa-secttitle{ font-weight:750; margin:20px 0 7px; font-size:.98rem; }
.price-wrap{ display:flex; gap:18px; flex-wrap:wrap; }
.price-card{ background:#ffffff; border:1px solid #e6e8f0; border-radius:20px; padding:28px; flex:1; min-width:240px;
  color:#0f172a; box-shadow:0 6px 24px rgba(15,23,42,.06); transition:transform .15s ease, box-shadow .15s ease; }
.price-card:hover{ transform:translateY(-3px); box-shadow:0 16px 40px rgba(15,23,42,.10); }
.price-card.popular{ border:2px solid var(--fa-primary); box-shadow:0 22px 54px rgba(99,102,241,.22);
  position:relative; transform:translateY(-4px); }
.price-card.popular:before{ content:"BELIEBT"; position:absolute; top:-12px; right:20px;
  background:linear-gradient(135deg,var(--fa-primary),var(--fa-accent2)); color:#fff;
  font-size:.7rem; font-weight:800; padding:4px 14px; border-radius:999px; letter-spacing:.5px; }
.price-card h3{ margin:0 0 2px; font-size:1.3rem; color:#0f172a; font-weight:800; }
.price-card .price{ font-size:2.3rem; font-weight:850; color:#0f172a; letter-spacing:-.6px; }
.price-card .per{ color:#64748b; font-size:.9rem; }
.price-card ul{ padding-left:18px; color:#334155; line-height:1.85; margin:14px 0 0; }
.price-card li{ color:#334155; }
.lock-card{ background:rgba(99,102,241,.06); border:1px dashed var(--fa-primary); border-radius:16px; padding:20px; }
.fa-foot{ color:var(--fa-muted); font-size:.82rem; margin-top:30px; border-top:1px solid var(--fa-border); padding-top:16px; }
"""

# Premium "Klavierlack / Autolack"-Look: tiefes glaenzendes Schwarz, Lichtreflexe, metallische Schrift.
CSS_GLOSS = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
/* Geometrische, Tesla-aehnliche Schrift (Montserrat, Open-Source - Teslas Gotham ist proprietaer) */
html, body, .stApp, [class*="css"], button, input, textarea, select,
[data-testid="stMarkdownContainer"]{
  font-family:'Montserrat',-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif !important;
}
.stApp{
  background:radial-gradient(135% 95% at 50% -12%, #1a1c24 0%, #0c0d11 52%, #050608 100%) fixed;
  color:#e9ebf2; font-size:16.5px;
}
.stApp, .block-container, [data-testid="stMarkdownContainer"], p, span, label, li, td, th, div{ color:#dfe2ec; }
/* Mehr Weissraum -> die App fuehlt sich groesser/edler an */
.block-container{ max-width:1320px !important; padding-top:2.4rem !important; padding-bottom:3rem !important; }
[data-testid="stVerticalBlock"]{ gap:1.05rem; }
h1,h2,h3,h4{ margin-top:.4rem; }
/* Ueberschriften: hell, weit gesperrt (Tesla-Stil) mit dezentem Metallic-Verlauf */
h1, h2, h3, h4, [data-testid="stHeading"]{
  background:linear-gradient(180deg,#ffffff 0%, #dfe3ec 50%, #b9bfce 100%);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  color:#eef0f6; font-weight:600; letter-spacing:.012em; text-shadow:0 1px 0 rgba(0,0,0,.5);
}
h1{ font-size:2.2rem; letter-spacing:.005em; }
[data-testid="stMetricValue"]{
  background:linear-gradient(180deg,#ffffff,#c9cedd); -webkit-background-clip:text; background-clip:text;
  -webkit-text-fill-color:transparent; color:#fff; font-weight:700; font-size:2.1rem; letter-spacing:.01em;
}
[data-testid="stMetricLabel"]{ color:#8b93a7; letter-spacing:.14em; }
/* ===== Control-Center: linke Leiste komplett glaenzend-schwarz + Nav als Schaltflaechen ===== */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg, #131419 0%, #08090c 100%) !important;
  border-right:1px solid rgba(255,255,255,.08);
  box-shadow:1px 0 0 rgba(255,255,255,.05) inset, 22px 0 50px rgba(0,0,0,.55);
  min-width:312px !important; width:312px !important;
}
[data-testid="stSidebar"] > div:first-child{ padding-top:1.3rem; padding-left:1rem; padding-right:1rem; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
  letter-spacing:.18em; text-transform:uppercase; font-size:1.05rem;
}
[data-testid="stSidebar"] [role="radiogroup"]{ gap:9px; }
[data-testid="stSidebar"] [role="radiogroup"] > label{
  display:flex; align-items:center; width:100%; cursor:pointer;
  background:linear-gradient(157deg, rgba(40,42,54,.55), rgba(15,16,21,.66));
  border:1px solid rgba(255,255,255,.06); border-radius:13px;
  padding:12px 16px !important; margin:0 !important;
  text-transform:uppercase; letter-spacing:.13em; font-size:.79rem; font-weight:600; color:#c7ccd9 !important;
  box-shadow:0 1px 0 rgba(255,255,255,.05) inset; transition:transform .16s ease, border-color .16s ease, background .16s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover{
  border-color:rgba(124,123,245,.5);
  background:linear-gradient(157deg, rgba(60,62,82,.62), rgba(22,23,30,.74)); transform:translateX(3px);
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked){
  background:linear-gradient(135deg, rgba(99,102,241,.34), rgba(139,92,246,.18)) !important;
  border-color:rgba(124,123,245,.85) !important; color:#ffffff !important;
  box-shadow:0 1px 0 rgba(255,255,255,.22) inset, 0 10px 26px rgba(99,102,241,.42);
}
[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child{ display:none !important; }
/* Glossy Flaechen: Kacheln, Karten, Eingaben - mit Reflex oben + tiefem Schatten */
[data-testid="stMetric"], .fa-onboard, .fa-verdict, .lock-card,
div[data-testid="stExpander"], .stTabs [data-baseweb="tab-panel"]{
  position:relative; overflow:hidden;
  background:linear-gradient(157deg, rgba(46,48,60,.92) 0%, rgba(22,23,29,.96) 46%, rgba(13,14,18,.98) 100%) !important;
  border:1px solid rgba(255,255,255,.07) !important;
  border-radius:18px !important;
  box-shadow:0 1px 0 rgba(255,255,255,.10) inset, 0 -1px 0 rgba(0,0,0,.5) inset, 0 22px 48px rgba(0,0,0,.55) !important;
}
[data-testid="stMetric"]::before{
  content:""; position:absolute; left:0; right:0; top:0; height:46%;
  background:linear-gradient(180deg, rgba(255,255,255,.09), rgba(255,255,255,0)); pointer-events:none; border-radius:18px 18px 0 0;
}
[data-testid="stMetric"]:hover{ box-shadow:0 1px 0 rgba(255,255,255,.14) inset, 0 26px 60px rgba(0,0,0,.6), 0 0 0 1px rgba(99,102,241,.5) !important; }
/* Eingaben dunkel-glaenzend */
.stTextInput input, .stNumberInput input, textarea,
.stTextInput div[data-baseweb="input"], .stNumberInput div[data-baseweb="input"],
.stSelectbox div[data-baseweb="select"], div[data-baseweb="select"] > div{
  background:linear-gradient(180deg, #1b1d24, #121319) !important; color:#e9ebf2 !important;
  border:1px solid rgba(255,255,255,.09) !important; border-radius:12px !important;
  box-shadow:0 1px 0 rgba(255,255,255,.05) inset, 0 6px 16px rgba(0,0,0,.4) !important;
}
.stTextInput input::placeholder, textarea::placeholder{ color:#6b7280; }
/* Sekundaere Buttons: glaenzendes Schwarz */
.stButton>button, .stDownloadButton>button{
  background:linear-gradient(157deg, rgba(44,46,58,.95), rgba(18,19,25,.98)) !important;
  color:#eef0f6 !important; border:1px solid rgba(255,255,255,.10) !important;
  box-shadow:0 1px 0 rgba(255,255,255,.10) inset, 0 10px 24px rgba(0,0,0,.5) !important;
}
/* Primaere Buttons: glaenzender Indigo/Violett-Verlauf mit Glanzkante */
.stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"],
[data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,#7c7bf5 0%, #6366f1 45%, #8b5cf6 100%) !important; color:#fff !important;
  border:0 !important;
  box-shadow:0 1px 0 rgba(255,255,255,.35) inset, 0 -2px 6px rgba(0,0,0,.3) inset, 0 14px 30px rgba(99,102,241,.5) !important;
}
/* Tabellen dunkel-glaenzend */
.fa-table{ border:1px solid rgba(255,255,255,.08) !important;
  background:linear-gradient(157deg, rgba(30,31,39,.9), rgba(15,16,21,.96)) !important; }
.fa-table th{ background:rgba(255,255,255,.04) !important; color:#9aa1b4 !important; }
.fa-table td{ border-bottom:1px solid rgba(255,255,255,.06) !important; color:#dfe2ec !important; }
.fa-table tbody tr:hover td{ background:rgba(99,102,241,.10) !important; }
/* Groessere, glaenzende Kacheln (mehr Praesenz) */
[data-testid="stMetric"]{ padding:22px 24px !important; border-radius:20px !important; }
[data-testid="stTabs"] [data-baseweb="tab"]{ font-size:.95rem; letter-spacing:.04em; }
/* Hero: tieferes, glaenzenderes Schwarz-Violett, groesser */
.fa-hero{
  background:linear-gradient(135deg, #131019 0%, #2a2350 40%, #4f46e5 100%) !important;
  box-shadow:0 1px 0 rgba(255,255,255,.16) inset, 0 30px 66px rgba(0,0,0,.62) !important;
  border:1px solid rgba(255,255,255,.09); padding:40px 44px !important; border-radius:24px !important;
}
.fa-hero h1{ -webkit-text-fill-color:#fff; background:none; font-size:2.7rem; font-weight:700;
  letter-spacing:.005em; text-shadow:0 2px 16px rgba(0,0,0,.5); }
.fa-hero .sub{ font-size:1.12rem; }
.fa-foot{ color:#7c8398; border-top:1px solid rgba(255,255,255,.07); }
hr{ border-top:1px solid rgba(255,255,255,.08) !important; }
::-webkit-scrollbar-thumb{ background:rgba(255,255,255,.16); }
"""


# ============================================================
#  GLOSSAR
# ============================================================
GLOSSARY = {
    "KGV (P/E)": "Kurs-Gewinn-Verhaeltnis. Aktienkurs geteilt durch Gewinn je Aktie. Wie viele Jahresgewinne man fuer die Aktie zahlt.",
    "EV/EBITDA": "Enterprise Value geteilt durch EBITDA. Bewertung unabhaengig von Kapitalstruktur - gut fuer Vergleiche.",
    "PEG": "KGV geteilt durch Gewinnwachstum. <1 = wachstumsbereinigt guenstig, >2 = teuer. Loest die KGV-Schwaeche bei Wachstumswerten.",
    "ROE": "Return on Equity. Reingewinn / Eigenkapital. Rendite auf das Aktionaerskapital. >15% gut.",
    "ROCE": "Return on Capital Employed. EBIT / eingesetztes Kapital. Misst Kapitaleffizienz. >15% sehr gut.",
    "FCF": "Free Cash Flow. Operativer Cashflow minus Investitionen. Das Geld, das wirklich uebrig bleibt.",
    "FCF Conversion": "FCF / Net Income. Wie viel des Buchgewinns als echter Cash ankommt. >90% exzellent.",
    "Net Debt/EBITDA": "Nettoverschuldung / EBITDA. Wie viele EBITDA-Jahre zum Schuldenabbau noetig. <1 stark, >3 riskant.",
    "Bruttomarge": "Bruttogewinn / Umsatz. Signalisiert Preissetzungsmacht. Software 70-85%, Retail 20-35%.",
    "Sharpe Ratio": "Ueberrendite (ueber risikofreiem Zins) geteilt durch Volatilitaet. Rendite pro Einheit Risiko. >1 gut, >2 aussergewoehnlich.",
    "Max Drawdown": "Groesster Wertverlust vom Hoch zum Tief. Misst das emotionale Worst-Case-Erlebnis.",
    "CAGR": "Compound Annual Growth Rate. Durchschnittliche jaehrliche Wachstumsrate ueber einen Zeitraum.",
    "Volatilitaet": "Schwankungsbreite der Renditen (Standardabweichung). Hoeher = riskanter.",
    "Moat": "Wirtschaftlicher Burggraben. Dauerhafter Wettbewerbsvorteil (Marke, Netzwerk, Kosten).",
    "XIRR": "Geldgewichtete Rendite. Beruecksichtigt Zeitpunkt UND Hoehe jeder Ein-/Auszahlung - die ehrliche Depot-Rendite bei Sparplan.",
}


# ============================================================
#  MAKRO-EINFLUSSFAKTOREN
# ============================================================
MACRO_FACTORS = [
    {"key": "zinsen_hoch", "name": "Zinsniveau steigend", "desc": "Hoehere Zinsen belasten Wachstumswerte & verschuldete Firmen.",
     "sectors": ["Technology", "Real Estate", "Utilities", "Financial Services", "Communication Services"], "default": -2.0},
    {"key": "zinsen_tief", "name": "Zinsniveau fallend", "desc": "Fallende Zinsen helfen Wachstum & Immobilien.",
     "sectors": ["Technology", "Real Estate", "Utilities", "Communication Services"], "default": 2.0},
    {"key": "inflation", "name": "Hohe Inflation", "desc": "Belastet Firmen ohne Preissetzungsmacht; hilft Rohstoff/Energie.",
     "sectors": ["Consumer Defensive", "Consumer Cyclical", "Energy", "Basic Materials"], "default": -1.0},
    {"key": "bip", "name": "Starkes BIP-Wachstum", "desc": "Treibt zyklische Branchen.",
     "sectors": ["Industrials", "Consumer Cyclical", "Basic Materials", "Financial Services"], "default": 2.0},
    {"key": "ki", "name": "KI-Adoption (Rueckenwind)", "desc": "Strukturelles Wachstum fuer Tech/Halbleiter/Cloud.",
     "sectors": ["Technology", "Communication Services"], "default": 3.0},
    {"key": "energie_hoch", "name": "Hohe Energiepreise", "desc": "Hilft Energie, belastet energieintensive Industrie.",
     "sectors": ["Energy", "Industrials", "Basic Materials"], "default": 1.0},
    {"key": "regulierung", "name": "Verschaerfte Regulierung", "desc": "Belastet Banken, Big Tech, Pharma.",
     "sectors": ["Financial Services", "Technology", "Healthcare", "Communication Services"], "default": -2.0},
    {"key": "demografie", "name": "Alternde Bevoelkerung", "desc": "Rueckenwind fuer Healthcare/Pharma.",
     "sectors": ["Healthcare"], "default": 2.0},
    {"key": "konsum", "name": "Starke Konsumlaune", "desc": "Treibt zyklischen Konsum.",
     "sectors": ["Consumer Cyclical", "Consumer Defensive"], "default": 1.5},
    {"key": "usd_stark", "name": "Starker US-Dollar", "desc": "Belastet US-Exporteure.",
     "sectors": ["Technology", "Industrials", "Consumer Cyclical"], "default": -1.0},
    {"key": "china_schwach", "name": "Schwache China-Nachfrage", "desc": "Belastet Firmen mit hohem China-Exposure.",
     "sectors": ["Technology", "Consumer Cyclical", "Basic Materials", "Industrials"], "default": -1.5},
    {"key": "defense", "name": "Steigende Verteidigungsbudgets", "desc": "Rueckenwind fuer Ruestung/Industrie.",
     "sectors": ["Industrials"], "default": 2.0},
]
def relevant_factors(sector):
    rel = [f for f in MACRO_FACTORS if sector in f["sectors"]]
    return rel if rel else MACRO_FACTORS[:4]


# ============================================================
#  QUALITATIVE TEMPLATES
# ============================================================
QUAL_SECTIONS = [
    ("geschaeft", "Geschaeftsmodell & Segmente",
     "Was verkauft die Firma? Umsatzsegmente, Margen je Segment, Geografie. Wie genau wird Geld verdient?"),
    ("chancen", "Chancen / Wachstumstreiber",
     "Strukturelle Treiber, neue Maerkte/Produkte, Preissetzungsmacht, TAM-Wachstum, Skaleneffekte."),
    ("risiken", "Risiken",
     "Wettbewerb, Regulierung, Disruption, Kundenkonzentration, Verschuldung, Zyklik, Klumpenrisiken."),
    ("moat", "Moat (Burggraben)",
     "Marke / Netzwerkeffekte / Skalen- & Kostenvorteile / Wechselkosten / immaterielle Werte. Wie breit & dauerhaft?"),
    ("branche", "Branche & Wettbewerb (Porter)",
     "Rivalitaet, Eintrittsbarrieren, Lieferantenmacht, Abnehmermacht, Substitute. Marktposition vs. Peers."),
    ("management", "Management & Kapitalallokation",
     "Track Record, Insider-Beteiligung, Umgang mit Kapital (Buybacks/Dividende/M&A/Capex), Verguetung, Offenheit."),
    ("szenarien", "Szenarien (Bull / Base / Bear)",
     "Bull / Base / Bear je mit Annahmen zu Wachstum, Marge, Multiple und grobem Kursziel."),
    ("katalysatoren", "Katalysatoren",
     "Was setzt den Wert frei und wann? Produktstart, Margenwende, Spin-off, Schuldenabbau, Index-Aufnahme."),
    ("bewertung", "Eigene Bewertung / Fazit",
     "Fairer Wert (eigene Schaetzung), Sicherheitsmarge, Wunsch-Kaufkurs, Positionsgroesse, Was wuerde These kippen?"),
]

CHECKLIST = [
    "Geschaeftsmodell in einem Satz erklaerbar",
    "Verstehe, wie das Unternehmen Geld verdient",
    "Dauerhafter Wettbewerbsvorteil (Moat) identifiziert",
    "Umsatz & FCF ueber 4+ Jahre gewachsen",
    "Solide Bilanz (Net Debt/EBITDA < 3)",
    "Management vertrauenswuerdig & gut im Kapitaleinsatz",
    "Hauptrisiken benannt und tragbar",
    "Bewertung geprueft (PEG / Multiples)",
    "Zahlen gegen Geschaeftsbericht gegengeprueft",
    "Ueberzeugung: wuerde bei Kursrueckgang nachkaufen",
]


# ============================================================
#  MONETARISIERUNG (Plaene)
# ============================================================
PLANS = [
    {"name": "Free", "price": "0 EUR", "per": "fuer immer", "popular": False,
     "features": ["Quant-Scorecard & Fazit", "Kennzahlen-Diagramme", "Qualitative Templates",
                  "Watchlist (bis 5 Titel)", "1 Portfolio-Backtest / Sitzung"]},
    {"name": "Plus", "price": "7,99 EUR", "per": "/ Monat", "popular": True,
     "features": ["Alles aus Free", "KI-Unternehmensueberblick", "Investment-Memo Export (.md/PDF)",
                  "Unbegrenzte Watchlist & Backtests", "Mein-Depot: XIRR + Depot-Backtest", "Werbefrei"]},
    {"name": "Pro", "price": "19,99 EUR", "per": "/ Monat", "popular": False,
     "features": ["Alles aus Plus", "Audit-grade Daten (FMP statt Yahoo)", "Peer-Vergleich & Sektor-Benchmarks",
                  "Excel-/PDF-Reports im Branding", "API-Zugang", "Prioritaets-Support"]},
]
def is_pro():
    return str(st.session_state.get("plan", "Pro (Vorschau)")).lower().startswith("pro")


# ============================================================
#  REAL-DEPOT: Beispiel-Bestand (editierbar in der App)
# ============================================================
# Hinweis: Bei Gold-ETC und US-Einzelaktien ist der korrekte EUR-Kurs vorbefuellt
# (Spalte "Kurs EUR"), weil der freie Yahoo-Ticker hier in USD/falscher Skala notiert
# bzw. von deinem Broker-EUR-Kurs (gettex) abweicht. Auf 0 setzen = Live-Kurs verwenden.
EXAMPLE_HOLDINGS = [
    ("iShares Core MSCI World (Acc)", "EUNL.DE", 13.0, "EUR", 0.0),
    ("iShares Physical Gold ETC", "SGLN.DE", 19.0, "EUR", 76.14),
    ("iShares Core MSCI EM IMI (Acc)", "IS3N.DE", 1.0, "EUR", 0.0),
    ("Pinduoduo ADR", "PDD", 2.0, "USD", 83.30),
    ("Meta Platforms A", "META", 2.0, "USD", 529.05),
    ("Microsoft", "MSFT", 1.0, "USD", 362.60),
    ("Bitcoin", "BTC-EUR", 0.0558354458, "EUR", 0.0),
    ("Ethereum", "ETH-EUR", 0.406690981052876, "EUR", 0.0),
    ("XRP", "XRP-EUR", 888.69133584, "EUR", 0.0),
    ("Solana", "SOL-EUR", 1.31599390784079, "EUR", 0.0),
    ("Cardano", "ADA-EUR", 109.02367476, "EUR", 0.0),
    ("Sui", "SUI-EUR", 4.26596097848622, "EUR", 0.0),
]

MARKET_INDICES = [
    ("^GSPC", "S&P 500"), ("^NDX", "Nasdaq 100"), ("^DJI", "Dow Jones"), ("^GDAXI", "DAX"),
    ("^STOXX50E", "Euro Stoxx 50"), ("^FTSE", "FTSE 100"), ("^N225", "Nikkei 225"), ("^VIX", "VIX (Angst)"),
    ("BTC-EUR", "Bitcoin"), ("ETH-EUR", "Ethereum"), ("GC=F", "Gold"), ("CL=F", "Oel (WTI)"),
    ("EURUSD=X", "EUR/USD"), ("^TNX", "US 10J-Zins"),
]


# ============================================================
#  DATEN-HELFER
# ============================================================
def pick(df, *names):
    if df is None or getattr(df, "empty", True):
        return None
    for n in names:
        if n in df.index:
            return df.loc[n]
    return None

def col(series, i):
    if series is None:
        return None
    try:
        v = series.iloc[i]
        if v is None or (isinstance(v, float) and v != v):
            return None
        return float(v) / 1e6
    except Exception:
        return None

def sdiv(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


@st.cache_data(ttl=3600, show_spinner=False)
def fetch(ticker):
    if yf is None:
        return None
    tk = yf.Ticker(ticker)
    info = tk.info or {}
    inc, bal, cf = tk.income_stmt, tk.balance_sheet, tk.cashflow
    cols = list(inc.columns) if (inc is not None and not inc.empty) else []
    n = min(len(cols), 4)
    if n == 0:
        return None
    years = []
    for c in cols[:n]:
        try:
            years.append(str(c.year))
        except Exception:
            years.append(str(c))
    sl = lambda s: [col(s, i) for i in range(n)][::-1]
    da = pick(cf, "Depreciation And Amortization", "Depreciation Amortization Depletion", "Depreciation")
    ocf = pick(cf, "Operating Cash Flow", "Total Cash From Operating Activities")
    capex = pick(cf, "Capital Expenditure", "CapitalExpenditures")
    return {
        "ticker": ticker.upper(), "name": info.get("longName") or info.get("shortName") or ticker.upper(),
        "sector": info.get("sector", "n/a"), "industry": info.get("industry", "n/a"),
        "currency": info.get("financialCurrency") or info.get("currency", "USD"),
        "country": info.get("country", ""), "website": info.get("website", ""),
        "employees": info.get("fullTimeEmployees"), "business_summary": info.get("longBusinessSummary", ""),
        "price": info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose"),
        "shares_m": (info.get("sharesOutstanding") or 0) / 1e6,
        "mcap_m": (info.get("marketCap") or 0) / 1e6, "ev_m": (info.get("enterpriseValue") or 0) / 1e6,
        "beta": info.get("beta"), "years": years[::-1],
        "revenue": sl(pick(inc, "Total Revenue")), "cogs": sl(pick(inc, "Cost Of Revenue")),
        "ebit": sl(pick(inc, "Operating Income", "EBIT")),
        "ebitda_raw": sl(pick(inc, "EBITDA", "Normalized EBITDA")), "da": sl(da),
        "interest": sl(pick(inc, "Interest Expense")),
        "netincome": sl(pick(inc, "Net Income", "Net Income Common Stockholders")),
        "shares_diluted": sl(pick(inc, "Diluted Average Shares")),
        "cash": sl(pick(bal, "Cash And Cash Equivalents")), "inventory": sl(pick(bal, "Inventory")),
        "cur_assets": sl(pick(bal, "Current Assets")), "tot_assets": sl(pick(bal, "Total Assets")),
        "cur_liab": sl(pick(bal, "Current Liabilities")),
        "st_debt": sl(pick(bal, "Current Debt", "Current Debt And Capital Lease Obligation")),
        "lt_debt": sl(pick(bal, "Long Term Debt", "Long Term Debt And Capital Lease Obligation")),
        "equity": sl(pick(bal, "Stockholders Equity", "Common Stock Equity")),
        "ocf": sl(ocf), "capex": sl(capex),
    }


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_prices(tickers, period="5y", start=None):
    """Historische (angepasste) Schlusskurse fuer Charts & Portfolio. start = ISO-Datum ueberschreibt period."""
    if yf is None:
        return None
    import time as _t, re as _re
    from datetime import datetime as _dt, timedelta as _td
    # yfinance kennt nur bestimmte Perioden (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max).
    # Nicht unterstuetzte wie '3y','4y','7y' in ein Startdatum umrechnen, sonst kommt leer zurueck.
    _VALID = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
    if start is None and period not in _VALID:
        _m = _re.match(r"^\s*(\d+)\s*y\s*$", str(period))
        if _m:
            start = (_dt.now() - _td(days=365 * int(_m.group(1)))).strftime("%Y-%m-%d")
            period = None
    def _raw(tk):                                  # Download mit Wiederholversuchen (gegen Drosselung)
        for _a in range(2):
            try:
                d = (yf.download(tk, start=start, progress=False, auto_adjust=True) if start
                     else yf.download(tk, period=period, progress=False, auto_adjust=True))
            except Exception:
                d = None
            if d is not None and not d.empty:
                return d
            _t.sleep(0.8 * (_a + 1))
        return None

    def _px(data, names):                          # Schlusskurse als DataFrame extrahieren
        if data is None or data.empty:
            return None
        if hasattr(data.columns, "levels"):
            lvl0 = data.columns.get_level_values(0)
            field = "Adj Close" if "Adj Close" in lvl0 else ("Close" if "Close" in lvl0 else None)
        else:
            field = "Adj Close" if "Adj Close" in data.columns else ("Close" if "Close" in data.columns else None)
        px = data[field] if field else data
        if isinstance(px, pd.Series):
            nm = names if isinstance(names, str) else (names[0] if names else "PX")
            px = px.to_frame(nm)
        return px

    px = _px(_raw(tickers), tickers)               # 1) Bulk-Versuch
    tlist = list(tickers) if isinstance(tickers, (list, tuple)) else [tickers]
    if (px is None or px.dropna(how="all").empty) and len(tlist) > 1:
        cols = {}                                  # 2) Fallback: jeden Ticker einzeln nachladen
        for tk in tlist:
            single = _px(_raw(tk), tk)
            if single is not None and not single.dropna(how="all").empty:
                cols[tk] = single.iloc[:, 0]
            _t.sleep(0.2)
        if cols:
            px = pd.DataFrame(cols)
    if px is None:
        return None
    return px.dropna(how="all")


@st.cache_data(ttl=900, show_spinner=False)
def latest_price(ticker):
    px = fetch_prices(ticker, "5d")
    if px is None or px.empty:
        return None
    ser = px.iloc[:, 0].dropna()
    return float(ser.iloc[-1]) if len(ser) else None


@st.cache_data(ttl=900, show_spinner=False)
def eurusd_rate():
    return latest_price("EURUSD=X")


@st.cache_data(ttl=900, show_spinner=False)
def market_history(symbols, period="1mo"):
    """Kursreihen fuer die Markt-Uebersicht (Mini-Charts + letzter Kurs/Veraenderung)."""
    return fetch_prices(list(symbols), period)


@st.cache_data(ttl=900, show_spinner=False)
def quote_search(ticker):
    """Sucht einen beliebigen Wert: 1-Monats-Kursreihe + letzter Kurs + Tagesveraenderung."""
    px = fetch_prices(ticker, "1mo")
    if px is None or px.empty:
        return None
    ser = px.iloc[:, 0].dropna()
    if len(ser) == 0:
        return None
    last = float(ser.iloc[-1])
    prev = float(ser.iloc[-2]) if len(ser) >= 2 else last
    return {"series": ser, "last": last, "chg": (last / prev - 1) if prev else 0.0}


# ============================================================
#  GELDGEWICHTETE RENDITE (XIRR) + WAEHRUNG
# ============================================================
def to_eur(price, currency, fx):
    if price is None:
        return None
    if currency and str(currency).upper() == "USD" and fx:
        return price / fx
    return price

def xnpv(rate, flows):
    if rate <= -1:
        rate = -0.999999
    t0 = min(d for d, _ in flows)
    return sum(cf / (1.0 + rate) ** ((d - t0).days / 365.0) for d, cf in flows)

def xirr(flows):
    amts = [a for _, a in flows]
    if len(flows) < 2 or min(amts) >= 0 or max(amts) <= 0:
        return None
    lo, hi = -0.9999, 10.0
    flo, fhi = xnpv(lo, flows), xnpv(hi, flows)
    if flo * fhi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2.0
        fmid = xnpv(mid, flows)
        if abs(fmid) < 1e-7:
            return mid
        if flo * fmid < 0:
            hi, fhi = mid, fmid
        else:
            lo, flo = mid, fmid
    return (lo + hi) / 2.0


# ============================================================
#  KENNZAHLEN
# ============================================================
def compute(d):
    n = len(d["years"])
    g = lambda k, i: (d[k][i] if d.get(k) and i < len(d[k]) else None)
    gross = [(g("revenue", i) - g("cogs", i)) if (g("revenue", i) is not None and g("cogs", i) is not None) else None for i in range(n)]
    ebitda = []
    for i in range(n):
        if g("ebitda_raw", i) is not None:
            ebitda.append(g("ebitda_raw", i))
        elif g("ebit", i) is not None and g("da", i) is not None:
            ebitda.append(g("ebit", i) + g("da", i))
        else:
            ebitda.append(None)
    fcf = [(g("ocf", i) + g("capex", i)) if (g("ocf", i) is not None and g("capex", i) is not None) else None for i in range(n)]
    eps = [sdiv(g("netincome", i), g("shares_diluted", i)) for i in range(n)]
    rows = {
        "Bruttomarge": [sdiv(gross[i], g("revenue", i)) for i in range(n)],
        "EBIT-Marge": [sdiv(g("ebit", i), g("revenue", i)) for i in range(n)],
        "EBITDA-Marge": [sdiv(ebitda[i], g("revenue", i)) for i in range(n)],
        "Nettomarge": [sdiv(g("netincome", i), g("revenue", i)) for i in range(n)],
        "FCF-Marge": [sdiv(fcf[i], g("revenue", i)) for i in range(n)],
        "ROE": [sdiv(g("netincome", i), g("equity", i)) for i in range(n)],
        "ROA": [sdiv(g("netincome", i), g("tot_assets", i)) for i in range(n)],
        "ROCE": [sdiv(g("ebit", i), (g("tot_assets", i) - g("cur_liab", i)) if (g("tot_assets", i) is not None and g("cur_liab", i) is not None) else None) for i in range(n)],
        "Net Debt/EBITDA": [sdiv(((g("st_debt", i) or 0) + (g("lt_debt", i) or 0) - (g("cash", i) or 0)), ebitda[i]) for i in range(n)],
        "Debt/Equity": [sdiv(((g("st_debt", i) or 0) + (g("lt_debt", i) or 0)), g("equity", i)) for i in range(n)],
        "Current Ratio": [sdiv(g("cur_assets", i), g("cur_liab", i)) for i in range(n)],
        "Interest Coverage": [sdiv(g("ebit", i), g("interest", i)) for i in range(n)],
        "FCF Conversion": [sdiv(fcf[i], g("netincome", i)) for i in range(n)],
        "Eigenkapitalquote": [sdiv(g("equity", i), g("tot_assets", i)) for i in range(n)],
    }
    price = d["price"]; ev = d["ev_m"]; latest = n - 1
    val_mult = {"KGV (P/E)": sdiv(price, eps[latest]) if eps[latest] else None,
                "EV/EBITDA": sdiv(ev, ebitda[latest]), "EV/FCF": sdiv(ev, fcf[latest]),
                "KBV (P/B)": sdiv(d.get("mcap_m"), g("equity", latest))}
    def cagr(v):
        a, b = v[0], v[-1]
        if a is None or b is None or a <= 0 or len(v) < 2:
            return None
        return (b / a) ** (1 / (len(v) - 1)) - 1
    cagrs = {"Umsatz-CAGR": cagr(d["revenue"]), "EPS-CAGR": cagr(eps), "FCF-CAGR": cagr(fcf)}
    return {"n": n, "gross": gross, "ebitda": ebitda, "fcf": fcf, "eps": eps,
            "rows": rows, "val_mult": val_mult, "cagrs": cagrs, "latest": latest}


# ============================================================
#  SCORING & FAZIT
# ============================================================
def score_hb(v, hi, lo): return None if v is None else (3 if v >= hi else (2 if v >= lo else 1))
def score_lb(v, hi, lo): return None if v is None else (3 if v <= hi else (2 if v <= lo else 1))

def verdict(q, val):
    if q is None or val is None:
        return "Unvollstaendige Daten"
    if q >= 0.7:
        if val >= 0.67: return "ATTRAKTIV: hohe Qualitaet + wachstumsbereinigt guenstig"
        if val >= 0.34: return "QUALITAET, fair bewertet - solide"
        return "QUALITAET, aber teuer - auf Korrektur warten"
    if q >= 0.5:
        return "DURCHWACHSEN + guenstig - genauer pruefen" if val >= 0.67 else "DURCHWACHSEN - genauer pruefen"
    return "VORSICHT: schwache Qualitaet, evtl. Value Trap" if val >= 0.67 else "UNATTRAKTIV: schwache Qualitaet + teuer"

def sector_kind(sector, industry=""):
    """Nur BILANZGETRIEBENE Finanzwerte (Banken & Versicherer) brauchen KBV/Eigenkapitalquote.
    Asset-light-Finanz (Zahlungsnetze, Boersen, Broker, Asset Manager) bleibt im Standard-Modus,
    weil dort Margen/EV-Multiples weiterhin sinnvoll sind."""
    ind = (industry or "").lower()
    if "bank" in ind:
        return "financial"
    if "insurance" in ind and "broker" not in ind:
        return "financial"
    if "versicher" in ind and "makler" not in ind:
        return "financial"
    return "standard"

def build_scorecard(m, gpct, kind="standard"):
    if kind == "financial":
        return _scorecard_financial(m, gpct)
    lt = m["latest"]; rows = m["rows"]; vm = m["val_mult"]; cg = m["cagrs"]
    prof = [("Bruttomarge", rows["Bruttomarge"][lt], score_hb(rows["Bruttomarge"][lt], 0.50, 0.30)),
            ("EBIT-Marge", rows["EBIT-Marge"][lt], score_hb(rows["EBIT-Marge"][lt], 0.20, 0.10)),
            ("Nettomarge", rows["Nettomarge"][lt], score_hb(rows["Nettomarge"][lt], 0.15, 0.08)),
            ("FCF-Marge", rows["FCF-Marge"][lt], score_hb(rows["FCF-Marge"][lt], 0.15, 0.05)),
            ("ROE", rows["ROE"][lt], score_hb(rows["ROE"][lt], 0.20, 0.12)),
            ("ROCE", rows["ROCE"][lt], score_hb(rows["ROCE"][lt], 0.15, 0.08))]
    health = [("Net Debt/EBITDA", rows["Net Debt/EBITDA"][lt], score_lb(rows["Net Debt/EBITDA"][lt], 1.0, 2.5)),
              ("Debt/Equity", rows["Debt/Equity"][lt], score_lb(rows["Debt/Equity"][lt], 0.5, 1.5)),
              ("Current Ratio", rows["Current Ratio"][lt], score_hb(rows["Current Ratio"][lt], 1.5, 1.0)),
              ("Interest Coverage", rows["Interest Coverage"][lt], score_hb(rows["Interest Coverage"][lt], 8.0, 3.0)),
              ("FCF Conversion", rows["FCF Conversion"][lt], score_hb(rows["FCF Conversion"][lt], 0.90, 0.70))]
    growth = [("Umsatz-CAGR", cg["Umsatz-CAGR"], score_hb(cg["Umsatz-CAGR"], 0.10, 0.04)),
              ("EPS-CAGR", cg["EPS-CAGR"], score_hb(cg["EPS-CAGR"], 0.10, 0.04)),
              ("FCF-CAGR", cg["FCF-CAGR"], score_hb(cg["FCF-CAGR"], 0.10, 0.04))]
    valuation = [("KGV (P/E)", vm["KGV (P/E)"], score_lb(vm["KGV (P/E)"], 15.0, 25.0)),
                 ("EV/EBITDA", vm["EV/EBITDA"], score_lb(vm["EV/EBITDA"], 10.0, 15.0)),
                 ("EV/FCF", vm["EV/FCF"], score_lb(vm["EV/FCF"], 20.0, 30.0))]
    ssum = lambda l: sum(s for _, _, s in l if s is not None)
    ps, hs, gs, vas = ssum(prof), ssum(health), ssum(growth), ssum(valuation)
    quality = (ps + hs + gs) / 42
    kgv = vm["KGV (P/E)"]
    peg = (kgv / gpct) if (kgv and gpct and gpct > 0) else None
    pscore = (3 if peg <= 1 else (2 if peg <= 2 else 1)) if peg is not None else None
    value_adj = (pscore * 2 + vas) / 15 if pscore is not None else vas / 9
    return {"prof": prof, "health": health, "growth": growth, "valuation": valuation,
            "prof_s": ps, "health_s": hs, "growth_s": gs, "val_abs_s": vas,
            "prof_max": 18, "health_max": 15, "growth_max": 9, "val_max": 9, "kind": "standard",
            "quality": quality, "value_adj": value_adj, "peg": peg, "peg_score": pscore,
            "verdict": verdict(quality, value_adj)}


def _scorecard_financial(m, gpct):
    """Sektor-Variante fuer Banken/Versicherer: KBV & Eigenkapitalquote statt KGV/EV-EBITDA/Net-Debt
    (diese passen fuer Finanzwerte strukturell nicht)."""
    lt = m["latest"]; rows = m["rows"]; vm = m["val_mult"]; cg = m["cagrs"]
    prof = [("ROE", rows["ROE"][lt], score_hb(rows["ROE"][lt], 0.12, 0.08)),
            ("ROA", rows["ROA"][lt], score_hb(rows["ROA"][lt], 0.012, 0.008)),
            ("Nettomarge", rows["Nettomarge"][lt], score_hb(rows["Nettomarge"][lt], 0.20, 0.10))]
    health = [("Eigenkapitalquote", rows["Eigenkapitalquote"][lt],
               score_hb(rows["Eigenkapitalquote"][lt], 0.10, 0.06))]
    growth = [("Umsatz-CAGR", cg["Umsatz-CAGR"], score_hb(cg["Umsatz-CAGR"], 0.08, 0.03)),
              ("EPS-CAGR", cg["EPS-CAGR"], score_hb(cg["EPS-CAGR"], 0.08, 0.03))]
    valuation = [("KBV (P/B)", vm.get("KBV (P/B)"), score_lb(vm.get("KBV (P/B)"), 1.2, 2.0)),
                 ("KGV (P/E)", vm["KGV (P/E)"], score_lb(vm["KGV (P/E)"], 12.0, 18.0))]
    ssum = lambda l: sum(s for _, _, s in l if s is not None)
    smax = lambda l: 3 * sum(1 for _, _, s in l if s is not None)
    ps, hs, gs = ssum(prof), ssum(health), ssum(growth)
    qmax = smax(prof) + smax(health) + smax(growth)
    quality = (ps + hs + gs) / qmax if qmax else None
    vas = ssum(valuation); vmax = smax(valuation)
    kgv = vm["KGV (P/E)"]
    peg = (kgv / gpct) if (kgv and gpct and gpct > 0) else None
    pscore = (3 if peg <= 1 else (2 if peg <= 2 else 1)) if peg is not None else None
    if pscore is not None and vmax:
        value_adj = (pscore * 2 + vas) / (6 + vmax)
    elif vmax:
        value_adj = vas / vmax
    else:
        value_adj = None
    return {"prof": prof, "health": health, "growth": growth, "valuation": valuation,
            "prof_s": ps, "health_s": hs, "growth_s": gs, "val_abs_s": vas,
            "prof_max": smax(prof), "health_max": smax(health), "growth_max": smax(growth),
            "val_max": vmax, "kind": "financial",
            "quality": quality, "value_adj": value_adj, "peg": peg, "peg_score": pscore,
            "verdict": verdict(quality, value_adj)}


def verification_flags(m, d, gpct):
    flags = []; lt = m["latest"]; rows = m["rows"]
    flags += [("Nettomarge / Net Income", "immer", "Yahoo bereinigt Einmaleffekte oft NICHT - gegen GuV pruefen."),
              ("EBITDA & Multiples", "immer", "EBITDA-Berechnung variiert; wird approximiert wenn D&A fehlt."),
              ("Wachstum / CAGR", "immer", "Nur 4 Jahre; CAGR von einem Tief-/Hochpunkt verzerrt stark."),
              ("EPS / Aktienzahl", "immer", "Aktienzahl Stichtag vs. gewichtet - relevant bei Rueckkaeufern.")]
    nm = rows["Nettomarge"][lt]
    if nm is not None and nm > 0.45: flags.append(("Nettomarge auffaellig hoch", "auffaellig", f"{nm*100:.1f}% - Einmaleffekt? pruefen."))
    if nm is not None and nm < 0: flags.append(("Nettomarge negativ", "auffaellig", "Verlustjahr - Ursache pruefen."))
    roe = rows["ROE"][lt]
    if roe is not None and roe > 0.60: flags.append(("ROE >60%", "auffaellig", "Oft Buyback-geschrumpftes Eigenkapital - mit ROA/ROCE pruefen."))
    nde = rows["Net Debt/EBITDA"][lt]
    if nde is not None and nde < 0: flags.append(("Net Debt/EBITDA negativ", "auffaellig", "Netto-Cash - positiv, im Kontext lesen."))
    if gpct is not None and gpct > 25: flags.append(("Wachstumsannahme >25%", "auffaellig", f"{gpct:.0f}% - selten dauerhaft. Realistisch schaetzen."))
    for name in ["Bruttomarge", "EBITDA-Marge", "FCF-Marge", "ROCE", "Net Debt/EBITDA", "Interest Coverage", "FCF Conversion"]:
        if rows[name][lt] is None: flags.append((f"{name}: kein Wert", "fehlend", "Yahoo liefert keine Daten - manuell ergaenzen."))
    for k, lab in [("Umsatz-CAGR", "Umsatz-CAGR"), ("EPS-CAGR", "EPS-CAGR"), ("FCF-CAGR", "FCF-CAGR")]:
        if m["cagrs"][k] is None: flags.append((f"{lab}: nicht berechenbar", "fehlend", "Negativer Startwert oder fehlende Daten."))
    return flags


# ============================================================
#  KI-UEBERBLICK
# ============================================================
def get_api_key():
    try:
        k = st.secrets.get("OPENAI_API_KEY")
        if k: return k
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY")

def ai_summary(data, m):
    business = (data.get("business_summary") or "").strip()
    key = get_api_key()
    if not key:
        return (business, "yahoo") if business else ("", "none")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key); lt = m["latest"]
        facts = (f"Name: {data['name']} ({data['ticker']})\nSektor: {data['sector']}, Branche: {data['industry']}\n"
                 f"Bruttomarge: {fmt_pct(m['rows']['Bruttomarge'][lt])}, EBIT-Marge: {fmt_pct(m['rows']['EBIT-Marge'][lt])}, "
                 f"Nettomarge: {fmt_pct(m['rows']['Nettomarge'][lt])}\nROE: {fmt_pct(m['rows']['ROE'][lt])}, "
                 f"Umsatz-CAGR: {fmt_pct(m['cagrs']['Umsatz-CAGR'])}\n")
        if business:
            facts += f"Beschreibung (Yahoo): {business[:1800]}"
            rule = "Stuetze dich auf Beschreibung + Kennzahlen. Erfinde keine Zahlen."
        else:
            facts += "Beschreibung: (von Yahoo nicht geliefert)"
            rule = "Keine Beschreibung vorhanden - nutze dein Wissen ueber die Firma. Keine erfundenen Finanzzahlen. Falls unbekannt, sag es."
        prompt = ("Strukturierter, analytischer Unternehmens-Ueberblick auf Deutsch fuer Investoren. Sachlich, kein Hype, "
                  f"KEINE Kaufempfehlung. {rule}\n\nStruktur (Markdown):\n**Was das Unternehmen macht**\n"
                  "**Wettbewerbsvorteil (Moat)**\n**Markt & Wettbewerb**\n**Wichtigste Risiken**\n\n" + f"Fakten:\n{facts}")
        resp = client.chat.completions.create(model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}], max_tokens=550, temperature=0.3)
        return (resp.choices[0].message.content.strip(), "ki")
    except Exception as e:
        return (business + f"\n\n_(KI nicht verfuegbar: {e})_" if business else f"KI-Fehler: {e}", "yahoo" if business else "none")


def ai_tutor(question, context=""):
    """KI-Lerntutor fuer Fundamentalanalyse. Gibt (antwort, status) zurueck.

    status: 'no_key' (kein Schluessel gesetzt), 'ki' (Antwort von der KI),
            'error' (Aufruf fehlgeschlagen)."""
    q = (question or "").strip()
    if not q:
        return ("Bitte stelle eine Frage zur Fundamentalanalyse.", "empty")
    key = get_api_key()
    if not key:
        return ("", "no_key")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        system = ("Du bist ein geduldiger, freundlicher Tutor fuer FUNDAMENTALANALYSE und Portfolio-Grundlagen fuer "
                  "private Anleger. Erklaere auf Deutsch, einfach und mit konkreten Beispielen, als wuerdest du es einem "
                  "Anfaenger erklaeren. WICHTIGE REGELN: (1) Gib NIEMALS eine Anlageberatung, keine Kauf- oder "
                  "Verkaufsempfehlung und keine Kursprognose fuer eine konkrete Aktie. (2) Bewerte keine konkrete "
                  "Aktie als 'kaufen/verkaufen/halten'. (3) Wenn jemand danach fragt, erklaere stattdessen die "
                  "METHODE, wie man es selbst beurteilt. (4) Bleibe sachlich, kein Hype. (5) Wenn du etwas nicht "
                  "sicher weisst, sag es. Antworte praegnant (meist 4-10 Saetze), nutze bei Bedarf Markdown.")
        user = (f"Kontext aus der aktuellen Lektion: {context}\n\n" if context else "") + f"Frage des Lernenden: {q}"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=600, temperature=0.4)
        return (resp.choices[0].message.content.strip(), "ki")
    except Exception as e:
        return (f"KI-Tutor nicht verfuegbar: {e}", "error")


# ============================================================
#  NEWS (rechtssicher: nur Schlagzeile + Kurzauszug + Quelle + Link)
# ============================================================
NEWS_PROVIDERS = {"finnhub": "Finnhub", "marketaux": "Marketaux"}

def get_news_key():
    try:
        k = st.secrets.get("NEWS_API_KEY")
        if k:
            return k
    except Exception:
        pass
    return os.environ.get("NEWS_API_KEY")

def get_news_provider():
    p = None
    try:
        p = st.secrets.get("NEWS_PROVIDER")
    except Exception:
        p = None
    p = (p or os.environ.get("NEWS_PROVIDER") or "finnhub").strip().lower()
    return p if p in NEWS_PROVIDERS else "finnhub"

def news_provider_label(provider):
    return NEWS_PROVIDERS.get((provider or "").lower(), provider or "Quelle")

def _news_shorten(s, n):
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"

def _news_date(val):
    """Akzeptiert Unix-Timestamp (int/float) oder ISO-String, gibt 'TT.MM.JJJJ' zurueck."""
    from datetime import datetime, timezone
    try:
        if isinstance(val, (int, float)) and val:
            return datetime.fromtimestamp(float(val), tz=timezone.utc).strftime("%d.%m.%Y")
        s = str(val)[:10]
        return datetime.strptime(s, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return ""

def normalize_news_items(raw, provider, max_items=10, max_summary=220):
    """Wandelt Provider-Rohdaten in einheitliche, rechtssichere Kurzeintraege um.
    Zeigt NUR Titel, kurzen Auszug, Quelle, Datum und Link - niemals den Volltext."""
    items = []
    if provider == "marketaux":
        data = raw.get("data", []) if isinstance(raw, dict) else (raw or [])
        for d in data:
            ents = d.get("entities") or []
            ticks = [e.get("symbol") for e in ents if e.get("symbol")]
            items.append({
                "title": (d.get("title") or "").strip(),
                "summary": _news_shorten(d.get("description") or d.get("snippet") or "", max_summary),
                "source": (d.get("source") or "").strip(),
                "url": (d.get("url") or "").strip(),
                "published": _news_date(d.get("published_at") or ""),
                "tickers": ticks,
            })
    else:  # finnhub (Standard)
        data = raw if isinstance(raw, list) else (raw.get("data", []) if isinstance(raw, dict) else [])
        for d in data:
            rel = d.get("related") or ""
            ticks = [x for x in str(rel).split(",") if x]
            items.append({
                "title": (d.get("headline") or "").strip(),
                "summary": _news_shorten(d.get("summary") or "", max_summary),
                "source": (d.get("source") or "").strip(),
                "url": (d.get("url") or "").strip(),
                "published": _news_date(d.get("datetime") or 0),
                "tickers": ticks,
            })
    seen = set(); out = []
    for it in items:
        if not it["title"] or not it["url"] or it["url"] in seen:
            continue
        seen.add(it["url"]); out.append(it)
    return out[:max_items]

def fetch_company_news(tickers, provider=None, key=None, max_items=10):
    """Holt News von einer lizenzierten Quelle. Gibt (items, status) zurueck.
    status: 'no_key' | 'empty' | 'ok' | 'error'."""
    provider = (provider or get_news_provider())
    key = key or get_news_key()
    if not key:
        return ([], "no_key")
    tickers = [str(t).strip().upper() for t in (tickers or []) if str(t).strip()]
    if not tickers:
        return ([], "empty")
    import json as _json, urllib.request as _req, urllib.parse as _parse
    from datetime import datetime, timedelta

    def _get(url):
        r = _req.Request(url, headers={"User-Agent": "FinAnalyse/1.0"})
        with _req.urlopen(r, timeout=8) as resp:
            return _json.loads(resp.read().decode("utf-8"))

    try:
        if provider == "marketaux":
            qs = _parse.urlencode({"symbols": ",".join(tickers[:20]), "filter_entities": "true",
                                   "language": "en,de", "limit": 20, "api_token": key})
            items = normalize_news_items(_get("https://api.marketaux.com/v1/news/all?" + qs),
                                         "marketaux", max_items=max_items)
        else:
            frm = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
            to = datetime.utcnow().strftime("%Y-%m-%d")
            merged = []
            for tk in tickers[:8]:
                qs = _parse.urlencode({"symbol": tk, "from": frm, "to": to, "token": key})
                try:
                    part = _get("https://finnhub.io/api/v1/company-news?" + qs)
                    if isinstance(part, list):
                        merged.extend(part[:4])
                except Exception:
                    continue
            items = normalize_news_items(merged, "finnhub", max_items=max_items)
        return (items, "ok" if items else "empty")
    except Exception:
        return ([], "error")

def depot_news_tickers():
    """Tickerliste fuers Depot-News-Modul: aus dem bearbeiteten Depot, sonst Beispiel-Depot."""
    ts = st.session_state.get("depot_tickers")
    if ts:
        return ts
    return [tk for _n, tk, *_rest in EXAMPLE_HOLDINGS]

@st.cache_data(ttl=900, show_spinner=False)
def cached_company_news(tickers, provider, key):
    """Gecachte News-Abfrage (15 Min), damit nicht bei jedem Rerun neu geladen wird."""
    return fetch_company_news(list(tickers), provider, key)


# ============================================================
#  PORTFOLIO-MATHEMATIK
# ============================================================
def backtest_portfolio(prices, weights, rf=0.03):
    rets = prices.pct_change().dropna()
    w = pd.Series(weights).reindex(rets.columns).fillna(0.0)
    if w.sum() > 0:
        w = w / w.sum()
    port = (rets * w).sum(axis=1)
    equity = (1 + port).cumprod()
    ann_ret = port.mean() * 252
    ann_vol = port.std() * np.sqrt(252)
    sharpe = (ann_ret - rf) / ann_vol if ann_vol and ann_vol > 0 else None
    running_max = equity.cummax()
    dd = (equity - running_max) / running_max
    return {"equity": equity, "ann_ret": ann_ret, "ann_vol": ann_vol,
            "sharpe": sharpe, "max_dd": dd.min(), "port_returns": port}

def project_portfolio(start_value, ann_ret, ann_vol, years):
    pts = list(range(years + 1))
    base = [start_value * (1 + ann_ret) ** y for y in pts]
    cons = [start_value * (1 + max(ann_ret - ann_vol, -0.5)) ** y for y in pts]
    opt = [start_value * (1 + ann_ret + ann_vol) ** y for y in pts]
    return pts, base, cons, opt


def project_series(latest_value, growth_pct, years=5):
    out = []; v = latest_value
    for _ in range(years):
        v = v * (1 + growth_pct / 100.0)
        out.append(v)
    return out


# ============================================================
#  FORMAT & HTML-BAUSTEINE
# ============================================================
def fmt_pct(v): return "-" if v is None else f"{v*100:.1f}%"
def fmt_x(v): return "-" if v is None else f"{v:.1f}"
def fmt_num(v): return "-" if v is None else f"{v:,.0f}"
def badge(s): return "grau" if s is None else {3: "stark", 2: "solide", 1: "schwach"}[s]
def fmt_quote(v):
    if v is None:
        return "-"
    av = abs(v)
    if av >= 1000: return f"{v:,.0f}"
    if av >= 10: return f"{v:,.2f}"
    return f"{v:,.4f}"

PILL = {3: ("stark", "#166534", "var(--fa-green-bg)"),
        2: ("solide", "#92400e", "var(--fa-amber-bg)"),
        1: ("schwach", "#991b1b", "var(--fa-red-bg)")}
def badge_html(s):
    if s is None:
        return '<span class="fa-pill" style="background:#e2e8f0;color:#475569">k.A.</span>'
    lbl, fg, bg = PILL[s]
    return f'<span class="fa-pill" style="background:{bg};color:{fg}">{lbl}</span>'

def scorecard_table_html(title, items, pct):
    rows = ""
    for nm, vv, s in items:
        val = fmt_pct(vv) if nm in pct else fmt_x(vv)
        sc = s if s else "-"
        rows += (f'<tr><td>{nm}</td>'
                 f'<td style="text-align:right;font-variant-numeric:tabular-nums">{val}</td>'
                 f'<td style="text-align:center">{sc}</td><td>{badge_html(s)}</td></tr>')
    return (f'<div class="fa-secttitle">{title}</div>'
            '<table class="fa-table"><thead><tr><th>Kennzahl</th>'
            '<th style="text-align:right">Wert</th><th style="text-align:center">Score</th>'
            f'<th>Bewertung</th></tr></thead><tbody>{rows}</tbody></table>')

def verdict_banner_html(v):
    if "UNATTRAKTIV" in v or "VORSICHT" in v:
        bg, fg = "var(--fa-red-bg)", "#991b1b"
    elif "ATTRAKTIV" in v:
        bg, fg = "var(--fa-green-bg)", "#166534"
    elif "teuer" in v:
        bg, fg = "var(--fa-amber-bg)", "#92400e"
    else:
        bg, fg = "#e0f2fe", "#075985"
    return f'<div class="fa-verdict" style="background:{bg};color:{fg}">FAZIT: {v}</div>'

def verdict_short(v):
    if "UNATTRAKTIV" in v: return ("UNATTRAKTIV", "#991b1b", "var(--fa-red-bg)")
    if "VORSICHT" in v: return ("VORSICHT", "#991b1b", "var(--fa-red-bg)")
    if "ATTRAKTIV" in v: return ("ATTRAKTIV", "#166534", "var(--fa-green-bg)")
    if "teuer" in v: return ("ZU TEUER", "#92400e", "var(--fa-amber-bg)")
    if "DURCHWACHSEN" in v: return ("DURCHWACHSEN", "#92400e", "var(--fa-amber-bg)")
    if "QUALITAET" in v: return ("SOLIDE", "#075985", "#e0f2fe")
    return ("PRUEFEN", "#475569", "#e2e8f0")

def dash_pill_html(v):
    lbl, fg, bg = verdict_short(v)
    return f'<span class="fa-pill" style="background:{bg};color:{fg}">{lbl}</span>'

def locked_card_html(title, desc):
    return (f'<div class="lock-card"><b>{title}</b> &nbsp;'
            '<span class="fa-pill" style="background:#1e293b;color:#fff">PRO</span>'
            f'<br><span style="font-size:.9rem">{desc}</span></div>')

def price_card_html(plan):
    feats = "".join(f"<li>{f}</li>" for f in plan["features"])
    cls = "price-card popular" if plan["popular"] else "price-card"
    return (f'<div class="{cls}"><h3>{plan["name"]}</h3>'
            f'<div class="price">{plan["price"]}</div><div class="per">{plan["per"]}</div>'
            f'<ul>{feats}</ul></div>')


# ============================================================
#  DASHBOARD-HELFER
# ============================================================
def watchlist_row(tk):
    try:
        d = fetch(tk)
        if d is None:
            return {"ticker": tk, "ok": False}
        m = compute(d)
        g = m["cagrs"]["EPS-CAGR"]
        base = round(g * 100, 1) if g else 10.0
        sc = build_scorecard(m, base, sector_kind(d.get("sector"), d.get("industry")))
        return {"ticker": tk, "name": d.get("name", tk), "q": sc["quality"],
                "v": sc["value_adj"], "peg": sc["peg"], "verdict": sc["verdict"], "ok": True}
    except Exception:
        return {"ticker": tk, "ok": False}


def holdings_values(holdings, fx):
    """Aktueller EUR-Wert je Ticker aus den Depot-Positionen (Override oder Live)."""
    wval = {}
    for _, r in holdings.iterrows():
        tk = str(r.get("Ticker") or "").strip().upper()
        if not tk:
            continue
        try:
            stk = float(r.get("Stueck") or 0)
        except Exception:
            stk = 0.0
        cur = str(r.get("Waehrung") or "EUR").strip()
        try:
            ov = float(r.get("Kurs EUR (0=live)") or 0)
        except Exception:
            ov = 0.0
        pe = ov if ov > 0 else to_eur(latest_price(tk), cur, fx)
        if pe and stk > 0:
            wval[tk] = wval.get(tk, 0.0) + stk * pe
    return wval


def portfolio_value_series(prices, qty, currencies, fx_series=None):
    """EUR-Wertverlauf der aktuellen Stueckzahlen ueber die Zeit.
    prices: DataFrame (Spalten=Ticker). qty/currencies: dict ticker->Stueck/Waehrung.
    fx_series: EURUSD-Reihe (USD je EUR) zur Umrechnung von USD-Positionen."""
    cols = getattr(prices, "columns", [])
    total = None
    for tk, q in qty.items():
        if tk not in cols or q <= 0:
            continue
        s = prices[tk].astype(float)
        if str(currencies.get(tk, "EUR")).upper() == "USD" and fx_series is not None:
            s = s / fx_series.reindex(s.index).ffill()
        contrib = q * s
        total = contrib if total is None else (total + contrib)
    if total is None:
        return None
    return total.dropna()


# ============================================================
#  REBALANCING & RISIKOPROFIL
# ============================================================
BUCKETS = ["Breite ETFs", "Einzelaktien", "Krypto", "Gold/Defensiv"]
CRYPTO_BASES = {"BTC", "ETH", "XRP", "SOL", "ADA", "SUI", "DOGE", "DOT", "LTC", "BCH",
                "AVAX", "MATIC", "LINK", "TRX", "XLM", "XMR", "ATOM", "NEAR", "APT", "ARB"}

def classify_asset(name, ticker):
    """Ordnet eine Position einer Anlageklasse zu (Heuristik)."""
    n = (name or "").lower(); tk = (ticker or "").upper()
    base = tk.split("-")[0].split(".")[0]
    if "-EUR" in tk or "-USD" in tk or base in CRYPTO_BASES or "bitcoin" in n or "ethereum" in n:
        return "Krypto"
    if "gold" in n or "silver" in n or "physical" in n or "bond" in n or "anleih" in n or "treasury" in n:
        return "Gold/Defensiv"
    if any(w in n for w in ["msci", "ftse", "s&p", "etf", "etc", "index", "core ", "stoxx",
                            "world", "emerging", "ucits", "nasdaq", "dax"]):
        return "Breite ETFs"
    return "Einzelaktien"

def target_allocation(risk, growth):
    """risk, growth in 0..100 -> Ziel-Gewichte je Anlageklasse (Summe 1)."""
    r = max(0.0, min(1.0, risk / 100.0))
    cons = {"Breite ETFs": 0.60, "Gold/Defensiv": 0.25, "Einzelaktien": 0.10, "Krypto": 0.05}
    aggr = {"Breite ETFs": 0.35, "Gold/Defensiv": 0.05, "Einzelaktien": 0.30, "Krypto": 0.30}
    base = {b: cons[b] * (1 - r) + aggr[b] * r for b in cons}
    # Wachstums-Tilt: hoeheres Wachstumsziel -> weniger Gold, mehr Aktien/Krypto
    g = max(0.0, min(1.0, growth / 100.0))
    shift = (g - 0.5) * 0.20
    base["Gold/Defensiv"] = max(0.0, base["Gold/Defensiv"] - shift)
    base["Einzelaktien"] += shift / 2.0
    base["Krypto"] += shift / 2.0
    base = {b: max(0.0, w) for b, w in base.items()}
    s = sum(base.values()) or 1.0
    return {b: base[b] / s for b in base}

def bucket_totals(pos_values, buckets):
    cur = {b: 0.0 for b in BUCKETS}
    for tk, v in pos_values.items():
        cur[buckets.get(tk, "Einzelaktien")] = cur.get(buckets.get(tk, "Einzelaktien"), 0.0) + v
    return cur

def rebalance_now(pos_values, buckets, target):
    """Voll-Rebalancing: pro Klasse Kauf/Verkauf, um Ziel JETZT zu treffen."""
    total = sum(pos_values.values())
    cur = bucket_totals(pos_values, buckets)
    rows = []
    for b in BUCKETS:
        tgt_eur = target.get(b, 0.0) * total
        rows.append({"bucket": b, "cur_eur": cur.get(b, 0.0),
                     "cur_w": (cur.get(b, 0.0) / total if total else 0.0),
                     "tgt_w": target.get(b, 0.0), "tgt_eur": tgt_eur,
                     "diff": tgt_eur - cur.get(b, 0.0)})
    return total, rows

def monthly_plan(pos_values, buckets, target, monthly):
    """Sparplan: verteilt die monatliche Einzahlung auf untergewichtete Klassen (kein Verkauf)."""
    total = sum(pos_values.values()); newtotal = total + monthly
    cur = bucket_totals(pos_values, buckets)
    gaps = {b: max(target.get(b, 0.0) * newtotal - cur.get(b, 0.0), 0.0) for b in BUCKETS}
    gsum = sum(gaps.values())
    buy = {}
    for b in BUCKETS:
        if gsum > 0:
            buy[b] = monthly * gaps[b] / gsum
        else:
            buy[b] = monthly * target.get(b, 0.0)
    return buy, cur, newtotal

def split_to_positions(amount, pos_values, buckets, bucket):
    """Verteilt einen Klassen-Betrag auf die Einzelpositionen dieser Klasse (nach aktuellem Wert)."""
    items = {tk: v for tk, v in pos_values.items() if buckets.get(tk) == bucket and v > 0}
    s = sum(items.values())
    if not items or amount <= 0:
        return {}
    if s <= 0:
        eq = amount / len(items)
        return {tk: eq for tk in items}
    return {tk: amount * v / s for tk, v in items.items()}


# ============================================================
#  RISIKOPROFIL-FRAGEBOGEN
# ============================================================
# Jede Antwort: (Label, Risiko-Punkte, Wachstums-Punkte) auf Skala 0..100
PROFILE_QUESTIONS = [
    {"key": "horizont", "q": "Wie lange kannst du das Geld investiert lassen?",
     "options": [("Unter 3 Jahre", 10, 10), ("3-7 Jahre", 40, 45),
                 ("7-15 Jahre", 70, 70), ("Ueber 15 Jahre", 90, 85)]},
    {"key": "reaktion", "q": "Dein Depot faellt in 3 Monaten um 30%. Was machst du?",
     "options": [("Alles verkaufen", 5, 10), ("Teilweise verkaufen", 30, 30),
                 ("Abwarten / halten", 65, 60), ("Nachkaufen", 95, 90)]},
    {"key": "ziel", "q": "Was ist dein Hauptziel?",
     "options": [("Kapital erhalten", 10, 10), ("Stetig & moderat wachsen", 40, 45),
                 ("Deutlich wachsen", 70, 75), ("Maximales Wachstum (mehr Risiko ok)", 95, 95)]},
    {"key": "erfahrung", "q": "Wie erfahren bist du mit schwankenden Anlagen (Aktien/Krypto)?",
     "options": [("Anfaenger", 20, 30), ("Etwas Erfahrung", 45, 50),
                 ("Erfahren", 70, 70), ("Sehr erfahren", 90, 85)]},
    {"key": "kapazitaet", "q": "Wie viel von diesem Geld brauchst du absehbar NICHT?",
     "options": [("Koennte ich bald brauchen", 15, 20), ("Grossteil ist langfristig", 50, 55),
                 ("Brauche ich sehr lange nicht", 85, 80)]},
]

def profile_from_answers(answers):
    """answers: dict key->gewaehltes Label. Liefert (risk, growth) auf 0..100 (5er-Schritte)."""
    rs, gs = [], []
    for qq in PROFILE_QUESTIONS:
        lab = answers.get(qq["key"])
        for (olab, rp, gp) in qq["options"]:
            if olab == lab:
                rs.append(rp); gs.append(gp); break
    if not rs:
        return 50, 60
    risk = max(0, min(100, 5 * round((sum(rs) / len(rs)) / 5)))
    growth = max(0, min(100, 5 * round((sum(gs) / len(gs)) / 5)))
    return int(risk), int(growth)

def profile_label(risk):
    if risk < 30: return "Defensiv"
    if risk < 55: return "Ausgewogen"
    if risk < 75: return "Wachstumsorientiert"
    return "Offensiv"

def apply_profile():
    """Callback: Fragebogen-Antworten -> Risiko/Wachstum -> setzt die Regler."""
    ans = {qq["key"]: st.session_state.get("pq_" + qq["key"]) for qq in PROFILE_QUESTIONS}
    risk, growth = profile_from_answers(ans)
    st.session_state["rb_risk"] = risk
    st.session_state["rb_growth"] = growth
    st.session_state["profile_label"] = profile_label(risk)


# ============================================================
#  INVESTMENT-MEMO
# ============================================================
def build_memo(data, m, sc, eff_growth, base_growth, selected_macro, qual, checklist_done, flags):
    lt = m["latest"]; rows = m["rows"]; cg = m["cagrs"]
    L = []
    L.append(f"# Investment-Memo: {data['name']} ({data['ticker']})")
    L.append(f"_Erstellt: {date.today().isoformat()} - Analyse- & Bildungs-Tool, KEINE Anlageberatung._\n")

    L.append("## 1. Ueberblick")
    L.append(f"- **Sektor / Branche:** {data.get('sector','-')} / {data.get('industry','-')}")
    price = f"{data['price']:.2f} {data['currency']}" if data.get("price") else "-"
    L.append(f"- **Kurs:** {price}  |  **Marktkap. (Mio.):** {fmt_num(data.get('mcap_m'))}  |  **Beta:** {fmt_x(data.get('beta'))}")
    if data.get("website"): L.append(f"- **Website:** {data['website']}")
    L.append("")

    L.append("## 2. Quantitatives Fazit")
    L.append(f"- **Quality-Score:** {fmt_pct(sc['quality'])}")
    L.append(f"- **Value-Score (wachstumsbereinigt):** {fmt_pct(sc['value_adj'])}")
    L.append(f"- **PEG:** {fmt_x(sc['peg'])}")
    L.append(f"- **=> FAZIT (quantitativ):** {sc['verdict']}\n")
    L.append("**Kernkennzahlen (letztes Geschaeftsjahr):**")
    L.append(f"- Bruttomarge {fmt_pct(rows['Bruttomarge'][lt])} | EBIT-Marge {fmt_pct(rows['EBIT-Marge'][lt])} | Nettomarge {fmt_pct(rows['Nettomarge'][lt])}")
    L.append(f"- ROE {fmt_pct(rows['ROE'][lt])} | ROCE {fmt_pct(rows['ROCE'][lt])} | FCF-Conversion {fmt_pct(rows['FCF Conversion'][lt])}")
    L.append(f"- Net Debt/EBITDA {fmt_x(rows['Net Debt/EBITDA'][lt])} | Debt/Equity {fmt_x(rows['Debt/Equity'][lt])}")
    L.append(f"- Umsatz-CAGR {fmt_pct(cg['Umsatz-CAGR'])} | EPS-CAGR {fmt_pct(cg['EPS-CAGR'])} | FCF-CAGR {fmt_pct(cg['FCF-CAGR'])}")
    L.append(f"- KGV {fmt_x(m['val_mult']['KGV (P/E)'])} | EV/EBITDA {fmt_x(m['val_mult']['EV/EBITDA'])} | EV/FCF {fmt_x(m['val_mult']['EV/FCF'])}\n")

    L.append("## 3. Wachstum & Makro-Annahmen")
    L.append(f"- **Basis-Wachstum:** {base_growth:.1f}% p.a.")
    if selected_macro:
        for nm, imp in selected_macro:
            L.append(f"- {nm}: {imp:+.1f} pp")
    else:
        L.append("- Keine Makro-Faktoren aktiviert.")
    L.append(f"- **Effektives Wachstum (Annahme):** {eff_growth:.1f}% p.a.\n")

    L.append("## 4. Qualitative Analyse")
    for key, title, _ in QUAL_SECTIONS:
        L.append(f"### {title}")
        txt = (qual.get(key) or "").strip()
        L.append(txt if txt else "_(noch nicht ausgefuellt)_")
        L.append("")

    done = sum(1 for x in checklist_done if x)
    L.append(f"## 5. Investment-Checkliste ({done}/{len(CHECKLIST)} erfuellt)")
    for item, ok in zip(CHECKLIST, checklist_done):
        L.append(f"- [{'x' if ok else ' '}] {item}")
    L.append("")

    n_pruef = len([f for f in flags if f[1] in ("auffaellig", "fehlend")])
    L.append("## 6. Datenqualitaet / Pruefhinweise")
    L.append(f"- {n_pruef} Kennzahl(en) auffaellig oder fehlend (Details im App-Tab 'Gegenpruefen').")
    L.append("- Zahlen stammen aus Yahoo Finance (Prototyp) - vor jeder Entscheidung gegen den Geschaeftsbericht (10-K) abgleichen.\n")

    L.append("---")
    L.append("_Dieses Memo ist ein Bildungs- und Strukturierungs-Werkzeug und stellt KEINE Anlageberatung oder Kaufempfehlung dar. "
             "Eigene Recherche und ggf. professionelle Beratung sind erforderlich._")
    return "\n".join(L)


def analysis_completeness(qual, checklist_done):
    filled = sum(1 for key, _, _ in QUAL_SECTIONS if (qual.get(key) or "").strip())
    chk = sum(1 for x in checklist_done if x)
    total = len(QUAL_SECTIONS) + len(CHECKLIST)
    return (filled + chk), total, filled, chk


# ============================================================
#  STREAMLIT UI
# ============================================================
st.set_page_config(page_title="FinAnalyse", page_icon=":bar_chart:", layout="wide")
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{CSS_GLOSS}</style>", unsafe_allow_html=True)
if "lang" not in st.session_state:
    st.session_state["lang"] = "de"
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []
if "nav" not in st.session_state:
    st.session_state["nav"] = "dash"

# ---- Sidebar ----
with st.sidebar:
    st.markdown("## FinAnalyse")
    st.caption("Analyse- & Bildungs-Tool")
    st.session_state["lang"] = st.radio("Sprache / Language", ["de", "en"],
                                        index=0 if st.session_state["lang"] == "de" else 1, horizontal=True)
    page = st.radio("Navigation", NAV, key="nav", format_func=nav_label,
                    help="Waehle den Bereich. Deine Eingaben bleiben waehrend der Sitzung erhalten.")
    st.markdown("---")
    st.markdown(f"**{t('plan')}**")
    st.session_state["plan"] = st.radio("Plan", ["Pro (Vorschau)", "Free"], label_visibility="collapsed",
                                        help="Demo-Umschalter: zeigt, welche Funktionen Plus/Pro vorbehalten waeren.")
    st.caption("Pro = alle Funktionen. Free zeigt die kostenlose Variante.")
    st.markdown("---")
    with st.expander(t("howto")):
        st.markdown(
            "**Dashboard** - Markt-Suche, deine Watchlist-Scores & Portfolio auf einen Blick.\n\n"
            "**Einzelanalyse** - Ticker eingeben -> Quant-Score & Fazit -> Templates ausfuellen -> Memo exportieren.\n\n"
            "**Mein Depot** - echte Positionen eingeben -> exakter Wert + Rendite (XIRR) + Depot-Backtest.\n\n"
            "**Portfolio & Backtest** - beliebige Gewichte testen: Rendite, Sharpe, Drawdown.\n\n"
            "_Tipp: Fahre ueber das (?) neben Eingaben fuer Erklaerungen. Keine Anlageberatung._")
    st.markdown(f"**{t('watchlist')}**")
    if st.session_state["watchlist"]:
        for w in list(st.session_state["watchlist"]):
            c1, c2 = st.columns([3, 1])
            c1.write(w)
            if c2.button("x", key=f"rm_{w}", help=f"{w} entfernen"):
                st.session_state["watchlist"].remove(w)
                st.rerun()
    else:
        st.caption("Noch leer - in der Einzelanalyse Titel mit 'Zur Watchlist' merken.")
    st.markdown("---")
    with st.expander(t("glossary")):
        for term, expl in GLOSSARY.items():
            st.markdown(f"**{term}**: {expl}")

# ---- Hero ----
plan_label = "PRO" if is_pro() else "FREE"
st.markdown(
    f'<div class="fa-hero"><h1>{t("title")}</h1>'
    f'<div class="sub">{t("subtitle")}</div>'
    f'<span class="tag">Daten: Yahoo Finance (Prototyp) - keine Anlageberatung - Plan: {plan_label}</span></div>',
    unsafe_allow_html=True)

# ---- Einmaliges Zustimmungs-Banner ----
if not st.session_state.get("consent_ok"):
    st.markdown('<div class="lock-card"><b>Kurzer Hinweis vor dem Start</b><br>'
                '<span style="font-size:.9rem">FinAnalyse ist ein Bildungs- &amp; Analyse-Tool und gibt KEINE '
                'Anlageberatung. Daten ohne Gewaehr; Investitionen koennen zum Totalverlust fuehren. Details unter '
                '„Rechtliches“.</span></div>', unsafe_allow_html=True)
    bcc1, bcc2 = st.columns([1, 4])
    bcc1.button("Verstanden & akzeptieren", on_click=accept_consent, type="primary", key="consent_btn")
    bcc2.button("Rechtliches lesen", on_click=goto_legal, key="consent_legal")

# ---- Gefuehrte Erst-Tour (mehrstufig, ueberspringbar) ----
if st.session_state.get("consent_ok") and not st.session_state.get("tour_done"):
    _step = min(st.session_state.get("onboard_step", 0), len(TOUR) - 1)
    _ti, _bo = TOUR[_step]
    _last = _step == len(TOUR) - 1
    st.markdown(
        f'<div class="fa-onboard"><h4>{_ti}</h4>'
        f'<p style="margin:.4rem 0 .2rem;line-height:1.65">{_bo}</p>'
        f'<div style="color:var(--fa-muted);font-size:.8rem;margin-top:.5rem">Schritt {_step+1} von {len(TOUR)} '
        f'- Tour der App</div></div>', unsafe_allow_html=True)
    tcc1, tcc2, tcc3 = st.columns([1.2, 1.2, 3.6])
    tcc1.button(("Fertig" if _last else "Weiter"), on_click=onboard_next, type="primary", key="tour_next")
    tcc2.button("Ueberspringen", on_click=onboard_skip, key="tour_skip")
    st.stop()

if yf is None:
    st.warning("yfinance nicht installiert - Live-Kurse deaktiviert. Installieren: pip install yfinance "
               "(im Tab 'Mein Depot' kannst du Kurse manuell als EUR-Override eintragen).")


# ============================================================
#  PORTFOLIO-AKADEMIE (Lerninhalte: Module, Lektionen, Tests)
# ============================================================
def two_asset_vol(w, vol1, vol2, corr):
    """Volatilitaet eines 2-Asset-Portfolios. w = Anteil Asset 1 (0..1). Fuer das Diversifikations-Labor."""
    w = max(0.0, min(1.0, w))
    var = (w * vol1) ** 2 + ((1 - w) * vol2) ** 2 + 2 * w * (1 - w) * corr * vol1 * vol2
    return float(np.sqrt(max(0.0, var)))

def _pfq(q, options, correct, explain):
    return {"q": q, "options": options, "correct": correct, "explain": explain}

CURRICULUM = [
 {"key": "m1", "title": "Modul 1 - Grundlagen des Investierens",
  "intro": "Bevor es um Portfolios geht: Warum man investiert, welche Bausteine es gibt und womit man sie kauft.",
  "lessons": [
    {"key": "pf_warum", "title": "Warum ueberhaupt investieren? (Zinseszins & Inflation)",
     "body": "Geld auf dem Konto verliert real an Wert: Bei 2-3% **Inflation** schrumpft die Kaufkraft Jahr fuer Jahr - "
             "nach 25 Jahren ist 1 Euro real nur noch ~50 Cent wert. Investieren bedeutet, Geld so anzulegen, dass es "
             "ueber der Inflation rentiert und dadurch real waechst. Der wichtigste Verbuendete dabei ist der "
             "**Zinseszins**: Ertraege erwirtschaften selbst wieder Ertraege. 100 Euro bei 7% p.a. werden in 10 Jahren "
             "zu ~197, in 30 Jahren zu ~761 Euro - der Loewenanteil entsteht in den spaeten Jahren, weil die Kurve "
             "exponentiell verlaeuft. Zwei Konsequenzen: erstens **frueh anfangen** (Zeit ist der staerkste Hebel), "
             "zweitens **dranbleiben** und Ertraege reinvestieren statt zu entnehmen. Investieren ist kein "
             "Reichwerden-ueber-Nacht, sondern geduldiges Wachsenlassen ueber Jahrzehnte.",
     "kernaussagen": ["Inflation frisst Kaufkraft - Nichtstun ist auch ein Risiko.",
                      "Zinseszins wirkt exponentiell: frueh anfangen schlaegt viel einzahlen.",
                      "Zeit im Markt ist der groesste Hebel."],
     "quizzes": [
        _pfq("Was bewirkt der Zinseszins?", ["Ertraege erwirtschaften selbst wieder Ertraege", "Er senkt die Inflation",
          "Er garantiert Gewinne"], 0, "Reinvestierte Ertraege wachsen exponentiell."),
        _pfq("Warum ist Geld nur auf dem Konto riskant?", ["Inflation senkt real die Kaufkraft", "Konten sind verboten",
          "Zinsen sind zu hoch"], 0, "Real verliert ungenutztes Geld an Wert."),
        _pfq("Welcher Hebel ist beim Zinseszins am staerksten?", ["Die Zeit (frueh anfangen)", "Ein perfekter Einstieg",
          "Hohe Gebuehren"], 0, "Je laenger, desto staerker die exponentielle Wirkung.")]},
    {"key": "pf_klassen", "title": "Die Anlageklassen",
     "body": "Ein Portfolio mischt verschiedene **Anlageklassen** mit unterschiedlichem Charakter. **Aktien** = Anteile "
             "an Firmen: hoechste erwartete Langfrist-Rendite, aber stark schwankend (in Krisen -50% moeglich). "
             "**Anleihen** = Kredite an Staaten/Firmen: planbare Zinsen, stabiler, geringere Rendite - oft "
             "Stabilisator. **Cash/Tagesgeld** = Sicherheit und Liquiditaet (Notgroschen!), verliert aber real durch "
             "Inflation. **Gold/Rohstoffe** = kein Cashflow, aber moeglicher Inflations-/Krisenschutz. **Immobilien** "
             "(direkt oder REITs) = laufende Ertraege + Inflationsschutz. **Krypto** = hochspekulativ, extrem volatil. "
             "Der Schluessel: Die Klassen verhalten sich unterschiedlich - das ist die Grundlage fuer Diversifikation. "
             "Wie du sie mischst (die Asset-Allokation), praegt dein Ergebnis staerker als die Auswahl einzelner Titel.",
     "kernaussagen": ["Jede Klasse hat ihr eigenes Risiko-/Rendite-Profil.",
                      "Cash sichert, Aktien wachsen, Anleihen stabilisieren.",
                      "Die Mischung der Klassen ist die wichtigste Entscheidung."],
     "quizzes": [
        _pfq("Welche Klasse hat langfristig die hoechste erwartete Rendite?", ["Aktien", "Tagesgeld", "Anleihen"], 0,
          "Dafuer schwanken Aktien am staerksten."),
        _pfq("Wofuer ist Cash/Tagesgeld v.a. gut?", ["Sicherheit & Notgroschen", "Maximale Rendite", "Inflationsschutz"], 0,
          "Liquide und sicher, aber real von Inflation betroffen."),
        _pfq("Warum mischt man ueberhaupt Klassen?", ["Weil sie sich unterschiedlich verhalten (Diversifikation)",
          "Weil es Vorschrift ist", "Um Steuern zu sparen"], 0, "Unterschiedliches Verhalten senkt das Gesamtrisiko.")]},
    {"key": "pf_instrumente", "title": "Die Instrumente: Aktie, ETF, Anleihe & Co.",
     "body": "Mit welchen Produkten kauft man die Anlageklassen? Eine **Aktie** ist ein direkter Firmenanteil - Chance "
             "auf Kurs + Dividende, aber Einzelrisiko bis zum Totalverlust. Ein **ETF** ist ein boersengehandelter "
             "Indexfonds: ein Korb aus vielen Wertpapieren in einem Produkt - mit einem Kauf breit gestreut und "
             "guenstig (oft 0,1-0,3% laufende Kosten). Aktive **Fonds** versuchen den Markt zu schlagen, kosten mehr "
             "und schaffen es nach Kosten meist nicht. Eine **Anleihe** ist ein verzinster Kredit an Staat/Firma. "
             "**Derivate** (Optionen, Hebelprodukte, CFDs) sind komplex und oft gehebelt - Verluste koennen "
             "vervielfacht werden, fuer Einsteiger ungeeignet. Fuer den Aufbau eines Portfolios sind breite ETFs der "
             "meistgenutzte Baustein, ergaenzt um einzelne, selbst verstandene Aktien. Grundregel: investiere nie in "
             "etwas, das du nicht in einem Satz erklaeren kannst.",
     "kernaussagen": ["ETF = breite Streuung in einem guenstigen Produkt.",
                      "Aktive Fonds schlagen den Markt nach Kosten meist nicht.",
                      "Gehebelte Derivate sind fuer Einsteiger ungeeignet."],
     "quizzes": [
        _pfq("Was ist ein ETF?", ["Ein Korb vieler Wertpapiere (meist Index, passiv)", "Eine Einzelaktie",
          "Ein Hebelprodukt"], 0, "Breite Streuung guenstig in einem Produkt."),
        _pfq("Was ist typisch fuer gehebelte Derivate?", ["Verluste koennen vervielfacht werden", "Sie sind risikolos",
          "Garantierte Zinsen"], 0, "Hebel verstaerkt Gewinne UND Verluste."),
        _pfq("Schlagen aktive Fonds den Markt langfristig?", ["Mehrheit nicht (nach Kosten)", "Immer", "Garantiert"], 0,
          "Gebuehren fressen den Vorsprung.")]},
  ]},
 {"key": "m2", "title": "Modul 2 - Risiko & Rendite",
  "intro": "Die zwei Seiten jeder Geldanlage - und wie man sie misst und ins Verhaeltnis setzt.",
  "lessons": [
    {"key": "pf_rendite", "title": "Was ist Rendite? (nominal, real, p.a.)",
     "body": "**Rendite** ist der Ertrag relativ zum eingesetzten Kapital, meist in Prozent. Wichtige "
             "Unterscheidungen: **nominal vs. real** - die reale Rendite zieht die Inflation ab und zeigt den echten "
             "Kaufkraftgewinn (7% nominal bei 3% Inflation = rund 3,9% real). **Pro Jahr (p.a.)** macht "
             "unterschiedlich lange Zeitraeume vergleichbar; dabei zaehlt die geometrische Durchschnittsrendite (CAGR), "
             "nicht der einfache Mittelwert - denn nach -50% braucht es +100%, um wieder bei null zu sein. "
             "**Gesamtrendite** umfasst Kursgewinne UND Ausschuettungen (Dividenden/Zinsen), die reinvestiert den "
             "Zinseszins befeuern. Und: Renditeangaben aus der Vergangenheit sind kein verlaesslicher Indikator fuer "
             "die Zukunft. Achte immer darauf, ob eine Zahl nominal oder real, vor oder nach Kosten und Steuern "
             "gemeint ist - das veraendert das Bild erheblich.",
     "kernaussagen": ["Real = nominal minus Inflation (echte Kaufkraft).",
                      "Vergleiche immer p.a. und geometrisch (CAGR).",
                      "Netto nach Kosten/Steuern zaehlt, nicht brutto."],
     "quizzes": [
        _pfq("Was zeigt die reale Rendite?", ["Den Ertrag nach Abzug der Inflation", "Den Bruttogewinn", "Die Dividende"], 0,
          "Sie misst den echten Kaufkraftgewinn."),
        _pfq("Nach -50% braucht es wieder ...?", ["+100% um bei null zu sein", "+50%", "+25%"], 0,
          "Verluste wiegen prozentual schwerer."),
        _pfq("Was gehoert zur Gesamtrendite?", ["Kursgewinn UND Ausschuettungen", "Nur der Kurs", "Nur Dividenden"], 0,
          "Reinvestierte Ausschuettungen befeuern den Zinseszins.")]},
    {"key": "pf_risiko", "title": "Was ist Risiko? (Volatilitaet & Drawdown)",
     "body": "Risiko ist nicht nur 'Verlustgefahr', sondern v.a. **Unsicherheit/Schwankung**. Das gaengigste Mass ist "
             "die **Volatilitaet** (Standardabweichung der Renditen, p.a.): wie stark der Wert um seinen Trend "
             "schwankt. Aktien-ETFs haben grob 15-20% Vola, Einzelaktien deutlich mehr, Anleihen weniger. Der **Max "
             "Drawdown** ist der groesste Verlust vom Hoch zum Tief - er trifft die Psyche am haertesten (breite "
             "Aktienmaerkte hatten schon -50% und mehr). Wichtig ist deine **Risikotragfaehigkeit** in zwei "
             "Dimensionen: finanziell (kannst du Verluste aushalten, ohne das Geld bald zu brauchen?) und emotional "
             "(haeltst du einen Crash aus, ohne panisch zu verkaufen?). Das groesste reale Risiko ist oft nicht die "
             "Schwankung selbst, sondern der **Notverkauf im Tief**. Wer seinen Horizont und seine Schmerzgrenze "
             "kennt, waehlt eine Allokation, die er auch in der Krise durchhaelt.",
     "kernaussagen": ["Volatilitaet misst die Schwankungsbreite (p.a.).",
                      "Max Drawdown = groesster Verlust vom Hoch zum Tief.",
                      "Das groesste Risiko ist oft der Notverkauf im Tief."],
     "quizzes": [
        _pfq("Was misst die Volatilitaet?", ["Die Schwankungsbreite der Renditen", "Die Dividende", "Die Gebuehren"], 0,
          "Standardabweichung der Renditen p.a."),
        _pfq("Was ist der Max Drawdown?", ["Groesster Verlust vom Hoch zum Tief", "Die jaehrliche Rendite",
          "Die Anzahl der Aktien"], 0, "Das psychologisch haerteste Mass."),
        _pfq("Risikotragfaehigkeit hat zwei Seiten:", ["Finanziell UND emotional", "Nur finanziell", "Nur die Rendite"], 0,
          "Beides muss zur Allokation passen.")]},
    {"key": "pf_sharpe", "title": "Risiko & Rendite im Verhaeltnis (Sharpe Ratio)",
     "body": "Mehr Rendite gibt es am Markt langfristig nur fuer mehr Risiko - die Frage ist, ob du fuer dein Risiko "
             "**fair entlohnt** wirst. Genau das misst die **Sharpe Ratio**: (Rendite minus risikofreier Zins) "
             "geteilt durch die Volatilitaet. Sie sagt, wie viel Ueberrendite du pro Einheit Risiko bekommst. "
             "Faustwerte: ueber 1 ist gut, ueber 2 sehr gut. Zwei Portfolios mit gleicher Rendite sind nicht gleich "
             "gut - das mit weniger Schwankung (hoehere Sharpe) ist ueberlegen, weil es ruhiger laeuft und leichter "
             "durchzuhalten ist. Genau hier setzt Diversifikation an: Sie kann das Risiko senken, ohne die erwartete "
             "Rendite im gleichen Mass zu senken - und hebt damit die Sharpe Ratio. Achte also nie nur auf die "
             "Rendite, sondern immer auf das Verhaeltnis von Rendite zu Risiko. (Die App zeigt dir die Sharpe Ratio "
             "im Depot-Backtest direkt an.)",
     "kernaussagen": ["Sharpe Ratio = Ueberrendite je Risikoeinheit.",
                      ">1 gut, >2 sehr gut.",
                      "Gleiche Rendite + weniger Risiko = besseres Portfolio."],
     "quizzes": [
        _pfq("Was misst die Sharpe Ratio?", ["Rendite pro Einheit Risiko", "Nur die Rendite", "Die Gebuehren"], 0,
          "(Rendite - risikofrei) / Volatilitaet."),
        _pfq("Zwei Portfolios, gleiche Rendite - welches ist besser?", ["Das mit weniger Schwankung",
          "Das mit mehr Schwankung", "Egal"], 0, "Hoehere Sharpe Ratio ist ueberlegen."),
        _pfq("Eine Sharpe Ratio von 2 ist ...?", ["Sehr gut", "Schlecht", "Unmoeglich"], 0, "Viel Rendite je Risiko.")]},
  ]},
 {"key": "m3", "title": "Modul 3 - Das Herzstueck: Diversifikation & Allokation",
  "intro": "Warum Streuung das einzige 'kostenlose Mittagessen' ist - und wie du dein Geld auf die Klassen verteilst.",
  "lessons": [
    {"key": "pf_diversifikation", "title": "Diversifikation & Korrelation",
     "body": "Diversifikation - Streuung - gilt als das einzige 'free lunch' an der Boerse: Sie kann das Risiko "
             "senken, ohne die erwartete Rendite entsprechend zu opfern. Der Schluessel ist die **Korrelation**: wie "
             "gleichlaeufig sich zwei Anlagen bewegen (von +1 = im Gleichschritt bis -1 = gegenlaeufig). Kombinierst "
             "du Anlagen, die NICHT perfekt korreliert sind, gleichen sich Schwankungen teilweise aus - die "
             "Portfolio-Volatilitaet ist dann KLEINER als der Durchschnitt der Einzel-Volatilitaeten. Genau deshalb "
             "sind zehn Tech-Aktien kaum Streuung (hohe Korrelation, fallen gemeinsam), waehrend Aktien + Anleihen + "
             "Gold sich oft unterschiedlich verhalten. Diversifizieren kannst du ueber Titel, Branchen, Laender und "
             "Anlageklassen. Wichtig: In schweren Krisen steigen Korrelationen oft kurzfristig an ('alles faellt "
             "zusammen') - perfekte Absicherung gibt es nicht, aber breite Streuung verhindert, dass ein einzelnes "
             "Ereignis dich ruiniert. (Im Rechner-Tab 'Diversifikation' kannst du den Effekt selbst ausprobieren.)",
     "kernaussagen": ["Diversifikation senkt Risiko ohne gleich viel Rendite zu opfern.",
                      "Korrelation < 1 erzeugt den Streuungseffekt.",
                      "Zehn aehnliche Titel sind keine echte Streuung."],
     "quizzes": [
        _pfq("Warum sind 10 Tech-Aktien keine echte Streuung?", ["Stark korreliert, fallen gemeinsam", "Zu wenige",
          "Tech ist verboten"], 0, "Hohe Korrelation = kaum Diversifikationseffekt."),
        _pfq("Was beschreibt die Korrelation?", ["Wie gleichlaeufig sich zwei Anlagen bewegen", "Die Rendite",
          "Die Gebuehr"], 0, "Von +1 (gleich) bis -1 (gegenlaeufig)."),
        _pfq("Diversifikation gilt als ...?", ["Das einzige 'free lunch' an der Boerse", "Garantie gegen Verluste",
          "Renditebremse"], 0, "Weniger Risiko bei aehnlicher erwarteter Rendite.")]},
    {"key": "pf_allokation", "title": "Asset-Allokation & Risikoprofil",
     "body": "Die **Asset-Allokation** - die prozentuale Aufteilung auf Anlageklassen - ist laut Studien der mit "
             "Abstand wichtigste Treiber des langfristigen Ergebnisses, wichtiger als die Auswahl einzelner Titel oder "
             "das Timing. Sie richtet sich nach zwei Dingen: deinem **Anlagehorizont** (wann brauchst du das Geld?) "
             "und deiner **Risikotragfaehigkeit** (finanziell und emotional). Je laenger und gelassener, desto hoeher "
             "kann die Aktienquote sein. Eine alte Faustformel war '110 minus Lebensalter = Aktienanteil' - heute eher "
             "grobe Orientierung als Regel. Typische Profile: defensiv (viel Anleihen/Cash, wenig Aktien), ausgewogen "
             "(etwa halbe-halbe) und offensiv (ueberwiegend Aktien). Wichtig ist eine Allokation, die du auch im Crash "
             "**durchhaeltst** - lieber etwas weniger Aktien und dabeibleiben als zu offensiv und im Tief verkaufen. "
             "Lege deine Zielquoten bewusst fest; sie sind der Bauplan, an dem du dich beim Rebalancing orientierst.",
     "kernaussagen": ["Allokation schlaegt Einzelauswahl und Timing.",
                      "Sie haengt an Horizont und Risikotragfaehigkeit.",
                      "Waehle eine Quote, die du auch im Crash durchhaeltst."],
     "quizzes": [
        _pfq("Was treibt das Ergebnis langfristig am staerksten?", ["Die Asset-Allokation", "Das Timing",
          "Die Aktienauswahl allein"], 0, "Die Aufteilung auf Klassen ist entscheidend."),
        _pfq("Wovon haengt die Allokation ab?", ["Horizont und Risikotragfaehigkeit", "Vom Wetter", "Vom Broker"], 0,
          "Wann brauchst du das Geld, wie viel haeltst du aus?"),
        _pfq("Welche Allokation ist die richtige?", ["Eine, die du auch im Crash durchhaeltst", "Immer 100% Aktien",
          "Immer 100% Cash"], 0, "Durchhalten schlaegt theoretisches Optimum.")]},
    {"key": "pf_mpt", "title": "Moderne Portfoliotheorie & Efficient Frontier",
     "body": "Harry Markowitz zeigte 1952 (Nobelpreis), dass man Portfolios mathematisch optimieren kann - die "
             "Geburtsstunde der **Modernen Portfoliotheorie**. Kernidee: Was zaehlt, ist nicht das Risiko einer "
             "einzelnen Anlage, sondern ihr Beitrag zum **Gesamtrisiko** des Portfolios. Durch geschickte Mischung "
             "wenig korrelierter Anlagen gibt es zu jedem Renditeniveau eine Mischung mit dem geringstmoeglichen "
             "Risiko. Die Menge dieser optimalen Mischungen bildet die **Efficient Frontier** (Effizienzkurve): Jedes "
             "Portfolio darauf ist 'effizient' - mehr Rendite gibt es nur mit mehr Risiko, weniger Risiko nur mit "
             "weniger Rendite. Portfolios UNTER der Kurve sind ineffizient. In der Praxis sind die noetigen Eingaben "
             "(kuenftige Renditen, Korrelationen) unsicher, weshalb man die Theorie nicht blind anwendet - aber die "
             "zentrale Lektion bleibt goldwert: **Mische so, dass das Risiko-Rendite-Verhaeltnis des GANZEN Portfolios "
             "moeglichst gut ist**, nicht das einzelner Positionen.",
     "kernaussagen": ["Was zaehlt, ist der Risiko-Beitrag zum Gesamtportfolio.",
                      "Die Efficient Frontier = beste Rendite je Risikoniveau.",
                      "Theorie ist idealisiert, die Kernlektion praktisch sehr wertvoll."],
     "quizzes": [
        _pfq("Was ist die Efficient Frontier?", ["Die Mischungen mit bester Rendite je Risiko",
          "Die teuersten Aktien", "Eine Steuerregel"], 0, "Portfolios darauf sind 'effizient'."),
        _pfq("Worauf kommt es laut Markowitz an?", ["Den Risikobeitrag zum Gesamtportfolio", "Nur Einzeltitel-Risiko",
          "Den gestrigen Kurs"], 0, "Das Zusammenspiel zaehlt, nicht die Einzelanlage."),
        _pfq("Warum wendet man MPT nicht blind an?", ["Kuenftige Renditen/Korrelationen sind unsicher",
          "Sie ist verboten", "Sie ist zu billig"], 0, "Die Eingaben kennt niemand exakt.")]},
  ]},
 {"key": "m4", "title": "Modul 4 - Portfolio bauen: Strategie & Kosten",
  "intro": "Wie du dein Portfolio konkret zusammensetzt - und warum Kosten und Steuern ueber Jahrzehnte entscheiden.",
  "lessons": [
    {"key": "pf_passiv", "title": "Passiv vs. aktiv & der Kern-Satellit-Ansatz",
     "body": "Die Grundsatzentscheidung: selbst auswaehlen oder den Markt einfach abbilden? **Passive ETFs** bilden "
             "einen breiten Index nach (z.B. einen Welt-Index mit Tausenden Firmen) - guenstig, transparent, breit "
             "gestreut, kein Stockpicking. **Aktive** Ansaetze versuchen, den Markt zu schlagen, kosten mehr und "
             "schaffen es nach Kosten meist nicht. Fuer die meisten Privatanleger ist ein breiter, guenstiger "
             "Welt-ETF als Fundament die solideste Basis. Der **Kern-Satellit-Ansatz** verbindet beides: Ein breiter "
             "ETF bildet den stabilen **Kern** (z.B. 70-90%), waehrend einzelne, selbst gruendlich analysierte Aktien "
             "oder Themen als kleinere **Satelliten** ergaenzt werden - genau hier hilft dir die Einzelanalyse dieser "
             "App. So kombinierst du die Sicherheit breiter Streuung mit der Chance eigener Ideen, ohne das ganze "
             "Depot zu riskieren. Wichtig: Einfachheit ist eine Tugend - ein Portfolio, das du verstehst und pflegen "
             "kannst, schlaegt ein zu kompliziertes.",
     "kernaussagen": ["Breiter, guenstiger ETF als Fundament.",
                      "Kern-Satellit: stabiler ETF-Kern + bewusste Satelliten.",
                      "Einfach und verstaendlich schlaegt kompliziert."],
     "quizzes": [
        _pfq("Was ist der Kern beim Kern-Satellit-Ansatz?", ["Ein breiter, guenstiger ETF", "Eine einzelne Aktie",
          "Ein Hebelprodukt"], 0, "Der stabile Hauptteil des Depots."),
        _pfq("Passiver ETF heisst ...?", ["Bildet einen Index nach", "Manager handelt taeglich", "Verlustfrei"], 0,
          "Er folgt einem Index statt aktiv auszuwaehlen."),
        _pfq("Was ist fuer die meisten die solide Basis?", ["Breiter Welt-ETF", "Nur Einzelaktien", "Nur Krypto"], 0,
          "Breit gestreut und guenstig.")]},
    {"key": "pf_kosten", "title": "Kosten & Steuern",
     "body": "Kosten sind einer der wenigen Faktoren, die du fast vollstaendig kontrollierst - und sie wirken ueber "
             "Jahrzehnte wie Gegenwind. Schon **1% laufende Kosten p.a.** kostet ueber 30 Jahre einen erheblichen Teil "
             "des Endkapitals (durch entgangenen Zinseszins). Achte auf: **Ordergebuehren/Spreads** beim Handel, die "
             "**TER** (laufende Kosten) von Fonds/ETFs und Depotgebuehren. Guenstige Broker und kostenarme Index-ETFs "
             "sind ein direkter Renditevorteil. Zu **Steuern** (Deutschland, allgemein - kein Steuerrat): Auf "
             "Kursgewinne und Ausschuettungen faellt i.d.R. **Abgeltungsteuer 25% + Soli** an (rund 26,4%), plus ggf. "
             "Kirchensteuer; es gibt einen jaehrlichen **Sparer-Pauschbetrag** (Freibetrag), und bei thesaurierenden "
             "Fonds die **Vorabpauschale**. Wer selten umschichtet, profitiert von der Steuerstundung. Merke: Am Ende "
             "zaehlt die **Nettorendite** nach Kosten und Steuern, nicht die schoene Bruttozahl. (Den Kosten-Effekt "
             "und einen Steuer-Schaetzer findest du im Rechner.)",
     "kernaussagen": ["Schon 1% Kosten p.a. kostet ueber Jahrzehnte viel.",
                      "TER, Spreads und Gebuehren druecken die Rendite.",
                      "Netto nach Kosten/Steuern zaehlt; Steuerstundung hilft."],
     "quizzes": [
        _pfq("Warum sind laufende Kosten so wichtig?", ["Sie schmaelern die Rendite ueber Jahre stark", "Einmalig egal",
          "Sie erhoehen die Dividende"], 0, "Zinseszins-Effekt wirkt auch bei Kosten."),
        _pfq("Abgeltungsteuer in DE grob?", ["25% + Soli (~26,4%)", "50%", "0%"], 0, "Plus ggf. Kirchensteuer."),
        _pfq("Was zaehlt am Ende?", ["Nettorendite nach Kosten/Steuern", "Bruttorendite", "Das Werbeversprechen"], 0,
          "Netto, nicht brutto.")]},
    {"key": "pf_sparplan", "title": "Sparplan, Cost-Average & Anlagehorizont",
     "body": "Ein **Sparplan** investiert regelmaessig einen festen Betrag - unabhaengig vom Kursniveau. Der "
             "**Cost-Average-Effekt** sorgt dafuer, dass du bei niedrigen Kursen mehr Anteile kaufst und bei hohen "
             "weniger; das glaettet den Einstiegspreis und nimmt die Emotion aus der Frage 'Ist jetzt der richtige "
             "Zeitpunkt?'. Genau diese Frage fuehrt naemlich zu teuren Fehlern: Der Versuch, Tief- und Hochpunkte zu "
             "erwischen (**Market Timing**), schadet den meisten Anlegern, weil die staerksten Boersentage oft direkt "
             "nach den schwaechsten kommen. 'Time in the market beats timing the market.' Entscheidend ist der "
             "**Anlagehorizont**: Geld, das du in 1-2 Jahren brauchst, gehoert nicht in schwankende Aktien; je laenger "
             "der Horizont, desto besser lassen sich Schwankungen aussitzen und desto staerker wirkt der Zinseszins. "
             "Trenne Notgroschen (sicher, verfuegbar) klar vom langfristigen Anlagegeld - und bleib dann diszipliniert "
             "dabei.",
     "kernaussagen": ["Sparplan + Cost-Average glaetten den Einstieg.",
                      "Market Timing schadet den meisten - dranbleiben gewinnt.",
                      "Kurzfristiges Geld nicht in schwankende Anlagen."],
     "quizzes": [
        _pfq("Was bewirkt ein Sparplan?", ["Cost-Average glaettet den Einstieg", "Garantiert Gewinne",
          "Vermeidet Steuern"], 0, "Feste Betraege mitteln den Einstandskurs."),
        _pfq("Was bringt Market Timing den meisten?", ["Es schadet eher", "Es funktioniert immer", "Risikolos"], 0,
          "Beste Tage folgen oft direkt auf die schlimmsten."),
        _pfq("Geld fuer in 1-2 Jahren gehoert ...?", ["Nicht in schwankende Aktien", "In Hebelprodukte", "In Krypto"], 0,
          "Kurzer Horizont vertraegt keine Schwankung.")]},
  ]},
 {"key": "m5", "title": "Modul 5 - Portfolio fuehren & Psychologie",
  "intro": "Ein Portfolio braucht Pflege und einen kuehlen Kopf - hier lernst du Rebalancing, typische Fehler und die Entnahme.",
  "lessons": [
    {"key": "pf_rebalancing", "title": "Rebalancing & Pflege",
     "body": "Mit der Zeit verschieben sich die Gewichte: Gut gelaufene Positionen werden immer groesser und sprengen "
             "deine Zielallokation - oft genau die, die zuletzt am teuersten wurden. **Rebalancing** bringt die "
             "Gewichte regelbasiert zurueck ans Ziel, typischerweise einmal jaehrlich oder wenn eine Klasse eine "
             "Bandbreite (z.B. +/-5 Prozentpunkte) verlaesst. Das wirkt **antizyklisch und diszipliniert**: Du "
             "reduzierst, was teuer geworden ist, und stockst auf, was guenstig ist - das Gegenteil des emotionalen "
             "Herdenverhaltens. Gleichzeitig begrenzt es **Klumpenrisiken**. Beachte: Verkaeufe koennen Steuern und "
             "Gebuehren ausloesen - in Sparplaenen laesst sich Rebalancing oft elegant ueber die Verteilung neuer "
             "Einzahlungen erreichen. Pflege heisst nicht staendiges Umschichten: selten, regelbasiert, und auf "
             "fundamentale Veraenderungen reagieren - nicht auf taegliches Kursrauschen. (Den Rebalancing-Rechner und "
             "die Klumpenrisiko-Uebersicht findest du unter 'Mein Depot'.)",
     "kernaussagen": ["Rebalancing fuehrt die Gewichte zurueck ans Ziel.",
                      "Es wirkt antizyklisch und begrenzt Klumpenrisiken.",
                      "Selten und regelbasiert - nicht staendig umschichten."],
     "quizzes": [
        _pfq("Ziel von Rebalancing?", ["Gewichte zurueck ans Ziel bringen", "Moeglichst oft traden",
          "Die beste Aktie finden"], 0, "Zurueck zur Zielallokation."),
        _pfq("Wie wirkt Rebalancing?", ["Antizyklisch (teuer reduzieren, guenstig aufstocken)", "Prozyklisch",
          "Zufaellig"], 0, "Das Gegenteil von Herdenverhalten."),
        _pfq("Wie oft typischerweise?", ["Selten, z.B. jaehrlich", "Taeglich", "Nie"], 0, "Oder bei Verlassen einer Bandbreite.")]},
    {"key": "pf_psychologie", "title": "Psychologie & typische Fehler",
     "body": "Die groesste Renditebremse sitzt im eigenen Kopf. Haeufige Denkfehler: **Bestaetigungsfehler** (nur "
             "Argumente suchen, die die eigene Meinung stuetzen), **Verlustaversion** (Verlierer zu lange halten, "
             "Gewinner zu frueh verkaufen, weil Verluste doppelt so weh tun wie Gewinne erfreuen), **Herdentrieb/FOMO** "
             "(kaufen, weil alle kaufen - oft am Hoch), **Recency Bias** (die juengste Entwicklung in die Zukunft "
             "fortschreiben) und **Overconfidence** nach ein paar Gewinnen. Die teuersten Fehler sind meist emotional: "
             "Panikverkauf im Crash und Gier-Kauf in der Euphorie. Gegenmittel sind **Prozesse statt Bauchgefuehl**: "
             "vorab einen schriftlichen Plan (Zielallokation, Sparrate, Rebalancing-Regel) festlegen und stur "
             "befolgen; Crashs als normalen Teil einplanen; weniger oft ins Depot schauen. Ein klarer, langweiliger, "
             "durchgehaltener Plan schlaegt fast jede geniale, aber emotional umgesetzte Strategie.",
     "kernaussagen": ["Emotionen (Panik/Gier) kosten am meisten Rendite.",
                      "Verlustaversion & Herdentrieb sind die Klassiker.",
                      "Ein schriftlicher Plan schlaegt Bauchentscheidungen."],
     "quizzes": [
        _pfq("Was ist der Bestaetigungsfehler?", ["Nur stuetzende Infos suchen", "Immer falsch rechnen",
          "Nur teuer kaufen"], 0, "Gegenargumente werden ausgeblendet."),
        _pfq("Wozu fuehrt Verlustaversion?", ["Verlierer zu lange halten", "Gewinner zu lange halten", "Nichts"], 0,
          "Verluste schmerzen ueberproportional."),
        _pfq("Bestes Gegenmittel gegen Emotionen?", ["Ein schriftlicher Plan, stur befolgt", "Mehr ins Depot schauen",
          "Auf Foren hoeren"], 0, "Prozesse schlagen Bauchgefuehl.")]},
    {"key": "pf_entnahme", "title": "Entnahme & Ruhestand (die 4%-Regel)",
     "body": "Irgendwann soll das Portfolio Geld AUSzahlen statt nur aufzubauen - die **Entnahmephase**. Beruehmt ist "
             "die **4%-Regel** (aus der US-'Trinity-Studie'): Wer im ersten Ruhestandsjahr 4% des Vermoegens entnimmt "
             "und den Betrag danach jaehrlich an die Inflation anpasst, kam historisch ueber 30 Jahre mit hoher "
             "Wahrscheinlichkeit aus. Bei 500.000 Euro waeren das rund 20.000 Euro im ersten Jahr (ca. 1.667/Monat). "
             "Wichtig: Das ist eine grobe **Orientierung**, keine Garantie - sie beruht auf historischen US-Daten und "
             "30 Jahren Horizont. Reale Risiken: ein Crash gleich zu Beginn der Entnahme ('Renditereihenfolge-Risiko') "
             "schadet besonders, und hoehere Inflation verkuerzt die Reichweite. Flexibel sein (in schlechten Jahren "
             "weniger entnehmen) erhoeht die Sicherheit deutlich. (Den Entnahme-Rechner mit der 4%-Regel findest du im "
             "Rechner.)",
     "kernaussagen": ["4%-Regel: grobe Orientierung fuer nachhaltige Entnahme.",
                      "Keine Garantie - Crash zu Beginn ist besonders gefaehrlich.",
                      "Flexibilitaet (in schlechten Jahren weniger) hilft stark."],
     "quizzes": [
        _pfq("Was besagt die 4%-Regel grob?", ["Im 1. Jahr 4% entnehmen, dann an Inflation anpassen", "4% Steuern zahlen",
          "4 Aktien kaufen"], 0, "Historisch oft 30 Jahre tragfaehig."),
        _pfq("Was ist das 'Renditereihenfolge-Risiko'?", ["Ein Crash gleich zu Beginn der Entnahme schadet besonders",
          "Zu hohe Dividenden", "Zu viele Trades"], 0, "Fruehe Verluste sind in der Entnahme am gefaehrlichsten."),
        _pfq("Was erhoeht die Sicherheit der Entnahme?", ["Flexibel sein (in schlechten Jahren weniger entnehmen)",
          "Immer mehr entnehmen", "Alles in eine Aktie"], 0, "Anpassung an die Marktlage hilft enorm.")]},
  ]},
]
CURRICULUM += [
 {"key": "m6", "title": "Modul 6 - Vertiefung: Anlageklassen & Faktoren im Detail",
  "intro": "Tiefer rein: ETF-Auswahl in der Praxis, Anleihen, Waehrungsrisiko, Faktor-Investing und Immobilien.",
  "lessons": [
    {"key": "pf_etf_auswahl", "title": "ETF in der Praxis auswaehlen",
     "body": "Einen Welt-ETF zu kaufen klingt einfach, hat aber Tiefe. Erstens der **Index**: Ein 'MSCI World' enthaelt "
             "nur Industrielaender (~1.500 Firmen), ein 'MSCI ACWI' oder 'FTSE All-World' zusaetzlich Schwellenlaender "
             "(~3.000+). Alle sind nach Marktkapitalisierung gewichtet - das fuehrt aktuell zu hohem **USA- und "
             "Tech-Anteil** (oft 60-70% USA), ein bewusst zu akzeptierendes Klumpenrisiko. Zweitens die "
             "**Replikation**: physisch vollstaendig (kauft alle Titel), Sampling (Auswahl) oder synthetisch "
             "(Swap mit einer Bank - guenstig, aber Kontrahentenrisiko). Drittens **ausschuettend vs. "
             "thesaurierend** - thesaurierend legt Ertraege automatisch wieder an (Zinseszins, weniger Aufwand), "
             "ausschuettend nutzt aktiv den Sparer-Pauschbetrag. Viertens die Kosten: Die **TER** ist nur die halbe "
             "Wahrheit - die **Tracking-Differenz** (wie genau der ETF den Index NACH Kosten trifft) ist oft "
             "aussagekraeftiger und kann sogar negativ sein (ETF schlaegt Index leicht, z.B. durch Wertpapierleihe). "
             "Dazu Fondsgroesse (sehr kleine ETFs koennen geschlossen werden), Domizil (Irland: Quellensteuervorteil "
             "bei US-Dividenden) und der Handels-Spread. Fazit: Ein grosser, guenstiger, physisch replizierender "
             "Welt-ETF aus Irland ist fuer die meisten ein solider Kern - aber wissen, was man kauft.",
     "kernaussagen": ["Index bestimmt die Streuung (World vs. All-World, USA-Klumpen).",
                      "Tracking-Differenz ist oft aussagekraeftiger als die TER.",
                      "Thesaurierend = Zinseszins automatisch; physisch = ohne Swap-Risiko."],
     "quizzes": [
        _pfq("Was enthaelt ein 'FTSE All-World' zusaetzlich zum 'MSCI World'?", ["Schwellenlaender", "Nur USA",
          "Nur Anleihen"], 0, "All-World deckt auch Emerging Markets ab."),
        _pfq("Was ist oft aussagekraeftiger als die TER?", ["Die Tracking-Differenz", "Der Fondsname", "Die Farbe"], 0,
          "Sie zeigt die echte Abweichung nach Kosten."),
        _pfq("Was macht ein thesaurierender ETF?", ["Legt Ertraege automatisch wieder an", "Zahlt alles aus",
          "Ist verlustfrei"], 0, "Foerdert den Zinseszins.")]},
    {"key": "pf_anleihen", "title": "Anleihen vertieft: Zins, Duration, Bonitaet",
     "body": "Eine Anleihe ist ein verzinster Kredit: Du leihst Staat oder Firma Geld, bekommst regelmaessig Zinsen "
             "(**Kupon**) und am Ende den Nennwert zurueck. Drei Kernrisiken: Erstens das **Zinsaenderungsrisiko** - "
             "steigen die Marktzinsen, FALLEN die Kurse bestehender Anleihen (und umgekehrt), denn niemand zahlt voll "
             "fuer eine 1%-Anleihe, wenn es neue mit 3% gibt. Wie stark eine Anleihe reagiert, misst die **Duration** "
             "(grob die Kursaenderung je 1 Prozentpunkt Zinsaenderung): lange Laufzeit = hohe Duration = stark "
             "schwankend. Zweitens das **Bonitaetsrisiko**: Ratings von AAA (sehr sicher) bis 'Ramsch'/High Yield - je "
             "schlechter, desto hoeher der Zins als Ausgleich (Investment Grade vs. High Yield). Drittens das "
             "**Inflationsrisiko** - feste Zinsen verlieren real an Wert; dagegen helfen inflationsindexierte Anleihen. "
             "Im Portfolio sind sichere Staatsanleihen klassisch der **Stabilisator** und Gegenpol zu Aktien. Aber "
             "Achtung: 2022 fielen Aktien UND Anleihen zugleich (Zinsschock) - die Diversifikation versagte zeitweise. "
             "Praktisch nutzen die meisten **Anleihen-ETFs**; kurze Laufzeiten sind ruhiger, lange chancenreicher, aber "
             "zinssensitiver.",
     "kernaussagen": ["Steigende Zinsen druecken bestehende Anleihekurse (Duration = Sensitivitaet).",
                      "Bonitaet: Investment Grade vs. High Yield - mehr Risiko, mehr Zins.",
                      "Anleihen stabilisieren meist - aber nicht immer (2022)."],
     "quizzes": [
        _pfq("Was passiert mit Anleihekursen, wenn die Zinsen steigen?", ["Sie fallen", "Sie steigen", "Nichts"], 0,
          "Bestehende niedrigere Kupons werden unattraktiver."),
        _pfq("Was misst die Duration?", ["Die Zins-Sensitivitaet des Kurses", "Die Dividende", "Die Bonitaet"], 0,
          "Kursaenderung je 1 Prozentpunkt Zinsaenderung."),
        _pfq("High-Yield-Anleihen bieten mehr Zins, weil ...?", ["Hoeheres Ausfallrisiko ausgeglichen wird",
          "Sie sicherer sind", "Der Staat zahlt"], 0, "Schlechtere Bonitaet = Risikoaufschlag.")]},
    {"key": "pf_waehrung", "title": "Waehrungsrisiko & Hedging",
     "body": "Wer als Euro-Anleger einen Welt-ETF haelt, besitzt ueberwiegend Anlagen in **Fremdwaehrungen** (viel "
             "US-Dollar). Damit traegst du ein **Waehrungsrisiko**: Faellt der Dollar gegenueber dem Euro, sinkt dein "
             "Wert in Euro - selbst wenn die Aktien in Dollar gleich bleiben (genau das siehst du, wenn die App "
             "US-Werte in EUR umrechnet). Bei breit gestreuten **Aktien** ist das langfristig meist untergeordnet und "
             "teils sogar nuetzlich (Waehrungen streuen zusaetzlich, Konzerne sind global). Bei **Anleihen** dagegen "
             "ist das Waehrungsrisiko oft groesser als der Ertrag selbst - hier sind 'EUR-hedged'-Varianten "
             "verbreitet, die den Wechselkurs gegen eine kleine Gebuehr absichern. **Hedging** kostet und lohnt sich "
             "v.a. bei schwankungsarmen Anlagen (Anleihen), kaum bei Aktien. Ein verwandtes Thema ist der **Home "
             "Bias**: Viele uebergewichten den Heimatmarkt aus Vertrautheit - das erhoeht das Klumpenrisiko und wird "
             "meist nicht belohnt. Fazit: Waehrungsrisiko bei globalen Aktien bewusst akzeptieren, bei Anleihen ueber "
             "Hedging nachdenken, Home Bias vermeiden.",
     "kernaussagen": ["Globale Aktien tragen Fremdwaehrungsrisiko - langfristig meist untergeordnet.",
                      "Bei Anleihen ist Waehrungssicherung (Hedging) oft sinnvoll.",
                      "Home Bias erhoeht Klumpenrisiko ohne Belohnung."],
     "quizzes": [
        _pfq("Wie wirkt ein fallender US-Dollar fuer Euro-Anleger?", ["Senkt den EUR-Wert von US-Anlagen",
          "Erhoeht ihn immer", "Keine Wirkung"], 0, "Der Wechselkurs schlaegt auf den Eurowert durch."),
        _pfq("Wo lohnt sich Waehrungssicherung am ehesten?", ["Bei Anleihen", "Bei breiten Aktien", "Nie"], 0,
          "Bei schwankungsarmen Anlagen ueberwiegt sonst das FX-Risiko."),
        _pfq("Was ist der Home Bias?", ["Uebergewichtung des Heimatmarkts", "Eine Steuer", "Ein ETF-Typ"], 0,
          "Erhoeht Klumpenrisiko, meist nicht belohnt.")]},
    {"key": "pf_faktoren", "title": "Faktor-Investing vertieft",
     "body": "Warum schwanken Renditen verschiedener Aktien systematisch? Die Forschung (Fama/French u.a.) fand neben "
             "dem allgemeinen **Marktrisiko** mehrere **Faktoren** mit langfristiger Mehrrendite ('Praemie'): **Value** "
             "(guenstig bewertete schlagen teure), **Size** (kleinere schlagen grosse), **Momentum** (zuletzt starke "
             "laufen weiter), **Quality/Profitability** (profitable, solide Firmen) und **Low Volatility** (ruhige "
             "Aktien mit erstaunlich gutem Risiko-Ertrag). Diese Praemien sind keine Gratisrendite, sondern Lohn fuer "
             "ein Risiko oder das Aushalten von Schmerz: Faktoren koennen **ueber ein Jahrzehnt** unterperformen (Value "
             "2010-2020!), was viele genau zum falschen Zeitpunkt aufgeben laesst. Umsetzbar sind sie ueber "
             "**Faktor-ETFs** (z.B. 'World Value/Momentum/Quality') oder Multi-Faktor-Produkte. Vorbehalte: Nach "
             "Veroeffentlichung schrumpfen Praemien oft, Kosten und Umschichtung zehren, und manches koennte "
             "Data-Mining sein. Faktor-Investing ist **kein Timing** ('jetzt Value') und kein Muss - fuer die meisten "
             "reicht ein breiter Markt-ETF. Wer Faktoren nutzt, braucht vor allem Disziplin, eine lange Durststrecke "
             "durchzuhalten - sonst dreht sich der Vorteil ins Gegenteil.",
     "kernaussagen": ["Dokumentierte Praemien: Value, Size, Momentum, Quality, Low-Vol.",
                      "Praemien sind real, koennen aber ein Jahrzehnt unterperformen.",
                      "Faktoren brauchen Disziplin - kein Timing, kein Muss."],
     "quizzes": [
        _pfq("Was ist KEIN klassischer Faktor?", ["Die Logo-Farbe", "Value", "Momentum"], 0,
          "Faktoren sind systematische Renditequellen, kein Branding."),
        _pfq("Was ist die groesste Gefahr beim Faktor-Investing?", ["Lange Durststrecken - man gibt zu frueh auf",
          "Zu hohe Sicherheit", "Keine Auswahl"], 0, "Value unterperformte z.B. 2010-2020."),
        _pfq("Faktor-Investing ist ...?", ["Langfristige Ausrichtung, kein Timing", "Schnelles Traden",
          "Garantiert"], 0, "Disziplin ueber Jahre entscheidet.")]},
    {"key": "pf_immobilien", "title": "Immobilien & REITs im Portfolio",
     "body": "Immobilien sind fuer viele die wichtigste Anlage - oft unbewusst. Das **Eigenheim** ist primaer Konsum "
             "und ein riesiges **Klumpenrisiko** (ein Objekt, ein Standort, meist stark gehebelt durch den Kredit) - es "
             "gehoert nicht ins Wertpapier-Portfolio, sollte aber im Gesamtvermoegen mitgedacht werden. Fuer "
             "Anlage-Immobilien im Depot gibt es **REITs** (Real Estate Investment Trusts) und Immobilien-ETFs: "
             "boersengehandelt, liquide, schuetten den Grossteil der Mieten als Dividende aus und bieten etwas "
             "Diversifikation plus Inflationsschutz. Aber: REITs sind **zinssensitiv** (steigende Zinsen belasten, da "
             "Immobilien fremdfinanziert sind) und korrelieren staerker mit Aktien, als viele denken - der "
             "Diversifikationsnutzen ist begrenzt. **Offene Immobilienfonds** haben eine eigene Tuecke: In Krisen "
             "koennen sie die Ruecknahme aussetzen (Liquiditaetsrisiko), obwohl sie 'stabil' aussehen. Fazit: "
             "Immobilien koennen ein sinnvoller, inflationsschuetzender Baustein sein - in Massen und im Bewusstsein, "
             "dass ein Eigenheim bereits ein grosses Immobilien-Exposure ist.",
     "kernaussagen": ["Eigenheim = Konsum + grosses Klumpenrisiko, im Gesamtvermoegen mitdenken.",
                      "REITs sind liquide, aber zinssensitiv und aktiennaeher als gedacht.",
                      "Offene Immofonds koennen die Ruecknahme aussetzen."],
     "quizzes": [
        _pfq("Das Eigenheim ist im Portfolio-Kontext v.a. ...?", ["Konsum + Klumpenrisiko", "Perfekt diversifiziert",
          "Risikolos"], 0, "Ein Objekt, ein Standort, oft gehebelt."),
        _pfq("Wovon haengen REITs stark ab?", ["Von den Zinsen", "Vom Goldpreis", "Von gar nichts"], 0,
          "Immobilien sind fremdfinanziert - zinssensitiv."),
        _pfq("Welches Risiko haben offene Immobilienfonds?", ["Aussetzung der Ruecknahme (Liquiditaet)", "Keines",
          "Garantierte Verluste"], 0, "In Krisen kann das Geld zeitweise feststecken.")]},
  ]},
 {"key": "m7", "title": "Modul 7 - Steuern, Altersvorsorge & Entnahme (Deutschland)",
  "intro": "Was am Ende netto bleibt: Steuern, Vorsorge und wie man im Ruhestand klug entnimmt.",
  "lessons": [
    {"key": "pf_steuern_de", "title": "Steuern fuer Anleger in Deutschland",
     "body": "Steuern entscheiden ueber die **Nettorendite** - hier die Grundzuege (allgemein, kein Steuerrat; Details "
             "mit Steuerberater). Auf Kapitalertraege (realisierte Kursgewinne, Dividenden, Zinsen) faellt die "
             "**Abgeltungsteuer** von 25% plus Solidaritaetszuschlag an (zusammen ~26,4%), ggf. plus Kirchensteuer. "
             "Jeder hat einen jaehrlichen **Sparer-Pauschbetrag** (1.000 EUR, Paare 2.000 EUR), bis zu dem Ertraege "
             "steuerfrei bleiben - per **Freistellungsauftrag** bei der Bank aktivieren, sonst verschenkt man ihn. Bei "
             "thesaurierenden Fonds greift die **Vorabpauschale**: eine jaehrliche Mindestbesteuerung auf einen "
             "fiktiven Basisertrag (in Niedrigzinsjahren niedrig oder null). Ein wichtiger Vorteil von Aktienfonds/-ETFs "
             "ist die **Teilfreistellung**: 30% der Ertraege sind steuerfrei. Beim Verkauf gilt **FIFO** (zuerst "
             "gekaufte Anteile zuerst verkauft). Verluste landen in **Verlustverrechnungstoepfen** und koennen Gewinne "
             "steuerlich ausgleichen. Der vielleicht groesste Hebel ist die **Steuerstundung**: Wer selten verkauft, "
             "laesst Gewinne unversteuert weiterarbeiten - der Staat gibt dir quasi einen zinslosen Kredit auf die "
             "spaeter faellige Steuer. Buy-and-hold ist damit auch steuerlich oft ueberlegen.",
     "kernaussagen": ["Abgeltungsteuer ~26,4% (+ ggf. Kirchensteuer); Pauschbetrag per Freistellungsauftrag nutzen.",
                      "Aktien-ETFs: 30% Teilfreistellung; Verluste sind verrechenbar.",
                      "Steuerstundung durch seltenes Verkaufen ist ein grosser Hebel."],
     "quizzes": [
        _pfq("Wie nutzt man den Sparer-Pauschbetrag?", ["Freistellungsauftrag bei der Bank", "Automatisch nichts tun",
          "Beim Finanzamt anrufen"], 0, "Ohne Auftrag wird er nicht beruecksichtigt."),
        _pfq("Was ist die Teilfreistellung bei Aktien-ETFs?", ["30% der Ertraege steuerfrei", "100% steuerfrei",
          "Eine Strafsteuer"], 0, "Ausgleich fuer Steuern auf Fondsebene."),
        _pfq("Warum hilft seltenes Verkaufen steuerlich?", ["Steuerstundung - Gewinne arbeiten unversteuert weiter",
          "Verkaufen ist verboten", "Gar nicht"], 0, "Zinsloser Steuerkredit bis zum Verkauf.")]},
    {"key": "pf_altersvorsorge", "title": "Altersvorsorge & langfristiger Aufbau",
     "body": "Die gesetzliche Rente allein reicht fuer die meisten nicht - es entsteht eine **Rentenluecke**. Vorsorge "
             "denkt man oft im **Drei-Schichten-Modell**: 1. Basis (gesetzliche Rente, Ruerup), 2. gefoerderte "
             "Zusatzvorsorge (betriebliche Altersvorsorge, Riester), 3. private, flexible Vorsorge (Depot, "
             "Immobilien). Fuer den langfristigen, flexiblen Aufbau ist ein **breiter ETF-Sparplan** ein beliebter "
             "Baustein: guenstig, liquide, transparent. Versicherungsmaentel (Renten-/Fondspolicen) bieten "
             "Steuervorteile in der Auszahlung, sind aber oft teuer und unflexibel - genau hinsehen lohnt. Entscheidend "
             "ist der **Zeithorizont**: Mit 30-40 Jahren Anlagedauer kann die Aktienquote hoch sein, weil Schwankungen "
             "ausgesessen werden. Naehert sich der Ruhestand, senkt man die Aktienquote oft schrittweise "
             "(**Glidepath**), um kurz vor der Entnahme nicht von einem Crash getroffen zu werden. Wichtig: frueh "
             "anfangen (Zinseszins!), Kosten niedrig halten und die Vorsorge zur eigenen Lebenslage passen lassen. "
             "Vorsorge ist Marathon, nicht Sprint.",
     "kernaussagen": ["Rentenluecke ist real - Drei-Schichten-Modell als Rahmen.",
                      "ETF-Sparplan: guenstig & flexibel; Policen oft teuer.",
                      "Zum Ruhestand hin Aktienquote schrittweise senken (Glidepath)."],
     "quizzes": [
        _pfq("Was beschreibt die 'Rentenluecke'?", ["Gesetzliche Rente deckt den Bedarf nicht", "Eine Steuer",
          "Ein ETF"], 0, "Daher private Zusatzvorsorge."),
        _pfq("Was ist ein 'Glidepath'?", ["Aktienquote zum Ruhestand hin senken", "Ein ETF-Name", "Eine Order"], 0,
          "Schutz vor Crash kurz vor der Entnahme."),
        _pfq("Was ist beim langfristigen Aufbau am wichtigsten?", ["Frueh anfangen + niedrige Kosten", "Market Timing",
          "Hebelprodukte"], 0, "Zeit und Kosten dominieren das Ergebnis.")]},
    {"key": "pf_entnahme_deep", "title": "Entnahmestrategien im Detail",
     "body": "Vom Vermoegen zu leben ist anspruchsvoller, als es aufzubauen. Die **4%-Regel** (im 1. Jahr 4% entnehmen, "
             "dann inflationsangepasst) ist nur der Ausgangspunkt - sie beruht auf historischen US-Daten und 30 "
             "Jahren. Das groesste Risiko ist das **Renditereihenfolge-Risiko**: Ein schwerer Crash gleich zu Beginn "
             "der Entnahme kann das Kapital so reduzieren, dass es sich nie erholt - dieselbe Durchschnittsrendite mit "
             "Crash am Anfang vs. am Ende fuehrt zu voellig verschiedenen Ergebnissen. Gegenmittel: **dynamische "
             "Entnahme** (in schlechten Jahren weniger, 'Leitplanken' a la Guyton-Klinger), ein **Cash-/Anleihen-"
             "Puffer** von 1-3 Jahresausgaben (man verkauft im Crash keine Aktien, sondern lebt vom Puffer = "
             "**Bucket-Strategie**) und eine etwas vorsichtigere Anfangsquote. Auch die Faehigkeit, grosse Ausgaben "
             "aufzuschieben, hilft enorm. Steuerlich entnimmt man oft zuerst aus Toepfen mit geringer Last und nutzt "
             "jaehrlich den Pauschbetrag. Kurz: Eine starre 4%-Entnahme ist riskanter als eine flexible Strategie mit "
             "Puffer - Anpassungsfaehigkeit schlaegt eine feste Zahl.",
     "kernaussagen": ["Renditereihenfolge-Risiko: fruehe Crashs sind in der Entnahme am gefaehrlichsten.",
                      "Cash-/Anleihen-Puffer (Bucket) verhindert Notverkaeufe im Tief.",
                      "Dynamisch statt starr entnehmen erhoeht die Sicherheit deutlich."],
     "quizzes": [
        _pfq("Was ist das Renditereihenfolge-Risiko?", ["Fruehe Verluste in der Entnahme wirken besonders stark",
          "Zu hohe Dividenden", "Eine Steuer"], 0, "Die Reihenfolge der Renditen entscheidet, nicht nur der Schnitt."),
        _pfq("Wozu dient ein Cash-/Anleihen-Puffer im Ruhestand?", ["Im Crash nicht Aktien verkaufen muessen",
          "Mehr Rendite", "Steuern sparen"], 0, "Bucket-Strategie gegen Notverkaeufe."),
        _pfq("Was ist sicherer als eine starre 4%-Entnahme?", ["Dynamische Entnahme mit Puffer", "Immer 4% egal was",
          "Alles sofort entnehmen"], 0, "Flexibilitaet schlaegt eine feste Zahl.")]},
  ]},
 {"key": "m8", "title": "Modul 8 - Praxis-Projekte: vom Wissen zum eigenen Plan",
  "intro": "Jetzt anwenden: ein eigenes Musterportfolio bauen und backtesten, den schriftlichen Plan schreiben, die Routine etablieren.",
  "lessons": [
    {"key": "pf_eigenes_portfolio", "title": "Projekt: Dein eigenes Musterportfolio bauen",
     "body": "Jetzt wird angewendet. In diesem Projekt baust du ein eigenes, breit gestreutes Musterportfolio und "
             "testest es. Vorgehen: 1. Lege anhand deines Risikoprofils eine **Zielallokation** fest (z.B. "
             "Aktien-ETF Welt, ein Anleihen-Anteil, etwas Cash; offensiver oder defensiver je nach dir). 2. Waehle "
             "konkrete, breite Bausteine (z.B. ein Welt-Aktien-ETF als Kern). 3. Trage die Positionen in 'Mein Depot' "
             "ein und lass den **Backtest** laufen: Schau dir Rendite p.a., Volatilitaet, Sharpe Ratio und Max "
             "Drawdown an - haettest du diesen Drawdown ausgehalten? 4. Pruefe die **Klumpenrisiko-/Allokations"
             "uebersicht**: Ist die Streuung wirklich breit, oder dominiert eine Klasse/Region? 5. Spiele im Rechner "
             "mit Sparplan und Diversifikation. Ziel ist nicht das 'perfekte' Portfolio (das gibt es nicht), sondern "
             "eines, das zu deinem Horizont und deiner Schmerzgrenze passt und das du verstehst. Dokumentiere deine "
             "Entscheidungen - das ist die Grundlage fuer den naechsten Schritt, deinen schriftlichen Plan.",
     "kernaussagen": ["Zielallokation festlegen, Bausteine waehlen, in 'Mein Depot' backtesten.",
                      "Max Drawdown ehrlich auf Aushaltbarkeit pruefen.",
                      "Ziel: ein Portfolio, das zu dir passt und das du verstehst."],
     "quizzes": [
        _pfq("Womit testest du dein Musterportfolio in der App?", ["Mit dem Depot-Backtest (Rendite, Sharpe, Drawdown)",
          "Mit dem Glossar", "Gar nicht"], 0, "Im Tab 'Mein Depot'."),
        _pfq("Worauf solltest du beim Max Drawdown achten?", ["Ob du ihn emotional ausgehalten haettest",
          "Dass er hoch ist", "Ihn ignorieren"], 0, "Durchhalten entscheidet ueber den Erfolg."),
        _pfq("Was ist das Ziel des Projekts?", ["Ein Portfolio, das zu dir passt und das du verstehst",
          "Das hoechstrenditeste", "Das komplizierteste"], 0, "Verstaendlich + durchhaltbar schlaegt 'optimal'.")]},
    {"key": "pf_ips", "title": "Projekt: Dein schriftlicher Anlageplan (IPS)",
     "body": "Profis arbeiten mit einem **Investment Policy Statement (IPS)** - einem kurzen schriftlichen Anlageplan. "
             "Fuer dich ist es das wirksamste Mittel gegen emotionale Fehler: Was schwarz auf weiss steht, befolgst du "
             "auch im Crash. Schreibe (1-2 Seiten genuegen) auf: dein **Ziel** und den **Zeithorizont** (wofuer, bis "
             "wann?); deine **Zielallokation** (z.B. 70% Aktien / 20% Anleihen / 10% Cash) und die erlaubten "
             "Bandbreiten; deine **Sparrate** und wie du sie automatisierst; deine **Rebalancing-Regel** (wann und "
             "wie); klare **Verkaufsgruende** - und ebenso wichtig, was KEIN Verkaufsgrund ist (z.B. 'der Markt "
             "faellt'); sowie **Verhaltensregeln** fuer Crashs ('Ich verkaufe nicht aus Angst; ich pruefe nur die "
             "These'). Lege auch fest, wie oft du ueberhaupt ins Depot schaust. Dieser Plan ist dein Kompass: in "
             "ruhigen Zeiten geschrieben, traegt er dich durch die stuermischen. Aktualisiere ihn nur bei echten "
             "Lebensaenderungen, nicht wegen Marktlaune.",
     "kernaussagen": ["Ein schriftlicher Plan (IPS) schuetzt vor emotionalen Fehlern.",
                      "Enthaelt Ziel, Allokation, Sparrate, Rebalancing- und Verkaufsregeln.",
                      "In ruhigen Zeiten schreiben, in stuermischen befolgen."],
     "quizzes": [
        _pfq("Wozu dient ein Investment Policy Statement?", ["Als Plan, der vor emotionalen Fehlern schuetzt",
          "Zur Steuererklaerung", "Als Werbung"], 0, "Geschrieben in Ruhe, befolgt im Sturm."),
        _pfq("Was gehoert in den Plan?", ["Zielallokation, Sparrate, Rebalancing- & Verkaufsregeln",
          "Nur der Lieblings-Tipp", "Nichts Konkretes"], 0, "Konkrete Regeln statt Bauchgefuehl."),
        _pfq("Wann aktualisiert man den IPS?", ["Bei echten Lebensaenderungen, nicht wegen Marktlaune", "Taeglich",
          "Nie"], 0, "Stabilitaet ist der Sinn der Sache.")]},
    {"key": "pf_review", "title": "Projekt: Deine jaehrliche Portfolio-Routine",
     "body": "Ein gutes Portfolio braucht wenig, aber regelmaessige Pflege - am besten als feste **Jahresroutine** "
             "(z.B. immer im Januar). Deine Checkliste: 1. **Allokation pruefen**: Weicht eine Klasse stark von der "
             "Zielquote ab? Dann **rebalancen** (oder ueber neue Sparraten ausgleichen). 2. **These/Fundament "
             "pruefen**: Stimmen die Annahmen noch (bei Einzelaktien: Moat, Zahlen)? 3. **Kosten checken**: Gibt es "
             "guenstigere Bausteine, schleichen sich Gebuehren ein? 4. **Sparrate anpassen**: mehr Einkommen -> mehr "
             "sparen (Gehaltserhoehung teilweise ins Depot). 5. **Steuern**: Pauschbetrag genutzt, Verluste "
             "verrechnet? 6. **Plan (IPS) abgleichen**: Haben sich Ziele/Lebensumstaende geaendert? Wichtig: NICHT "
             "oefter als noetig eingreifen - haeufiges Umschichten kostet Rendite, Steuern und Nerven. Eine ruhige, "
             "disziplinierte Jahresroutine schlaegt taegliches Nachschauen bei Weitem.",
     "kernaussagen": ["Einmal jaehrlich: Allokation, These, Kosten, Sparrate, Steuern, Plan pruefen.",
                      "Rebalancing am elegantesten ueber neue Einzahlungen.",
                      "Seltener eingreifen schlaegt taegliches Nachschauen."],
     "quizzes": [
        _pfq("Wie oft sollte die Portfolio-Routine idealerweise stattfinden?", ["Einmal jaehrlich", "Taeglich",
          "Nie"], 0, "Selten und diszipliniert."),
        _pfq("Wie rebalanciert man oft am elegantesten?", ["Ueber neue Sparraten", "Durch taegliches Traden",
          "Gar nicht"], 0, "Spart Steuern und Gebuehren."),
        _pfq("Was schadet der Rendite?", ["Haeufiges Umschichten", "Eine ruhige Jahresroutine", "Niedrige Kosten"], 0,
          "Aktionismus kostet Rendite, Steuern und Nerven.")]},
  ]},
]

# Lernzeit (Minuten, inkl. Lesen + Praxis-Uebung + Test) und Praxis-Uebung je Lektion
PF_DAUER = {
    "pf_warum": 60, "pf_klassen": 70, "pf_instrumente": 70,
    "pf_rendite": 75, "pf_risiko": 75, "pf_sharpe": 75,
    "pf_diversifikation": 95, "pf_allokation": 100, "pf_mpt": 85,
    "pf_passiv": 75, "pf_kosten": 80, "pf_sparplan": 90,
    "pf_rebalancing": 80, "pf_psychologie": 70, "pf_entnahme": 80,
    "pf_etf_auswahl": 100, "pf_anleihen": 95, "pf_waehrung": 85, "pf_faktoren": 100, "pf_immobilien": 80,
    "pf_steuern_de": 105, "pf_altersvorsorge": 95, "pf_entnahme_deep": 95,
    "pf_eigenes_portfolio": 150, "pf_ips": 120, "pf_review": 80,
}
PF_UEBUNG = {
    "pf_warum": "Rechne im Rechner (Tab 'Sparplan & Zinseszins') aus, was aus 200 EUR/Monat ueber 10, 20 und 30 Jahre wird - und notiere, wie sich der Ertragsanteil veraendert.",
    "pf_klassen": "Liste fuer dich auf, welche Anlageklassen du heute besitzt (inkl. Konto, Eigenheim, Rente) und schaetze grob ihre Anteile.",
    "pf_instrumente": "Suche zwei breite Welt-ETFs und notiere je Index, TER, ausschuettend/thesaurierend - vergleiche sie.",
    "pf_rendite": "Rechne eine nominale Rendite (z.B. 7%) bei 3% Inflation in die reale um - und ueberlege, was das ueber 20 Jahre fuer die Kaufkraft heisst.",
    "pf_risiko": "Schaetze ehrlich: Wie viel Prozent Depot-Minus haeltst du aus, ohne zu verkaufen? Notiere deine 'Schmerzgrenze'.",
    "pf_sharpe": "Lass in 'Mein Depot' einen Backtest laufen und lies Rendite, Volatilitaet und Sharpe Ratio ab - interpretiere die Zahlen.",
    "pf_diversifikation": "Oeffne im Rechner das Tab 'Diversifikation' und beobachte, wie die Portfolio-Vola bei Korrelation +1, 0 und -1 reagiert.",
    "pf_allokation": "Lege deine persoenliche Zielallokation fest (Aktien/Anleihen/Cash in %) - passend zu Horizont und Schmerzgrenze.",
    "pf_mpt": "Variiere im Diversifikations-Labor die Gewichtung und finde die Mischung mit der geringsten Volatilitaet.",
    "pf_passiv": "Skizziere ein Kern-Satellit-Depot: Welcher ETF waere dein Kern (%), welche 1-2 Satelliten kaemen in Frage?",
    "pf_kosten": "Vergleiche im Rechner ('Kosten-Effekt') 0,2% vs. 1,5% Kosten ueber 30 Jahre - wie gross ist der Unterschied?",
    "pf_sparplan": "Lege im Rechner deine realistische monatliche Sparrate fest und schau dir den 20-Jahres-Verlauf an.",
    "pf_rebalancing": "Lege deine Rebalancing-Regel fest (Intervall ODER Bandbreite, z.B. +/-5 Prozentpunkte).",
    "pf_psychologie": "Schreibe DEINE zwei groessten Anlagefehler-Risiken auf und je eine konkrete Gegenregel.",
    "pf_entnahme": "Rechne im Rechner ('Entnahme/4%-Regel') aus, welche monatliche Entnahme dein Zielvermoegen dauerhaft tragen koennte.",
    "pf_etf_auswahl": "Vergleiche drei konkrete Welt-ETFs nach Index, Replikation, Ausschuettung, TER und (wenn moeglich) Tracking-Differenz.",
    "pf_anleihen": "Schau dir zwei Anleihen-ETFs an (kurze vs. lange Laufzeit) und notiere den Unterschied bei Duration/Schwankung.",
    "pf_waehrung": "Pruefe bei deinem (geplanten) Welt-ETF den USA-/USD-Anteil und ueberlege, ob du bei Anleihen 'EUR-hedged' moechtest.",
    "pf_faktoren": "Recherchiere einen Faktor-ETF (z.B. Value oder Momentum) und beschreibe in 3 Saetzen seine Idee und sein Risiko.",
    "pf_immobilien": "Schaetze dein gesamtes Immobilien-Exposure (Eigenheim + REITs) und ueberlege, ob es ein Klumpenrisiko ist.",
    "pf_steuern_de": "Pruefe, ob dein Freistellungsauftrag eingerichtet ist, und schaetze im Rechner ('Steuer (DE)') die Steuer auf einen Beispielgewinn.",
    "pf_altersvorsorge": "Verschaffe dir einen Ueberblick ueber deine Vorsorge-Schichten (gesetzlich/betrieblich/privat) und identifiziere Luecken.",
    "pf_entnahme_deep": "Spiele im Entnahme-Rechner ein 'schlechtes Startjahr' durch (hohe Inflation, niedrige Rendite) und vergleiche die Reichweite.",
    "pf_eigenes_portfolio": "Baue in 'Mein Depot' ein vollstaendiges Musterportfolio, lass den Backtest laufen und pruefe Sharpe, Drawdown und Klumpenrisiko.",
    "pf_ips": "Schreibe deinen 1-seitigen Anlageplan (Ziel, Allokation, Sparrate, Rebalancing-Regel, Verkaufsgruende, Crash-Verhalten).",
    "pf_review": "Erstelle eine Review-Checkliste und trage dir einen festen jaehrlichen Termin in den Kalender ein.",
}
PF_HOURS = sum(PF_DAUER.values()) / 60.0

PF_TOTAL = sum(len(m["lessons"]) for m in CURRICULUM)

def render_portfolio_academy():
    """Lern-Spur 'Portfolio-Akademie' fuer die Lernen-Seite: Module -> Lektion -> Test."""
    st.subheader("Portfolio-Akademie: alles ueber Portfolios")
    st.caption(f"Vollwertiges Lernprogramm: rund {PF_HOURS:.0f} Lernstunden in {len(CURRICULUM)} Modulen und "
               f"{PF_TOTAL} Lektionen - jede mit Praxis-Uebung zum direkten Anwenden in 'Mein Depot' und 'Rechner'. "
               "Reine Bildung, keine Anlageberatung.")
    pfdone = st.session_state.setdefault("pf_done", [])
    done_min = sum(PF_DAUER.get(l["key"], 60) for m in CURRICULUM for l in m["lessons"] if l["key"] in pfdone)
    st.progress(len(pfdone) / PF_TOTAL if PF_TOTAL else 0.0,
                text=f"Fortschritt: {len(pfdone)}/{PF_TOTAL} Lektionen  ·  ~{done_min/60:.1f} von {PF_HOURS:.0f} Std.")
    mtitles = [m["title"] for m in CURRICULUM]
    mi = st.selectbox("Modul", list(range(len(CURRICULUM))), format_func=lambda i: mtitles[i], key="pf_mod")
    M = CURRICULUM[mi]
    mod_min = sum(PF_DAUER.get(l["key"], 60) for l in M["lessons"])
    st.caption(f"{M['intro']}  (Modul-Lernzeit: ~{mod_min/60:.1f} Std., {len(M['lessons'])} Lektionen)")
    ltitles = [("✓ " if l["key"] in pfdone else "") + l["title"] for l in M["lessons"]]
    li = st.selectbox("Lektion", list(range(len(M["lessons"]))), format_func=lambda i: ltitles[i], key="pf_les")
    L = M["lessons"][li]
    st.markdown(f"### {L['title']}")
    st.caption(f"⏱ Lernzeit: ~{PF_DAUER.get(L['key'], 60)} Min (inkl. Praxis-Uebung & Test)"
               + ("  ·  ✓ bereits bestanden" if L["key"] in pfdone else ""))
    st.markdown(L["body"])
    st.info("Kernaussagen: " + "  •  ".join(L["kernaussagen"]))
    if L["key"] in PF_UEBUNG:
        st.markdown(f'<div class="lock-card"><b>Praxis-Uebung</b><br><span style="font-size:.92rem">'
                    f'{PF_UEBUNG[L["key"]]}</span></div>', unsafe_allow_html=True)
    qs = L["quizzes"]; need = max(1, -(-(len(qs) * 7) // 10))
    st.markdown(f"**Test ({len(qs)} Fragen - ab {need} richtig bestanden)**")
    with st.form(key=f"pfform_{L['key']}"):
        picks = [st.radio(f"**{i+1}. {q['q']}**", q["options"], index=None, key=f"pfq_{L['key']}_{i}")
                 for i, q in enumerate(qs)]
        sub = st.form_submit_button("Test auswerten", type="primary")
    if sub:
        if any(p is None for p in picks):
            st.warning("Bitte alle Fragen beantworten.")
        else:
            correct = 0
            for i, (q, p) in enumerate(zip(qs, picks)):
                ok = q["options"].index(p) == q["correct"]; correct += ok
                if ok:
                    st.success(f"{i+1}. Richtig. {q['explain']}")
                else:
                    st.error(f"{i+1}. Leider falsch. Richtig: „{q['options'][q['correct']]}“ - {q['explain']}")
            st.markdown(f"**Ergebnis: {correct}/{len(qs)} ({correct/len(qs)*100:.0f}%)**")
            if correct >= need:
                st.success("Bestanden!")
                if L["key"] not in pfdone:
                    pfdone.append(L["key"]); st.session_state["pf_done"] = pfdone
            else:
                st.warning(f"Noch nicht bestanden - du brauchst {need}/{len(qs)}. Lektion nochmal lesen und erneut versuchen.")
    if len(pfdone) == PF_TOTAL:
        st.success("Stark - du hast die ganze Portfolio-Akademie geschafft!")
    st.markdown('<div class="fa-foot">FinAnalyse - reine Bildung, keine Anlageberatung. '
                'Direkt anwenden: Tab "Mein Depot" (Backtest, Allokation) und "Rechner" (Diversifikation, Sparplan, Entnahme).</div>',
                unsafe_allow_html=True)


# ============================================================
#  FINANZ-RECHNER (reine Funktionen - testbar, kein Netz)
#  Reine Bildungs-/Rechenwerkzeuge auf eigene Eingaben. Keine Anlageberatung.
# ============================================================
def fv_savings(monthly, years, annual_rate, initial=0.0):
    """Sparplan-Endwert: Startkapital + monatliche Rate (am Monatsende), monatlich verzinst.
    Gibt end, eingezahlt, ertrag, jaehrliche Serie und Monatszahl zurueck."""
    r = annual_rate / 12.0
    n = max(0, int(round(years * 12)))
    bal = float(initial)
    series = []
    for m in range(1, n + 1):
        bal = bal * (1 + r) + monthly
        if m % 12 == 0:
            series.append(round(bal, 2))
    eingezahlt = float(initial) + monthly * n
    return {"end": bal, "eingezahlt": eingezahlt, "ertrag": bal - eingezahlt, "series": series, "monate": n}

def emergency_fund(monthly_expenses, months=3):
    """Notgroschen-Zielbetrag = monatliche Ausgaben x Monate (ueblich 3-6)."""
    return max(0.0, float(monthly_expenses)) * max(0, int(months))

def fee_drag(initial, monthly, years, gross_rate, fee_rate):
    """Kosten-Effekt: Endwert mit Bruttorendite vs. mit Nettorendite (brutto - Kosten p.a.)."""
    brutto = fv_savings(monthly, years, gross_rate, initial)["end"]
    netto = fv_savings(monthly, years, max(-0.99, gross_rate - fee_rate), initial)["end"]
    return {"brutto": brutto, "netto": netto, "kosten": brutto - netto}

def abgeltung_net(gain, pauschbetrag=1000.0, kirchensteuer_rate=0.0):
    """Netto nach Abgeltungsteuer (25%) + Soli (5,5%) + optional Kirchensteuer, auf Gewinn ueber Freibetrag.
    Allgemeine Rechnung, kein Steuerrat."""
    gain = float(gain)
    zu_versteuern = max(0.0, gain - max(0.0, pauschbetrag))
    base = zu_versteuern * 0.25
    soli = base * 0.055
    kist = base * max(0.0, kirchensteuer_rate)
    steuer = base + soli + kist
    return {"steuer": steuer, "netto": gain - steuer, "zu_versteuern": zu_versteuern,
            "satz_eff": (steuer / gain if gain > 0 else 0.0)}

def withdrawal_years(capital, monthly_withdrawal, annual_rate, infl=0.0, max_years=100):
    """Wie lange reicht das Kapital bei monatlicher Entnahme (optional inflationsangepasst)?
    Gibt Jahre (float) zurueck oder None, wenn es laenger als max_years reicht."""
    r = annual_rate / 12.0
    g = infl / 12.0
    bal = float(capital)
    w = float(monthly_withdrawal)
    cap_m = int(max_years * 12)
    for m in range(1, cap_m + 1):
        bal = bal * (1 + r) - w
        w = w * (1 + g)
        if bal <= 0:
            return round(m / 12.0, 2)
    return None

def safe_withdrawal(capital, rate=0.04):
    """4%-Regel (Orientierung, keine Empfehlung): jaehrliche und monatliche Entnahme."""
    jahr = float(capital) * rate
    return {"jahr": jahr, "monat": jahr / 12.0}

def position_size(depot_value, max_pct):
    """Maximaler Euro-Betrag pro Einzelposition nach selbst gewaehlter Max-%-Regel."""
    return max(0.0, float(depot_value)) * max(0.0, float(max_pct))

def allocation_breakdown(rows):
    """rows: Liste von {Name, Ticker, Wert EUR}. Gruppiert nach Anlageklasse (classify_asset).
    Gibt (dict klasse->(wert, anteil), total, groesste_position(name, wert, anteil)) zurueck."""
    buckets = {}
    total = 0.0
    biggest = (None, 0.0)
    for r in rows:
        w = r.get("Wert EUR")
        if not isinstance(w, (int, float)):
            continue
        total += w
        cls = classify_asset(str(r.get("Name", "")), str(r.get("Ticker", "")))
        buckets[cls] = buckets.get(cls, 0.0) + w
        if w > biggest[1]:
            biggest = (str(r.get("Name", ""))[:24], float(w))
    out = {k: (v, (v / total if total else 0.0)) for k, v in buckets.items()}
    big = (biggest[0], biggest[1], (biggest[1] / total if total else 0.0))
    return out, total, big


def sparkline(series, up=True, height=70):
    """Saubere Mini-Sparkline (Altair): y auf den Datenbereich gezoomt (nicht ab 0!),
    keine Achsen/Gitter, dezente Flaeche + Linie, Farbe nach Auf/Ab. None = Fallback."""
    try:
        import altair as alt
        vals = [float(v) for v in list(series.values)]
        if len(vals) < 2:
            return None
        df = pd.DataFrame({"i": list(range(len(vals))), "v": vals})
        lo, hi = min(vals), max(vals)
        pad = (hi - lo) * 0.18 if hi > lo else (abs(hi) * 0.02 + 1e-6)
        color = "#16a34a" if up else "#dc2626"
        base = alt.Chart(df).encode(
            x=alt.X("i:Q", axis=None),
            y=alt.Y("v:Q", scale=alt.Scale(domain=[lo - pad, hi + pad]), axis=None))
        area = base.mark_area(color=color, opacity=0.14, line=False)
        line = base.mark_line(color=color, strokeWidth=2.2)
        return (area + line).properties(height=height).configure_view(strokeWidth=0).configure_axis(grid=False)
    except Exception:
        return None


# ====================== SEITE: DASHBOARD ======================
if page == "dash":
    if yf is None:
        st.stop()

    h1, h2 = st.columns([3, 1])
    h1.subheader(t("dashboard"))
    h2.caption(f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    st.markdown(f"#### {t('market_today')}")
    query = st.text_input(t("market_search"), value="",
                          placeholder="Ticker eingeben, z.B. AAPL, NVDA, BTC-EUR, GC=F (Gold), ^GSPC (S&P 500)",
                          key="mkt_search",
                          help="yfinance-Format. US: AAPL. Deutschland: SAP.DE. Krypto: BTC-EUR. Index: ^GDAXI. Rohstoff: GC=F.").strip().upper()
    if query:
        with st.spinner(f"Suche {query} ..."):
            res = quote_search(query)
        if res is not None:
            qc1, qc2 = st.columns([1, 2])
            qc1.metric(query, fmt_quote(res["last"]), delta=f"{res['chg']*100:+.2f}%")
            qc1.button("Vollanalyse oeffnen", key="mkt_full", on_click=goto_analyze, args=(query,),
                       help="Wechselt zur Einzelanalyse mit diesem Ticker.")
            _sp = sparkline(res["series"], res.get("chg", 0) >= 0, height=150)
            with qc2:
                if _sp is not None:
                    st.altair_chart(_sp, use_container_width=True)
                else:
                    st.line_chart(res["series"], height=160)
            st.caption("Letzter Kurs & Veraenderung zum Vortag, Chart = letzter Monat. Quelle: Yahoo, ohne Gewaehr.")
        else:
            st.warning(f"Kein Kurs fuer '{query}' gefunden. Tickerformat pruefen: US (AAPL), Deutschland (SAP.DE), "
                       "Krypto (BTC-EUR), Index (^GDAXI), Rohstoff (GC=F).")

    with st.spinner("Lade Marktdaten ..."):
        hist = market_history(tuple(s for s, _ in MARKET_INDICES), "1mo")
    per_row = 4
    for start in range(0, len(MARKET_INDICES), per_row):
        chunk = MARKET_INDICES[start:start + per_row]
        cols = st.columns(per_row)
        for j, (sym, lab) in enumerate(chunk):
            ser = None
            if hist is not None and sym in getattr(hist, "columns", []):
                s = hist[sym].dropna()
                if len(s):
                    ser = s
            with cols[j]:
                if ser is not None:
                    last = float(ser.iloc[-1])
                    prev = float(ser.iloc[-2]) if len(ser) >= 2 else last
                    chg = (last / prev - 1) if prev else 0.0
                    st.metric(lab, fmt_quote(last), delta=f"{chg*100:+.2f}%")
                    _sp = sparkline(ser, chg >= 0, height=70)
                    if _sp is not None:
                        st.altair_chart(_sp, use_container_width=True)
                    else:
                        st.line_chart(ser, height=90)
                else:
                    st.metric(lab, "-")
    st.caption("Kacheln: letzter Kurs + Veraenderung zum Vortag, Mini-Chart = letzter Monat. Quelle: Yahoo, ohne Gewaehr.")

    st.markdown("---")
    st.markdown(f"#### {t('your_wl')}")
    if not st.session_state["watchlist"]:
        st.info("Deine Watchlist ist noch leer. Analysiere eine Aktie und merke sie dir - dann erscheint sie hier "
                "automatisch mit Live-Score und Fazit.")
        st.button("Jetzt erste Aktie analysieren", key="wl_empty_go", on_click=goto_single, type="primary")
    else:
        with st.spinner("Berechne Scores ..."):
            rows = [watchlist_row(tk) for tk in st.session_state["watchlist"]]
        hdr = st.columns([2, 1, 1, 1, 1.5, 1.2])
        for c, txt in zip(hdr, ["Titel", "Quality", "Value", "PEG", "Fazit", ""]):
            c.markdown(f"**{txt}**")
        for r in rows:
            c = st.columns([2, 1, 1, 1, 1.5, 1.2])
            if not r["ok"]:
                c[0].markdown(f"**{r['ticker']}**")
                c[1].caption("Daten n/a")
                c[5].button(t("analyze"), key=f"dash_an_{r['ticker']}", on_click=goto_analyze, args=(r["ticker"],))
                continue
            c[0].markdown(f"**{r['ticker']}**  \n<span style='color:#8a97ab;font-size:.78rem'>{r['name'][:24]}</span>", unsafe_allow_html=True)
            c[1].write(fmt_pct(r["q"]))
            c[2].write(fmt_pct(r["v"]))
            c[3].write(f"{r['peg']:.2f}" if r["peg"] else "-")
            c[4].markdown(dash_pill_html(r["verdict"]), unsafe_allow_html=True)
            c[5].button(t("analyze"), key=f"dash_an_{r['ticker']}", on_click=goto_analyze, args=(r["ticker"],))

    st.markdown("---")
    st.markdown(f"#### {t('pf_snapshot')}")
    if "bt" in st.session_state:
        B = st.session_state["bt"]; bt = B["bt"]; cap = B.get("capital", 10000.0)
        end = float(cap * bt["equity"].iloc[-1])
        pc = st.columns(4)
        pc[0].metric("Endwert", f"{end:,.0f} EUR", delta=f"{(bt['equity'].iloc[-1]-1)*100:+.1f}%")
        pc[1].metric("Rendite p.a.", f"{bt['ann_ret']*100:.1f}%")
        pc[2].metric("Sharpe", f"{bt['sharpe']:.2f}" if bt['sharpe'] else "-")
        pc[3].metric("Max Drawdown", f"{bt['max_dd']*100:.1f}%")
        st.line_chart(bt["equity"] * cap)
    else:
        st.info("Noch kein Backtest - im Tab 'Portfolio & Backtest' ein Portfolio testen, dann erscheint hier der Snapshot.")

    st.markdown("---")
    st.markdown("#### News zu deinen Positionen")
    if not is_pro():
        st.markdown(locked_card_html("News zu deinen Positionen (Plus & Pro)",
                    "Aktuelle Wirtschafts-News, automatisch gefiltert nach deinen Depot-Werten - "
                    "Schlagzeile, Kurzfassung und Link zur Originalquelle."),
                    unsafe_allow_html=True)
    else:
        news_ticks = depot_news_tickers()
        nkey = get_news_key(); nprov = get_news_provider()
        if not news_ticks:
            st.info("Lege zuerst Positionen unter 'Mein Depot' an - dann erscheinen hier passende News.")
        elif not nkey:
            st.info("News braucht eine lizenzierte Quelle. Hinterlege `NEWS_API_KEY` (und optional `NEWS_PROVIDER` = "
                    "'finnhub' oder 'marketaux') in den Streamlit-Secrets oder als Umgebungsvariable. Es werden dann nur "
                    "Schlagzeile, kurzer Auszug und ein Link zur Originalquelle angezeigt - kein Volltext.")
        else:
            with st.spinner("Lade News zu deinen Positionen ..."):
                news_items, news_status = cached_company_news(tuple(news_ticks), nprov, nkey)
            if news_status == "ok" and news_items:
                for it in news_items:
                    meta = " · ".join(x for x in [it.get("source", ""),
                                                  ", ".join(it.get("tickers", [])[:3]),
                                                  it.get("published", "")] if x)
                    st.markdown(f"**[{it['title']}]({it['url']})**")
                    if it.get("summary"):
                        st.caption(it["summary"])
                    if meta:
                        st.caption(meta)
                    st.markdown("<hr style='margin:4px 0 10px;border:0;border-top:1px solid rgba(130,130,155,.18)'>",
                                unsafe_allow_html=True)
                st.caption(f"Quelle: {news_provider_label(nprov)}. Es werden nur Schlagzeile, kurzer Auszug und Link "
                           "gezeigt; vollstaendige Artikel beim jeweiligen Anbieter. Fuer den oeffentlichen Betrieb eine "
                           "lizenzierte Quelle nutzen und robots.txt/AGB beachten. Reine Information, keine Anlageberatung.")
            elif news_status == "error":
                st.warning("News konnten nicht geladen werden - Schluessel, Provider oder Kontingent pruefen.")
            else:
                st.info("Aktuell keine passenden News zu deinen Positionen gefunden. Manche Ticker (z.B. ETFs, Krypto, "
                        "Rohstoffe) liefern bei der Quelle keine Unternehmens-News.")

    st.markdown('<div class="fa-foot">FinAnalyse - Bildungs- & Analyse-Tool. Keine Anlageberatung. '
                'Marktdaten ggf. verzoegert, ohne Gewaehr.</div>', unsafe_allow_html=True)


# ====================== SEITE: MEIN DEPOT ======================
elif page == "depot":
    st.subheader(t("mein_depot"))
    st.caption("Reale Positionen + Live-Kurse = exakter Depotwert. Plus geldgewichtete Rendite (XIRR) und ein "
               "Backtest deiner echten Mischung. Daten bleiben nur in dieser Sitzung.")

    st.markdown("#### 1. Positionen")
    st.caption("Ticker ggf. anpassen (yfinance-Format, z.B. EUNL.DE, BTC-EUR, MSFT). "
               "Spalte 'Kurs EUR' nur ausfuellen, wenn du den Live-Kurs ueberschreiben willst (sonst 0 = live).")
    base_df = pd.DataFrame(
        [{"Name": n, "Ticker": tk, "Stueck": q, "Waehrung": cur, "Kurs EUR (0=live)": ov}
         for n, tk, q, cur, ov in EXAMPLE_HOLDINGS])
    holdings = st.data_editor(base_df, num_rows="dynamic", use_container_width=True, key="hold_edit")
    # Tickerliste fuer das News-Modul im Dashboard merken
    st.session_state["depot_tickers"] = [str(t).strip().upper() for t in holdings["Ticker"].tolist()
                                         if isinstance(t, str) and str(t).strip()]

    cdep1, cdep2 = st.columns(2)
    cash = cdep1.number_input("Cash / Verrechnungskonto (EUR)", value=133.83, step=10.0, key="depot_cash",
                              help="Nicht investiertes Guthaben auf dem Verrechnungskonto.")
    broker_total = cdep2.number_input("Depotwert lt. Broker (EUR, optional Abgleich)", value=10430.18, step=10.0,
                                      key="depot_broker", help="Zum Vergleich: der Gesamtwert, den deine Broker-App anzeigt.")

    if st.button("Depotwert berechnen", type="primary", key="calc_depot"):
        fx = eurusd_rate()
        rows_out = []
        total = 0.0
        for _, r in holdings.iterrows():
            try:
                stk = float(r.get("Stueck") or 0)
            except Exception:
                stk = 0.0
            tk = str(r.get("Ticker") or "").strip()
            cur = str(r.get("Waehrung") or "EUR").strip()
            try:
                ov = float(r.get("Kurs EUR (0=live)") or 0)
            except Exception:
                ov = 0.0
            if ov > 0:
                price_eur, src = ov, "manuell"
            else:
                lp = latest_price(tk) if tk else None
                price_eur, src = (to_eur(lp, cur, fx), "live") if lp is not None else (None, "fehlt")
            val = (stk * price_eur) if (price_eur is not None) else None
            if val is not None:
                total += val
            rows_out.append({"Name": r.get("Name", tk), "Ticker": tk, "Stueck": stk,
                             "Kurs EUR": (round(price_eur, 4) if price_eur is not None else "-"),
                             "Wert EUR": (round(val, 2) if val is not None else "Kurs fehlt"),
                             "Quelle": src})
        st.session_state["depot_calc"] = {"rows": rows_out, "total": total, "cash": cash,
                                          "broker": broker_total, "fx": fx}
        st.toast("Depotwert berechnet.")

    if "depot_calc" in st.session_state:
        D = st.session_state["depot_calc"]
        st.markdown("##### Ergebnis")
        st.dataframe(pd.DataFrame(D["rows"]), hide_index=True, use_container_width=True)
        gesamt = D["total"] + D["cash"]
        k1, k2, k3 = st.columns(3)
        k1.metric("Positionen", f"{D['total']:,.2f} EUR")
        k2.metric("+ Cash", f"{D['cash']:,.2f} EUR")
        k3.metric("Depotwert (berechnet)", f"{gesamt:,.2f} EUR")
        if D["broker"]:
            diff = gesamt - D["broker"]
            st.metric("Abgleich vs. Broker", f"{D['broker']:,.2f} EUR", delta=f"{diff:+,.2f} EUR Differenz")
            if abs(diff) < 1.0:
                st.success("Perfekter Abgleich - die Daten stimmen auf den Euro.")
            elif abs(diff) < max(50.0, 0.01 * D["broker"]):
                st.info("Geringe Differenz - meist Rundung, ein fehlender Live-Kurs oder Cash-Abweichung.")
            else:
                st.warning("Groessere Differenz - 'Kurs fehlt'-Zeilen pruefen (Ticker korrigieren oder Kurs EUR manuell eintragen).")
        if D["fx"]:
            st.caption(f"USD-Positionen mit EURUSD = {D['fx']:.4f} umgerechnet. Quelle 'live' = Yahoo, 'manuell' = dein Override.")
        vals = {}
        for _r in D["rows"]:
            _w = _r.get("Wert EUR")
            if isinstance(_w, (int, float)):
                vals[str(_r.get("Name", ""))[:20]] = _w
        if vals:
            st.markdown("**Verteilung nach Position (EUR)**")
            st.bar_chart(pd.Series(vals, name="EUR").sort_values(ascending=False))

        # ---- Allokation & Klumpenrisiko ----
        alloc, alloc_total, biggest = allocation_breakdown(D["rows"])
        if alloc and alloc_total > 0:
            st.markdown("**Allokation nach Anlageklasse**")
            st.bar_chart(pd.DataFrame({"Anteil %": {k: round(v[1] * 100, 1) for k, v in alloc.items()}}))
            if biggest[0]:
                share = biggest[2]
                txt = f"Groesste Einzelposition: **{biggest[0]}** mit {share*100:.1f}% des Wertpapierdepots."
                if share > 0.25:
                    st.warning(txt + " Deutliches Klumpenrisiko (ueber 25% in einer Position).")
                elif share > 0.15:
                    st.info(txt + " Achte auf das Klumpenrisiko (ueber 15%).")
                else:
                    st.caption(txt)
            st.caption("Reine Ist-Analyse deines Depots, keine Empfehlung. Hintergrund: Lektion 'Diversifikation' im Tab Lernen.")

        # ---- Wertentwicklung seit Start-/Kaufdatum ----
        st.markdown("**Wertentwicklung deiner aktuellen Positionen (EUR)**")
        wcs1, wcs2 = st.columns([1.6, 1])
        start_dt = wcs1.date_input("Seit (Start-/Kaufdatum)", value=date(2024, 1, 1), key="dev_start",
                                   help="Zeigt den Wertverlauf deiner HEUTIGEN Stueckzahlen seit diesem Datum bis heute.")
        wcs2.write(""); wcs2.write("")
        if wcs2.button("Verlauf anzeigen", key="dev_run", use_container_width=True):
            qmap, cmap = {}, {}
            for _, r in holdings.iterrows():
                tk = str(r.get("Ticker") or "").strip().upper()
                try:
                    q = float(r.get("Stueck") or 0)
                except Exception:
                    q = 0.0
                if tk and q > 0:
                    qmap[tk] = q; cmap[tk] = str(r.get("Waehrung") or "EUR")
            with st.spinner("Hole Kurshistorie ..."):
                pxh = fetch_prices(list(qmap.keys()) + ["EURUSD=X"], start=start_dt.isoformat()) if qmap else None
            if pxh is None or pxh.empty:
                st.error("Keine Kurshistorie erhalten. Ticker/Datum pruefen.")
                st.session_state.pop("dev_series", None)
            else:
                fx_series = pxh["EURUSD=X"] if "EURUSD=X" in getattr(pxh, "columns", []) else None
                vs = portfolio_value_series(pxh, qmap, cmap, fx_series)
                if vs is None or len(vs) < 2:
                    st.error("Zu wenige Datenpunkte - frueheres Datum oder andere Ticker probieren.")
                    st.session_state.pop("dev_series", None)
                else:
                    st.session_state["dev_series"] = vs
        if "dev_series" in st.session_state:
            vs = st.session_state["dev_series"]
            st.line_chart(vs.rename("Depotwert (EUR)"))
            dv1, dv2, dv3 = st.columns(3)
            dv1.metric("Startwert", f"{vs.iloc[0]:,.0f} EUR")
            dv2.metric("Aktuell", f"{vs.iloc[-1]:,.0f} EUR")
            chg = (vs.iloc[-1] / vs.iloc[0] - 1) * 100 if vs.iloc[0] else 0.0
            dv3.metric("Veraenderung", f"{chg:+.1f}%")
            st.caption("Wert deiner HEUTIGEN Stueckzahlen, rueckgerechnet mit historischen Kursen (live, EUR-konvertiert). "
                       "Beruecksichtigt keine zwischenzeitlichen Kaeufe/Verkaeufe oder Sparplan-Raten - zeigt den reinen "
                       "Kursverlauf deiner aktuellen Mischung. Keine Anlageberatung.")

    # ---- 2. XIRR ----
    st.markdown("---")
    st.markdown("#### 2. Echte Rendite (XIRR)")
    if not is_pro():
        st.markdown(locked_card_html("Geldgewichtete Rendite (XIRR)",
                    "Deine echte Rendite inkl. Sparplan-Timing - in Plus & Pro enthalten."),
                    unsafe_allow_html=True)
    else:
        st.caption("Trage jede Einzahlung/jeden Kauf ein (Datum + investierter Betrag). Der heutige Depotwert "
                   "wird automatisch als Schluss-Cashflow ergaenzt. Das ergibt deine echte Jahresrendite.")
        flows_df = pd.DataFrame([
            {"Datum (JJJJ-MM-TT)": "2024-12-01", "Investiert EUR": 5000.0},
            {"Datum (JJJJ-MM-TT)": "2025-06-01", "Investiert EUR": 3000.0},
            {"Datum (JJJJ-MM-TT)": "2025-12-01", "Investiert EUR": 1700.0},
        ])
        flows = st.data_editor(flows_df, num_rows="dynamic", use_container_width=True, key="flows_edit")
        end_val_default = 0.0
        if "depot_calc" in st.session_state:
            end_val_default = st.session_state["depot_calc"]["total"] + st.session_state["depot_calc"]["cash"]
        end_val = st.number_input("Heutiger Depotwert (EUR)", value=float(round(end_val_default or 10430.18, 2)),
                                  step=100.0, key="xirr_endval", help="Wird automatisch aus Schritt 1 uebernommen, falls berechnet.")
        if st.button("Rendite berechnen", key="calc_xirr"):
            cflows = []
            invested = 0.0
            for _, r in flows.iterrows():
                try:
                    d = datetime.fromisoformat(str(r["Datum (JJJJ-MM-TT)"]).strip()[:10]).date()
                    amt = float(r["Investiert EUR"] or 0)
                except Exception:
                    continue
                if amt > 0:
                    cflows.append((d, -amt)); invested += amt
            cflows.append((date.today(), float(end_val)))
            rr = xirr(cflows)
            st.session_state["xirr_res"] = {"rate": rr, "invested": invested, "end": end_val,
                                            "abs": end_val - invested, "n": len(cflows) - 1}

        if "xirr_res" in st.session_state:
            R = st.session_state["xirr_res"]
            x1, x2, x3, x4 = st.columns(4)
            x1.metric("Investiert (Summe)", f"{R['invested']:,.0f} EUR")
            x2.metric("Heutiger Wert", f"{R['end']:,.0f} EUR")
            x3.metric("Absolut", f"{R['abs']:+,.0f} EUR")
            x4.metric("Rendite p.a. (XIRR)", f"{R['rate']*100:.1f}%" if R["rate"] is not None else "n/a",
                      help="Geldgewichtet: beruecksichtigt Zeitpunkt UND Hoehe jeder Einzahlung.")
            if R["rate"] is None:
                st.warning("XIRR nicht berechenbar - mind. eine Einzahlung (positiver Betrag) und ein Datum noetig.")
            else:
                st.caption(f"XIRR ueber {R['n']} Einzahlung(en) + heutigen Wert. Geldgewichtet - beruecksichtigt "
                           "Zeitpunkt UND Hoehe jeder Einzahlung (anders als die simple +/- %-Anzeige im Broker).")

    # ---- 3. Depot-Backtest ----
    st.markdown("---")
    st.markdown("#### 3. Gesamtbewertung: Backtest & Szenario-Prognose")
    if not is_pro():
        st.markdown(locked_card_html("Depot-Gesamtbewertung",
                    "Backtest genau DEINER Positionen (Rendite p.a., Sharpe, Drawdown) PLUS Szenario-Prognose "
                    "(konservativ/basis/optimistisch) fuer dein ganzes Depot. In Plus & Pro."),
                    unsafe_allow_html=True)
    else:
        st.caption("Nutzt die Positionen aus Schritt 1, gewichtet nach aktuellem Wert. Zeigt Rendite p.a., "
                   "Sharpe Ratio und Max Drawdown - so haette sich genau deine Mischung in der Vergangenheit entwickelt.")
        bc1, bc2 = st.columns(2)
        bt_period = bc1.selectbox("Zeitraum", ["1y", "2y", "3y", "5y", "max"], index=2, key="depot_bt_period",
                                  help="Wie weit zurueck der Backtest reicht.")
        bt_cap_default = 10000.0
        if "depot_calc" in st.session_state:
            bt_cap_default = round(st.session_state["depot_calc"]["total"] + st.session_state["depot_calc"]["cash"], 2)
        bt_cap = bc2.number_input("Startkapital (EUR)", value=float(bt_cap_default or 10000.0), step=500.0,
                                  key="depot_bt_cap", help="Hypothetische Einmalanlage zu Beginn des Zeitraums.")
        if st.button("Depot-Backtest starten", type="primary", key="run_depot_bt"):
            fx = eurusd_rate()
            wval = holdings_values(holdings, fx)
            with st.spinner("Hole Kurshistorie & rechne ..."):
                prices = fetch_prices(list(wval.keys()), bt_period) if wval else None
            if prices is None or prices.empty:
                st.error("Keine Kursdaten erhalten - meist eine voruebergehende Yahoo-Drosselung. "
                         "Bitte 1-2x erneut starten oder kurz warten. Falls es bleibt: Ticker-Format pruefen "
                         "(z.B. SAP.DE, BTC-EUR) oder Internetverbindung/yfinance checken.")
                st.session_state.pop("depot_bt", None)
            else:
                prices = prices.reindex(columns=[c for c in wval if c in prices.columns]).dropna()
                if prices.shape[1] == 0 or prices.shape[0] < 10:
                    st.error("Zu wenige gueltige Kursdaten fuer einen Backtest. Ticker/Zeitraum pruefen.")
                    st.session_state.pop("depot_bt", None)
                else:
                    total_val = sum(wval.values())
                    incl_val = sum(wval[c] for c in prices.columns)
                    bt = backtest_portfolio(prices, wval)
                    st.session_state["depot_bt"] = {
                        "bt": bt, "prices": prices, "cap": bt_cap, "period": bt_period,
                        "weights": {c: (wval[c] / incl_val if incl_val else 0) for c in prices.columns},
                        "coverage": (incl_val / total_val if total_val else 0.0),
                        "missing": [c for c in wval if c not in prices.columns]}
                    st.toast("Depot-Backtest fertig.")

        if "depot_bt" in st.session_state:
            Bd = st.session_state["depot_bt"]; btx = Bd["bt"]; cap = Bd["cap"]
            endv = float(cap * btx["equity"].iloc[-1])
            st.markdown(f"##### Ergebnis ({Bd['period']}, {len(Bd['prices'])} Handelstage)")
            kk1, kk2, kk3, kk4 = st.columns(4)
            kk1.metric("Rendite p.a.", f"{btx['ann_ret']*100:.1f}%")
            kk2.metric("Volatilitaet", f"{btx['ann_vol']*100:.1f}%", help="Schwankungsbreite p.a. Hoeher = riskanter.")
            kk3.metric("Sharpe Ratio", f"{btx['sharpe']:.2f}" if btx['sharpe'] else "-", help="Rendite pro Risiko. >1 gut, >2 sehr gut.")
            kk4.metric("Max Drawdown", f"{btx['max_dd']*100:.1f}%", help="Groesster Verlust vom Hoch zum Tief.")
            ee1, ee2 = st.columns(2)
            ee1.metric("Startkapital", f"{cap:,.0f} EUR")
            ee2.metric("Endwert (Backtest)", f"{endv:,.0f} EUR", delta=f"{(btx['equity'].iloc[-1]-1)*100:+.1f}%")
            st.caption("Gewichtung (nach Wert): " + ", ".join(f"{c} {w*100:.0f}%" for c, w in Bd["weights"].items()))
            if Bd["coverage"] < 0.999:
                miss = ", ".join(Bd["missing"]) if Bd["missing"] else "-"
                st.warning(f"Abgedeckt: {Bd['coverage']*100:.0f}% des Depotwerts. Ohne Kurshistorie (ausgeschlossen): {miss}. "
                           "Ticker ggf. anpassen (z.B. EUR-Listing oder anderes Kuerzel).")
            st.markdown("**Depotwert-Kurve (EUR)**")
            st.line_chart(btx["equity"] * cap)
            st.markdown("**Einzelkurse (normiert)**")
            st.line_chart(Bd["prices"] / Bd["prices"].iloc[0])
            st.caption("Annahme: Einmalanlage am Startdatum mit DEINEN aktuellen Gewichten, taeglich rebalanciert. "
                       "Returns je Titel in Heimatwaehrung (FX vereinfacht), reproduziert NICHT den echten historischen "
                       "Depotverlauf (Sparplan/Kaeufe), sondern das Rendite-/Risikoprofil deiner Mischung. Keine Anlageberatung.")

            # ---- Szenario-Prognose aus dem Depot-Profil ----
            st.markdown("---")
            st.markdown("##### Szenario-Prognose (aus deinem Depot-Profil)")
            st.caption("Schreibt das Rendite-/Risikoprofil deiner Mischung in die Zukunft fort - in drei Szenarien.")
            _pc = st.session_state.get("depot_calc")
            proj_default = round((_pc["total"] + _pc["cash"]) if _pc else cap)
            pj1, pj2 = st.columns(2)
            p_horizon = pj1.selectbox("Prognose-Horizont (Jahre)", [1, 3, 5, 10, 20], index=2, key="depot_proj_h")
            p_start = pj2.number_input("Startwert heute (EUR)", value=float(proj_default or 0.0), step=1000.0,
                                       key="depot_proj_start", help="Standard = dein aktueller Depotwert inkl. Cash.")
            pts, base, cons, opt = project_portfolio(p_start, btx["ann_ret"], btx["ann_vol"], int(p_horizon))
            proj_df = pd.DataFrame({"Konservativ": cons, "Basis": base, "Optimistisch": opt}, index=list(pts))
            proj_df.index.name = "Jahr"
            st.line_chart(proj_df)
            _d = lambda v: (f"{(v/p_start-1)*100:+.0f}%" if p_start else None)
            pm1, pm2, pm3 = st.columns(3)
            pm1.metric(f"Konservativ (J{p_horizon})", f"{cons[-1]:,.0f} EUR", delta=_d(cons[-1]))
            pm2.metric(f"Basis (J{p_horizon})", f"{base[-1]:,.0f} EUR", delta=_d(base[-1]))
            pm3.metric(f"Optimistisch (J{p_horizon})", f"{opt[-1]:,.0f} EUR", delta=_d(opt[-1]))
            st.caption(f"Basis nutzt die historische Rendite deiner Mischung ({btx['ann_ret']*100:.1f}% p.a.), "
                       f"Konservativ = minus 1 Volatilitaet ({btx['ann_vol']*100:.1f}%), Optimistisch = plus 1. "
                       "Drei Szenarien, KEINE Garantie - die Zukunft kann auch ausserhalb dieser Spanne liegen. "
                       "Vergangene Wertentwicklung ist kein verlaesslicher Indikator. Keine Anlageberatung.")

    # ---- 4. Rebalancing-Rechner & Risikoprofil (Bildung) ----
    st.markdown("---")
    st.markdown("#### 4. Rebalancing-Rechner & Risikoprofil (Bildung)")
    if not is_pro():
        st.markdown(locked_card_html("Rebalancing-Rechner & Risikoprofil",
                    "Orientierungs-Fragebogen, Beispiel-Allokation und Rechner fuer deine eigenen Positionen - in Plus & Pro."),
                    unsafe_allow_html=True)
    else:
        st.info("Bildungs- und Rechenwerkzeug - KEINE Anlageberatung, keine persoenliche Empfehlung und keine "
                "Eignungspruefung. Du legst Profil und Zielgewichte selbst fest; die App rechnet nur auf deinen "
                "eigenen Positionen. Die gezeigten Allokationen sind allgemeine Beispiele, nicht auf deine "
                "persoenliche Situation zugeschnitten.")
        st.session_state.setdefault("rb_risk", 50)
        st.session_state.setdefault("rb_growth", 60)

        with st.expander("Orientierungs-Fragebogen (waehlt ein allgemeines Beispiel-Profil)", expanded=("profile_label" not in st.session_state)):
            st.caption("Dient nur dazu, ein allgemeines Beispiel-Profil vorzuschlagen - keine Eignungspruefung oder Beratung nach WpHG.")
            for qq in PROFILE_QUESTIONS:
                st.radio(qq["q"], [o[0] for o in qq["options"]], key="pq_" + qq["key"])
            st.button("Beispiel-Profil uebernehmen", on_click=apply_profile, type="primary", key="apply_prof",
                      help="Setzt die Regler auf ein allgemeines Beispiel-Profil. Du kannst alles selbst aendern.")
            if "profile_label" in st.session_state:
                st.success(f"Dein Antwortmuster entspricht typischerweise einem {st.session_state['profile_label']}-Beispiel-Profil "
                           f"(Risiko {st.session_state['rb_risk']}/100, Wachstum {st.session_state['rb_growth']}/100). "
                           "Die Regler unten kannst du frei anpassen - du entscheidest.")

        rsl1, rsl2 = st.columns(2)
        risk = rsl1.slider("Risikobereitschaft", 0, 100, step=5, key="rb_risk",
                           help="0 = sehr defensiv (viel ETF/Gold), 100 = sehr offensiv (mehr Einzelaktien/Krypto).")
        growth = rsl2.slider("Wachstumsziel", 0, 100, step=5, key="rb_growth",
                             help="Hoeher = mehr Gewicht auf wachstumsstarke, schwankungsreiche Klassen statt Gold/Defensiv.")
        target = target_allocation(risk, growth)
        st.markdown(f"**Beispiel-Allokation fuer ein {profile_label(risk)}-Profil** (allgemeines Bildungsbeispiel - keine Empfehlung)")
        st.bar_chart(pd.DataFrame({"Beispiel %": {b: round(target[b] * 100, 1) for b in BUCKETS}}))
        st.caption("Das uebernimmst du als deine selbst gewaehlten Zielgewichte (Anlageklassen-Ebene, allgemeines Beispiel).  "
                   + "  ·  ".join(f"{b}: {target[b]*100:.0f}%" for b in BUCKETS))
        mode = st.radio("Rechen-Modus", ["Sparrate aufteilen (nur kaufen)", "Abweichung jetzt (kaufen & verkaufen)"],
                        horizontal=True, key="rb_mode")
        monthly = 0.0
        if mode.startswith("Sparrate"):
            monthly = st.number_input("Monatliche Sparrate (EUR)", value=250.0, min_value=0.0, step=50.0, key="rb_monthly",
                                      help="Rein rechnerisch: wie liesse sich dieser Betrag auf deine vorhandenen Positionen verteilen, um deine Zielgewichte zu halten.")
        if st.button("Berechnen", type="primary", key="rb_run"):
            fx = eurusd_rate()
            wval = holdings_values(holdings, fx)
            if not wval:
                st.error("Keine Positionswerte - in Schritt 1 Stueck/Kurs eintragen (oder 'Depotwert berechnen').")
                st.session_state.pop("rebal", None)
            else:
                name_by_tk = {}
                for _, r in holdings.iterrows():
                    tkx = str(r.get("Ticker") or "").strip().upper()
                    if tkx:
                        name_by_tk[tkx] = r.get("Name", tkx)
                bk = {tk: classify_asset(name_by_tk.get(tk, tk), tk) for tk in wval}
                st.session_state["rebal"] = {"wval": wval, "bk": bk, "target": target,
                                             "mode": mode, "monthly": monthly}

        if "rebal" in st.session_state:
            Rb = st.session_state["rebal"]; wval = Rb["wval"]; bk = Rb["bk"]; target = Rb["target"]
            total = sum(wval.values())
            cur = bucket_totals(wval, bk)
            comp = [{"Klasse": b, "Ist %": round((cur.get(b, 0) / total * 100) if total else 0, 1),
                     "Zielgewicht %": round(target[b] * 100, 1),
                     "Ist EUR": round(cur.get(b, 0), 0), "Ziel EUR": round(target[b] * total, 0)} for b in BUCKETS]
            st.markdown("**Ist vs. deine Zielgewichte**")
            st.dataframe(pd.DataFrame(comp), hide_index=True, use_container_width=True)
            if Rb["mode"].startswith("Sparrate"):
                buy, _, _ = monthly_plan(wval, bk, target, Rb["monthly"])
                st.markdown(f"**Rechnerische Aufteilung deiner Sparrate ({Rb['monthly']:,.0f} EUR) auf deine vorhandenen Positionen**")
                plan_rows = []
                for b in BUCKETS:
                    if buy[b] <= 0.5:
                        continue
                    parts = split_to_positions(buy[b], wval, bk, b)
                    if parts:
                        for tk, amt in parts.items():
                            plan_rows.append({"Position": tk, "Klasse": b, "rechnerischer Anteil (EUR)": round(amt, 2)})
                    else:
                        plan_rows.append({"Position": f"(Klasse {b} nicht im Depot)", "Klasse": b, "rechnerischer Anteil (EUR)": round(buy[b], 2)})
                if plan_rows:
                    st.dataframe(pd.DataFrame(plan_rows), hide_index=True, use_container_width=True)
                else:
                    st.info("Dein Depot liegt rechnerisch nahe an deinen Zielgewichten.")
                st.caption("Reine Rechnung auf deinen eigenen Positionen und deinen selbst gewaehlten Zielgewichten "
                           "(neues Geld in die untergewichteten Klassen, kein Verkauf noetig). Ob, was und wann du "
                           "kaufst, entscheidest ausschliesslich du. Keine Empfehlung, keine Anlageberatung.")
            else:
                _, rrows = rebalance_now(wval, bk, target)
                act = []
                for row in rrows:
                    diff = row["diff"]
                    status = ("untergewichtet" if diff > 1 else ("uebergewichtet" if diff < -1 else "im Ziel"))
                    act.append({"Klasse": row["bucket"], "Ist EUR": round(row["cur_eur"], 0),
                                "Ziel EUR": round(row["tgt_eur"], 0), "Abweichung EUR": round(diff, 0),
                                "Status": status})
                st.markdown("**Abweichung zu deinen Zielgewichten (rechnerisch)**")
                st.dataframe(pd.DataFrame(act), hide_index=True, use_container_width=True)
                st.caption("Reine Abweichungsrechnung gegen deine selbst gesetzten Zielgewichte (positiv = untergewichtet, "
                           "negativ = uebergewichtet). Keine Kauf-/Verkaufsempfehlung - Entscheidung und Umsetzung liegen bei dir.")

        st.caption("Hinweis: Dieser Bereich ist ein Bildungs- und Rechenwerkzeug und stellt keine Anlageberatung, "
                   "Anlageempfehlung oder Eignungspruefung im Sinne des WpHG dar.")

    st.markdown('<div class="fa-foot">FinAnalyse - Bildungs- & Analyse-Tool. Keine Anlageberatung. '
                'Live-Kurse via Yahoo, ohne Gewaehr - zum Stichtag.</div>', unsafe_allow_html=True)


# ====================== SEITE: EINZELANALYSE ======================
elif page == "single":
    if yf is None:
        st.stop()
    pending = st.session_state.pop("pending_ticker", None)
    POP = ["AAPL", "MSFT", "META", "GOOGL", "AMZN", "NVDA", "ASML", "NOVO-B.CO", "SAP.DE", "MC.PA"]
    ci, cs, cb = st.columns([2.2, 1.4, 1])
    with ci:
        typed = st.text_input(t("ticker_in"), value="", placeholder="z.B. AAPL, META, SAP.DE",
                              help="Boersenkuerzel. US: AAPL, META. Deutschland: SAP.DE. Krypto: BTC-EUR.").strip().upper()
    with cs:
        chosen = st.selectbox(t("popular"), [""] + POP, help="Schnellauswahl bekannter Titel.")
    with cb:
        st.write(""); st.write("")
        analyze_btn = st.button(t("analyze"), type="primary", use_container_width=True)
    ticker = typed or chosen or (pending or "")
    analyze = (analyze_btn and bool(ticker)) or bool(pending)

    if analyze and ticker:
        with st.spinner(f"Hole Daten fuer {ticker} ..."):
            data = fetch(ticker)
            prices = fetch_prices(ticker, "5y")
        if data is None:
            st.error(f"Keine Daten fuer '{ticker}'. Tipp: Boerse anhaengen (z.B. SAP.DE) oder anderes Kuerzel probieren.")
        else:
            m = compute(data)
            with st.spinner("Erstelle Ueberblick ..."):
                stext, ssrc = ai_summary(data, m)
            st.session_state["fa"] = {"data": data, "m": m, "ticker": ticker,
                                      "summary_text": stext, "summary_src": ssrc, "prices": prices}

    if "fa" in st.session_state:
        S = st.session_state["fa"]; data, m, ticker = S["data"], S["m"], S["ticker"]
        hc1, hc2 = st.columns([4, 1])
        with hc1:
            st.subheader(f"{data['name']} ({data['ticker']})")
        with hc2:
            st.write("")
            if st.button(t("add_wl"), use_container_width=True, help="Diesen Titel im Dashboard mitverfolgen."):
                if not is_pro() and len(st.session_state["watchlist"]) >= 5 and ticker not in st.session_state["watchlist"]:
                    st.warning("Free-Limit: max. 5 Titel. Mit Plus unbegrenzt.")
                elif ticker not in st.session_state["watchlist"]:
                    st.session_state["watchlist"].append(ticker)
                    st.toast(f"{ticker} zur Watchlist hinzugefuegt.")
                    st.rerun()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sektor", data["sector"])
        c2.metric("Kurs", f"{data['price']:.2f} {data['currency']}" if data["price"] else "-")
        c3.metric("Marktkap. (Mio.)", fmt_num(data["mcap_m"]))
        c4.metric("Beta", f"{data['beta']:.2f}" if data["beta"] else "-", help="Schwankung relativ zum Markt. >1 = schwankt staerker.")

        with st.expander(t("overview"), expanded=True):
            if S["summary_src"] == "ki":
                if is_pro():
                    st.markdown(S["summary_text"])
                    st.caption("KI-generiert. Kann Fehler enthalten - pruefen. Keine Anlageberatung.")
                else:
                    st.markdown(locked_card_html("KI-Unternehmensueberblick",
                                "Strukturierte KI-Analyse (Geschaeftsmodell, Moat, Markt, Risiken). In Plus & Pro enthalten."),
                                unsafe_allow_html=True)
            elif S["summary_src"] == "yahoo":
                st.write(S["summary_text"]); st.caption("Quelle: Yahoo. Fuer KI-Ueberblick OPENAI_API_KEY setzen.")
            else:
                prof = []
                for lbl, k in [("Sektor", "sector"), ("Branche", "industry"), ("Land", "country"), ("Website", "website")]:
                    if data.get(k) and data[k] != "n/a": prof.append(f"**{lbl}:** {data[k]}")
                if data.get("employees"): prof.append(f"**Mitarbeiter:** {data['employees']:,}")
                if prof: st.markdown("  \n".join(prof))
                st.info("Yahoo lieferte keine Textbeschreibung. Fuer KI-Ueberblick OPENAI_API_KEY setzen.")

        with st.expander(t("macro"), expanded=False):
            st.caption("Vorbelegt mit dem historischen Wachstum. Faktoren anhaken = Wachstumsannahme anpassen "
                       "(wirkt sofort auf PEG & Fazit).")
            rel = relevant_factors(data["sector"])
            eps_cagr = m["cagrs"]["EPS-CAGR"]
            base_default = round(eps_cagr * 100, 1) if eps_cagr else 10.0
            base_growth = st.number_input(t("growth") + " (Basis)", value=float(base_default),
                                          min_value=-50.0, max_value=200.0, step=1.0, key="base_g",
                                          help="Geschaetztes jaehrliches Gewinnwachstum. Realistisch: meist 5-15%.")
            macro_sum = 0.0
            selected_macro = []
            mc1, mc2 = st.columns(2)
            for idx, f in enumerate(rel):
                target = mc1 if idx % 2 == 0 else mc2
                with target:
                    on = st.checkbox(f["name"], key=f"mf_{f['key']}", help=f["desc"])
                    if on:
                        imp = st.slider(f"Impact '{f['name']}' (%-Punkte)", -6.0, 6.0, float(f["default"]), 0.5, key=f"mi_{f['key']}")
                        macro_sum += imp
                        selected_macro.append((f["name"], imp))
            eff_growth = base_growth + macro_sum
            st.metric(t("eff_growth"), f"{eff_growth:.1f}%", delta=f"{macro_sum:+.1f} pp Makro")

        sc = build_scorecard(m, eff_growth, sector_kind(data.get("sector"), data.get("industry")))
        flags = verification_flags(m, data, eff_growth)
        n_pruef = len([f for f in flags if f[1] in ("auffaellig", "fehlend")])

        st.markdown("---")
        fc1, fc2, fc3 = st.columns(3)
        fc1.metric(t("quality"), fmt_pct(sc["quality"]), help="Anteil erreichter Punkte aus Profitabilitaet, Bilanz & Wachstum (0-100%).")
        fc2.metric(t("value"), fmt_pct(sc["value_adj"]), help="Bewertung wachstumsbereinigt (PEG-gewichtet). Hoeher = guenstiger.")
        fc3.metric("PEG", f"{sc['peg']:.2f}" if sc["peg"] else "-", help="KGV / Wachstum. <1 guenstig, >2 teuer.")
        st.caption(f"Annahme: {eff_growth:.1f}% Wachstum p.a. (anpassbar oben unter '{t('macro')}').")
        st.markdown(verdict_banner_html(sc["verdict"]), unsafe_allow_html=True)
        if n_pruef:
            st.warning(f"{n_pruef} Kennzahl(en) auffaellig/fehlend - Details im Tab '{t('tab_check')}'.")

        tabs = st.tabs([t("tab_eval"), t("tab_hist"), t("tab_chart"), t("tab_qual"),
                        t("tab_summary"), t("tab_raw"), f"{t('tab_check')} ({len(flags)})"])

        with tabs[0]:
            pct_prof = {"Bruttomarge", "EBIT-Marge", "Nettomarge", "FCF-Marge", "ROE", "ROCE", "ROA", "Eigenkapitalquote"}
            html = (scorecard_table_html(f"1. Profitabilitaet ({sc['prof_s']}/{sc['prof_max']})", sc["prof"], pct_prof)
                    + scorecard_table_html(f"2. Gesundheit ({sc['health_s']}/{sc['health_max']})", sc["health"],
                        {"FCF Conversion", "Eigenkapitalquote"})
                    + scorecard_table_html(f"3. Wachstum ({sc['growth_s']}/{sc['growth_max']})", sc["growth"],
                        {"Umsatz-CAGR", "EPS-CAGR", "FCF-CAGR"})
                    + scorecard_table_html(f"4. Bewertung ({sc['val_abs_s']}/{sc['val_max']})", sc["valuation"], set()))
            st.markdown(html, unsafe_allow_html=True)
            if sc.get("kind") == "financial":
                st.caption("Sektor-Modus Finanzwerte: bewertet ueber KBV & Eigenkapitalquote statt "
                           "KGV/EV-EBITDA/Net-Debt - diese passen fuer Banken/Versicherer strukturell nicht.")
            st.info("Rein QUANTITATIV. Moat/Management/Branche separat bewerten (Tab 'Qualitativ').")

        with tabs[1]:
            yrs = data["years"]
            st.markdown("**Margen-Entwicklung (%)**")
            margins = pd.DataFrame({k: [(x * 100 if x is not None else None) for x in m["rows"][k]]
                                    for k in ["Bruttomarge", "EBIT-Marge", "Nettomarge", "FCF-Marge"]}, index=yrs)
            st.bar_chart(margins)
            st.markdown("**Rendite-Kennzahlen (%)**")
            rends = pd.DataFrame({k: [(x * 100 if x is not None else None) for x in m["rows"][k]]
                                  for k in ["ROE", "ROA", "ROCE"]}, index=yrs)
            st.bar_chart(rends)
            st.markdown("**Umsatz & Gewinn (Mio.)**")
            fin = pd.DataFrame({"Umsatz": data["revenue"], "Net Income": data["netincome"], "FCF": m["fcf"]}, index=yrs)
            st.bar_chart(fin)
            st.markdown("**Verschuldung & Liquiditaet**")
            lev = pd.DataFrame({k: m["rows"][k] for k in ["Net Debt/EBITDA", "Debt/Equity", "Current Ratio"]}, index=yrs)
            st.bar_chart(lev)

        with tabs[2]:
            st.markdown("**Historischer Kursverlauf (5 Jahre)**")
            if S.get("prices") is not None and not S["prices"].empty:
                st.line_chart(S["prices"])
            else:
                st.info("Keine Kurshistorie verfuegbar.")
            st.markdown(f"**Umsatz-Prognose (5 Jahre, bei {eff_growth:.1f}% Wachstum)**")
            yrs = data["years"]
            rev_hist = data["revenue"]
            last_rev = next((x for x in reversed(rev_hist) if x is not None), None)
            if last_rev:
                proj = project_series(last_rev, eff_growth, 5)
                try:
                    next_year = int(yrs[-1]) + 1
                    future_years = [str(next_year + i) for i in range(5)]
                except Exception:
                    future_years = [f"+{i+1}" for i in range(5)]
                hist_prog = [None] * len(rev_hist)
                hist_prog[-1] = last_rev
                hist_df = pd.DataFrame({"Historisch": rev_hist, "Prognose": hist_prog}, index=yrs)
                proj_df = pd.DataFrame({"Historisch": [None]*5, "Prognose": proj}, index=future_years)
                full = pd.concat([hist_df, proj_df])
                st.line_chart(full)
                st.caption(f"Prognose extrapoliert den letzten Umsatz mit {eff_growth:.1f}% p.a. "
                           "Aendert sich live mit Wachstumsannahme/Makro-Faktoren. Vereinfachte Hochrechnung, keine Garantie.")
            else:
                st.info("Kein Umsatz fuer Prognose verfuegbar.")

        with tabs[3]:
            st.markdown("### Qualitative Analyse - Vorlagen ausfuellen")
            st.caption("Jeder Block ist eine Vorlage. Was du hier schreibst, fliesst automatisch in die Zusammenfassung "
                       "und das Investment-Memo. Eingaben werden pro Ticker gespeichert.")
            for key, title, prompt in QUAL_SECTIONS:
                st.markdown(f"**{title}**")
                st.caption(prompt)
                st.text_area(title, key=f"qual_{ticker}_{key}", height=150, label_visibility="collapsed",
                             placeholder=prompt)
            st.markdown("---")
            st.markdown("**Investment-Checkliste**")
            st.caption("Abhaken, was erfuellt ist. Fliesst in die Vollstaendigkeit & ins Memo.")
            chk1, chk2 = st.columns(2)
            for i, item in enumerate(CHECKLIST):
                (chk1 if i % 2 == 0 else chk2).checkbox(item, key=f"chk_{ticker}_{i}")

        with tabs[4]:
            qual = {key: st.session_state.get(f"qual_{ticker}_{key}", "") for key, _, _ in QUAL_SECTIONS}
            checklist_done = [bool(st.session_state.get(f"chk_{ticker}_{i}", False)) for i in range(len(CHECKLIST))]
            got, total, filled_sec, chk_done = analysis_completeness(qual, checklist_done)
            st.markdown(f"### {t('completeness')}")
            st.progress(got / total if total else 0.0,
                        text=f"{got}/{total} - Qualitativ {filled_sec}/{len(QUAL_SECTIONS)} Bloecke, Checkliste {chk_done}/{len(CHECKLIST)}")
            if got < total:
                st.info("Noch nicht vollstaendig - fehlende Bloecke im Tab 'Qualitativ' ausfuellen. "
                        "Das Memo wird trotzdem schon erstellt (offene Punkte sind markiert).")
            else:
                st.success("Analyse vollstaendig - quantitativ + qualitativ + Checkliste.")

            memo = build_memo(data, m, sc, eff_growth, base_growth, selected_macro, qual, checklist_done, flags)
            if is_pro():
                st.download_button(t("download_memo"), data=memo,
                                   file_name=f"Investment-Memo_{data['ticker']}_{date.today().isoformat()}.md",
                                   mime="text/markdown", type="primary", use_container_width=True)
            else:
                st.markdown(locked_card_html("Investment-Memo Export",
                            "Das fertige Memo als .md/PDF herunterladen ist in Plus & Pro enthalten. Vorschau siehst du unten."),
                            unsafe_allow_html=True)
            st.markdown("---")
            st.markdown(memo)

        with tabs[5]:
            yrs = data["years"]
            raw = {"Umsatz": data["revenue"], "Bruttogewinn": m["gross"], "EBIT": data["ebit"],
                   "EBITDA": m["ebitda"], "Net Income": data["netincome"], "FCF": m["fcf"],
                   "EPS": m["eps"], "Eigenkapital": data["equity"], "Gesamt Aktiva": data["tot_assets"]}
            dfr = pd.DataFrame({k: [(f"{x:.2f}" if (k == "EPS" and x is not None) else fmt_num(x)) for x in vv] for k, vv in raw.items()}, index=yrs).T
            dfr.columns = yrs
            st.dataframe(dfr, use_container_width=True)
            st.caption(f"Mio. {data['currency']}. Quelle: Yahoo, {date.today().isoformat()}.")

        with tabs[6]:
            st.markdown("### Gegen Geschaeftsbericht pruefen")
            icons = {"immer": "[STETS]", "auffaellig": "[AUFFAELLIG]", "fehlend": "[FEHLT]"}
            order = {"auffaellig": 0, "fehlend": 1, "immer": 2}
            for metric, typ, reason in sorted(flags, key=lambda f: order.get(f[1], 9)):
                (st.error if typ == "auffaellig" else st.warning if typ == "fehlend" else st.info)(f"**{icons.get(typ,'')} {metric}** - {reason}")
            st.markdown("**Pruefen:** stockanalysis.com/stocks/TICKER -> 10-K / Geschaeftsbericht -> Umsatz/Net Income/FCF abgleichen.")
    else:
        st.info("Gib oben einen Ticker ein (oder waehle einen bekannten Titel) und klicke 'Analysieren'. "
                "Beispiele: AAPL, MSFT, SAP.DE.")

    st.markdown('<div class="fa-foot">FinAnalyse - Bildungs- & Analyse-Tool. Keine Anlageberatung. '
                'Daten ohne Gewaehr - vor jeder Entscheidung gegen den Geschaeftsbericht pruefen.</div>',
                unsafe_allow_html=True)


# ====================== SEITE: PORTFOLIO & BACKTEST ======================
elif page == "portfolio":
    if yf is None:
        st.stop()
    st.subheader(t("portfolio"))
    st.caption("Beliebiges Portfolio testen (allgemein). Fuer DEIN echtes Depot: Tab 'Mein Depot' -> Schritt 3.")

    default_tickers = ", ".join(st.session_state["watchlist"]) if st.session_state["watchlist"] else "AAPL, MSFT, NVDA"
    tin = st.text_area("Ticker (kommagetrennt)", value=default_tickers, height=70,
                       help="Mehrere Titel mit Komma trennen, z.B. AAPL, MSFT, BTC-EUR.")
    tickers = [x.strip().upper() for x in tin.replace("\n", ",").split(",") if x.strip()]

    st.markdown("**Gewichte (%)** - leer = Gleichgewichtung")
    weights = {}
    if tickers:
        wcols = st.columns(min(len(tickers), 5))
        for i, tk in enumerate(tickers):
            with wcols[i % len(wcols)]:
                weights[tk] = st.number_input(tk, min_value=0.0, max_value=100.0,
                                              value=round(100.0 / len(tickers), 1), step=1.0, key=f"w_{tk}")

    cc1, cc2 = st.columns(2)
    start_capital = cc1.number_input(t("start_capital"), value=10000.0, min_value=0.0, step=1000.0, key="capital",
                                     help="Hypothetische Einmalanlage zu Beginn des Zeitraums.")
    period = cc2.selectbox("Backtest-Zeitraum", ["1y", "2y", "3y", "5y", "10y", "max"], index=3,
                           help="Wie weit zurueck getestet wird.")
    run = st.button("Backtest starten", type="primary")

    if run and tickers:
        with st.spinner("Hole Kurshistorie ..."):
            prices = fetch_prices(tickers, period)
        if prices is None or prices.empty:
            st.error("Keine Kursdaten erhalten. Ticker pruefen.")
            st.session_state.pop("bt", None)
        else:
            prices = prices.reindex(columns=[c for c in tickers if c in prices.columns]).dropna()
            if prices.shape[1] == 0 or prices.shape[0] < 10:
                st.error("Zu wenige gueltige Kursdaten. Ticker/Zeitraum pruefen.")
                st.session_state.pop("bt", None)
            else:
                wsum = sum(weights.get(c, 0) for c in prices.columns)
                wn = {c: (weights.get(c, 0) / wsum if wsum > 0 else 1.0 / prices.shape[1]) for c in prices.columns}
                bt = backtest_portfolio(prices, wn)
                st.session_state["bt"] = {"bt": bt, "prices": prices, "weights": wn,
                                          "period": period, "capital": start_capital}

    if "bt" in st.session_state:
        B = st.session_state["bt"]; bt = B["bt"]; prices = B["prices"]; capital = B.get("capital", 10000.0)
        end_value = float(capital * bt["equity"].iloc[-1])
        st.markdown(f"### Backtest-Ergebnis ({B['period']}, {len(prices)} Handelstage)")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Annual. Rendite", f"{bt['ann_ret']*100:.1f}%")
        k2.metric("Volatilitaet", f"{bt['ann_vol']*100:.1f}%", help="Schwankungsbreite p.a. Hoeher = riskanter.")
        k3.metric("Sharpe Ratio", f"{bt['sharpe']:.2f}" if bt['sharpe'] else "-", help="Rendite pro Risiko. >1 gut, >2 sehr gut.")
        k4.metric("Max Drawdown", f"{bt['max_dd']*100:.1f}%", help="Groesster Verlust vom Hoch zum Tief.")
        e1, e2 = st.columns(2)
        e1.metric("Startkapital", f"{capital:,.0f} EUR")
        e2.metric("Endwert (Backtest)", f"{end_value:,.0f} EUR", delta=f"{(bt['equity'].iloc[-1]-1)*100:+.1f}%")
        st.caption("Gewichtung: " + ", ".join(f"{c} {w*100:.0f}%" for c, w in B["weights"].items()))
        st.caption("Hinweis: Einmalanlage am Startdatum, taeglich rebalanciert.")
        st.markdown("**Depotwert-Kurve (EUR)**")
        st.line_chart(bt["equity"] * capital)
        st.markdown("**Einzelkurse (normiert)**")
        st.line_chart(prices / prices.iloc[0])

        st.markdown("---")
        st.markdown("### Zukunftsprognose (begruendet)")
        if is_pro():
            pc1, pc2 = st.columns(2)
            horizon = pc1.selectbox("Prognose-Horizont (Jahre)", [1, 3, 5, 10, 20], index=2, key="horizon")
            start_val = pc2.number_input("Startwert der Prognose (EUR)", value=float(round(end_value)),
                                         step=1000.0, key="startval")
            pts, base, cons, opt = project_portfolio(start_val, bt["ann_ret"], bt["ann_vol"], horizon)
            proj_df = pd.DataFrame({"Konservativ": cons, "Basis": base, "Optimistisch": opt}, index=list(pts))
            proj_df.index.name = "Jahr"
            st.line_chart(proj_df)
            cprj1, cprj2, cprj3 = st.columns(3)
            cprj1.metric(f"Konservativ (J{horizon})", f"{cons[-1]:,.0f} EUR")
            cprj2.metric(f"Basis (J{horizon})", f"{base[-1]:,.0f} EUR")
            cprj3.metric(f"Optimistisch (J{horizon})", f"{opt[-1]:,.0f} EUR")
            st.caption(f"Begruendung: Basis-Szenario nutzt die historische annualisierte Rendite ({bt['ann_ret']*100:.1f}%). "
                       f"Konservativ = Rendite minus 1 Volatilitaet ({bt['ann_vol']*100:.1f}%), Optimistisch = plus 1 Volatilitaet. "
                       "Annahme: Vergangenheit indikativ fuer Zukunft - das ist NICHT garantiert. Keine Anlageberatung.")
        else:
            st.markdown(locked_card_html("Zukunftsprognose (Szenarien)",
                        "Konservativ/Basis/Optimistisch ueber waehlbare Horizonte - in Plus & Pro enthalten."),
                        unsafe_allow_html=True)
    elif not tickers:
        st.info("Ticker eingeben (oder aus Watchlist) und Backtest starten.")

    st.markdown('<div class="fa-foot">FinAnalyse - Bildungs- & Analyse-Tool. Keine Anlageberatung. '
                'Backtests sind historisch und keine Garantie fuer die Zukunft.</div>', unsafe_allow_html=True)


# ====================== SEITE: RECHNER ======================
elif page == "rechner":
    st.subheader("Rechner: die wichtigsten Werkzeuge fuer Privatanleger")
    st.caption("Alles reine Rechen- und Bildungswerkzeuge auf deine eigenen Eingaben - keine Anlage- oder "
               "Steuerberatung. Ergebnisse sind Schaetzungen, keine Garantie.")
    rt = st.tabs(["Sparplan & Zinseszins", "Notgroschen", "Kosten-Effekt",
                  "Steuer (DE)", "Entnahme / 4%-Regel", "Positionsgroesse", "Diversifikation"])

    # --- Sparplan & Zinseszins ---
    with rt[0]:
        st.markdown("**Wie viel wird aus deinem Sparplan?**")
        c1, c2, c3 = st.columns(3)
        sp_init = c1.number_input("Startkapital (EUR)", value=1000.0, step=500.0, min_value=0.0, key="sp_init")
        sp_mon = c2.number_input("Monatliche Rate (EUR)", value=200.0, step=50.0, min_value=0.0, key="sp_mon")
        sp_yrs = c3.number_input("Laufzeit (Jahre)", value=20, step=1, min_value=1, max_value=70, key="sp_yrs")
        sp_rate = st.slider("Erwartete Rendite p.a. (%)", 0.0, 12.0, 6.0, 0.5, key="sp_rate") / 100.0
        res = fv_savings(sp_mon, int(sp_yrs), sp_rate, sp_init)
        m1, m2, m3 = st.columns(3)
        m1.metric("Endkapital", f"{res['end']:,.0f} EUR")
        m2.metric("Eingezahlt", f"{res['eingezahlt']:,.0f} EUR")
        m3.metric("davon Ertrag", f"{res['ertrag']:,.0f} EUR")
        if res["series"]:
            sp_chart = pd.DataFrame({"EUR": res["series"]}, index=list(range(1, len(res["series"]) + 1)))
            sp_chart.index.name = "Jahr"
            st.line_chart(sp_chart)
        st.caption("Annahme: konstante Rendite, monatliche Einzahlung am Monatsende. Maerkte schwanken - real geht es "
                   "auf und ab. Der Ertrag entsteht durch den Zinseszins (Lektion 'Sparplan & Zinseszins').")

    # --- Notgroschen ---
    with rt[1]:
        st.markdown("**Wie gross sollte dein Notgroschen sein?**")
        c1, c2 = st.columns(2)
        ef_exp = c1.number_input("Monatliche Ausgaben (EUR)", value=2000.0, step=100.0, min_value=0.0, key="ef_exp")
        ef_mon = c2.slider("Monate Puffer", 1, 12, 4, key="ef_mon")
        ef = emergency_fund(ef_exp, ef_mon)
        st.metric("Ziel-Notgroschen", f"{ef:,.0f} EUR")
        st.caption("Ueblich sind 3-6 Monatsausgaben auf einem sicheren, jederzeit verfuegbaren Konto (Tagesgeld). "
                   "Der Notgroschen gehoert NICHT in schwankende Aktien - er soll dich vor Notverkaeufen schuetzen.")

    # --- Kosten-Effekt ---
    with rt[2]:
        st.markdown("**Was kosten dich Gebuehren ueber die Zeit?**")
        c1, c2, c3 = st.columns(3)
        fd_init = c1.number_input("Startkapital (EUR)", value=10000.0, step=1000.0, min_value=0.0, key="fd_init")
        fd_mon = c2.number_input("Monatliche Rate (EUR)", value=200.0, step=50.0, min_value=0.0, key="fd_mon")
        fd_yrs = c3.number_input("Laufzeit (Jahre)", value=30, step=1, min_value=1, max_value=70, key="fd_yrs")
        c4, c5 = st.columns(2)
        fd_gross = c4.slider("Bruttorendite p.a. (%)", 0.0, 12.0, 7.0, 0.5, key="fd_gross") / 100.0
        fd_fee = c5.slider("Laufende Kosten p.a. (%)", 0.0, 3.0, 1.0, 0.1, key="fd_fee") / 100.0
        fr = fee_drag(fd_init, fd_mon, int(fd_yrs), fd_gross, fd_fee)
        m1, m2, m3 = st.columns(3)
        m1.metric("Ohne Kosten", f"{fr['brutto']:,.0f} EUR")
        m2.metric("Mit Kosten", f"{fr['netto']:,.0f} EUR")
        m3.metric("Kosten kosten dich", f"{fr['kosten']:,.0f} EUR")
        st.caption("Schon ein Prozentpunkt laufende Kosten frisst ueber Jahrzehnte durch den Zinseszins erstaunlich "
                   "viel Endkapital. Niedrige Kosten sind eine der wenigen fast sicheren Renditequellen.")

    # --- Steuer (DE) ---
    with rt[3]:
        st.markdown("**Abgeltungsteuer-Schaetzer (Deutschland)**")
        c1, c2 = st.columns(2)
        tx_gain = c1.number_input("Realisierter Gewinn / Ertrag (EUR)", value=5000.0, step=500.0, min_value=0.0, key="tx_gain")
        tx_pb = c2.number_input("Sparer-Pauschbetrag (EUR)", value=1000.0, step=1000.0, min_value=0.0, key="tx_pb",
                                help="2026: 1.000 EUR pro Person, 2.000 EUR fuer zusammenveranlagte Paare.")
        tx_ki = st.selectbox("Kirchensteuer", ["keine", "8% (BY/BW)", "9% (uebrige)"], index=0, key="tx_ki")
        ki_rate = {"keine": 0.0, "8% (BY/BW)": 0.08, "9% (uebrige)": 0.09}[tx_ki]
        tr_ = abgeltung_net(tx_gain, tx_pb, ki_rate)
        m1, m2, m3 = st.columns(3)
        m1.metric("Zu versteuern", f"{tr_['zu_versteuern']:,.0f} EUR")
        m2.metric("Steuer (geschaetzt)", f"{tr_['steuer']:,.0f} EUR")
        m3.metric("Netto", f"{tr_['netto']:,.0f} EUR")
        st.caption(f"Effektive Steuerlast auf den Gewinn: {tr_['satz_eff']*100:.1f}%. Grundsatz: 25% Abgeltungsteuer "
                   "+ 5,5% Soli (+ ggf. Kirchensteuer) auf den Teil ueber dem Pauschbetrag. Vereinfachte Schaetzung, "
                   "keine Steuerberatung - deine konkrete Lage klaerst du mit einem Steuerberater.")

    # --- Entnahme / 4%-Regel ---
    with rt[4]:
        st.markdown("**Wie lange reicht dein Kapital - und was ist 'sicher'?**")
        c1, c2 = st.columns(2)
        wd_cap = c1.number_input("Vorhandenes Kapital (EUR)", value=300000.0, step=10000.0, min_value=0.0, key="wd_cap")
        wd_w = c2.number_input("Monatliche Entnahme (EUR)", value=1200.0, step=100.0, min_value=0.0, key="wd_w")
        c3, c4 = st.columns(2)
        wd_rate = c3.slider("Rendite p.a. (%)", 0.0, 10.0, 5.0, 0.5, key="wd_rate") / 100.0
        wd_infl = c4.slider("Inflation p.a. (%)", 0.0, 6.0, 2.0, 0.5, key="wd_infl") / 100.0
        yrs = withdrawal_years(wd_cap, wd_w, wd_rate, wd_infl)
        sw = safe_withdrawal(wd_cap)
        m1, m2 = st.columns(2)
        if yrs is None:
            m1.metric("Reichweite", "> 100 Jahre")
        else:
            m1.metric("Reichweite", f"{yrs:.1f} Jahre")
        m2.metric("4%-Regel: sichere Entnahme", f"{sw['monat']:,.0f} EUR / Monat", help=f"{sw['jahr']:,.0f} EUR pro Jahr.")
        st.caption("Die 4%-Regel ist eine grobe historische Orientierung (US-Daten, 30 Jahre) - keine Garantie und "
                   "keine Empfehlung. Inflation laesst die Entnahme real steigen, was die Reichweite verkuerzt.")

    # --- Positionsgroesse ---
    with rt[5]:
        st.markdown("**Wie gross darf eine Einzelposition sein?**")
        c1, c2 = st.columns(2)
        ps_dep = c1.number_input("Depotwert (EUR)", value=50000.0, step=1000.0, min_value=0.0, key="ps_dep")
        ps_max = c2.slider("Maximaler Anteil je Position (%)", 1, 30, 8, key="ps_max") / 100.0
        st.metric("Maximaler Betrag pro Position", f"{position_size(ps_dep, ps_max):,.0f} EUR")
        st.caption("Eine vorab festgelegte Obergrenze (oft 5-10%) begrenzt das Klumpenrisiko: Selbst ein Totalausfall "
                   "einer Position bleibt verkraftbar. Spekulatives kleiner halten, Hochwertiges darf groesser sein.")

    # --- Diversifikations-Labor (Lektion 'Diversifikation & Korrelation' zum Anfassen) ---
    with rt[6]:
        st.markdown("**Diversifikation: wie Streuung das Risiko senkt**")
        st.caption("Zwei Anlagen mit je eigener Schwankung. Je niedriger ihre Korrelation, desto kleiner die "
                   "Portfolio-Volatilitaet - das ist der Diversifikationseffekt.")
        dc1, dc2 = st.columns(2)
        dv1 = dc1.slider("Volatilitaet Anlage A (%)", 5.0, 40.0, 18.0, 1.0, key="dv_v1") / 100.0
        dv2 = dc2.slider("Volatilitaet Anlage B (%)", 1.0, 40.0, 8.0, 1.0, key="dv_v2") / 100.0
        dcorr = st.slider("Korrelation A/B", -1.0, 1.0, 0.2, 0.1, key="dv_corr")
        wsteps = [i / 20 for i in range(21)]
        port = [two_asset_vol(w, dv1, dv2, dcorr) * 100 for w in wsteps]
        avg = [(w * dv1 + (1 - w) * dv2) * 100 for w in wsteps]
        ddf = pd.DataFrame({"Portfolio-Vola": port, "gewichteter Schnitt (ohne Effekt)": avg},
                           index=[f"{int(w*100)}%" for w in wsteps])
        ddf.index.name = "Anteil A"
        st.line_chart(ddf)
        best = min(range(len(wsteps)), key=lambda i: port[i])
        st.metric("Geringste Portfolio-Vola", f"{port[best]:.1f}%", help=f"bei {int(wsteps[best]*100)}% Anlage A")
        st.caption("Die 'Portfolio-Vola' liegt unter dem gewichteten Schnitt - genau das ist Diversifikation. Bei "
                   "Korrelation +1 verschwindet der Effekt, bei negativer Korrelation wird er am groessten. "
                   "Vertiefung: Lektion 'Diversifikation & Korrelation' (Tab Lernen -> Portfolio-Akademie).")

    st.markdown('<div class="fa-foot">FinAnalyse - Bildungs- & Rechenwerkzeuge. Keine Anlage- oder Steuerberatung. '
                'Ergebnisse sind Schaetzungen ohne Gewaehr.</div>', unsafe_allow_html=True)


# ====================== SEITE: LERNEN ======================
elif page == "lernen":
    _track = st.radio("Lern-Spur", ["Fundamentalanalyse (Aktien)", "Portfolio-Akademie"],
                      horizontal=True, key="lern_track")
    if _track == "Portfolio-Akademie":
        render_portfolio_academy()
        st.stop()
    st.subheader("Lernen: Fundamentalanalyse von 0 auf")
    st.caption("In kurzen Lektionen vom Anfaenger zum eigenstaendigen Analysieren. Jede Lektion endet mit einem "
               "kleinen Test (5-10 Fragen). Reine Bildung - keine Anlageberatung.")
    done = st.session_state.setdefault("lessons_done", [])
    st.progress(len(done) / len(LESSONS), text=f"Fortschritt: {len(done)}/{len(LESSONS)} Lektionen bestanden")
    titles = [("✓ " if L['key'] in done else f"{i+1}. ") + L['title'] for i, L in enumerate(LESSONS)]
    idx = st.selectbox("Lektion waehlen", list(range(len(LESSONS))), format_func=lambda i: titles[i], key="lesson_idx")
    L = LESSONS[idx]
    st.markdown(f"### {idx+1}. {L['title']}")
    if L["key"] in done:
        st.caption("Diese Lektion hast du schon bestanden.")
    st.markdown(L["body"])
    st.info("Faustregel: " + L["faustregel"])

    quizzes = L.get("quizzes") or [L["quiz"]]
    # ab 70% richtig gilt die Lektion als bestanden (aufgerundete Mindestpunktzahl)
    need = max(1, -(-(len(quizzes) * 7) // 10))
    st.markdown(f"#### Test zur Lektion  \n<span style='color:#8a97ab;font-size:.85rem'>"
                f"{len(quizzes)} Fragen - ab {need} richtigen bestanden</span>", unsafe_allow_html=True)
    with st.form(key=f"quizform_{L['key']}"):
        picks = []
        for i, q in enumerate(quizzes):
            picks.append(st.radio(f"**{i+1}. {q['q']}**", q["options"], index=None, key=f"quiz_{L['key']}_{i}"))
        submitted = st.form_submit_button("Test auswerten", type="primary")
    if submitted:
        unanswered = [i + 1 for i, p in enumerate(picks) if p is None]
        if unanswered:
            st.warning(f"Bitte alle Fragen beantworten. Offen: {', '.join(map(str, unanswered))}")
        else:
            correct = 0
            for i, (q, p) in enumerate(zip(quizzes, picks)):
                ok = q["options"].index(p) == q["correct"]
                correct += ok
                right = q["options"][q["correct"]]
                if ok:
                    st.success(f"{i+1}. Richtig. {q['explain']}")
                else:
                    st.error(f"{i+1}. Leider falsch. Richtig waere: „{right}“ - {q['explain']}")
            pct = correct / len(quizzes)
            st.markdown(f"**Ergebnis: {correct}/{len(quizzes)} richtig ({pct*100:.0f}%)**")
            if correct >= need:
                st.success("Bestanden! Lektion als abgeschlossen markiert.")
                if L["key"] not in done:
                    done.append(L["key"]); st.session_state["lessons_done"] = done
            else:
                st.warning(f"Noch nicht bestanden - du brauchst {need}/{len(quizzes)}. Lies die Lektion nochmal "
                           "und versuche es erneut.")
    if len(done) == len(LESSONS):
        st.success("Stark - du hast alle Lektionen bestanden! Wende es jetzt in der Einzelanalyse an.")
    st.button("Jetzt eine Aktie analysieren", on_click=goto_single, key="lesson_to_single")

    st.markdown("---")
    st.markdown("### KI-Tutor")
    st.caption("Stelle Fragen zur Fundamentalanalyse und zu Portfolio-Grundlagen. Der Tutor erklaert die Methode - "
               "er gibt keine Anlageberatung und keine Kauf-/Verkaufsempfehlungen.")
    if not is_pro():
        st.markdown(locked_card_html("KI-Tutor (Plus & Pro)",
                    "Persoenlicher KI-Lernassistent, der deine Fragen zur Fundamentalanalyse beantwortet."),
                    unsafe_allow_html=True)
    elif not get_api_key():
        st.info("KI-Tutor benoetigt einen OpenAI-Schluessel. Hinterlege ihn als `OPENAI_API_KEY` in den "
                "Streamlit-Secrets (.streamlit/secrets.toml) oder als Umgebungsvariable - dann ist der Tutor sofort aktiv.")
    else:
        tutor_q = st.text_input("Deine Frage an den Tutor",
                                placeholder="z.B. Was sagt mir der PEG genau? Warum ist Cashflow wichtiger als Gewinn?",
                                key="tutor_q")
        ex1, ex2 = st.columns([1, 3])
        if ex1.button("Tutor fragen", type="primary", key="tutor_btn"):
            if not (tutor_q or "").strip():
                st.warning("Bitte gib zuerst eine Frage ein.")
            else:
                ctx = f"Aktuelle Lektion: {L['title']} - Faustregel: {L['faustregel']}"
                with st.spinner("Tutor denkt nach ..."):
                    answer, status = ai_tutor(tutor_q, ctx)
                if status == "ki":
                    st.markdown(answer)
                    st.caption("KI-generiert, kann Fehler enthalten. Reine Bildung, keine Anlageberatung.")
                elif status == "no_key":
                    st.info("Kein OpenAI-Schluessel hinterlegt - bitte OPENAI_API_KEY setzen.")
                else:
                    st.warning(answer)

    st.markdown('<div class="fa-foot">FinAnalyse - Bildungs- & Analyse-Tool. Keine Anlageberatung.</div>',
                unsafe_allow_html=True)


# ====================== SEITE: KRYPTO ======================
elif page == "krypto":
    st.subheader("Krypto: alles zum Kennenlernen")
    st.caption("Lerne die wichtigsten Kryptowaehrungen und Grundbegriffe kennen. Reine Bildung - keine Anlageberatung.")
    st.markdown('<div class="lock-card"><b>Wichtiger Risikohinweis</b><br><span style="font-size:.9rem">'
                'Kryptowaehrungen sind hochspekulativ und extrem schwankungsanfaellig. Ein Totalverlust ist jederzeit '
                'moeglich. Investiere niemals Geld, dessen Verlust du nicht verschmerzen kannst. Dies ist Bildung, '
                'keine Anlageberatung.</span></div>', unsafe_allow_html=True)

    st.markdown("#### Grundbegriffe")
    for _titel, _txt in CRYPTO_BASICS:
        with st.expander(_titel):
            st.markdown(_txt)

    st.markdown("#### Die wichtigsten Coins im Portrait")
    _cnames = [f"{c['name']} ({c['symbol']}) - {c['kategorie']}" for c in CRYPTO_INFO]
    _ci = st.selectbox("Coin waehlen", list(range(len(CRYPTO_INFO))), format_func=lambda i: _cnames[i], key="crypto_pick")
    C = CRYPTO_INFO[_ci]
    st.markdown(f"### {C['name']} ({C['symbol']})")
    st.caption(f"Kategorie: {C['kategorie']}")
    st.markdown(C["body"])
    st.info("Schnellfakten: " + C["fakten"])
    st.warning("Risiko: " + C["risiko"])

    if is_pro():
        cc1, cc2 = st.columns([1, 3])
        if cc1.button("Aktuellen Kurs zeigen", key="crypto_px"):
            with st.spinner("Hole Kurs ..."):
                _res = quote_search(C["symbol"] + "-EUR")
            if _res is not None:
                cc1.metric(f"{C['symbol']}-EUR", fmt_quote(_res["last"]), delta=f"{_res['chg']*100:+.2f}%")
                _sp = sparkline(_res["series"], _res.get("chg", 0) >= 0, height=150)
                with cc2:
                    if _sp is not None:
                        st.altair_chart(_sp, use_container_width=True)
                    else:
                        st.line_chart(_res["series"], height=160)
            else:
                cc2.warning("Kein Live-Kurs gefunden (Quelle evtl. gedrosselt oder Ticker nicht handelbar).")
    else:
        st.markdown(locked_card_html("Live-Kurs & Chart",
                    "Aktuellen Kurs und Monats-Chart je Coin direkt hier ansehen - in Plus & Pro."),
                    unsafe_allow_html=True)

    st.markdown('<div class="fa-foot">FinAnalyse - reine Bildung, keine Anlageberatung. '
                'Krypto ist hochriskant; Daten ohne Gewaehr.</div>', unsafe_allow_html=True)


# ====================== SEITE: RECHTLICHES ======================
elif page == "legal":
    st.subheader(t("rechtliches"))
    st.info("MUSTER / kein Rechtsrat - vor Veroeffentlichung anwaltlich pruefen lassen. Platzhalter [...] ausfuellen. "
            "Ausfuehrliche Fassung: Dokument FinAnalyse_Rechtstexte_Muster.docx.")
    with st.expander("Haftungsausschluss / Disclaimer", expanded=True):
        st.markdown(LEGAL_DISCLAIMER)
    with st.expander("Nutzungsbedingungen (Kurzfassung)"):
        st.markdown(LEGAL_AGB)
    with st.expander("Impressum (Paragraph 5 DDG)"):
        st.markdown(LEGAL_IMPRESSUM)
    with st.expander("Datenschutz (Eckpunkte)"):
        st.markdown(LEGAL_DATENSCHUTZ)
    st.markdown('<div class="fa-foot">FinAnalyse - Bildungs- & Analyse-Tool. Keine Anlageberatung. '
                'Texte sind Muster und ersetzen keine anwaltliche Pruefung.</div>', unsafe_allow_html=True)


# ====================== SEITE: PREISE ======================
else:
    st.subheader("Plaene & Preise")
    st.caption("Demo der geplanten Monetarisierung. Der Plan-Umschalter links steuert, was in der App freigeschaltet ist.")
    st.markdown('<div class="price-wrap">' + "".join(price_card_html(p) for p in PLANS) + '</div>',
                unsafe_allow_html=True)
    st.markdown("")
    st.info("Hinweis: Echte Abrechnung erfordert Login + Zahlungsanbieter (z.B. Stripe) und eine "
            "kommerzielle Datenlizenz (Yahoo ist nicht fuer kommerzielle Nutzung freigegeben). "
            "Vor dem Verkauf rechtliche Pruefung (Abgrenzung zur Anlageberatung) einholen.")
    st.markdown('<div class="fa-foot">FinAnalyse - Bildungs- & Analyse-Tool. Keine Anlageberatung. '
                'Alle Angaben ohne Gewaehr.</div>', unsafe_allow_html=True)


# ====================== GLOBALE FOOTER-LINKS (jede Seite) ======================
st.markdown("---")
flc = st.columns([1, 1, 1.2, 4])
flc[0].button("Disclaimer", on_click=goto_legal, key="ft_disc", use_container_width=True)
flc[1].button("Impressum", on_click=goto_legal, key="ft_imp", use_container_width=True)
flc[2].button("Datenschutz", on_click=goto_legal, key="ft_dat", use_container_width=True)
flc[3].caption("FinAnalyse - Bildungs- & Analyse-Tool. Keine Anlageberatung. Alle Angaben ohne Gewaehr.")
