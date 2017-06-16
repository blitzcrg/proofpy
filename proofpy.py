#!/usr/bin/python
import requests, argparse, re, socket, sys
from _socket import gaierror

#Class Definitions
class Range(argparse.Action):
    '''
    Validation of argument ranges that doesn't print every possible value to the console if a bad argument is supplied.
    '''
    def __init__(self, min=None, max=None, *args, **kwargs):
        self.min = min
        self.max = max
        kwargs["metavar"] = "[%d-%d]" % (self.min, self.max)
        super(Range, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        if not (self.min <= value <= self.max):
            msg = 'Invalid choice: %r (choose from [%d-%d])' % \
                (value, self.min, self.max)
            raise argparse.ArgumentError(self, msg)
        setattr(namespace, self.dest, value)

#Functions
def api_validate(apikey):
    '''
    Input: String
    Output: String
    Make sure the secret/principal is at least possibly correct before querying the API.
    '''
    svalue = str(apikey)
    if len(svalue) < 1 or len(svalue) > 64:   
        raise argparse.ArgumentTypeError("%s is not a valid principal or secret." % svalue)
    return svalue

def host_validate(var):
    '''
    Input: String
    Output: String
    Check that the syslog destination host/IP is a valid one.
    '''
    svalue = str(var)
    validIpAddressRegex = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
    validHostnameRegex = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
    if validHostnameRegex.match(svalue) or validIpAddressRegex.match(svalue):
        return svalue
    else:
        raise argparse.ArgumentTypeError("%s is not a valid IP address or hostname" % svalue)
 
def api_query(principal, secret, seconds, category, output='syslog'):
    '''
    Input: Principal (string), secret (string), seconds (int), category (string), output (string)
    Output: list[strings]
    Makes the API query and returns a list of strings. If the status code is anything other than 200, print the status code and an error message, then call sys.exit()
    '''
    url = 'https://tap-api-v2.proofpoint.com/v2/siem/{}?format={}&sinceSeconds={}'.format(category, 
                                                                                          output, 
                                                                                          str(seconds))
    r = requests.get(url, auth=(principal, secret))
    if r.status_code == 200:
        eventlist = r.text.split('\n')
        return eventlist
    else:
        print('Error: query did not complete successfully. Request status code was: ' + str(r.status_code))
        sys.exit()

def sendlogs(eventlist, sysloghost, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        destination = socket.gethostbyname(sysloghost)
    except gaierror:
        print('Hostname {} could not be resolved. Check network settings, or use an IP address instead. Exiting'.format(sysloghost))
    for i in eventlist:
        msg = str(i)
        sock.sendto(msg.encode(), (destination, port))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("principal", help="Your ProofPoint API User Principal ID", type=api_validate)
    parser.add_argument("secret", help="Your ProofPoint API User Secret", type=api_validate)
    parser.add_argument("sysloghost", help="The hostname or IP address of the destination syslog server", type=host_validate)
    parser.add_argument("-s", "--seconds", type=int, min=60, max=3600, metavar="[60-3600]", help="Number of seconds [%(min)d-%(max)d] worth of events up to right now to retrieve. Default: %(default)s.", default=300, action=Range)
    parser.add_argument("-c", "--category", help="API category. Valid arguments are 'issues' or 'all'. Default: %(default)s.", choices=['issues', 'all'], default='issues')
    parser.add_argument("-t", "--port", type=int, min=1, max=65535, metavar="[0-65535]", help="Syslog destination port [%(min)d-%(max)d]. Default: %(default)s.", default=514, action=Range)
    parser.add_argument("--show", dest="show", help="Print to console instead of sending as syslog.", action="store_true", default=False)
    args = parser.parse_args()
    
    if args.show:
        eventlist = api_query(args.principal, args.secret, args.seconds, args.category)
        for i in eventlist:
            print(i)
    else:
        sendlogs(api_query(args.principal, args.secret, args.seconds, args.category), args.sysloghost, args.port)
    
if __name__ == "__main__":
    main()