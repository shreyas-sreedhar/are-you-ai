"""Local, model-free detection of the tactics fraud relies on.

This exists for two reasons:

1. It runs in microseconds, so it can tell the language model what a keyword
   scan already noticed — which measurably improves the model's precision.
2. When NIM is unreachable, it is the answer. A user looking at a message
   demanding gift cards should get a warning even if the API is down.

Patterns describe *behaviour*, not topic. "Money" is not suspicious. "Money by
a route that cannot be reversed, from someone you were not expecting" is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.verdict import Severity, Signal

# Contribution to the heuristic score, per matched pattern.
_WEIGHTS = {Severity.HIGH: 0.35, Severity.MEDIUM: 0.18, Severity.LOW: 0.08}

# Fraud is a combination, not a keyword. Pressure plus a payment request is
# worth more than the sum of its parts.
_COMBINATION_BONUS = 0.15
_HEURISTIC_CEILING = 0.95


@dataclass(frozen=True)
class Pattern:
    key: str
    label: str
    detail: str
    severity: Severity
    phrases: tuple[str, ...]

    def matcher(self) -> re.Pattern[str]:
        alternatives = "|".join(re.escape(phrase) for phrase in self.phrases)
        # \b on both ends stops "now" matching inside "know".
        return re.compile(rf"\b(?:{alternatives})\b", re.IGNORECASE)


PATTERNS: tuple[Pattern, ...] = (
    Pattern(
        key="irreversible_payment",
        label="Asks to pay in a way you cannot undo",
        detail=(
            "It asks for gift cards, a wire transfer, or cryptocurrency. "
            "Money sent this way can almost never be got back."
        ),
        severity=Severity.HIGH,
        phrases=(
            "gift card", "gift cards", "itunes card", "steam card",
            "google play card", "apple gift", "wire transfer", "western union",
            "moneygram", "bitcoin", "crypto", "cryptocurrency", "usdt",
            "zelle", "cash app", "venmo", "money order",
        ),
    ),
    Pattern(
        key="asks_for_secrets",
        label="Asks for private numbers or codes",
        detail=(
            "It wants a password, a one-time code, or a bank or Social Security "
            "number. No real organisation asks for these in a message."
        ),
        severity=Severity.HIGH,
        phrases=(
            "password", "pin number", "one-time code", "one time code",
            "verification code", "security code", "otp", "cvv",
            "social security number", "ssn", "routing number",
            "account number", "card number", "login details", "credentials",
        ),
    ),
    Pattern(
        key="family_emergency",
        label="Claims a family emergency",
        detail=(
            "It says a relative is in trouble and needs money now. This is one of "
            "the most common scams aimed at grandparents."
        ),
        severity=Severity.HIGH,
        phrases=(
            "grandma", "grandpa", "grandson", "granddaughter",
            "in jail", "arrested", "bail money", "post bail",
            "car accident", "in the hospital", "don't tell mom",
            "dont tell mom", "don't tell anyone", "dont tell anyone",
        ),
    ),
    Pattern(
        key="impersonates_authority",
        label="Claims to be an official organisation",
        detail=(
            "It says it is from a government body, a bank, or a big company. "
            "Look their number up yourself rather than using the one given here."
        ),
        severity=Severity.MEDIUM,
        phrases=(
            "irs", "internal revenue", "social security administration",
            "medicare", "medicaid", "fbi", "sheriff", "federal agent",
            "microsoft support", "apple support", "amazon security",
            "paypal security", "bank of america", "wells fargo", "chase bank",
            "customs", "warrant for your arrest",
        ),
    ),
    Pattern(
        key="manufactured_urgency",
        label="Pushes you to act fast",
        detail=(
            "It says you must act immediately. Urgency is there to stop you "
            "checking, and real matters can wait."
        ),
        severity=Severity.MEDIUM,
        phrases=(
            "act now", "immediately", "right away", "within 24 hours",
            "final notice", "last chance", "expires today", "expiring soon",
            "urgent", "urgently", "as soon as possible", "before it is too late",
            "before it's too late", "do not delay",
        ),
    ),
    Pattern(
        key="fear",
        label="Tries to frighten you",
        detail=(
            "It threatens arrest, a lawsuit, or losing access to an account. "
            "Frightened people stop thinking clearly, which is the point."
        ),
        severity=Severity.MEDIUM,
        phrases=(
            "lawsuit", "legal action", "suspended", "deactivated",
            "frozen", "locked out", "unauthorized access", "unusual activity",
            "security breach", "your account has been", "deported",
            "you will be arrested", "criminal charges",
        ),
    ),
    Pattern(
        key="unearned_prize",
        label="Offers a prize you never entered for",
        detail=(
            "It says you have won something. Real prizes do not arrive by "
            "surprise message, and never ask for a fee."
        ),
        severity=Severity.MEDIUM,
        phrases=(
            "you won", "you have won", "congratulations", "winner",
            "lottery", "sweepstakes", "claim your prize", "claim your reward",
            "free gift", "you have been selected", "inheritance",
            "beneficiary", "unclaimed funds",
        ),
    ),
    Pattern(
        key="too_good_to_be_true",
        label="Promises money that is not realistic",
        detail=(
            "It promises large, certain returns. No genuine investment can "
            "guarantee a profit."
        ),
        severity=Severity.MEDIUM,
        phrases=(
            "guaranteed return", "guaranteed profit", "risk free",
            "risk-free", "double your money", "triple your money",
            "insider tip", "get rich", "financial freedom",
        ),
    ),
    Pattern(
        key="disguised_link",
        label="Uses a disguised web link",
        detail=(
            "The link hides where it really goes. Type addresses in yourself "
            "instead of tapping links in messages."
        ),
        severity=Severity.MEDIUM,
        phrases=(
            "bit.ly", "tinyurl", "goo.gl", "rebrand.ly", "cutt.ly",
            "is.gd", "t.ly", "shorturl", "tiny.cc",
        ),
    ),
    Pattern(
        key="unexpected_affection",
        label="Very affectionate for a stranger",
        detail=(
            "Strong affection early on is how romance scams begin. They are "
            "patient, and the money request comes later."
        ),
        severity=Severity.LOW,
        phrases=(
            "my love", "my dearest", "my darling", "soulmate", "soul mate",
            "destined to be", "i love you so much",
        ),
    ),
)

_COMPILED = tuple((pattern, pattern.matcher()) for pattern in PATTERNS)

_MONEY_KEYS = {"irreversible_payment", "asks_for_secrets", "too_good_to_be_true"}
_PRESSURE_KEYS = {"manufactured_urgency", "fear", "family_emergency"}


def _normalise(text: str) -> str:
    """Fold the curly apostrophes phones insert, so "don't" matches "don’t"."""
    return text.replace("’", "'").replace("‘", "'")


@dataclass(frozen=True)
class ScanResult:
    signals: list[Signal]
    score: float
    matched_keys: frozenset[str]

    @property
    def summary_for_prompt(self) -> str:
        """A one-line brief for the model, or an explicit 'nothing'."""
        if not self.signals:
            return "nothing"
        return "; ".join(signal.label.lower() for signal in self.signals)


def scan(text: str) -> ScanResult:
    """Run every pattern over the text and score what matched."""
    if not text or not text.strip():
        return ScanResult(signals=[], score=0.0, matched_keys=frozenset())

    haystack = _normalise(text)
    signals: list[Signal] = []
    matched: set[str] = set()
    score = 0.0

    for pattern, matcher in _COMPILED:
        if not matcher.search(haystack):
            continue
        matched.add(pattern.key)
        score += _WEIGHTS[pattern.severity]
        signals.append(
            Signal(label=pattern.label, detail=pattern.detail, severity=pattern.severity)
        )

    if matched & _MONEY_KEYS and matched & _PRESSURE_KEYS:
        score += _COMBINATION_BONUS

    return ScanResult(
        signals=signals,
        score=min(score, _HEURISTIC_CEILING),
        matched_keys=frozenset(matched),
    )
