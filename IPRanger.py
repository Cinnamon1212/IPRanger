import os
import socket
import sys
import ipaddress
import re
from icmplib import ping
"""
Usage: ./LAN_Discover.py (ip)/(range) (interface) (option)
Example: ./LAN_Discover.py 192.168.1.1/24 wlan0
For more option information, use -h or --help

"""


def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def validate_iprange(s):
    if '/' in s:
        ip_range = s[-2:]
        try:
            int(ip_range)
        except ValueError:
            return False
        if int(ip_range) <= 32:
            return True
        else:
            return False


def main(argv):
    if len(argv) != 0:
        ips = argv[0]
        if ips == "-h" or argv[0] == "--help":
            print("""
            -h, --help shows this help menu
            -v, verbose response
            -o, write output to a file

            """)
        else:
            if validate_ip(ips[:-3]) is True:
                if validate_iprange(ips) is True:
                    IPs_To_Check = list(ipaddress.ip_network(ips, False).hosts())
                    NIC = argv[1]
                    i = 1
                    if "-o" in argv:
                        i = 0
                        for arg in argv:
                            if arg == "-o":
                                break
                            else:
                                i += 1
                        try:
                            filename = argv[i + 1]
                            if filename == "-v":
                                print("Please enter a filename")
                                sys.exit()
                        except IndexError:
                            print("Please enter a filename")
                            sys.exit()

                    if 'filename' in locals():
                        if os.isfile(filename):
                            f = open(filename, "a")
                        else:
                            f = open(filename, "x")
                    i = 1
                    for ip in IPs_To_Check:
                        source = re.search(re.compile(r'(?<=inet )(.*)(?=\/)', re.M), os.popen(f'ip addr show {NIC}').read()).groups()[0]
                        reply = ping(str(ip), timeout=1, source=source)

                        try:
                            if reply.isalive:
                                if len(argv) == 3 or len(argv) == 4:
                                    if argv[2] == "-v" or argv[3] == "-v":
                                        print(f"""
                                        {reply.address} is online!
                                            Average rrt: {reply.avg_rtt}
                                            Min rrt: {reply.min_rrt}
                                            Packet loss: {reply.packet_loss}
                                            Packets sent: {reply.packets_sent}
                                            Packets recieve {reply.packets_recieved}
                                        """)
                                        if 'f' in locals():
                                            f.write(f"""
                                            {reply.address} is online!
                                                Average rrt: {reply.avg_rtt}
                                                Min rrt: {reply.min_rrt}
                                                Packet loss: {reply.packet_loss}
                                                Packets sent: {reply.packets_sent}
                                                Packets recieve {reply.packets_recieved} \n
                                            """)
                                        else:
                                            pass
                                else:
                                    print(f"{reply.address} is online")
                                    if 'f' in locals():
                                        f.write(f"{reply.address} is online")
                                    else:
                                        pass
                            else:
                                continue
                        except AttributeError:
                            if len(argv) == 3 or len(argv) == 4:
                                if argv[2] == "-v" or argv[3] == "-v":
                                    print(f"{reply.address} is offline! ({i}/{len(IPs_To_Check)})")
                                    if 'f' in locals():
                                        f.write(f"{reply.address} is offline! ({i}/{len(IPs_To_Check)}) \n")
                                    i += 1
                                else:
                                    print(f"{round(i / len(IPs_To_Check) * 100, 2)}% complete ", end="\r")
                                    if 'f' in locals():
                                        f.write(f"{reply.address} is offline! ({i}/{len(IPs_To_Check)}) \n")
                                    i += 1
                            else:
                                print(f"{round(i / len(IPs_To_Check) * 100, 2)}% complete ", end="\r")
                                if 'f' in locals():
                                    f.write(f"{reply.address} is offline! ({i}/{len(IPs_To_Check)}) \n")
                                i += 1

                else:
                    print("Invalid IP range, use (ip)/1 to (ip)/32")

                if "f" in locals():
                    f.close()
                else:
                    pass
            else:
                print("Invalid IP, please use ip/(range)")
                sys.exit()
    else:
        print("Please provide an IP or use -h")



if __name__ == "__main__":
    main(sys.argv[1:])
