from send_email import send_report
from generate_report import generate_summary

summary = generate_summary()

send_report(
    "keerthiyat@g3cyberspace.com",
    "SharePoint Summary Report (Test)",
    summary
)
