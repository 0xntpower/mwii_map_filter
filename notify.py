from win10toast import ToastNotifier
import smtpd

def send_email_notification(recipient: str, subject: str, body: str):
    """
    Send an email notification with the given subject and body to the recipient.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    sender_email = "dev@nort721.com"
    sender_password = "your_password"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_windows_notification(message: str):
    """
    Send a desktop notification with the given message.
    Works on Windows using Toast notifications.
    """
    try:
        toaster = ToastNotifier()
        toaster.show_toast("Notification", message, duration=10)
    except ImportError:
        print("win10toast module not found. Please install it to receive notifications.")