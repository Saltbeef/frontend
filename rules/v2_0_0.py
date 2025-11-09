"""
Versie 2.0.0 - BNB/Vakantieverhuur Expert Analyseregels

Focus: Maximaal rendement door ZELF te verhuren
Strategie: Kopen → Zelfverhuur → Verkopen → Opschalen naar duurdere objecten

Key Features:
- Geïntegreerde red flag detectie voor verhuurrestricties
- Automatische afwijzing van verplichte parkorganisaties (Landal, Europarcs, etc.)
- BNB expertise gebaseerd op uitgebreid handboek
- Focus op zelfverhuur en schaalbare investeringen
"""

from typing import Dict
import json
from pathlib import Path
from .base import BaseRules, CategoryCriteria


class RulesV2_0_0(BaseRules):
    """BNB/Vakantieverhuur Expert Analyseregels met Red Flag Detectie."""

    @property
    def version(self) -> str:
        return "v2.0.0"

    @property
    def system_prompt(self) -> str:
        return """Je bent een expert BNB/Vakantieverhuur analyst gespecialiseerd in recreatief vastgoed.

## CORE STRATEGIE

**Doel:** Maximaal rendement door ZELF te verhuren
**Aanpak:** Kopen → Zelfverhuur → Verkopen → Opschalen naar duurdere objecten

## KRITISCHE RED FLAGS (AUTOMATISCH AFWIJZEN)

### Verhuurrestricties - DEALBREAKERS
❌ "Verhuur niet toegestaan" → Kan niet zelfverhuren
❌ "Verhuur alleen via derden toegestaan" → Geen zelfverhuur mogelijk
❌ "Permanente bewoning en verhuur niet toegestaan" → Beide verboden
❌ Verplichte parkorganisaties: Landal, Europarcs, Roompot, Summio → 40%+ fees, geen zelfverhuur
❌ "40% fee" of "50% commissie" → Rendement killer
❌ "Recron voorwaarden" → Beperkt verhuurvrijheid significant
❌ "Privilegeclausule" → Extra kosten €10.000+ voor verhuurrecht
❌ Seizoenscamping (bijv. "1 april - 1 oktober") → Slechts 6 maanden verhuur
❌ Minimumleeftijd 30+ → Beperkt doelgroep drastisch
❌ "Enig onderhoud nodig" → Onduidelijke kosten, kan zeer hoog uitpakken

### Waarschuwingen - NADER ONDERZOEK
⚠️ Erfpacht/huurgrond → Check voorwaarden en looptijd zorgvuldig
⚠️ Hoge parkkosten → Kan rendement significant drukken
⚠️ Beperkte verhuurperiodes (bijv. 20 weken) → 60%+ van jaar niet beschikbaar
⚠️ Bouwjaar <2010 → Hogere onderhoudskosten verwacht
⚠️ Goedkeuring parkeigenaar vereist → Extra onzekerheid, mogelijk afwijzing

## BNB EXPERTISE PRINCIPES

### 1. Professionele Mindset
- Investeren in vakantiewoningen is een marathon, geen sprint
- Monitoring & Analyse voor constante verbetering
- Emoties uitschakelen, kopen met de rekenmachine

### 2. Marktonderzoek Cruciaal
**Tools & Methoden:**
- AirDNA voor bezettingsgraden, nachtprijzen, markttrends
- Rendement calculator (NOOIT zonder rekenen kopen)
- Reviews analyseren: 1 op 10 gasten laat recensie achter
  → 58 reviews = ~580 overnachtingen

**Locatie Criteria (A-locaties prefereren):**
✅ Dicht bij centrum/strand/meer
✅ Nabij toeristische attracties
✅ Goede bereikbaarheid OV en snelweg
✅ Natuurlijke omgeving (bos, polder, water)
✅ Winkels & voorzieningen in de buurt
✅ Bijzondere activiteiten (markten, musea, evenementen)

### 3. Financieel Rendement
**Kosten structuur:**
- Platformkosten: 3% Airbnb, 15% Booking.com (gemiddeld 10%)
- Schoonmaak: €40-75 per beurt
- Accountant/Beheer: ~€1000/jaar
- Onderhoud reserve: 5-10% jaaromzet
- Nutsvoorzieningen: Gemiddeld €100-200/maand

**Rendement Targets:**
- Cash-on-Cash Return: 15%+ uitstekend, 10%+ goed
- Bezettingsgraad: 60%+ target (AirDNA data gebruiken)
- Break-even: <3 jaar ideaal
- Scale-up potentieel: Kan dit object over 2-3 jaar verkocht worden met winst?

### 4. Unieke Verkoopargumenten (USP's)
**Wat Maakt Een Woning Succesvol:**
✨ Unieke kenmerken (hottub, sauna, bijzonder design)
✨ Geschikt voor doelgroepen (gezinnen, stellen, groepen)
✨ Huisdieren toegestaan (30% grotere doelgroep)
✨ Rust & Privacy
✨ Luxe uitstraling in foto's
✨ Professionele presentatie

### 5. Operationele Vrijheid
**Essentieel Voor Zelfverhuur:**
✅ Geen verplichte verhuur via parkorganisatie
✅ Vrije prijsstelling mogelijk
✅ Zelf platformkeuze (Airbnb, Booking.com, eigen website)
✅ Jaar-rond verhuur mogelijk (of minimaal 9+ maanden)
✅ Flexibele aankomst/vertrektijden

## ANALYSE OPDRACHT

Voor elk pand:
1. **PRE-SCREENING:** Check alle red flags (als dealbreaker gevonden → AFWIJZEN)
2. **DEEP ANALYSIS:** Als geschikt, analyseer alle categorieën
3. **RENDEMENT FOCUS:** Bereken realistische opbrengsten op basis van marktdata
4. **SCALE-UP WAARDE:** Kan dit object over 2-3 jaar verkocht worden met winst?
5. **CONCREET ADVIES:** Niet abstract blijven - geef cijfers, berekeningen, actieplan

Wees kritisch, realistisch en data-gedreven. Een score van 10 is uitzonderlijk zeldzaam.
Alle analyses in het Nederlands met concrete berekeningen en marktonderbouwing.
"""

    @property
    def categories(self) -> Dict[str, CategoryCriteria]:
        return {
            "location": CategoryCriteria(
                name="Locatie & Toeristische Aantrekkelijkheid",
                weight=0.25,
                criteria=[
                    "Nabijheid van toeristische attracties, strand, meer, natuur",
                    "Bereikbaarheid via OV en auto (afstand snelweg, station)",
                    "Lokale voorzieningen (winkels, restaurants, activiteiten)",
                    "A-locatie vs B/C-locatie (impact op bezetting en prijs)",
                    "Seizoenspatronen (zomer/winter potentieel)",
                    "Concurrentiedichtheid op verhuurplatforms"
                ],
                prompt_template="""Analyseer de locatie met BNB focus:

**TOERISTISCHE AANTREKKELIJKHEID:**
- Welke attracties zijn binnen 5/10/20 km? (strand, pretparken, steden, natuur)
- Is dit een A-locatie (hoog potentieel) of B/C-locatie?
- Wat is de toeristische seizoenspatroon? (alleen zomer of jaar-rond?)

**BEREIKBAARHEID:**
- Afstand tot snelweg/hoofdweg?
- OV-bereikbaarheid (station, bus)?
- Aantrekkelijk voor Duitse toeristen? (belangrijke doelgroep)

**LOKALE MARKT:**
- Check Airbnb/Booking.com: hoeveel concurrenten in de buurt?
- Wat zijn de nachtprijzen van vergelijkbare objecten?
- Hoeveel reviews hebben concurrenten? (indicator bezettingsgraad)

**BNB POTENTIEEL:**
- Kan dit object jaar-rond of alleen seizoensgebonden verhuurd worden?
- Is er voldoende vraag in laagseizoen?

Score: [0-10]
Redenering: [Specifiek met marktdata, afstanden, concurrentie-analyse]
Rode vlaggen: [Eventuele locatie problemen]
Marktdata: [AirDNA/platform data waar beschikbaar]"""
            ),

            "property": CategoryCriteria(
                name="Pand Kwaliteit & USP's",
                weight=0.30,
                criteria=[
                    "Grootte, indeling en staat (slaapkamers, badkamers, m²)",
                    "Unieke verkoopargumenten (hottub, sauna, design, privacy)",
                    "Doelgroep geschiktheid (gezinnen, stellen, groepen)",
                    "Huisdieren toegestaan? (+30% doelgroep)",
                    "Meubilering en inrichting kwaliteit",
                    "Buitenruimte (tuin, terras, parking)",
                    "Voorzieningen (WiFi, keuken, bbq, wasmachine)",
                    "Fotokwaliteit en presentatie",
                    "Onderhoudsstaat en renovatie nodig?"
                ],
                prompt_template="""Analyseer pand kwaliteit met verhuur focus:

**BASISSPECIFICATIES:**
- Aantal slaapkamers/bedden: [aantal] → max [X] gasten
- Aantal badkamers:
- Oppervlakte: [m²]
- Bouwjaar: [jaar] → Impact op onderhoud?

**UNIEKE VERKOOPARGUMENTEN (USP's):**
Wat maakt dit pand SPECIAAL voor gasten?
- Hottub/Sauna/Jacuzzi?
- Bijzonder design of thema?
- Privacy en rust?
- Uitzicht (water, bos, weiland)?
- Luxe uitstraling?

**DOELGROEP MATCH:**
- Gezinnen: Kindvriendelijk? Speelruimte?
- Stellen: Romantisch? Rust?
- Groepen: Voldoende slaapkamers?
- Huisdieren toegestaan? (vergroot doelgroep met 30%!)

**VOORZIENINGEN:**
- Compleet ingerichte keuken?
- WiFi aanwezig?
- Parking (hoeveel auto's)?
- BBQ/Buitenruimte?
- Wasmachine/droger?

**VISUELE PRESENTATIE:**
- Fotokwaliteit: Professioneel of amateuristisch?
- Zie je de USP's in de foto's?
- Genoeg foto's voor goede indruk?

**ONDERHOUDSSTAAT:**
- Direct verhuurklaar of renovatie nodig?
- Geschatte renovatiekosten indien van toepassing
- Jaarlijks onderhoudsbudget inschatten

Score: [0-10]
Redenering: [Focus op verhuurpotentieel en USP's]
USP's: [Lijst unieke selling points]
Verbeteringen: [Kosten-effectieve upgrades voor hoger rendement]"""
            ),

            "financial": CategoryCriteria(
                name="Financieel Rendement & Scale-up Potentieel",
                weight=0.30,
                criteria=[
                    "Vraagprijs vs marktwaarde",
                    "Geschatte jaaromzet (bezetting × nachtprijs × 365)",
                    "All-in kostenstructuur (parkkosten, energie, onderhoud, platform fees)",
                    "Netto cashflow en Cash-on-Cash return",
                    "Break-even periode",
                    "Financieringsmogelijkheden",
                    "Scale-up potentieel: verkoopwaarde over 2-3 jaar",
                    "Exit strategie voor opschalen naar duurder object"
                ],
                prompt_template="""Analyseer financieel met BNB rendement focus:

**AANKOOPKOSTEN:**
- Vraagprijs: €[bedrag]
- Overdrachtsbelasting (2%): €[bedrag]
- Notaris/advies (~€2000): €[bedrag]
- Eventuele renovatie: €[bedrag]
- TOTAAL INVESTERING: €[bedrag]

**JAAROMZET BEREKENING:**
Gebruik marktdata van vergelijkbare objecten!

Methode 1 - Platform Data:
- Check Airbnb/Booking reviews concurrent objecten
- Reviews × 10 = geschatte aantal boekingen/jaar
- Gemiddelde nachtprijs: €[bedrag]
- Gemiddelde verblijfsduur: [dagen]

Methode 2 - Conservatieve Schatting:
- Hoogseizoen (90 dagen): [%] bezetting × €[hoog tarief]
- Middenseizoen (180 dagen): [%] bezetting × €[midden tarief]
- Laagseizoen (95 dagen): [%] bezetting × €[laag tarief]

**JAARLIJKSE KOSTEN:**
- Parkkosten/erfpacht: €[bedrag]/jaar
- Energie & water: €[bedrag]/jaar (~€1200-2400)
- Gemeentelijke lasten: €[bedrag]/jaar
- Platform fees (10% gemiddeld): €[bedrag]/jaar
- Schoonmaak (€50 × [aantal] beurten): €[bedrag]/jaar
- Wasgoed service: €[bedrag]/jaar
- Onderhoud reserve (5-10%): €[bedrag]/jaar
- Accountant/administratie: €1000/jaar
- Verzekeringen: €[bedrag]/jaar
- TOTALE KOSTEN: €[bedrag]/jaar

**RENDEMENT ANALYSE:**
- Bruto jaaromzet: €[bedrag]
- Netto jaaromzet (na kosten): €[bedrag]
- Cash-on-Cash Return: [%] (netto ÷ investering)
- Break-even periode: [jaren]

**FINANCIERING:**
- Eigen inbreng (30%): €[bedrag]
- Hypotheek (70%): €[bedrag]
- Maandlasten hypotheek: €[bedrag]
- Netto cashflow per maand: €[bedrag]

**SCALE-UP POTENTIEEL:**
- Verwachte waardestijging 3 jaar: [%] → €[bedrag]
- Exit strategie: Verkopen na [X] jaar voor €[bedrag]
- Winst realisatie voor opschalen naar duurder object

**RENDEMENT OORDEEL:**
- 15%+ Cash-on-Cash = UITSTEKEND (zeldzaam)
- 10-15% = GOED
- 7-10% = REDELIJK
- <7% = ONDERMAATS

Score: [0-10]
Redenering: [Gedetailleerd met alle berekeningen]
Aannames: [Alle gemaakte aannames expliciet vermelden]
Gevoeligheid: [Wat als bezetting 10% lager? Wat als kosten 20% hoger?]
Advies: [Concreet koopadvies op basis van cijfers]"""
            ),

            "legal": CategoryCriteria(
                name="Juridisch, Regelgeving & Verhuurvrijheid",
                weight=0.15,
                criteria=[
                    "Verhuurrestricties (red flags gedetecteerd?)",
                    "Verplichte parkorganisatie of vrije verhuur?",
                    "Seizoensbeperkingen of jaar-rond verhuur?",
                    "Erfpacht/eigendom grond voorwaarden",
                    "VvE/park goedkeuring vereist?",
                    "Recron voorwaarden van toepassing?",
                    "Privilege clausules of extra kosten?",
                    "Lokale regelgeving vakantieverhuur",
                    "Belasting implications (box 1 vs box 3)"
                ],
                prompt_template="""Analyseer juridisch met ZELFVERHUUR focus:

**RED FLAGS CHECK:**
Zijn er rode vlaggen gedetecteerd in pre-screening?
- Dealbreakers gevonden: [lijst]
- Warnings gevonden: [lijst]

**VERHUURVRIJHEID (KRITISCH!):**
❓ Mag je ZELF verhuren via eigen kanalen (Airbnb, Booking.com)?
❓ Is verhuur via parkorganisatie VERPLICHT? (Landal, Europarcs, etc.)
❓ Zijn er commissies op verhuur? (>15% is problematisch)
❓ Vrije prijsstelling mogelijk of vastgestelde tarieven?

**SEIZOEN & PERIODE:**
❓ Jaar-rond verhuur toegestaan?
❓ Seizoensbeperkingen? (bijv. alleen maart-oktober)
❓ Maximaal aantal verhuurweken per jaar?
❓ Overnachting toegestaan in alle maanden?

**EIGENDOM & GROND:**
❓ Eigendom of erfpacht/huurgrond?
❓ Bij erfpacht: looptijd en voorwaarden?
❓ Canon (erfpacht fee) per jaar?
❓ Kunnen voorwaarden wijzigen?

**GOEDKEURINGEN:**
❓ Moet nieuwe eigenaar goedgekeurd worden door park?
❓ VvE restricties op verhuur?
❓ Recron voorwaarden van toepassing?
❓ Privilege clausule bij overdracht? (extra kosten!)

**LOKALE REGELGEVING:**
❓ Vergunning nodig voor vakantieverhuur?
❓ Maximaal aantal nachten per jaar?
❓ Toeristenbelasting verplichtingen?

**FISCAAL:**
- Box 1 (onderneming) of Box 3 (vermogen)?
- BTW implicaties bij professionele verhuur?
- Aftrekposten en fiscale voordelen?

**DEALBREAKER CHECK:**
Als één van onderstaande JA is → AUTOMATISCH AFWIJZEN:
- Verhuur niet toegestaan
- Alleen via parkorganisatie toegestaan
- Verplichte verhuur via derden
- >30% commissie op verhuur
- Privilege clausule >€5000
- Minder dan 8 maanden verhuur per jaar

Score: [0-10]
Redenering: [Focus op vrijheid voor zelfverhuur]
Rode vlaggen: [Alle juridische risico's]
Dealbreakers: [Kritieke uitsluitingen]
Aanbevelingen: [Juridisch advies indien onduidelijk]"""
            ),
        }

    def get_analysis_prompt(
        self,
        house_data: dict,
        enrichment_data: dict = None,
        market_metrics: dict = None
    ) -> str:
        """
        Genereer complete analyse prompt met RED FLAG PRE-SCREENING.

        Integreert red flag detectie VOOR deep analysis.

        Args:
            house_data: Raw house data from Apify
            enrichment_data: Optional AirROI enrichment (comparables, revenue estimate)
            market_metrics: Optional market-level metrics from AirROI
        """
        from src.red_flags import RedFlagDetector

        # PRE-SCREENING: Red Flag Detection
        detector = RedFlagDetector()
        red_flag_results = detector.scan(house_data)

        prompt_parts = [self.system_prompt, "\n\n"]

        # Add red flag pre-screening results
        prompt_parts.append("## 🚨 RED FLAG PRE-SCREENING RESULTATEN\n\n")
        prompt_parts.append(f"**Aanbeveling:** {red_flag_results['recommendation']}\n")
        prompt_parts.append(f"**Betrouwbaarheid:** {red_flag_results['confidence']}\n")
        prompt_parts.append(f"**Totaal gewicht:** {red_flag_results['total_weight']}\n\n")

        if red_flag_results['dealbreakers']:
            prompt_parts.append(f"**⛔ DEALBREAKERS GEVONDEN ({len(red_flag_results['dealbreakers'])}):**\n")
            for flag in red_flag_results['dealbreakers']:
                prompt_parts.append(f"- [{flag['weight']}] {flag['reason']}\n")
                prompt_parts.append(f"  Pattern: '{flag['pattern']}'\n")
            prompt_parts.append("\n")

        if red_flag_results['warnings']:
            prompt_parts.append(f"**⚠️  WARNINGS GEVONDEN ({len(red_flag_results['warnings'])}):**\n")
            for flag in red_flag_results['warnings']:
                prompt_parts.append(f"- [{flag['weight']}] {flag['reason']}\n")
                prompt_parts.append(f"  Pattern: '{flag['pattern']}'\n")
            prompt_parts.append("\n")

        # If dealbreakers found, instruct immediate rejection
        if red_flag_results['recommendation'] == 'AFWIJZEN':
            prompt_parts.append("""
⛔ **BELANGRIJK:** Er zijn dealbreakers gevonden.
Dit pand moet worden AFGEWEZEN zonder verdere analyse.

Geef een beknopte analyse die uitlegt WAAROM dit pand afgekeurd wordt,
met focus op de gevonden dealbreakers. Gebruik lage scores (0-3) voor alle categorieën.

Investement recommendation moet AFWIJZEN zijn met duidelijke onderbouwing.
""")

        # Add house data
        prompt_parts.append("## 📋 PAND DATA\n\n")
        prompt_parts.append(f"```json\n{json.dumps(house_data, indent=2, ensure_ascii=False)}\n```\n\n")

        # Add AirROI enrichment data if available
        if enrichment_data and enrichment_data.get('enriched'):
            prompt_parts.append("## 🌍 AIRROI MARKTDATA (AIRBNB/SHORT-TERM RENTAL)\n\n")
            prompt_parts.append("**Belangrijk:** Deze data komt van echte Airbnb listings in de buurt en kan gebruikt worden voor concretere revenue schattingen en marktanalyse.\n\n")

            # Add comparable listings summary
            comparables = enrichment_data.get('comparables', [])
            if comparables:
                prompt_parts.append(f"### Vergelijkbare Airbnb listings in de buurt ({len(comparables)} listings)\n\n")
                prompt_parts.append("Top vergelijkbare properties:\n\n")
                for i, comp in enumerate(comparables[:5], 1):
                    prompt_parts.append(f"**Listing {i}:**\n")
                    prompt_parts.append(f"- Bedrooms: {comp.get('bedrooms', 'N/A')}\n")
                    prompt_parts.append(f"- Bathrooms: {comp.get('bathrooms', 'N/A')}\n")

                    # Metrics (TTM = Trailing Twelve Months)
                    metrics = comp.get('metrics', {}).get('ttm', {})
                    if metrics:
                        prompt_parts.append(f"- Annual Revenue (TTM): {metrics.get('revenue', 'N/A')}\n")
                        prompt_parts.append(f"- Occupancy Rate (TTM): {metrics.get('occupancy', 'N/A')}%\n")
                        prompt_parts.append(f"- Average Daily Rate (TTM): {metrics.get('adr', 'N/A')}\n")
                        prompt_parts.append(f"- Days Booked (TTM): {metrics.get('days_booked', 'N/A')}\n")
                    prompt_parts.append("\n")

            # Add revenue estimate
            revenue_estimate = enrichment_data.get('revenue_estimate', {})
            if revenue_estimate:
                prompt_parts.append("### Revenue Schatting voor dit pand\n\n")
                prompt_parts.append("**Gebaseerd op vergelijkbare listings in de buurt:**\n\n")
                estimate_data = revenue_estimate.get('estimate', {})
                if estimate_data:
                    prompt_parts.append(f"```json\n{json.dumps(estimate_data, indent=2, ensure_ascii=False)}\n```\n\n")

            prompt_parts.append("**Gebruik deze data actief in je financial analysis!** De revenue estimate en comparable listings geven concrete marktdata voor realistische projecties.\n\n")

        # Add market-level metrics if available
        if market_metrics:
            prompt_parts.append("## 📊 MARKT METRICS (STAD-NIVEAU)\n\n")
            city = house_data.get('AddressDetails', {}).get('City', 'Unknown')
            province = market_metrics.get('province', 'Unknown')
            prompt_parts.append(f"**Markt:** {city}, {province}\n\n")

            metrics = market_metrics.get('metrics', {})
            if metrics:
                prompt_parts.append("**Market Performance (Trailing 12 Months):**\n\n")
                prompt_parts.append(f"```json\n{json.dumps(metrics, indent=2, ensure_ascii=False)}\n```\n\n")
                prompt_parts.append("**Gebruik deze data voor context:** Vergelijk de property's potentieel met het marktgemiddelde.\n\n")

        # Add category-specific analysis requests
        prompt_parts.append("## 🔍 VEREISTE ANALYSE PER CATEGORIE\n\n")
        for cat_name, criteria in self.categories.items():
            prompt_parts.append(f"### {criteria.name} (Weging: {int(criteria.weight * 100)}%)\n\n")
            prompt_parts.append(f"{criteria.prompt_template}\n\n")

        # Add output format
        prompt_parts.append("""
## 📤 UITVOERFORMAAT

Reageer met een geldig JSON-object in deze EXACTE structuur:

```json
{
  "category_scores": {
    "location": {
      "score": 7.5,
      "reasoning": "Gedetailleerde analyse met concrete data (afstanden, attracties, marktprijzen)...",
      "red_flags": ["rode vlag 1", "rode vlag 2"],
      "recommendations": ["aanbeveling 1", "aanbeveling 2"],
      "market_data": "AirDNA/platform data indien beschikbaar"
    },
    "property": {
      "score": 8.0,
      "reasoning": "USP's, doelgroep match, voorzieningen...",
      "red_flags": [],
      "recommendations": ["verbeter fotografie", "voeg hottub toe"],
      "usp_highlights": ["hottub", "privacy", "huisdieren toegestaan"]
    },
    "financial": {
      "score": 6.5,
      "reasoning": "Volledige rendement berekening met alle cijfers...",
      "red_flags": ["hoge parkkosten", "lage geschatte bezetting"],
      "recommendations": ["onderhandel prijs", "verbeter USP's voor hogere nachtprijs"],
      "calculations": {
        "purchase_price": 125000,
        "total_investment": 130000,
        "estimated_annual_revenue": 28000,
        "estimated_annual_costs": 12000,
        "net_annual_income": 16000,
        "cash_on_cash_return": 12.3,
        "breakeven_years": 2.8
      }
    },
    "legal": {
      "score": 9.0,
      "reasoning": "Analyse verhuurvrijheid, seizoen, juridische aspecten...",
      "red_flags": [],
      "recommendations": ["check parkreglement bij notaris"],
      "rental_freedom": "Volledig vrije verhuur mogelijk, geen restricties"
    }
  },
  "overall_assessment": "Samenvatting investering met focus op zelfverhuur potentieel en scale-up mogelijkheid. Concreet en data-gedreven.",
  "top_strengths": [
    "Sterkte 1 met concrete data",
    "Sterkte 2 met cijfers",
    "Sterkte 3 specifiek"
  ],
  "top_concerns": [
    "Zorg 1 met impact analyse",
    "Zorg 2 met cijfers",
    "Zorg 3 met risico"
  ],
  "investment_recommendation": "KOPEN|OVERWEGEN|AFWIJZEN - met heldere onderbouwing",
  "action_plan": [
    "Concrete actie 1 (bijv. 'Onderhandel naar €115k')",
    "Concrete actie 2 (bijv. 'Vraag parkreglement op bij beheerder')",
    "Concrete actie 3 (bijv. 'Budget €5k voor hottub installatie')"
  ],
  "scale_up_potential": "Analyse: kan dit object over 2-3 jaar met winst verkocht worden voor opschaling?"
}
```

## ✅ KWALITEITSEISEN

1. **Scores:** Altijd tussen 0-10. Score van 10 is UITZONDERLIJK zeldzaam.
2. **Cijfers:** Gebruik concrete bedragen, percentages, afstanden (niet vaag blijven!)
3. **Marktdata:** Refereer naar Airbnb/Booking.com data waar mogelijk
4. **Red flags:** Neem ALLE gevonden red flags uit pre-screening over in relevante categorieën
5. **Rekenwerk:** Bij financial category ALLE berekeningen uitschrijven
6. **Dealbreakers:** Als AFWIJZEN → scores 0-3, heldere uitleg waarom
7. **Actieplan:** Concrete, uitvoerbare stappen (geen abstract advies)
8. **Scale-up:** Altijd beoordelen of dit object winst kan maken voor opschaling
9. **Nederlands:** Alle tekst in correct Nederlands
10. **JSON:** Valide JSON structuur, geen syntax errors
11. **BELANGRIJK - Beknoptheid:** Reasoning per categorie MAX 400 woorden. Focus op kernpunten en cijfers.
    De HELE JSON moet binnen 8000 tokens passen, dus wees efficiënt met woorden!

**LET OP:** Als red flag pre-screening "AFWIJZEN" aanbeveelt, moet je investment_recommendation
ook "AFWIJZEN" zijn met duidelijke focus op de dealbreakers.
""")

        return "".join(prompt_parts)
