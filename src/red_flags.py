"""
Red Flag Detection System voor BNB/Vakantieverhuur
Makkelijk uitbreidbaar via patterns en categorieën

Focus: Maximaal rendement via zelfverhuur
Dealbreakers: Verplichte parkorganisaties, verhuurrestricties
"""

from typing import List, Dict, Tuple, Optional
import re


class RedFlagCategory:
    DEALBREAKER = "dealbreaker"  # Automatisch NEE
    WARNING = "warning"           # MISSCHIEN
    INFO = "info"                 # Opmerking


class RedFlag:
    """Single red flag pattern met matching logica"""

    def __init__(self, pattern: str, category: str, reason: str, weight: int = 10):
        self.pattern = pattern.lower()
        self.category = category
        self.reason = reason
        self.weight = weight
        self.regex = self._compile_pattern()

    def _compile_pattern(self):
        """Flexible matching: woorden kunnen uit elkaar staan"""
        words = self.pattern.split()
        pattern = r'.*'.join(map(re.escape, words))
        return re.compile(pattern, re.IGNORECASE | re.DOTALL)

    def matches(self, text: str) -> bool:
        return bool(self.regex.search(text.lower()))


# DEALBREAKERS - Automatisch NEE advies
DEALBREAKER_FLAGS = [
    # Verhuurrestricties - Core dealbreakers
    RedFlag("verhuur niet toegestaan", RedFlagCategory.DEALBREAKER,
            "Verhuur niet toegestaan - kan niet zelfverhuren", weight=100),
    RedFlag("permanente bewoning en verhuur zijn niet toegestaan", RedFlagCategory.DEALBREAKER,
            "Zowel bewoning als verhuur verboden", weight=100),
    RedFlag("verhuur aan derden is niet toegestaan", RedFlagCategory.DEALBREAKER,
            "Verhuur aan derden (gasten) verboden", weight=100),
    RedFlag("verhuur niet mogelijk", RedFlagCategory.DEALBREAKER,
            "Verhuur expliciet niet mogelijk", weight=100),

    # Verplichte parkorganisatie - Geen zelfverhuur
    RedFlag("verplichte verhuur via", RedFlagCategory.DEALBREAKER,
            "Verplichte verhuur via parkorganisatie - geen zelfverhuur mogelijk", weight=100),
    RedFlag("verhuurmogelijkheden via de organisatie op het park", RedFlagCategory.DEALBREAKER,
            "Verhuur alleen via parkorganisatie toegestaan", weight=90),
    RedFlag("verhuur alleen via derden toegestaan", RedFlagCategory.DEALBREAKER,
            "Geen zelfverhuur toegestaan", weight=100),
    RedFlag("uitsluitend verhuur via", RedFlagCategory.DEALBREAKER,
            "Uitsluitend verhuur via parkorganisatie", weight=100),

    # Specifieke parkorganisaties (lock-in met hoge fees)
    RedFlag("landal", RedFlagCategory.DEALBREAKER,
            "Landal - verplichte verhuurstructuur met hoge fees (40%+)", weight=100),
    RedFlag("europarcs", RedFlagCategory.DEALBREAKER,
            "Europarcs - verplichte verhuurstructuur met hoge fees", weight=100),
    RedFlag("roompot", RedFlagCategory.DEALBREAKER,
            "Roompot - verplichte verhuurstructuur met hoge fees", weight=100),
    RedFlag("summio", RedFlagCategory.DEALBREAKER,
            "Summio - verplichte verhuurstructuur met hoge fees", weight=100),

    # Hoge commissies - Rendement killer
    RedFlag("40% fee", RedFlagCategory.DEALBREAKER,
            "40% fee op verhuur - veel te hoog voor rendement", weight=95),
    RedFlag("40% commissie", RedFlagCategory.DEALBREAKER,
            "40% commissie op verhuur - rendement niet haalbaar", weight=95),
    RedFlag("50% commissie", RedFlagCategory.DEALBREAKER,
            "50% commissie - extreem hoog, onrendabel", weight=95),
    RedFlag("over de verhuuropbrengst wordt een fee van 40%", RedFlagCategory.DEALBREAKER,
            "40% fee op opbrengst - te hoge kosten", weight=95),

    # Leeftijdsrestricties - Beperkt doelgroep
    RedFlag("minimum leeftijd voor bewoners is 30 jaar", RedFlagCategory.DEALBREAKER,
            "Leeftijdsrestrictie 30+ beperkt doelgroep drastisch", weight=80),
    RedFlag("minimumleeftijd 30 jaar", RedFlagCategory.DEALBREAKER,
            "Leeftijdsrestrictie beperkt verhuurpotentieel", weight=80),

    # Recron - Beperkte vrijheid
    RedFlag("recron voorwaarden zijn van toepassing", RedFlagCategory.DEALBREAKER,
            "Recron voorwaarden beperken verhuurvrijheid significant", weight=85),
    RedFlag("recron voorwaarden", RedFlagCategory.DEALBREAKER,
            "Recron regelgeving beperkt operationele vrijheid", weight=85),

    # Privilege clausule - Extra kosten
    RedFlag("privilegeclausule", RedFlagCategory.DEALBREAKER,
            "Privilege clausule: extra kosten (vaak €10.000+) voor verhuurrecht", weight=90),
    RedFlag("dient er door iedere nieuwe eigenaar de privilegeclausule afgenomen te worden",
            RedFlagCategory.DEALBREAKER,
            "Verplichte privilege clausule bij overdracht (€9.797 extra)", weight=90),

    # Seizoensbeperkingen - Te kort verhuurseizoen
    RedFlag("seizoenscamping 1 april - 1 oktober", RedFlagCategory.DEALBREAKER,
            "Alleen zomerseizoen (6 maanden) - 50% van jaar niet bruikbaar", weight=85),
    RedFlag("seizoenscamping april tot oktober", RedFlagCategory.DEALBREAKER,
            "Alleen zomerseizoen - rendement te laag", weight=85),
    RedFlag("geopend van maart t/m oktober", RedFlagCategory.DEALBREAKER,
            "Park slechts 8 maanden open - beperkt rendement", weight=80),

    # Onderhoudsstaat - Onduidelijke kosten
    RedFlag("enig onderhoud nodig", RedFlagCategory.DEALBREAKER,
            "Onduidelijke onderhoudskosten - kan zeer hoog uitpakken", weight=75),
    RedFlag("renovatie noodzakelijk", RedFlagCategory.DEALBREAKER,
            "Grote renovatie nodig - extra kapitaal vereist", weight=80),
    RedFlag("het chalet heeft enig onderhoud nodig", RedFlagCategory.DEALBREAKER,
            "Onderhoud nodig zonder specificatie - risicovol", weight=75),
]


