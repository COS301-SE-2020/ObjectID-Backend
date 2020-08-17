import email_to
import secrets as secrets
import smtplib
import os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send(address,type):
    server = email_to.EmailServer('smtp.gmail.com', 587, 'ctrl.intelligence@gmail.com', secrets.email_password)

    if type == 1:
        server.quick_email(address,"Successful Registration",['Welcome ' + address +'.\n', 'You have successfully been registered on the ObjectID system you will now be able ' +
                                                                    'to log in and use the functionalities of the system.\n', 'Thank you for using ObjectID.'])

    elif type == 2:
        server.quick_email(address, "Account Removed", ['Greetings ' + address + '.\n', 'Your account has been suspended, and you will no longer be able to use the ObjectID system ' +
                                                                'if you require any assistance please mail ctrl.intelligence@gmail.com.\n', 'Thank you for using ObjectID.'])

def flagged_notification(address,lic_plate,flag,image,location, make, model,color):
    server = email_to.EmailServer('smtp.gmail.com', 587, 'ctrl.intelligence@gmail.com', secrets.email_password)
    server.quick_email(address, "FLAGGED VEHICLE SPOTTED", ["WARNING " + address+ '.\n', "A " + color+" "+ make+" "+model+" with the number plate "+lic_plate+" has been spotted on a camera at "
        + location + ", our system shows that " + flag+".", "Please take the nesscary precautions and report the vehicle to the authorities if it is spotted. A snapshot of the vehicle is "+
        "attached to this email."])


def flagged_mail(address, lic_plate, flag, image, location, make, model, color):
    port = 587
    smtp_server = "smtp.gmail.com"
    login = "ctrl.intelligence@gmail.com"
    password = secrets.email_password

    subject = "FLAGGED VEHICLE SPOTTED"
    sender_email = "ctrl.intelligence@gmail.com"

    msg = MIMEMultipart()
    msg["From"] = login
    msg["To"] = address
    msg["Subject"] = subject

    body = "WARNING " + address + '.\n' + "A " + color+" " + make+" "+model + \
        " with the number plate "+lic_plate+" has been spotted on a camera at "
    body += location + ", our system shows that " + flag+".\n" + \
        "Please take the nesscary precautions and report the vehicle to the authorities if it is spotted. A snapshot of the vehicle is "
    body += "attached to this email."
    msg.attach(MIMEText(body, "plain"))

    with open(image, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    img_data = open(image, 'rb').read()
    part = MIMEImage(img_data, name=os.path.basename(image))

    msg.attach(part)
    text = msg.as_string()

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.connect("smtp.gmail.com", 587)
    server.starttls()
    server.login(login, password)
    server.sendmail(
        sender_email, address, text
    )
    server.quit()

