from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

app = Flask(__name__)

# HTML Email Template
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application for {specific_role} Role at {company_name}</title>
    <style>
        /* General Reset */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            padding: 20px;
        }}
        .email-container {{
            max-width: 650px;
            margin: auto;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            border: 1px solid #e0e0e0;
        }}

        /* Header */
        .header {{
            background:  linear-gradient(135deg, #9b59b6, #e84393);
            color: #ffffff;
            padding: 30px;
            text-align: center;
            background-image: url('https://ayusharya.me/assets/header.png');
           background-size: cover;
           background-repeat: no-repeat;
           background-position: center;
           padding: 30px;
           text-align: center;

        }}
        .header h1 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .header p {{
            font-size: 16px;
            margin-top: 5px;
        }}
        /* Content */
        .content {{
            padding: 25px 30px;
            font-size: 16px;
            line-height: 1.6;
            color: #555;
        }}
        .content p {{
            margin: 15px 0;
        }}
        .highlight {{
            color: #9b59b6;
            font-weight: 600;
        }}
        .cta-button {{
            display: inline-block;
            padding: 12px 24px;
            margin-top: 20px;
            background-color: #3498db; /* Solid background for desktop */
            color: #ffffff;
            text-decoration: none;
            font-weight: 600;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }}
        .cta-button:hover {{
            background-color: #2980b9; /* Darker shade on hover for desktop */
        }}

        /* Responsive styles */
        @media (max-width: 600px) {{
            .cta-button {{
                background-color: #e84393; /* Different color for mobile */
                padding: 10px 18px;
                font-size: 15px;
                }}
            .cta-button:hover {{
                background-color: #d6336c; /* Darker shade on hover for mobile */}}
                }}


        /* Footer */
        .footer {{
            background-color: #e7e7e7;
            padding: 20px;
            text-align: center;
            font-size: 14px;
            color: #333;
            border-top: 1px solid #e0e0e0;
        }}
        .footer a {{
            color: black;
            text-decoration: none;
            font-weight: 500;
            margin: 0 10px;
        }}
        .footer .icon {{
            margin: 0 5px;
            vertical-align: middle;
        }}
        .footer img {{
            width: 20px; /* Size of the icons */
            height: 20px;
            vertical-align: middle;
            margin-right: 5px;
        }}

        /* Media Queries for Mobile */
        @media (max-width: 600px) {{
            .content {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 20px;
            }}
            .cta-button {{
                padding: 10px 18px;
                font-size: 15px;
            }}
            .footer {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header Section -->
        <div class="header">
            <h1>Application for Entry-Level {specific_role} Role at {company_name}</h1>
            <p>An Enthusiastic Candidate Ready to Make an Impact</p>
        </div>

        <!-- Content Section -->                       
     <div class="content">
    <p>Dear <span class="highlight">{hr_name}</span>,</p>

     <p>I hope you're doing well. My name is Ayush Arya, and I am a passionate Software Developer with expertise in Python, Machine Learning, and full-stack development. With experience at Astroverse Pvt Ltd and IIT BHU, I have built AI-driven solutions, optimized data pipelines, and developed user-friendly interfaces to enhance efficiency.</p>

        <p>Attached is my resume, detailing my skills in React, Django, Flask, cloud computing (AWS, Azure), and DevOps. Notably, I improved chatbot accuracy using prompt engineering and enhanced UI accessibility for research tools. I am eager to bring my problem-solving mindset and technical expertise to <span class="highlight">{company_name}</span></p>

        <p>I would be grateful for the opportunity to discuss how I can contribute to your team. Please find my resume attached for your review.</p>

        <p>Thank you for considering my application. I look forward to the possibility of contributing to your team.</p>
        <p>Warm regards,<br>
        Ayush Arya<br>
        </div>

        <!-- Footer Section -->
        <div class="footer">
            <p>
                <a href="https://ayusharya.me">
                    <img src="https://img.icons8.com/ios-filled/50/domain.png" class="icon" alt="Website">Website
                </a> |
                <a href="https://github.com/Ayush01arya">
                    <img src="https://img.icons8.com/ios-filled/50/000000/github.png" class="icon" alt="Phone">Ayush01arya
                </a> |
                <a href="https://linkedin.com/in/ayusharya25">
                    <img src="https://img.icons8.com/ios-filled/50/000000/linkedin.png" class="icon" alt="LinkedIn">LinkedIn
                </a> |
                <a href="https://ayusharya.me/assets/resume.pdf">
                    <img src="https://img.icons8.com/ios-filled/50/resume.png" class="icon" alt="Resume">Resume
                </a> 
            </p>
        </div>
    </div>
</body>
</html>
"""

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
    html_body = data.get('html_body')  # Custom HTML body if template is not used
    
    # Template variables for job application email
    company_name = data.get('company_name', 'Your Company')
    specific_role = data.get('specific_role', 'Software Developer')
    hr_name = data.get('hr_name', 'Hiring Manager')
    
    # Path to resume attachment file (if provided)
    resume_path = data.get('resume_path')
    
    # Validate required fields
    if not sender_email or not recipients or not subject:
        return jsonify({
            "error": "Missing required fields",
            "required_fields": ["sender_email", "recipients", "subject"]
        }), 400
    
    # Convert single recipient to list if needed
    if isinstance(recipients, str):
        recipients = [recipients]
    
    try:
        # Create message
        message = MIMEMultipart('alternative')
        message['From'] = sender_email
        message['To'] = ', '.join(recipients)
        message['Subject'] = subject
        
        # Attach plain text version if available
        if body:
            message.attach(MIMEText(body, 'plain'))
        
        # If custom HTML is provided, use that. Otherwise, use the template
        if html_body:
            message.attach(MIMEText(html_body, 'html'))
        else:
            # Format the template with provided variables
            formatted_html = EMAIL_TEMPLATE.format(
                company_name=company_name,
                specific_role=specific_role,
                hr_name=hr_name
            )
            message.attach(MIMEText(formatted_html, 'html'))
        
        # Attach resume if path is provided
        if resume_path and os.path.exists(resume_path):
            with open(resume_path, 'rb') as f:
                resume_attachment = MIMEApplication(f.read(), _subtype="pdf")
                resume_attachment.add_header('Content-Disposition', 'attachment', filename="resume.pdf")
                message.attach(resume_attachment)
        
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
