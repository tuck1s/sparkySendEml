#!/usr/bin/env python3
import argparse, time, json, email, requests
from common import eprint, getenv_check, getenv, host_cleanup, strip_start

T = 20                  # Global timeout value for API requests

# Each of these functions add flags from a list of tuples comprising (name, help string)
def add_str_args(group, flags):
    for f in flags:
        group.add_argument('--'+f[0], type=str, action='store', help=f[1])


def add_boolean_args(group, flags):
    bool_choices = [False, True]
    for f in flags:
        group.add_argument('--'+f[0], type=bool_option, action='store', default=None, choices=bool_choices, help=f[1])


def add_json_args(group, flags):
    for f in flags:
        group.add_argument('--'+f[0], type=json_option, action='store', help=f[1])


def bool_option(s):
    """
    Command-line option str which must resolve to [true|false]
    """
    s = s.lower()
    if s=='true':
        return True
    elif s=='false':
        return False
    else:
        raise TypeError # Let argparse know there's a problem


def json_option(s):
    """
    Command-line option str which must resolve to a valid JSON object
    """
    try:
        j = json.loads(s)
        return j
    except:
        raise TypeError # Let argparse know there's a problem


def send_transmission(url, apiKey, tx_obj):
    startT = time.time()
    try:
        h = {'Authorization': apiKey, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.post(url, timeout=T, headers=h, data=json.dumps(tx_obj))
        endT = time.time()
        if(response.status_code == 200):
            return response.json()
        else:
            eprint('Error:', response.status_code, ':', response.json(), 'in', round(endT - startT, 3), 'seconds')
            return None
    except ConnectionError as err:
        eprint('error code', err.status_code)
        return None


def tx_api_obj(arg_dict):
    """
    Build a SparkPost Transmission API object from the command-line args (passed in as a dict), recipients, and mesage content
    """
    send_obj = { 'options': {}  }
    for key, val in arg_dict.items(): # iterate through args as a dict
        if key in ['infile', 'json_out'] or val == None: # these are not needed in the API call
            continue
        elif key.startswith(opt_prefix):
            stderr_report(key, val)
            send_obj['options'][strip_start(key, opt_prefix)] = val
        else:
            stderr_report(key, val)
            send_obj[key] = val
    return send_obj


def recipients(msg):
    """
    Input is an email.message.
    Returns SparkPost recipients attribute built from the collected To, Cc, Bcc recipients
    See https://support.sparkpost.com/customer/portal/articles/2432290-using-cc-and-bcc-with-the-rest-api
    """
    recips = []
    for hdr in ['to', 'cc', 'bcc']:
        if hdr in msg:
            for (name, addr) in email.utils.getaddresses(msg.get_all(hdr, [])):
                r = { 'address': { 'name': name, 'email': addr } }
                # TODO: do we need to fix up header_to attributes as well?
                stderr_report(hdr.title(), '"{}" <{}>'.format(name, addr))
                recips.append(r)
    return recips


def remove_bcc(msg):
    """
    Removes any bcc headers from msg payload, as per https://tools.ietf.org/html/rfc5322#section-3.6.3
    """
    for header in msg._headers:
        if header[0].lower() == 'bcc':
            msg._headers.remove(header)


def stderr_report(key, val, **kwargs):
    """
    Reporting via stderr, with fixed key : value tabulation
    """
    eprint('{:24} {}'.format(key + ':', val), **kwargs)


# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description='Parse and send an RFC822-compliant file (e.g. .eml extension) via SparkPost.')
parser.add_argument('-i', '--infile', type=argparse.FileType('r'), default='-',
    help='File containing RFC822 formatted content including subject, from, to, and MIME parts. If omitted, will read from stdin')
parser.add_argument('--json_out', action='store_true',
    help='Write the transmission API JSON on stdout instead of sending.')

# See https://developers.sparkpost.com/api/transmissions/#transmissions-create-a-transmission
group = parser.add_argument_group('SparkPost Transmission API attributes')
add_str_args(group, [
    ('campaign_id', 'Name of the campaign. Maximum length - 64 bytes'),
    ('description', 'Description of the transmission. Maximum length - 1024 bytes'),
    ('return_path', 'Email address to use for envelope FROM'),
])
group = parser.add_argument_group('JSON-format attributes - enclose content in quotes " "')
add_json_args(group, [
    ('metadata', 'Transmission level metadata'),
    ('substitution_data', 'Transmission level metadata'),
])

group = parser.add_argument_group('SparkPost Transmission API options')
opt_prefix = 'options.'
add_str_args(group, [
    (opt_prefix+'start_time', 'The system will not attempt to deliver messages until this datetime. Format: YYYY-MM-DDTHH:MM:SS+-HH:MM'),
    (opt_prefix+'ip_pool', 'The ID of a dedicated IP pool to send from. If this field is not provided, the account default dedicated IP pool is used (if there are IPs assigned to it)'),
])
add_boolean_args(group,[
    (opt_prefix+'open_tracking', 'Enable or disable open tracking. If omitted, default is true'),
    (opt_prefix+'click_tracking', 'Enable or disable click tracking. If omitted, default is true'),
    (opt_prefix+'transactional', 'Distinguish between transactional and non-transactional messages for unsubscribe and suppression purposes If omitted, default is false'),
    (opt_prefix+'sandbox', 'Whether to use the sandbox sending domain. If omitted, default is false'),
    (opt_prefix+'skip_suppression', 'Whether to ignore customer suppression rules. *Enterprise only*. If omitted, default is false'),
    (opt_prefix+'inline_css', 'Whether to inline the CSS in <style> tags in the <head> in the HTML content. Not performed on AMPHTML Email content. If omitted, default is false'),
    (opt_prefix+'perform_substitutions', 'Enable or disable substitutions. Can only set to false when using an inline template. If omitted, default is true')
])
args = parser.parse_args()
if args.infile.isatty():
    eprint('(Awaiting input from stdin)') # show the user we're waiting for input, without touching the stdout stream
msg = email.message_from_file(args.infile)

apiKey = getenv_check('SPARKPOST_API_KEY')                      # API key is mandatory
host = host_cleanup(getenv('SPARKPOST_HOST', default='api.sparkpost.com'))
url = host + '/api/v1/transmissions/'

# Compose transmission object, with attributes, options, recipients and content
send_obj = tx_api_obj(vars(args))
send_obj['recipients'] = recipients(msg)
remove_bcc(msg)
msg_str = msg.as_bytes().decode('utf8')
send_obj['content'] = {'email_rfc822': msg_str}

stderr_report('Subject',msg['subject'])
stderr_report('Message length (bytes)',len(msg_str))
if args.json_out:
    print(json.dumps(send_obj, indent=2))
else:
    stderr_report('Sending via', url)
    res = send_transmission(url, apiKey, send_obj)
    if res:
        r = res.get('results')
        stderr_report('Accepted recipients', r.get('total_accepted_recipients'))
        stderr_report('Rejected recipients', r.get('total_rejected_recipients'))
        stderr_report('Transmission id', r.get('id'))
