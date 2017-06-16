# proofpy
A hacked-together shim to pull syslog data from the ProofPoint TAP API

#Requires

requests

#Usage

proofpy.py userprincipal usersecret sysloghost -s seconds -c category -t port --show

userprincipal: Your proofpoint API principal
usersecret: Your proofpoint API secret
sysloghost: IP address or hostname of your SIEM/syslog server
-s: Interval in seconds (60-3600). Defaults to 300.
-c: Category. Valid choices are 'issues' and 'all'. Default is 'issues'
-t: Syslog port. Default is 514.
--show: Print output to console instead of forwarding to a syslog server.

Currently, has to be automated with cron/task scheduler. 

#TODO
Rewrite to support execution as a systemd service
Cleanup & prettify
