from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

app = Flask(__name__)

@app.route('/send-email', methods=['POST'])
def send_email():
    sender_email = request.headers.get('email-id')
    sender_password = request.headers.get('email-password')
    recipient_email = request.headers.get('recipient-email')

    if not sender_email or not sender_password or not recipient_email:
        return jsonify({"error": "Missing headers: email-id, email-password, recipient-email"}), 400

    data = request.get_json()
    subject = data.get('subject')
    body = data.get('body')

    if not subject or not body:
        return jsonify({"error": "Missing body fields: subject, body"}), 400

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return jsonify({"message": "Email sent successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Only for Vercel – ignore during local run
def handler(request, context):
    return app(request, context)


# ✅ This part runs the API server locally
if __name__ == '__main__':
    app.run(debug=True)
