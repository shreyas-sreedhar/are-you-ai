"""Every sentence an older adult reads, in one file.

Copy rules for this file, applied to every string below:

  * Short sentences. One idea each.
  * Plain words: "money", not "financial assets"; "made by a computer", not
    "synthetically generated".
  * Never blame the reader. "This looks like a scam", not "you almost fell
    for a scam".
  * Advice is a concrete next action, not a feeling.
  * No jargon, no emoji, no exclamation marks. Urgency is the scammer's tool,
    not ours.

Keeping the copy here — rather than scattered through analysers and UI —
means it can be reviewed, translated, or read aloud as one body of text.
"""

from __future__ import annotations

from .verdict import CheckKind, Risk

# (headline, summary) per kind and risk level.
_HEADLINES: dict[CheckKind, dict[Risk, tuple[str, str]]] = {
    CheckKind.VIDEO: {
        Risk.SAFE: (
            "This looks like a real video",
            "We did not find signs that a computer made this footage.",
        ),
        Risk.CAUTION: (
            "Some parts of this video look odd",
            "A few things here do not move the way real footage does. "
            "It may still be genuine, so take a closer look before you believe it.",
        ),
        Risk.DANGER: (
            "This video was probably made by AI",
            "Several things in this footage could not happen in real life. "
            "Treat what it shows as unproven.",
        ),
    },
    CheckKind.MESSAGE: {
        Risk.SAFE: (
            "Nothing alarming in this message",
            "This message does not use the tricks that scammers usually use.",
        ),
        Risk.CAUTION: (
            "Be careful with this message",
            "This message uses some of the pressure tactics scammers rely on. "
            "There is no rush — you can check before you answer.",
        ),
        Risk.DANGER: (
            "This looks like a scam",
            "This message behaves the way fraud does: it wants money, secrets, "
            "or a fast decision. Please do not reply.",
        ),
    },
    CheckKind.ARTICLE: {
        Risk.SAFE: (
            "No clear signs of false information",
            "The claims here line up with what is generally known.",
        ),
        Risk.CAUTION: (
            "Some claims here need checking",
            "Parts of this story could not be confirmed. Look for the same "
            "story somewhere you already trust before sharing it.",
        ),
        Risk.DANGER: (
            "This story does not hold up",
            "The main claims here conflict with what is known. "
            "Please do not pass it on.",
        ),
    },
}

_ADVICE: dict[CheckKind, dict[Risk, list[str]]] = {
    CheckKind.VIDEO: {
        Risk.SAFE: [
            "Nothing to do. You can keep watching.",
        ],
        Risk.CAUTION: [
            "Watch it once more before you believe it.",
            "See whether a news source you already trust is showing the same thing.",
            "Do not send it on to friends or family yet.",
        ],
        Risk.DANGER: [
            "Do not share this video with anyone.",
            "If it asks for money, an investment, or your details, stop and talk to someone you trust.",
            "Look for the same story on a news source you already use.",
        ],
    },
    CheckKind.MESSAGE: {
        Risk.SAFE: [
            "Nothing to do. This message looks ordinary.",
        ],
        Risk.CAUTION: [
            "Take your time. A real request can wait an hour.",
            "Look up the company's phone number yourself instead of using the one in the message.",
            "Ask someone you trust to read it with you.",
        ],
        Risk.DANGER: [
            "Do not reply, and do not send money, gift cards, or bank details.",
            "Do not open any link in the message.",
            "If it claims to be someone you know, phone them on the number you already have for them.",
            "Show this message to a family member or friend before you do anything.",
            "You can report it at reportfraud.ftc.gov.",
        ],
    },
    CheckKind.ARTICLE: {
        Risk.SAFE: [
            "Nothing to do. Nothing here looks made up.",
        ],
        Risk.CAUTION: [
            "Search for the main claim to see who else is reporting it.",
            "Check the date. Old stories are often shared as if they were new.",
            "Hold off on sharing until you have found a second source.",
        ],
        Risk.DANGER: [
            "Do not share this article.",
            "Check the main claim on a news source you already trust.",
            "If it is asking you to act — to buy, donate, or vote a certain way — be extra careful.",
        ],
    },
}

# Shown when the AI service could not be reached and RUAI fell back to the
# local keyword checks. Honesty about degraded answers is part of the product.
DEGRADED_NOTE = (
    "RUAI could not reach its AI service, so this is a quick local check only. "
    "Treat it as a rough guide."
)

# Shown on first run, in the popup, above everything else.
WELCOME = (
    "RUAI checks whether what you are looking at is real. "
    "Open a video or a message and it will tell you in plain words."
)


def headline_for(kind: CheckKind, risk: Risk) -> tuple[str, str]:
    """The headline and summary for a verdict."""
    return _HEADLINES[kind][risk]


def advice_for(kind: CheckKind, risk: Risk) -> list[str]:
    """What the reader should actually do next."""
    return list(_ADVICE[kind][risk])
