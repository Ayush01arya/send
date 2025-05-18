from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

@app.route('/api/send-email', methods=['POST'])
def send_email():
    # Get authentication details from headers
    email = request.headers.get('X-Email')
    app_password = request.headers.get('X-App-Password')
    
    # Check if authentication details are provided
    if not email or not app_password:
        return jsonify({"error": "Missing authentication details in headers"}), 401
    
    # Get email details from JSON body
    data = request.get_json()
    
    # Validate JSON payload
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Extract email information from JSON
    sender_email = data.get('sender_email')
    recipients = data.get('recipients')
    subject = data.get('subject')
    body = data.get('body')
    
    # Validate required fields
    if not sender_email or not recipients or not subject or not body:
        return jsonify({
            "error": "Missing required fields",
            "required_fields": ["sender_email", "recipients", "subject", "body"]
        }), 400
    
    # Convert single recipient to list if needed
    if isinstance(recipients, str):
        recipients = [recipients]
    
    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ', '.join(recipients)
        message['Subject'] = subject
        
        # Attach body text
        message.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server (Gmail example)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable TLS encryption
            server.login(email, app_password)
            server.send_message(message)
        
        return jsonify({"success": True, "message": "Email sent successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
