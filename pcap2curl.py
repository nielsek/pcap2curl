#!/usr/bin/env python

import sys
from scapy.all import PcapReader, re, Raw, TCP


def payload2curl(p):
    lines = re.compile("[\n\r]+").split(p.decode('utf-8', errors='ignore'))
    start_line = re.search("^([A-Z]+) ([^ ]+) (HTTP\/[0-9\/]+)", lines[0])
    if start_line is None:
        return 0
    method = start_line.group(1)
    url = start_line.group(2)
    version = start_line.group(3)  # Never used

    del lines[0]
    headers = []
    for line in lines:
        if ":" in line:
            headers.append("-H '{}'".format(line))
        if "Host:" in line:
            host_header = re.search("^Host: (.*)", line)
            host_name = host_header.group(1)

    proto_host = 'http://{}/'.format(host_name)
    if not url.startswith(proto_host):
        url = "{}{}".format(proto_host, url[1:] if url[0] == "/" else url)
    curl = "curl '{}' \\\n -X {} \\\n ".format(url, method)
    curl += " \\\n ".join(headers)
    return curl


def main():
    if len(sys.argv) != 2:
        print ("I need an input file. Usage ./pcap2curl.py inputfilename")
        return

    infile = sys.argv[1]

    with PcapReader(infile) as packets:
        for p in packets:
            if p.haslayer(TCP) and p.haslayer(Raw) and p[TCP].dport == 80:
                payload = p[Raw].load
                print(payload2curl(payload))


if __name__ == "__main__":
    main()
