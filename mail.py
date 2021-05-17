#!/usr/bin/env python3

import os
import sys
import syslog
import base64
import quopri
import re

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


def decode_mail_address(encoded_mail_address):
    try:
        encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}= (.*){1}'
        charset, encoding, encoded_text, mail = re.match(
            encoded_word_regex, encoded_mail_address).groups()

        if encoding is 'B':
            byte_string = base64.b64decode(encoded_text)
        elif encoding is 'Q':
            byte_string = quopri.decodestring(encoded_text)

        return byte_string.decode(charset) + ' ' + mail
    except:
        return encoded_mail_address


def decode_subject(encoded_subject):
    try:
        encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
        charset, encoding, encoded_text = re.match(
            encoded_word_regex, encoded_subject).groups()

        if encoding is 'B':
            byte_string = base64.b64decode(encoded_text)
        elif encoding is 'Q':
            byte_string = quopri.decodestring(encoded_text)

        return byte_string.decode(charset)
    except:
        return encoded_subject


syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_MAIL)

syslog.syslog('FORUM Sending mail %s' % sys.argv)

data = sys.stdin.readlines()
if len(data) == 0:
    syslog.syslog(syslog.LOG_ERR, 'Data is empty')
    sys.exit(0)

is_body = False
params = {}

for line in data:
    if len(line.strip()) == 0:
        is_body = True
        continue

    if is_body:
        params['body'] = params.setdefault('body', '') + line
    else:
        try:
            key, value = line.split(':', 1)
            params[key] = value.strip()
        except:
            syslog.syslog(syslog.LOG_ERR, 'Invalid data: %s' % line)
            pass


try:
    params['From'] = decode_mail_address(params['From'])
    params['To'] = decode_mail_address(params['To'])
    params['Subject'] = decode_subject(params['Subject'])

    syslog.syslog('Params: %s' % params)

    mail = Mail(from_email=params['From'],
                to_emails=params['To'],
                subject=params['Subject'],
                plain_text_content=params['body'])

    sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    response = sg.send(mail)

    syslog.syslog('Response: Code %s' % response.status_code)
except Exception as e:
    syslog.syslog(syslog.LOG_ERR, 'ERROR: %s' % e)

syslog.syslog('FORUM Sending mail finished')
