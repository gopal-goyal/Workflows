import smtplib
import ssl
import certifi
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def send_email(to_address: str, subject: str, body: str, attachment_path: str = None):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    # Add body
    msg.attach(MIMEText(body, "plain"))

    # Add attachment if provided
    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=attachment_path.split("/")[-1])
        part["Content-Disposition"] = f'attachment; filename="{attachment_path.split("/")[-1]}"'
        msg.attach(part)

    # Send email
    context = ssl.create_default_context(cafile=certifi.where())
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_address, msg.as_string())

    print(f"✅ Email with attachment sent to {to_address}")


if __name__ == "__main__":
    send_email(
        "goyal11.gopal@gmail.com",
        "Application for AI Engineer Role at Rellins",
        "Dear HR,\n\nPlease find attached my resume for your consideration.\n\nBest regards,\nGopal Goyal",
        attachment_path="examples/Gopal_Goyal_Resume_30_08_737.pdf"
    )