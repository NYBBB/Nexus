import imaplib
import email
from email.header import decode_header
import datetime
import sys
import os
import re

# Add Config Utils
try:
    from config_utils import load_config
except ImportError:
    import config_utils
    load_config = config_utils.load_config

# Set recursion limit higher just in case
sys.setrecursionlimit(2000)

# Gmail IMAP settings
IMAP_SERVER = "imap.gmail.com"
# DEFAULT_USER removed. Must be in config.

def clean_text(text):
    if not text:
        return ""
    # Replace common non-GBK characters if system encoding is strictly GBK
    # But better: just filter to printable or ignore errors during print
    return text.encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding)

def get_email_summary(password=None, user=None):
    if not password:
        cfg = load_config()
        password = cfg.get("gmail_token")
        if not user:
            user = cfg.get("gmail_user") # Must be set in config
            
    if not password:
        return "Error: No Gmail App Password provided in config (gmail_token). Please run nexus_config key=gmail_token value=..."
    
    if not user:
         return "Error: No Gmail User provided in config (gmail_user). Please run nexus_config key=gmail_user value=..."

    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(user, password)
        mail.select("inbox")

        # Calculate date for "since yesterday"
        date_since = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%b-%Y")
        
        status, messages = mail.search(None, f'(SINCE "{date_since}")')
        
        if status != "OK":
            return "No emails found."

        email_ids = messages[0].split()
        latest_email_ids = email_ids[-20:]
        
        summary_list = []
        
        for e_id in reversed(latest_email_ids):
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                    
                    from_hdr, encoding = decode_header(msg["From"])[0]
                    if isinstance(from_hdr, bytes):
                        from_hdr = from_hdr.decode(encoding if encoding else "utf-8", errors="ignore")

                    # Add to list (clean it later or during print)
                    summary_list.append(f"- From: {from_hdr} | Subject: {subject}")

        mail.close()
        mail.logout()

        if not summary_list:
            return "No recent emails found in Gmail inbox."
            
        output = "## Recent Emails (Gmail & Forwarded)\n" + "\n".join(summary_list)
        return clean_text(output)

    except Exception as e:
        return f"Error checking email: {e}"

if __name__ == "__main__":
    pwd = None
    if len(sys.argv) > 1:
        pwd = sys.argv[1]
        
    # Direct print, clean_text handles encoding safety
    print(get_email_summary(pwd))
