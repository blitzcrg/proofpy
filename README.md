# proofpy

I no longer have access to a Proofpoint TAP API endpoint to verify whether this code still works, so use with caution. 

```
usage: proofpy.py [-h] [-s [60-3600]] [-c {issues,all}] [-t [1-65535]]
                  [--show]
                  principal secret sysloghost

positional arguments:
  principal             Your ProofPoint API User Principal ID
  secret                Your ProofPoint API User Secret
  sysloghost            The hostname or IP address of the destination syslog
                        server

optional arguments:
  -h, --help            show this help message and exit
  -s [60-3600], --seconds [60-3600]
                        Number of seconds [60-3600] worth of events up to
                        right now to retrieve. Default: 300.
  -c {issues,all}, --category {issues,all}
                        API category. Valid arguments are 'issues' or 'all'.
                        Default: issues.
  -t [1-65535], --port [1-65535]
                        Syslog destination port [1-65535]. Default: 514.
  --show                Print to console instead of sending as syslog.

```
# mailtap

The notification output script that triggers whenever my SIEM sees a relevant
event in order to automatically notify the offending user they may be
compromised. Modify parameters in the main method to suit your environment.
Works with RSA Netwitness - support for other SIEM platforms will depend on
you.
