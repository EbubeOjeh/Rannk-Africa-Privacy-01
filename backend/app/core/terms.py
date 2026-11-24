"""Terms & Conditions copy (PRS §18) — surfaced at registration/submission and
recorded on active acceptance for legal cover.
"""
from __future__ import annotations

from app.models.terms_acceptance import CURRENT_TERMS_VERSION

TERMS_CONFIRMATION = (
    "By submitting this application, you confirm that all information provided is "
    "true and accurate. Providing false, misleading, or fraudulent information may "
    "result in profile removal, disqualification from rankings, suspension of your "
    "account, and, where applicable, legal action or recovery of investigation costs."
)

TERMS_CLAUSES: list[str] = [
    "Rank Africa provides visibility and recognition but does not guarantee "
    "employment, internships, scholarships, admissions, funding, or any other opportunity.",
    "Rankings are generated using the Rank Africa AI Scoring Framework and verified "
    "information provided by users.",
    "Rankings reflect registered and verified participants on the platform and are "
    "not official national rankings of every student in Nigeria.",
    "Rank Africa reserves the right to verify submitted information and update "
    "rankings following verification.",
    "Employers are independently vetted before being granted access to student "
    "profiles; however, Rank Africa is not responsible for employers' hiring "
    "decisions or employment outcomes.",
    # No Guarantee of Opportunities.
    "No Guarantee of Opportunities: the Platform is designed to increase visibility "
    "and connect users with potential opportunities, but does not guarantee "
    "employment, contracts, funding, partnerships, interviews, admissions, or any "
    "specific outcome. All opportunities are awarded solely at the discretion of "
    "third parties.",
    # Third-Party Interactions and Personal Safety.
    "Third-Party Interactions and Personal Safety: the Platform serves solely as a "
    "medium for connecting students with organizations and opportunities. We are not "
    "responsible for the actions, omissions, conduct, safety, or decisions of any "
    "student, recruiter, organization, employer, sponsor, or other third party. Users "
    "participate in interviews, meetings, internships, employment, training, events, "
    "travel, and other activities at their own discretion and risk. To the fullest "
    "extent permitted by applicable law, the Platform shall not be liable for any "
    "injury, loss, damage, theft, accident, illness, death, or other harm arising "
    "from or related to such activities or third-party interactions.",
    "No Endorsement: listing an organization or opportunity does not mean the "
    "Platform endorses, guarantees, or verifies it.",
    "User Due Diligence: users are responsible for verifying the legitimacy of "
    "opportunities and for exercising reasonable caution before participating.",
    "Third-Party Content: the Platform is not responsible for the accuracy of "
    "information provided by recruiters, organizations, or other users.",
    "Accuracy of Your Information: you are responsible for the accuracy of the "
    "information you provide, and recruiters/organizations are responsible for their "
    "own recruitment decisions.",
    # Right to Modify or Discontinue the Service.
    "Right to Modify or Discontinue the Service: we reserve the right to modify, "
    "suspend, or discontinue the Platform or any feature at any time, with or without "
    "notice. To the fullest extent permitted by law, we are not liable for any loss, "
    "damages, or claims resulting from such changes or discontinuation.",
    "Suspension and Removal: the Platform may suspend or remove any user or "
    "organization that violates these Terms or our policies.",
    "Limitation of Liability: to the fullest extent permitted by law, the Platform's "
    "total liability for any claim arising out of or relating to the service is "
    "limited, and the Platform is not liable for any indirect, incidental, special, "
    "or consequential damages.",
    "Indemnification: you agree to indemnify and hold harmless the Platform and its "
    "team from any claims, damages, or expenses arising out of your use of the "
    "Platform, your interactions with third parties, or your breach of these Terms.",
    "Force Majeure: the Platform is not liable for delays or interruptions caused by "
    "events beyond its reasonable control (e.g., internet outages, natural disasters, "
    "government actions, or cyberattacks).",
    "Governing Law and Dispute Resolution: these Terms are governed by the laws of "
    "the Federal Republic of Nigeria, and any disputes shall be resolved in "
    "accordance with those laws.",
]


def terms_info() -> dict:
    return {
        "version": CURRENT_TERMS_VERSION,
        "confirmation": TERMS_CONFIRMATION,
        "clauses": TERMS_CLAUSES,
    }
