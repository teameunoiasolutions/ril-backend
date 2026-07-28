import logging
import os

import resend
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

FROM_ADDRESS = os.getenv("BROCHURE_FROM_EMAIL", "Royale Isles Lanka <onboarding@resend.dev>")


class PasswordResetNotConfiguredError(Exception):
    pass


class PasswordResetSendError(Exception):
    pass


def _build_reset_email_html(reset_url: str) -> str:
    return f"""
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
                  Traveller Access
                </p>
                <h1 style="margin:0 0 24px;font-size:28px;font-weight:400;line-height:1.25;color:#1a1a1a;">
                  Reset your password
                </h1>
                <p style="margin:0 0 24px;font-family:Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4a4a;">
                  We received a request to reset the password for your Royale Isles Lanka traveller
                  account. Use the button below to choose a new one. This link expires in 30 minutes.
                </p>
                <p style="margin:0 0 32px;">
                  <a href="{reset_url}" style="display:inline-block;padding:14px 28px;background:#004225;color:#fbf9f5;font-family:Arial,sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;text-decoration:none;">
                    Choose a New Password
                  </a>
                </p>
                <p style="margin:0 0 32px;font-family:Arial,sans-serif;font-size:13px;line-height:1.7;color:#8a8a8a;">
                  If you did not request this, you can safely ignore this email — your password will
                  not change.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:24px 48px;background:#0d1f17;text-align:center;">
                <p style="margin:0;font-family:Arial,sans-serif;font-size:10px;letter-spacing:1px;color:rgba(251,249,245,0.5);">
                  © Royale Isles Lanka · Traveller Private Office
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>"""


def send_password_reset_email(email: str, reset_url: str) -> None:
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise PasswordResetNotConfiguredError("RESEND_API_KEY is not configured")

    resend.api_key = api_key

    try:
        response = resend.Emails.send(
            {
                "from": FROM_ADDRESS,
                "to": email,
                "subject": "Reset your password — Royale Isles Lanka",
                "html": _build_reset_email_html(reset_url),
            }
        )
    except Exception as exc:
        logger.error("Resend reset send failed for %s: %s", email, exc)
        raise PasswordResetSendError(str(exc)) from exc

    if not response or not response.get("id"):
        logger.error("Resend returned no email id for reset to %s: %r", email, response)
        raise PasswordResetSendError("Resend did not return a confirmed email id")