# WARNINGS - MISSCHIEN advies (verder onderzoek nodig)
WARNING_FLAGS = [
    # Erfpacht/huur - Geen eigendom grond
    RedFlag("erfpacht", RedFlagCategory.WARNING,
            "Erfpacht - check voorwaarden, kosten en looptijd zorgvuldig", weight=50),
    RedFlag("huurgrond", RedFlagCategory.WARNING,
            "Huurgrond - doorlopende kosten, geen eigendom grond, beperkte exit", weight=50),
    RedFlag("geen eigendom grond", RedFlagCategory.WARNING,
            "Grond niet in eigendom - beperkte controle en exit opties", weight=55),

    # Parkkosten - Kan rendement drukken
    RedFlag("parkkosten", RedFlagCategory.WARNING,
            "Parkkosten - vraag specificatie op (gas/water/elektra included?)", weight=35),
    RedFlag("servicekosten", RedFlagCategory.WARNING,
            "Servicekosten - vraag exacte breakdown", weight=35),
    RedFlag("hoge parkkosten", RedFlagCategory.WARNING,
            "Hoge parkkosten vermeld - kan rendement significant drukken", weight=60),
    RedFlag("parkkosten €", RedFlagCategory.WARNING,
            "Check of parkkosten all-inclusive zijn (energie/water)", weight=30),

    # Eigenaar goedkeuring - Extra stap in proces
    RedFlag("parkeigenaar wil voordat koop tot stand komt gesprek", RedFlagCategory.WARNING,
            "Goedkeuring parkeigenaar vereist - screeningsproces, mogelijk afwijzing", weight=45),
    RedFlag("goedkeuring eigenaar vereist", RedFlagCategory.WARNING,
            "Eigenaar moet nieuwe koper goedkeuren - extra onzekerheid", weight=45),
    RedFlag("toestemming eigenaar", RedFlagCategory.WARNING,
            "Toestemming eigenaar nodig - kan proces vertragen", weight=40),

    # Beperkte verhuurperiodes - Minder dan ideaal
    RedFlag("chalet mag 20 weken per jaar recreatief verhuurd worden", RedFlagCategory.WARNING,
            "Beperkt tot 20 weken verhuur per jaar - 60% van jaar niet beschikbaar", weight=70),
    RedFlag("mag 20 weken verhuurd worden", RedFlagCategory.WARNING,
            "Slechts 20 weken verhuur toegestaan - beperkt rendement", weight=70),
    RedFlag("park is geopend van maart t/m oktober", RedFlagCategory.WARNING,
            "Park alleen zomerseizoen open (8 mnd) - wintermaanden beperkt", weight=55),
    RedFlag("verblijf op dit park mag vanaf 25 maart tot 31 oktober", RedFlagCategory.WARNING,
            "Seizoensbeperking maart-oktober - winter niet mogelijk", weight=55),
    RedFlag("geen overnachting in de winter", RedFlagCategory.WARNING,
            "Wintermaanden geen verhuur mogelijk - rendement impact", weight=60),
    RedFlag("in de overige maanden mag overdag gerecreëerd worden maar niet worden overnacht",
            RedFlagCategory.WARNING,
            "Geen overnachtingen buiten seizoen - beperkt verhuurperiode", weight=60),

    # Bouwjaar - Verouderd (hoger onderhoud)
    RedFlag("bouwjaar 2010", RedFlagCategory.WARNING,
            "Bouwjaar 2010 - check staat, mogelijke renovatie nodig", weight=40),
    RedFlag("bouwjaar 2005", RedFlagCategory.WARNING,
            "15+ jaar oud - hogere onderhoudskosten te verwachten", weight=45),
    RedFlag("bouwjaar 2000", RedFlagCategory.WARNING,
            "20+ jaar oud - waarschijnlijk renovatie nodig", weight=50),
    RedFlag("bouwjaar 1995", RedFlagCategory.WARNING,
            "25+ jaar oud - significante renovatie waarschijnlijk", weight=55),
    RedFlag("bouwjaar 1990", RedFlagCategory.WARNING,
            "30+ jaar oud - hoge renovatiekosten verwacht", weight=60),
]


