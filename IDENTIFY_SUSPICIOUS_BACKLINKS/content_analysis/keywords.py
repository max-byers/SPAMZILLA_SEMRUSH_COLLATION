# content_analysis/keywords.py
"""
Suspicious keyword definitions and patterns for content analysis.
"""

# Suspicious keyword categories and terms with regex patterns
SUSPICIOUS_KEYWORDS = {
    'Adult': [
        r'\bxxx\b', r'\bporn\b', r'\badult\b', r'\bsex\b', r'\bescort\b', r'\bdating\b',
        r'\bnude\b', r'\bnaked\b', r'\bviagra\b', r'\bcialis\b', r'\badult\s+content\b',
        r'\bmature\s+content\b', r'\bescorts?\b', r'\bstrip\s+club\b', r'\bstripper\b',
        r'\bbrothel\b', r'\bcasino\b', r'\bgambling\b', r'\bbetting\b', r'\bxvideos\b',
        r'\bpornhub\b', r'\bxhamster\b', r'\berotic\b'
    ],
    'Gambling': [
        r'\bcasino\b', r'\bpoker\b', r'\bbet\b', r'\bbetting\b', r'\bgambling\b',
        r'\blottery\b', r'\bslot\b', r'\bblackjack\b', r'\broulette\b', r'\bwagering\b',
        r'\bsportsbook\b', r'\bbaccarat\b', r'\bgames?\s+of\s+chance\b', r'\bbookmaker\b',
        r'\bspin\s+to\s+win\b', r'\bjackpot\b', r'\bslot\s+machine\b', r'\bcasinoclub\b',
        r'\bon\s?line\s+gambling\b', r'\bgamble\b', r'\blive\s+dealer\b', r'\bbettors\b',
        r'\bbookies\b', r'\bpunters?\b'
    ],
    'Pharmaceuticals': [
        r'\bpharmacy\b', r'\bdrug\b', r'\bprescription\b', r'\bmedication\b', r'\bmed\b',
        r'\bpills\b', r'\bcheap\s+meds\b', r'\bbuy\s+medication\b', r'\bonline\s+pharmacy\b',
        r'\bno\s+prescription\b', r'\bdiscount\s+drugs\b', r'\bviagra\b', r'\bcialis\b',
        r'\bvalium\b', r'\bxanax\b', r'\badderall\b', r'\britalin\b', r'\bpercocet\b',
        r'\boxyco(ntin|done)\b', r'\bopioid\b', r'\bsteroids?\b', r'\bhgh\b',
        r'\bhuman\s+growth\s+hormone\b', r'\banabolic\b', r'\bweight\s+loss\s+pills\b'
    ],
    'Fake News': [
        r'\bfake\s+news\b', r'\bconspiracy\b', r'\bhoax\b', r'\bclickbait\b', r'\bpropaganda\b',
        r'\bdisinformation\b', r'\bmisinformation\b', r'\bfact\s+check\b', r'\bdebunked\b',
        r'\bexposed\b', r'\btape\s+they\s+don\'t\s+want\s+you\s+to\s+see\b', r'\bshocking\s+truth\b',
        r'\blying\s+media\b', r'\bmedia\s+cover\s?up\b', r'\b(hillary|obama|trump)\s+exposed\b',
        r'\bcensored\b', r'\btruth\s+they\s+hide\b', r'\balternative\s+facts\b', r'\bfalsified\b'
    ],
    'Hacking': [
        r'\bhack\b', r'\bcrack\b', r'\bwarez\b', r'\bkeygen\b', r'\bserial\b', r'\bpirate\b',
        r'\btorrent\b', r'\bleaked\b', r'\bjailbreak\b', r'\bbypass\b', r'\bnulled\b', r'\bstolen\b',
        r'\bpassword\s+crack', r'\bsecurity\s+bypass\b', r'\bfree\s+download\s+(premium|paid)\b',
        r'\bcyber\s+attack\b', r'\bhacker\b', r'\bbotnets?\b', r'\bmalware\b', r'\brunkit\b',
        r'\bkeylogger\b', r'\bransomware\b', r'\bcybercrime\b', r'\bvulnerabilit(y|ies)\b',
        r'\bexploit\b', r'\bbackdoor\b', r'\bsql\s+injection\b', r'\bdark\s+web\b'
    ],
    'Loans': [
        r'\bpayday\s+loan\b', r'\bquick\s+cash\b', r'\bfast\s+cash\b', r'\beasy\s+money\b',
        r'\bquick\s+loan\b', r'\bcash\s+advance\b', r'\bbad\s+credit\b', r'\bno\s+credit\s+check\b',
        r'\binstant\s+approval\b', r'\bcredit\s+fix\b', r'\bcredit\s+repair\b',
        r'\bcash\s+now\b', r'\bno\s+document\s+loans\b', r'\bno\s+verification\b',
        r'\bapproved\s+in\s+minutes\b', r'\beasy\s+loans\s+online\b', r'\bin\s+debt\b',
        r'\bdebt\s+consolidation\b', r'\bquick\s+approval\b', r'\bno\s+hassle\s+loans\b'
    ],
    'Crypto Scams': [
        r'\bcrypto\b', r'\bbitcoin\b', r'\binvestment\s+scheme\b', r'\bdouble\s+your\s+money\b',
        r'\bguaranteed\s+return\b', r'\b100%\s+profit\b', r'\binvestment\s+opportunity\b',
        r'\bblockchain\b', r'\bico\b', r'\btoken\s+sale\b', r'\bcryptocurrency\b',
        r'\betherium\b', r'\bdoge(coin)?\b', r'\bpassive\s+income\b', r'\bcrypto\s+mining\b',
        r'\bnft\b', r'\btrade\s+crypto\b', r'\bcoin\s+offering\b', r'\bbitcoin\s+profit\b',
        r'\bmining\s+opportunity\b', r'\bcrypto\s+exchange\b', r'\bcrypto\s+investment\b'
    ],
    'General Scams': [
        r'\bmake\s+money\s+fast\b', r'\bget\s+rich\s+quick\b', r'\bwork\s+from\s+home\b',
        r'\bmiracle\b', r'\bsecret\b', r'\bguaranteed\b', r'\bfree\s+money\b', r'\bhidden\b',
        r'\bthey\s+don\'t\s+want\s+you\s+to\s+know\b', r'\bone\s+weird\s+trick\b',
        r'\blose\s+weight\s+fast\b', r'\blife\s+hack\b', r'\binstant\s+results\b',
        r'\bfree\s+trial\b', r'\blimited\s+time\s+offer\b', r'\bexclusive\s+offer\b',
        r'\bact\s+now\b', r'\bonly\s+\$\d+\b', r'\brisk[- ]free\b', r'\bclaim\s+your\b',
        r'\bgiveaway\b', r'\breward\b', r'\bprize\b', r'\byou\'ve\s+been\s+selected\b',
        r'\bwe\s+pay\s+you\b', r'\beach\s+day\b', r'\bin\s+your\s+sleep\b'
    ]
}


def get_all_keywords():
    """Get a flat list of all suspicious keywords."""
    all_keywords = []
    for category, patterns in SUSPICIOUS_KEYWORDS.items():
        all_keywords.extend(patterns)
    return all_keywords


def get_keywords_by_category(category_name):
    """Get keywords for a specific category."""
    return SUSPICIOUS_KEYWORDS.get(category_name, [])


def get_category_names():
    """Get a list of all category names."""
    return list(SUSPICIOUS_KEYWORDS.keys())


def get_category_for_keyword(keyword):
    """Find the category a keyword belongs to."""
    for category, patterns in SUSPICIOUS_KEYWORDS.items():
        if keyword in patterns:
            return category
    return None