"""Disposable email addresses for test data.

VERIFIED 2026-07-16: the real Fridai backend runs strict email validation
(the `POST /crm/customers` call behind Create Order) that rejects `.local`
(and, per RFC 2606, likely `.test`/`.example`/`.invalid`/`.localhost` too)
as reserved special-use domains — confirmed via a live 422 response:
"value is not a valid email address: The part after the @-sign is a
special-use or reserved name that cannot be used with email." A normal,
non-reserved-looking commercial domain is accepted instead.

Use `disposable_email()` for any customer/user email a test creates via a
real form submission. Don't use `.local`/`.test`/etc. domains anywhere
data actually gets validated server-side.
"""

from __future__ import annotations

DISPOSABLE_EMAIL_DOMAIN = "friday-automation-test.com"


def disposable_email(local_part: str) -> str:
    return f"{local_part}@{DISPOSABLE_EMAIL_DOMAIN}"
