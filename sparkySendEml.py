#!/usr/bin/env python3
from __future__ import print_function
import configparser, time, json, sys, os, email, requests

T = 20                  # Global timeout value for API requests

def printHelp():
    progName = sys.argv[0]
    shortProgName = os.path.basename(progName)
    print('\nNAME')
    print('  ' + progName)
    print('  Parse and send an RFC822-compliant file (e.g. .eml extension) via SparkPost.')
    print('')
    print('SYNOPSIS')
    print('  ./' + shortProgName + ' infile\n')
    print('  infile must contain RFC822 formatted content including subject, from, to, and MIME parts.')
    print('')
    print('  cc and bcc headers are also read and applied.');

# Call the transmission endpoint using requests library directly, as sparkpost-python lib doesn't currently support RFC822 content
# sendObj is a native Python dict object
def sendTransmission(uri, apiKey, sendObj):
    startT = time.time()
    try:
        path = uri+'/api/v1/transmissions'
        h = {'Authorization': apiKey, 'Accept': 'application/json'}
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
        print('Subject:',msg['subject'])
        print('Total message length:',len(rfc822msg), 'bytes')
        # Build the request structure
        sendObj = {
            'content': {'email_rfc822': rfc822msg},
            'recipients': allRecips
        }
        print('Sending to ',baseUri)
        res = sendTransmission(baseUri, apiKey, sendObj)
        if res:
            print("Total accepted recipients:",res['results']['total_accepted_recipients'])
            print("Total rejected recipients:",res['results']['total_rejected_recipients'])
            print("Transmission id:          ",res['results']['id']);
else:
    printHelp()