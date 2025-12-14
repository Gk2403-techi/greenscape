from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# This is a mock of the full app.
# In a real app, you would have more routes and logic.
app = Flask(__name__)

# Dummy route for rendering the template
@app.route('/')
def index():
    return render_template('index.html', result=None, bulk_plans=None)

@app.route('/schedule', methods=['POST'])
def schedule_appointment():
    """
    Handles the consultation schedule form submission and sends an email notification.
    """
    try:
        # --- 1. Get form data ---
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date = request.form.get('date')
        message = request.form.get('message', 'No message provided.')

        # --- 2. Set up email credentials and server ---
        # IMPORTANT: For security, use environment variables to store your email and password.
        # You will provide these values manually in your environment.
        smtp_server = "smtp.gmail.com"  # Example for Gmail. Change for other providers.
        smtp_port = 587                 # For TLS encryption
        sender_email = os.environ.get("krishnangopi353@gmail.com") # Your email address
        sender_password = os.environ.get("zvpx dfpa ppbd uifm") # Your email/app password

        # The email address where you want to receive notifications.
        recipient_email = "your_admin_email@example.com"

        if not sender_email or not sender_password:
            print("ERROR: Email credentials are not set in environment variables.")
            return jsonify({"message": "Server configuration error. Could not send message."}), 500

        # --- 3. Create the email message ---
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"New GreenScape Consultation Request from {name}"

        body = f"""
        You have received a new consultation request:

        Name: {name}
        Email: {email}
        Phone: {phone}
        Preferred Date: {date}

        Message:
        {message}
        """
        msg.attach(MIMEText(body, 'plain'))

        # --- 4. Send the email ---
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection. [1]
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return jsonify({"message": "Thank you! Your consultation request has been sent."}), 200

    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error. Check credentials or app-specific password settings.")
        return jsonify({"message": "Could not send email due to an authentication failure."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": "An error occurred. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)