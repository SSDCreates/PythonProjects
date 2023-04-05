
# log in to existing mail account and then use smtp to send mail

#import smtp library from python
import smtplib

#import
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

#define server and port (25 for smtp)
server = smtplib.SMTP('smtp-mail.outlook.com', 25)

# start servivce
server.ehlo()

server.starttls()

server.ehlo()

username = input("Enter email: ")
password = input("Enter Password: ")

# log into account
server.login(username, password)

#define message as mime multiplart
msg = MIMEMultipart()
msg['From'] = 'User'
msg['To'] = 'email@gmail.com'
msg['Subject'] = 'Test'

with open('message.txt', 'r') as f:
    message = f.read()

msg.attach(MIMEText(message, 'plain'))

picturefile = 'cat.jpg'

#open with readable binary for image
attachment = open(picturefile, 'rb')

p = MIMEBase('application', 'octet-stream')
p.set_payload(attachment.read())

#encode image data
encoders.encode_base64(p)
#add header
p.add_header('Content-Disposition', f'attachment;, filename={picturefile}')

#attach payload to message
msg.attach(p)

txt = msg.as_string()

server.sendmail(username, 'email@email.com', txt)


