#!/usr/bin/env python3
from __future__ import print_function
import configparser, time, json, sys, os, email, requests

T = 90                  # Global timeout value for API requests

def printHelp():
    progName = sys.argv[0]
    shortProgName = os.path.basename(progName)
    print('\nNAME')
    print('  ' + progName)
    print('  Parse and send an RFC822-compliant file (e.g. .eml extension) via SparkPost.')
    print('')
    print('SYNOPSIS')
    print('  ./' + shortProgName + ' infile N\n')
    print('  infile must contain RFC822 formatted content including subject, from, to, and MIME parts.')
    print('  N = integer, number of times to send the message')
    print('')
    print('  cc and bcc headers are also read and applied.');

# Call the transmission endpoint using requests library directly, as sparkpost-python lib doesn't currently support RFC822 content
# sendObj is a native Python dict object
def sendTransmission(uri, apiKey, sendObj):
    startT = time.time()
    try:
        path = uri+'/api/v1/transmissions'
        h = {'Authorization': apiKey, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.post(path, timeout=T, headers=h, data=json.dumps(sendObj))
        endT = time.time()
        if(response.status_code == 200):
            return response.json()
        else:
            print('Error:', response.status_code, ':', response.json(), 'in', round(endT - startT, 3), 'seconds')
            return None
    except ConnectionError as err:
        print('error code', err.status_code)
        return None

# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
# Get parameters from .ini file
configFile = 'sparkpost.ini'
config = configparser.ConfigParser()
config.read_file(open(configFile))
cfg = config['SparkPost']
apiKey = cfg.get('Authorization', '')                   # API key is mandatory
if not apiKey:
    print('Error: missing Authorization line in ' + configFile)
    exit(1)
baseUri = 'https://' + cfg.get('Host', 'api.sparkpost.com')

# Compose optional transmission parameters from the .ini file, if present
sendObj = {}
if cfg.get('Binding'):
    sendObj['metadata'] = {"binding": cfg.get('Binding')}
if cfg.get('Return-Path'):
    sendObj['return_path'] = cfg.get('Return-Path')
if cfg.get('Campaign'):
    sendObj['campaign_id']  = cfg.get('Campaign')               # native JSON attribute name, as not using the sparkpost-python lib

if len(sys.argv) >= 2:
    emlFname = sys.argv[1]
    with open(emlFname, 'rb') as emlfile:
        msg = email.message_from_binary_file(emlfile)

        # "recipients" attribute is built from the collected To, Cc, Bcc recipients
        # See https://support.sparkpost.com/customer/portal/articles/2432290-using-cc-and-bcc-with-the-rest-api
        allRecips = []
        for hdrName in ['to', 'cc', 'bcc']:
            print(hdrName.title()+':')
            for i in email.utils.getaddresses(msg.get_all(hdrName, [])):
                r = {
                    'address': {
                        'name': i[0],
                        'email': i[1]
                    }
                }
                print('    '+'"'+i[0]+'" <'+i[1]+'>')
                allRecips.append(r)

        # Remove any bcc headers from the message payload. Work backwards, as deletion changes later indices.
        for i in reversed(range(len(msg._headers))):
            hdrName = msg._headers[i][0].lower()
            if hdrName == 'bcc':
                del(msg._headers[i])

        rfc822msg = msg.as_bytes().decode('utf8')
        #rfc822msg = 'Content-Type: text/plain\nFrom: \"stevet test\" <stevet@ca.mail.e.sparkpost.com>\nSubject: Example Email\n\nHello World'

        print('Subject:',msg['subject'])
        print('Total message length:',len(rfc822msg), 'bytes')
        # Build the request structure
        sendObj.update({
            'content': {'email_rfc822': rfc822msg},
            'recipients': allRecips
        })

        print('Sending to ',baseUri)

        if len(sys.argv) >= 3:
            # optional "do n times" parameter
            doN = int(sys.argv[2])
            print('Sending ', doN, 'times')
            print('timestamp, API_response_time, result');
            for i in range(0, doN):
                startT = time.time()
                res = sendTransmission(baseUri, apiKey, sendObj)
                endT = time.time()
                outstr = time.strftime('[%Y-%m-%dT%H:%M:%S%z]', time.gmtime(startT))
                outstr += ',{0:.3f}'.format(endT - startT)
                outstr += ',' + json.dumps(res)
                print(outstr)
        else:
            print('missing parameter N for number of times to send the message')
else:
    printHelp()