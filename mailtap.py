#!/usr/bin/env python
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from smtplib import SMTP
import time
import json
import sys
import io

def dispatch(alert):
    """
    The default dispatch just prints the 'last' alert to /tmp/esa_alert.json.
    Alert details are available in the Python hash passed to this method e.g.
    alert['id'], alert['severity'],alert['module_name'], alert['events'][0],
    etc. These can be used to implement the external integration required.
    """
    with open("/tmp/esa_alert.json", mode='w') as alert_file:
        alert_file.write(json.dumps(alert, indent=True))

def build_alert(alert_json):
    """
    Extract specific values from JSON alert data into a list of strings, and
    return that list.

    This works for alerts with a single event; multiple events would each have
    their own indices in the events[] list.
    """
    alert_strings = []

    if 'email_src' in alert_json['events'][0]:
        alert_strings.append(alert_json['events'][0]['email_src'])
    else:
        alert_strings.append('Unknown')

    if 'email_dst' in alert_json['events'][0]:
        alert_strings.append(alert_json['events'][0]['email_dst'])
    else:
        alert_strings.append('Unknown')

    if 'mail_url' in alert_json['events'][0]:
        alert_strings.append(alert_json['events'][0]['mail_url'])
    else:
        alert_strings.append('Unknown')

    if 'mail_time' in alert_json['events'][0]:
        alert_strings.append(alert_json['events'][0]['mail_time'])
    else:
        alert_strings.append('Unknown')

    if 'mail_clicktime' in alert_json['events'][0]:
        alert_strings.append(alert_json['events'][0]['mail_clicktime'])
    else:
        alert_strings.append('Unknown')

    return alert_strings

def build_message(message_from, message_to, subject, alert_from,
                alert_to, alert_url, delivery_time, click_time, img_):
    """
    Do the things that define our multipart MIME message so mail clients that
    don't allow HTML can still read the thing, but also show a fancy header
    image to mail clients that do allow HTML.
    """
    message_to_string = ",".join(message_to)

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = message_from
    message['To'] = message_to_string

    # Let's not resend the evil URL, maybe...
    safe_url = alert_url.replace("http","hxxp")

# Format these message strings as desired. One is the plaintext version, one is
# html.

    text = '''Hello,\n\nYou are being contacted today because one of our
            security systems indicates this address may have been the
            victim of a phishing attack and that a link to a malicious
            site was clicked:\n\nRecipient: %s\nSender: %s\nURL: %s\nClick
            Time: %s\nDelivery Time: %s\n\n
            ''' % (alert_to, alert_from, safe_url, delivery_time,
                                click_time)

    html = '''
     <html>
        <body>
            <p>Hello,
              <br>
              <br>
               You are being contacted today because one of our security
               systems indicates that this address may have been the victim of
               a phishing attack and that a link to a malicious site was
               clicked:
              <br>
              <br>
            <table>
                <tr>
                    <td>Recipient: </td>
                    <td>%s</td>
                </tr>
                <tr>
                    <td>Sender:</td>
                    <td>%s</td>
                </tr>
                <tr>
                    <td>URL:</td>
                    <td>%s</td>
                </tr>
                <tr>
                    <td>Delivery time:</td>
                    <td>%s</td>
                </tr>
                <tr>
                    <td>Click time:</td>
                    <td>%s</td>
            </table>
            <br>
            <br>
            </p>
        </body>
     </html>

    ''' % (img_url, alert_to, alert_from, safe_url, delivery_time,
            click_time)

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    message.attach(part1)
    message.attach(part2)

    return message

def send_mail(smtp_server, smtp_port, message, smtp_user, smtp_pass):
    """
    Take the message we built and send it to our recipients.
    """
    smtp = SMTP(smtp_server, smtp_port)
    smtp.sendmail(email_from, email_to, message.as_string())
    smtp.quit()

if __name__ == "__main__":
    """
    Global Parameters: modify to fit environment. email_to is a list,
    because we add the user who triggered the alert to it. If you don't want to
    send yourself/your SOC a copy of the alert message, leave email_to = []

    No support yet for SMTP auth.
    """
    email_from = 'soc_replyto@yourorg.com'
    email_to = ['soc_messagefrom@yourorg.com']
    smtp_server = 'mail.server.yourorg.com'
    smtp_port = 25
    message_subject = 'Potential Infection Alert'
    smtp_user=''
    smtp_pass=''

    #Write the alert to a file; copied from RSA's documentation
    dispatch(json.loads(sys.argv[1])

    #Wait a second to make sure that file is where it's supposed to be
    time.sleep(1)

    #Load the alert JSON into a dict from the temp file. This should probably
    #just come straight from sys.argv...
    esa_alert = json.loads(open('/tmp/esa_alert.json').read())

    #Define a list of strings
    alert_strings = build_alert(esa_alert)

    #Set recipients; uncomment the second half for prod
    mail_to = email_to #+ alert_strings[1]

    #Create MIME message
    alert_message = build_message(email_from, email_to,message_subject,
                                    header_image_path, alert_strings[0],
                                    alert_strings[1], alert_strings[2],
                                    alert_strings[3], alert_strings[4])

    #Send that sucker
    send_mail(smtp_server, smtp_port, alert_message, smtp_user, smtp_pass)

    sys.exit(0)
