import aiohttp
from fastapi import HTTPException, status
from app.core.config import settings


async def send_activation_email(email: str, token: str):
    activation_link = f"{settings.BASE_URL}/activate?token={token}"

    mailgun_url = f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages"
    auth = aiohttp.BasicAuth("api", settings.MAILGUN_API_KEY)

    data = aiohttp.FormData()
    data.add_field("from", f"Online Cinema <mailgun@{settings.MAILGUN_DOMAIN}>")
    data.add_field("to", email)
    data.add_field("subject", "Account Activation")
    data.add_field(
        "html",
        f"""
        <html>
            <body>
                <h1>Welcome to Online Cinema!</h1>
                <p>Please follow the link to activate your account:</p>
                <a href="{activation_link}">Activate your account</a>
                <p>This link is valid for 24 hours.</p>
            </body>
        </html>
        """
    )

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(mailgun_url, auth=auth, data=data) as response:
                if response.status not in (200, 201):
                    response_text = await response.text()
                    print(f"Mailgun error: {response.status} - {response_text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to send activation email. Please try again later."
                    )
                print(f"Activation email sent successfully to {email}")
        except aiohttp.ClientError as e:
            print(f"Mailgun connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Connection to email service failed."
            )
