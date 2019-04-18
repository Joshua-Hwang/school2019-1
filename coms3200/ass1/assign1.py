#!/usr/bin/env python3
import sys
import argparse
import socket
from urllib.parse import urlparse
from datetime import datetime, timedelta

FAMILY = socket.AF_INET
TYPE = socket.SOCK_STREAM # changes will need to be made for UDP
PORT = 80
TZ = 10 # a 10 hour shift
BUFFER_SIZE = 1024

MIN_ERROR = 400 # the HTTP respsonses which are errors
MAX_ERROR = 500

def save_file(content_type, content):
    # determine content type
    ext = {
        'text/plain' : '.txt',
        'text/html' : '.html',
        'text/css' : '.css',
        'text/javascript' : '.js',
        'application/javascript' : '.js',
        'application/json' : '.json',
        'application/octet-stream' : '',
    }.get(content_type, '')

    with open("output%s"%ext, 'wb') as s:
        s.write(content)

def recv_all(sock):
    msg = b''
    while True:
        chunk = sock.recv(BUFFER_SIZE)
        if len(chunk) <= 0:
            break
        else:
            msg += chunk
    return msg

def split_http_header(msg): # msg should be byte string in utf-8
    msg = msg.decode('utf-8')
    header_index = msg.index('\r\n\r\n')
    header = msg[0:header_index].strip()
    body = msg[header_index+4:].encode('utf-8') # body doesn't have \r\n\r\n
    return (header, body)

# returns a http get request based on the parsed url
def http_get_msg(host, path):
    msg = "GET %s HTTP/1.1\r\n" % (path if path else '/') + \
          "Host: %s\r\n" % host + \
          "Accept: text/plain,text/html,text/css," + \
          "application/javascript,application/json," + \
          "application/octet-stream\r\n" + \
          "Connection: close\r\n\r\n"
    return msg

def http_header_parse(msg):
    ret = {}
    lines = msg.splitlines()
    # get response code from first line
    ret['Response'] = lines[0].split(' ')[1]
    for line in lines:
        index = line.find(':')
        if index > 0:
            ret[line[:index]] = line[index + 1:].strip()

    return ret

def print_times(parsed_msg):
    access_date = datetime.strptime(parsed_msg['Date'], \
            "%a, %d %b %Y %H:%M:%S %Z") + timedelta(hours=TZ)
    print("Date Accessed: %s" \
            % access_date.strftime("%d/%m/%Y %H:%M:%S AEST"))

    if 'Last-Modified' in parsed_msg:
        modify_date = datetime.strptime(parsed_msg['Last-Modified'], \
                "%a, %d %b %Y %H:%M:%S %Z") + timedelta(hours=TZ)
        print("Date Modified: %s" \
                % modify_date.strftime("%d/%m/%Y %T AEST"))
    else:
        print("Last Modified not available")

def main(url, first_one=True):
    if first_one:
        print("URL requested:", url)
    parsed_url = urlparse(url)
    protocol = parsed_url.scheme
    host = parsed_url.netloc
    path = parsed_url.path
    content_type = ''
    content = b''  # this is where we save the file
    response = 0
    relocation = ''

    if protocol == 'https':    # http is the only one supported
        print("HTTPS Not supported")
        return

    with socket.socket(FAMILY, TYPE) as s:
        # get server ip
        server_addr = socket.getaddrinfo(host, PORT, FAMILY, TYPE)[0][-1]

        try:
            s.connect(server_addr)

            # get client ip
            client_addr = s.getsockname()
            print("Client: %s %s" % client_addr)
            print("Server: %s %s" % server_addr)

            req_msg = http_get_msg(parsed_url.netloc, parsed_url.path)
            s.sendall(bytes(req_msg, 'utf-8'))

            res_msg = recv_all(s)
            res_header, res_body = split_http_header(res_msg)

            parsed_msg = http_header_parse(res_header)

            if MIN_ERROR <= int(parsed_msg['Response']) < MAX_ERROR: # error codes
                print("Retrieval Failed (%s)" % parsed_msg['Response'])
                return

            content_type = parsed_msg.get('Content-Type','')
            content = res_body
            response = int(parsed_msg.get('Response',''))
            relocation = parsed_msg.get('Location', '')
            # For debugging
            #print(res_msg.decode('utf-8'))
            #print(parsed_msg)

        except socket.timeout:
            print("Timeout")
            return

    # check for redirection
    if response in (301, 302): # moved permanently
        is_temp = response == 302
        print("Resource %s moved to %s" \
                %('temporarily' if is_temp else 'permanently', relocation))
        main(relocation, False)
        return

    print("Retrieval Successful")
    print_times(parsed_msg)
    save_file(content_type, content)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gets data from a url")
    parser.add_argument('parsed_url', type=str, help="parsed_url to GET data from")

    args = parser.parse_args()
    main(args.parsed_url);
