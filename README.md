<a href="https://www.sparkpost.com"><img src="https://www.sparkpost.com/sites/default/files/attachments/SparkPost_Logo_2-Color_Gray-Orange_RGB.svg" width="200px"/></a>

[Sign up](https://app.sparkpost.com/join?plan=free-0817?src=Social%20Media&sfdcid=70160000000pqBb&pc=GitHubSignUp&utm_source=github&utm_medium=social-media&utm_campaign=github&utm_content=sign-up) for a SparkPost account and visit our [Developer Hub](https://developers.sparkpost.com) for even more content.

# sparkySendEml

[![Build Status](https://travis-ci.com/tuck1s/sparkySendEml.svg?branch=master)](https://travis-ci.com/tuck1s/sparkySendEml)

Parse and send an RFC822-compliant file (e.g. .eml extension) via SparkPost.

This is useful in the following scenarios:
- You have an email generation tool-chain that produces fully formed RFC-compliant email files
- You cannot inject using secure SMTP (STARTTLS) maybe due to limitations in your infrastructure

> API injection can be faster than SMTP, particularly if you are geographically far from our injection endpoints (because SMTP is a chatty protocol).

## Easy installation

Firstly ensure you have `python3`, `pip` and `git`. Install `pipenv`:

`pip install pipenv`

(Depending on how it was installed, you might need to type `pip3 install pipenv` instead).

Get the project, and install dependencies.

```
git clone https://github.com/tuck1s/sparkySendEml.git
cd sparkySendEml
pipenv install
pipenv shell
```

You can now type `./sparkySendEml.py -h` and see usage info.

## Pre-requisites

Set the following environment variables. Note these are case-sensitive.

```
SPARKPOST_HOST (optional)
    The URL of the SparkPost API service you're using. Defaults to https://api.sparkpost.com.

SPARKPOST_API_KEY
    API key on your SparkPost account, with Recipient Validation rights.
```

## Usage

There are a lot of parameters, but they are optional.

```
./sparkySendEml.py -h
```

```
usage: sparkySendEml.py [-h] [-i INFILE] [--json_out] [--campaign_id CAMPAIGN_ID] [--description DESCRIPTION] [--return_path RETURN_PATH]
                        [--metadata METADATA] [--substitution_data SUBSTITUTION_DATA] [--options.start_time OPTIONS.START_TIME]
                        [--options.ip_pool OPTIONS.IP_POOL] [--options.open_tracking {False,True}] [--options.click_tracking {False,True}]
                        [--options.transactional {False,True}] [--options.sandbox {False,True}] [--options.skip_suppression {False,True}]
                        [--options.inline_css {False,True}] [--options.perform_substitutions {False,True}]

Parse and send an RFC822-compliant file (e.g. .eml extension) via SparkPost.

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        File containing RFC822 formatted content including subject, from, to, and MIME parts. If omitted, will read from stdin
  --json_out            Write the transmission API JSON on stdout instead of sending.

SparkPost Transmission API attributes:
  --campaign_id CAMPAIGN_ID
                        Name of the campaign. Maximum length - 64 bytes
  --description DESCRIPTION
                        Description of the transmission. Maximum length - 1024 bytes
  --return_path RETURN_PATH
                        Email address to use for envelope FROM

JSON-format attributes - enclose content in quotes " ":
  --metadata METADATA   Transmission level metadata
  --substitution_data SUBSTITUTION_DATA
                        Transmission level metadata

SparkPost Transmission API options:
  --options.start_time OPTIONS.START_TIME
                        The system will not attempt to deliver messages until this datetime. Format: YYYY-MM-DDTHH:MM:SS+-HH:MM
  --options.ip_pool OPTIONS.IP_POOL
                        The ID of a dedicated IP pool to send from. If this field is not provided, the account default dedicated IP pool is used (if
                        there are IPs assigned to it)
  --options.open_tracking {False,True}
                        Enable or disable open tracking. If omitted, default is true
  --options.click_tracking {False,True}
                        Enable or disable click tracking. If omitted, default is true
  --options.transactional {False,True}
                        Distinguish between transactional and non-transactional messages for unsubscribe and suppression purposes If omitted, default
                        is false
  --options.sandbox {False,True}
                        Whether to use the sandbox sending domain. If omitted, default is false
  --options.skip_suppression {False,True}
                        Whether to ignore customer suppression rules. *Enterprise only*. If omitted, default is false
  --options.inline_css {False,True}
                        Whether to inline the CSS in <style> tags in the <head> in the HTML content. Not performed on AMPHTML Email content. If
                        omitted, default is false
  --options.perform_substitutions {False,True}
                        Enable or disable substitutions. Can only set to false when using an inline template. If omitted, default is true
```

## Example output
```
 ./sparkySendEml.py --infile SparkPost_Messenger_Aug_2017.eml
```

```
To:                      "Alice" <alice@emltest.sink.sparkpostmail.com>
To:                      "Bob Lumreeker" <bob.lumreeker@gmail.com>
Cc:                      "Charlie" <charles.tapdancer@gmail.com>
Cc:                      "Diana" <diana@emltest.sink.sparkpostmail.com>
Bcc:                     "Ewina" <ed@emltest.sink.sparkpostmail.com>
Bcc:                     "Fred" <steve.tuck@sparkpost.com>
Subject:                 The Messenger: Email Insights from SparkPost
Message length (bytes):  42877
Sending via:             https://api.sparkpost.com/api/v1/transmissions/
Accepted recipients:     6
Rejected recipients:     0
Transmission id:         6920251779208728743
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

The tool sends to the recipients specified in the `.eml` file, so it's ideal for personalised mailings where you have fully-formed messages.

## See also

Article explaining why you should run your campaigns with individual To: recipients: [Thou Shalt Not BCC.](https://www.sparkpost.com/blog/thou-shalt-not-bcc-pitfalls/)

[Using CC and BCC with the REST API.](https://www.sparkpost.com/docs/faq/cc-bcc-with-rest-api/)

[What are the differences between CC, BCC, and archive recipients?](https://www.sparkpost.com/docs/faq/cc-bcc-archive-recipients/)

If you want to leverage the template substitution and multi-recipient generation capability of SparkPost, take look at
[Sending Scheduled Mailings Simply with SparkPost.](https://www.sparkpost.com/blog/sending-scheduled-mailings-simply/)

## Current RFCs (at time of writing)

[RFC5322](https://tools.ietf.org/html/rfc5322) - email message format. This is the successor document to RFC822.

[RFC2045](https://tools.ietf.org/html/rfc2045) -   MIME parts.

[RFC7159](https://tools.ietf.org/html/rfc7159)  - JSON.