# sparkySendEml
Parse and send an RFC822-compliant file (e.g. .eml extension) via SparkPost.


This is useful in the following scenarios:
- Existing email generation tool-chain that produces fully formed RFC-compliant email files
- Cannot inject using secure SMTP (STARTTLS) maybe due to limitations in your infrastructure
- API injection can be faster than SMTP, particularly if you are geographically far from our injection endpoints (because SMTP is a chatty protocol)

## Pre-requisites

Ensure you have `python3` and `pip3` using the following commands.
If you don't have them, there are [install suggestions here.](https://www.sparkpost.com/blog/sparkpost-message-events-api/)
```bash
$ python3 --version
Python 3.5.1
$ pip3 --version
pip 9.0.1 from /usr/local/lib/python3.5/site-packages (python 3.5)
```

Install the following libraries:
```bash
$ pip3 install requests
```

Install this tool using `git clone`.
Rename `sparkpost.ini.example` to `sparkpost.ini`, and insert your API key.

## Usage
```
NAME
  ./sparkySendEml.py
  Parse and send an RFC822-compliant file (e.g. .eml extension) via SparkPost.

SYNOPSIS
  ./sparkySendEml.py infile

  infile must contain RFC822 formatted content including subject, from, to, and MIME parts.

  cc and bcc headers are also read and applied.

```
## Example output
```
$ ./sparkySendEml.py SparkPost_Messenger_Aug_2017.eml 
To:
    "Bob" <bob.lumreeker@emltest.sink.sparkpostmail.com>
Cc:
    "Alice" <alice.cleanheels@emltest.sink.sparkpostmail.com>
Bcc:
    "Charles" <charles.tapdancer@emltest.sink.sparkpostmail.com>
Subject:  The Messenger - Email Insights from SparkPost
Total message length  27398 bytes
Total accepted recipients: 3
Total rejected recipients: 0
Transmission id:           30631141777298845
```

Note the `Cc:` `Bcc:` entries above are to demo the capabilities of the tool. Usually you would create a campaign mailing
with just a single `To:` recipient.

## Preparing input files for update
The nature of eml files is fully-formed, RFC-compliant content.  You can make files by creating a draft in your
favourite email client such as OSX mail.app or Mozilla Thunderbird, and saving it as a file (or just dragging it to the desktop).

Open the file in a text editor, check and remove any headers you don't want. The minimum you need are `From:`, `To:` and you should also have a `Subject:`
MIME parts will be present in a rich email too.

```
From: SparkPost Test <test@email.example.com>
To: "Bob" <bob.lumreeker@example.com>
Subject: The Messenger - Email Insights from SparkPost
MIME-Version: 1.0
Content-Type: multipart/alternative; 
	boundary="----=_Part_1971470054_922638219.1464874841278"

------=_Part_1971470054_922638219.1464874841278
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: quoted-printable

June 2, 2016
EDITOR'S PICK
:
:
```

This tool sends to the recipients specified in the .eml file, so it's ideal for personalised mailings where you have fully-formed messages.

## See also

Article explaining why you should run your campaigns with individual To: recipients: [Thou Shalt Not BCC](https://www.sparkpost.com/blog/thou-shalt-not-bcc-pitfalls/)

[Using CC and BCC with the REST API.](https://www.sparkpost.com/docs/faq/cc-bcc-with-rest-api/)

[What are the differences between CC, BCC, and archive recipients?](https://www.sparkpost.com/docs/faq/cc-bcc-archive-recipients/)

If you want to leverage the template substitution and multi-recipient generation capability of SparkPost, take look at 
[Sending Scheduled Mailings Simply with SparkPost.](https://www.sparkpost.com/blog/sending-scheduled-mailings-simply/)