class RedFlagDetector:
    """Main detector class voor red flag scanning"""

    def __init__(self):
        self.dealbreakers = DEALBREAKER_FLAGS.copy()
        self.warnings = WARNING_FLAGS.copy()

    def scan(self, property_data: Dict) -> Dict:
        """
        Scan property voor red flags

        Returns:
            Dict met recommendation, found flags, en scoring
        """
        # Verzamel alle tekst
        text = self._extract_text(property_data)

        found_dealbreakers = []
        found_warnings = []
        total_weight = 0

        # Check dealbreakers
        for flag in self.dealbreakers:
            if flag.matches(text):
                found_dealbreakers.append({
                    'pattern': flag.pattern,
                    'reason': flag.reason,
                    'weight': flag.weight
                })
                total_weight += flag.weight

        # Check warnings
        for flag in self.warnings:
            if flag.matches(text):
                found_warnings.append({
                    'pattern': flag.pattern,
                    'reason': flag.reason,
                    'weight': flag.weight
                })
                total_weight += flag.weight

        # Determine recommendation
        if found_dealbreakers or total_weight >= 100:
            recommendation = "AFWIJZEN"
            recommendation_color = "red"
            confidence = "HOOG"
        elif found_warnings or total_weight >= 50:
            recommendation = "VERDER ONDERZOEK"
            recommendation_color = "yellow"
            confidence = "MIDDEL"
        else:
            recommendation = "GESCHIKT"
            recommendation_color = "green"
            confidence = "LAAG"

        return {
            'recommendation': recommendation,
            'recommendation_color': recommendation_color,
            'confidence': confidence,
            'dealbreakers': found_dealbreakers,
            'warnings': found_warnings,
            'total_weight': total_weight,
            'dealbreaker_count': len(found_dealbreakers),
            'warning_count': len(found_warnings),
            'scanned_text_length': len(text)
        }

    def _extract_text(self, property_data: Dict) -> str:
        """Extract alle relevante tekst uit property data"""
        texts = []

        # Beschrijving (belangrijkste bron)
        if desc := property_data.get('ListingDescription', {}).get('Description'):
            texts.append(desc)

        # Title
        if title := property_data.get('ListingDescription', {}).get('Title'):
            texts.append(title)

        # Kenmerken sections
        for section in property_data.get('KenmerkSections', []):
            # Section title
            if section_title := section.get('Title'):
                texts.append(section_title)

            # Kenmerken
            for kenmerk in section.get('KenmerkenList', []):
                if value := kenmerk.get('Value'):
                    texts.append(value)
                if label := kenmerk.get('Label'):
                    texts.append(label)

        # Adres details
        if subtitle := property_data.get('AddressDetails', {}).get('SubTitle'):
            texts.append(subtitle)

        # Labels (soms belangrijke info)
        for label in property_data.get('Labels', []):
            if isinstance(label, str):
                texts.append(label)
            elif isinstance(label, dict) and 'Text' in label:
                texts.append(label['Text'])

        return ' '.join(texts).lower()

    def add_dealbreaker(self, pattern: str, reason: str, weight: int = 100):
        """Voeg custom dealbreaker toe (makkelijk uitbreiden!)"""
        self.dealbreakers.append(
            RedFlag(pattern, RedFlagCategory.DEALBREAKER, reason, weight)
        )
        print(f"✅ Dealbreaker toegevoegd: '{pattern}'")

    def add_warning(self, pattern: str, reason: str, weight: int = 50):
        """Voeg custom warning toe"""
        self.warnings.append(
            RedFlag(pattern, RedFlagCategory.WARNING, reason, weight)
        )
        print(f"⚠️  Warning toegevoegd: '{pattern}'")

    def get_statistics(self) -> Dict:
        """Get statistics over configured flags"""
        return {
            'total_dealbreakers': len(self.dealbreakers),
            'total_warnings': len(self.warnings),
            'total_flags': len(self.dealbreakers) + len(self.warnings)
        }


def get_detector() -> RedFlagDetector:
    """Convenience function voor getting detector instance"""
    return RedFlagDetector()


if __name__ == "__main__":
    # Test code
    detector = RedFlagDetector()
    print(f"Red Flag Detector geïnitialiseerd")
    print(f"Dealbreakers: {len(detector.dealbreakers)}")
    print(f"Warnings: {len(detector.warnings)}")
    print(f"\nTest patterns:")

    test_cases = [
        "Dit chalet mag alleen via Landal verhuurd worden",
        "Verhuur niet toegestaan op dit park",
        "Erfpacht grond met parkkosten €3000/jaar",
        "Prachtig chalet met eigen grond en vrije verhuur"
    ]

    for test in test_cases:
        result = detector.scan({'ListingDescription': {'Description': test}})
        print(f"\nTest: '{test[:50]}...'")
        print(f"Result: {result['recommendation']} ({result['total_weight']} weight)")
        if result['dealbreakers']:
            print(f"  Dealbreakers: {len(result['dealbreakers'])}")
        if result['warnings']:
            print(f"  Warnings: {len(result['warnings'])}")
