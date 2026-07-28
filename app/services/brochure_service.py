import logging
import os
from pathlib import Path

import resend
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BROCHURE_PATH = Path(__file__).resolve().parent.parent / "assets" / "royale-isles-lanka-private-brochure.pdf"
FROM_ADDRESS = os.getenv("BROCHURE_FROM_EMAIL", "Royale Isles Lanka <onboarding@resend.dev>")


class BrochureNotConfiguredError(Exception):
    pass


class BrochureSendError(Exception):
    pass


def _build_brochure_email_html() -> str:
    return """
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0d1f17;padding:40px 0;font-family:Georgia,'Times New Roman',serif;">
      <tr>
        <td align="center">
          <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="background:#fbf9f5;">
            <tr>
              <td style="padding:48px 48px 32px;text-align:center;border-bottom:1px solid rgba(197,160,89,0.35);">
                <p style="margin:0;font-family:Arial,sans-serif;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#c5a059;">
                  Royale Isles Lanka
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:44px 48px 8px;">
                <p style="margin:0 0 12px;font-family:Arial,sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#c5a059;">
                  Private Sri Lanka Briefing
                </p>
                <h1 style="margin:0 0 24px;font-size:30px;font-weight:400;line-height:1.25;color:#1a1a1a;">
                  Your private brochure has arrived.
                </h1>
                <p style="margin:0 0 20px;font-family:Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4a4a;">
                  Thank you for your interest in Sri Lanka, held privately. Attached is a considered introduction for
                  private families, principals, and thoughtful travellers: quiet residences, trusted hosts, protected
                  timing, and private moments arranged with discretion rather than display.
                </p>
                <p style="margin:0 0 32px;font-family:Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4a4a;">
                  This briefing was sent to you directly, without an automated itinerary or mailing-list noise. If
                  anything here draws you further, simply reply to this email and we will begin a personal conversation.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:0 48px 48px;">
                <p style="margin:0;font-family:Arial,sans-serif;font-size:12px;line-height:1.7;color:#8a8a8a;">
                  With discretion,<br />The Royale Isles Lanka Private Office
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:24px 48px;background:#0d1f17;text-align:center;">
                <p style="margin:0;font-family:Arial,sans-serif;font-size:10px;letter-spacing:1px;color:rgba(251,249,245,0.5);">
                  © Royale Isles Lanka · Sent privately in response to your request
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>"""


def send_brochure_email(email: str) -> None:
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise BrochureNotConfiguredError("RESEND_API_KEY is not configured")

    resend.api_key = api_key

    if not BROCHURE_PATH.exists():
        raise BrochureNotConfiguredError(f"Brochure PDF not found at {BROCHURE_PATH}")

    with open(BROCHURE_PATH, "rb") as brochure_file:
        pdf_bytes = list(brochure_file.read())

    try:
        response = resend.Emails.send(
            {
                "from": FROM_ADDRESS,
                "to": email,
                "subject": "Your Private Sri Lanka Briefing — Royale Isles Lanka",
                "html": _build_brochure_email_html(),
                "attachments": [
                    {
                        "filename": "Royale-Isles-Lanka-Private-Brochure.pdf",
                        "content": pdf_bytes,
                    }
                ],
            }
        )
    except Exception as exc:
        logger.error("Resend send failed for %s: %s", email, exc)
        raise BrochureSendError(str(exc)) from exc

    if not response or not response.get("id"):
        logger.error("Resend returned no email id for %s: %r", email, response)
        raise BrochureSendError("Resend did not return a confirmed email id")
