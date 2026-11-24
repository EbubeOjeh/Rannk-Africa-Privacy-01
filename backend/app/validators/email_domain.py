"""Email-domain rules for school self-registration.

Schools must register with an institutional email (e.g. ``@student.babcock.edu.ng``)
not a personal/free-mail address (Gmail, Yahoo, Outlook, etc.). The boss's
guidance:

    "they should register with the school domain email not personal email,
    like @gmail or yahoo."

We enforce this by blocklisting common free-mail providers and exposing
``extract_apex_domain`` so the API can normalise sub-domains
(``student.babcock.edu.ng`` -> ``babcock.edu.ng``) for duplicate detection.
"""
from __future__ import annotations

# Common free / personal email providers. Anyone signing up as a school
# admin with one of these is rejected with a clear message.
FREE_EMAIL_DOMAINS: frozenset[str] = frozenset(
    {
        "gmail.com", "googlemail.com",
        "yahoo.com", "yahoo.co.uk", "yahoo.com.ng", "ymail.com", "rocketmail.com",
        "hotmail.com", "hotmail.co.uk", "outlook.com", "outlook.co.uk",
        "live.com", "msn.com",
        "icloud.com", "me.com", "mac.com",
        "aol.com",
        "proton.me", "protonmail.com", "pm.me",
        "zoho.com", "mail.com", "gmx.com", "gmx.net",
        "yandex.com", "yandex.ru",
        "inbox.com", "fastmail.com", "tutanota.com", "rediff.com",
        "hey.com", "duck.com", "tuta.io",
    }
)

# Sub-domain prefixes we strip off when computing the apex (registrable) domain.
_KNOWN_SUB_PREFIXES = {"student", "students", "mail", "alumni", "staff", "www", "email"}


def extract_domain(email: str) -> str:
    """Return the raw domain part of an email (lower-cased), or '' if invalid."""
    if not email or "@" not in email:
        return ""
    return email.rsplit("@", 1)[1].strip().lower()


def extract_apex_domain(email: str) -> str:
    """Normalise to the apex registrable domain.

    ``student.babcock.edu.ng`` -> ``babcock.edu.ng``
    ``admin@ui.edu.ng``        -> ``ui.edu.ng``
    ``staff.unilag.edu.ng``    -> ``unilag.edu.ng``
    """
    domain = extract_domain(email)
    if not domain:
        return ""
    parts = domain.split(".")
    while parts and parts[0] in _KNOWN_SUB_PREFIXES:
        parts.pop(0)
    return ".".join(parts)


def is_free_email(email: str) -> bool:
    return extract_apex_domain(email) in FREE_EMAIL_DOMAINS


def looks_institutional(email: str) -> bool:
    """Heuristic check that the email belongs to an academic / .edu / .org / .gov host.

    We're deliberately lenient — the only hard rule is "not a free provider".
    The Super Admin sees every pending registration and is the final gate.
    """
    if is_free_email(email):
        return False
    apex = extract_apex_domain(email)
    if not apex or "." not in apex:
        return False
    # Most Nigerian institutions use *.edu.ng or *.ac.ng / *.gov.ng.
    # We don't enforce this strictly — private bootcamps etc. may use .com.
    return True
