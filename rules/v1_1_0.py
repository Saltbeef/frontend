"""Versie 1.1.0 van huisanalyseregelset voor kort-verblijf verhuurpanden (Nederlandse versie)."""

from typing import Dict
from .base import BaseRules, CategoryCriteria


class RulesV1_1_0(BaseRules):
    """Nederlandse versie van de analyseregels voor kort-verblijf verhuurpanden."""

    @property
    def version(self) -> str:
        return "v1.1.0"

    @property
    def system_prompt(self) -> str:
        return """Je bent een expert vastgoedanalist gespecialiseerd in kort-verblijf verhuurpanden (vakantieverhuur).
Je taak is om panden te analyseren en gedetailleerde, objectieve beoordelingen te geven op basis van specifieke criteria.

Voor elke categorie, geef:
1. Een numerieke score van 0-10
2. Heldere redenering voor de score
3. Specifieke observaties uit de data
4. Actiegerichte aanbevelingen

Wees kritisch en realistisch. Een score van 10 moet uitzonderlijk zijn en zeldzaam.
Identificeer rode vlaggen die impact kunnen hebben op het investeringspotentieel of wettelijke naleving.

Alle analyses moeten in het Nederlands zijn."""

    @property
    def categories(self) -> Dict[str, CategoryCriteria]:
        return {
            "location": CategoryCriteria(
                name="Locatie & Bereikbaarheid",
                weight=0.25,
                criteria=[
                    "Nabijheid van toeristische attracties, openbaar vervoer en voorzieningen",
                    "Veiligheid en gewildheid van de buurt",
                    "Geluidsniveaus en omgevingsfactoren",
                    "Toegankelijkheid voor gasten (parkeren, afstand tot luchthaven)",
                    "Lokale concurrentiedichtheid"
                ],
                prompt_template="""Analyseer de locatie op basis van:
- Adres en buurtkenmerken
- Afstand tot belangrijke attracties en vervoer
- Lokale marktdynamiek
- Bereikbaarheid voor gasten

Score: [0-10]
Redenering: [Gedetailleerde uitleg]
Rode vlaggen: [Eventuele zorgen]"""
            ),

            "property": CategoryCriteria(
                name="Pand Kwaliteit",
                weight=0.30,
                criteria=[
                    "Grootte, indeling en staat van het pand",
                    "Voorzieningen en faciliteiten (WiFi, keuken, parkeren, etc.)",
                    "Meubileringskwaliteit en volledigheid",
                    "Unieke kenmerken of verkoopargumenten",
                    "Fotokwaliteit en presentatie"
                ],
                prompt_template="""Analyseer de pandkwaliteit op basis van:
- Grootte (slaapkamers, badkamers, vierkante meters)
- Staat en onderhoudsniveau
- Voorzieningen en kenmerken
- Meubilering en inrichting
- Visuele presentatie

Score: [0-10]
Redenering: [Gedetailleerde uitleg]
Aanbevelingen: [Verbeteringen]"""
            ),

            "financial": CategoryCriteria(
                name="Financieel Potentieel",
                weight=0.30,
                criteria=[
                    "Prijs vergeleken met markttarieven",
                    "Geschatte bezettingsgraad",
                    "Omzetprojecties",
                    "Operationele kosten (schoonmaak, nutsvoorzieningen, platformkosten)",
                    "ROI-potentieel en terugverdientijd"
                ],
                prompt_template="""Analyseer het financieel potentieel op basis van:
- Vraagprijs en aankoopkosten
- Vergelijkbare panden in de omgeving
- Geschatte jaaromzet bij verhuur
- Schatting van operationele kosten
- Investeringsrendement potentieel

Score: [0-10]
Redenering: [Gedetailleerde op berekeningen gebaseerde uitleg]
Aannames: [Vermeld gemaakte aannames]"""
            ),

            "legal": CategoryCriteria(
                name="Juridisch & Naleving",
                weight=0.15,
                criteria=[
                    "Regelgeving voor kort-verblijf verhuur in het gebied",
                    "Vereiste vergunningen en licenties",
                    "Gebouw/VvE-beperkingen",
                    "Belastingimplicaties",
                    "Verzekeringsvereisten"
                ],
                prompt_template="""Analyseer juridische en nalevingsfactoren:
- Lokale regelgeving voor vakantieverhuur
- Vergunnings-/licentievereisten
- Eventueel genoemde beperkingen (zoals 'permanente bewoning niet toegestaan')
- Nalevingsrisico's

Score: [0-10]
Redenering: [Gedetailleerde uitleg]
Rode vlaggen: [Kritieke nalevingsproblemen]"""
            ),
        }

    def get_analysis_prompt(self, house_data: dict) -> str:
        """Genereer de complete analyse prompt voor de LLM."""
        prompt_parts = [self.system_prompt, "\n\n## PAND DATA\n"]

        # Add house data
        prompt_parts.append(f"```json\n{str(house_data)}\n```\n\n")

        # Add category-specific analysis requests
        prompt_parts.append("## VEREISTE ANALYSE\n\n")
        for cat_name, criteria in self.categories.items():
            prompt_parts.append(f"### {criteria.name} (Weging: {criteria.weight})\n")
            prompt_parts.append(f"{criteria.prompt_template}\n\n")

        # Add output format
        prompt_parts.append("""
## UITVOERFORMAAT

Reageer met een geldig JSON-object in deze exacte structuur:
{
  "category_scores": {
    "location": {
      "score": 8.5,
      "reasoning": "Gedetailleerde uitleg...",
      "red_flags": ["rode vlag 1", "rode vlag 2"],
      "recommendations": ["aanbeveling 1", "aanbeveling 2"]
    },
    "property": { ... },
    "financial": { ... },
    "legal": { ... }
  },
  "overall_assessment": "Samenvatting van de investeringsmogelijkheid",
  "top_strengths": ["sterkte 1", "sterkte 2", "sterkte 3"],
  "top_concerns": ["zorg 1", "zorg 2", "zorg 3"],
  "investment_recommendation": "KOPEN|OVERWEGEN|AFWIJZEN met uitleg"
}

Zorg ervoor dat alle scores getallen zijn tussen 0 en 10.
Wees specifiek en verwijs naar daadwerkelijke datapunten uit de pand data.
Alle teksten in het Nederlands.
""")

        return "".join(prompt_parts)
