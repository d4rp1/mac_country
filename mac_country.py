#!/bin/pyton3

# mac_country.py, Author d4rp1 (David Roldan)

import sys
import signal
import requests
import argparse
import subprocess
from random import randint
from bs4 import BeautifulSoup

def argsparser():
    """get and handle arguments (interface) (country code) and return"""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='e.g:\tpython3 %(prog)s -i eth0  -c us\n\tpython3 %(prog)s -i wlan0 -c br\n\tpython3 %(prog)s -i eth0  -c es',
            usage='python3 %(prog)s [-i] INTERFACE [-c] COUNTRY\nhelp: python3 %(prog)s [-h] ')
    parser.add_argument('-i', type=str, help='your network interface', dest='interface', required=True)
    parser.add_argument('-c', type=str, help='choose a country code', dest='country', required=True)
    args = parser.parse_args()
    return args.country, args.interface

def obtain_range(country='us'):
    """get country mac address range and return it"""
    url           = f'https://hwaddress.com/country/{country}/'
    content       = requests.get(url).content
    soup          = BeautifulSoup(content, 'html.parser')
    macs_range    = soup.find('a', class_='mac').text.split()
    macs_range[1] = '/'
    mac_range     = ''.join(macs_range)
    return mac_range

def obtain_mac(mac_range):
    """choose a mac address from country range code"""
    nrandom       = randint(0,1)
    url           = f'https://hwaddress.com/mac-address-range/{mac_range}/'
    content       = requests.get(url).content
    soup          = BeautifulSoup(content, 'html.parser')
    mac_group     = soup.find('span', class_='mac').text.split()
    mac_group.pop(1)
    return mac_group[nrandom].replace('-', ':')

def change_mac(mac,interf):
    """turn off the network interface, change the mac address and turn on again"""
    subprocess.call(['sudo','ifconfig', interf, 'down'])
    subprocess.call(['sudo','ifconfig', interf, 'hw', 'ether', mac])
    subprocess.call(['sudo','ifconfig', interf, 'up'])

def ctrl_c(sig,frame):
    """exit with Ctrl+c"""
    print('\n[*] Exiting...\n')
    sys.exit(1)

# main

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c)
    # get the arguments
    country,interf = argsparser()
    # error handling
    try:
        mac_range = obtain_range(country)       
        mac = obtain_mac(mac_range)
        change_mac(mac,interf)
    except FileNotFoundError:
        print("[x] Error: bad interface or can't change your MAC address")
        sys.exit(1)
    except AttributeError:
        print("[x] Error: wrong country code\nsee the correct country codes here: https://en.wikipedia.org/wiki/ISO_3166-1")
        sys.exit(1)  
    else:
        print(f'[✓] MAC changed successfully\nYour new MAC address is: {mac}')
        sys.exit(0)