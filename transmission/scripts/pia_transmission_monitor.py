import ast
import fileinput
import os
import shlex
import sys
import logging
from collections import namedtuple
from datetime import datetime
from os.path import expanduser
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep
try:
    import configparser as configparser
except ImportError:
    import ConfigParser as configparser
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


def get_config():
    """Parse config.ini. Return namedtuple of
    (user, pw, client_id, pia_url, transmission_rc, tun_dev, transmission_uid,
    transmission_gid, transmission_command, openvpn_command)
    user:           PIA username
    pw:             PIA password
    client_id:      PIA generated client_id (see port forwarding forum post)
    pia_url:        PIA port forwarding API URL
    transmission_rc file path to transmission-daemon settings.json
    tun_dev:        name of tun/tap device (tun)
    transmission_uid: uid of user to run the transmission daemon
    transmission_gid: gid of group to run the transmission daemon
    transmission_command: actual transmission command to run
    netrc:          Location of netrc file
    """
    conf = configparser.ConfigParser()
    conf.read(os.getenv('TRANSMISSION_HOME', '/config') + '/config.ini')
    with open(expanduser(conf.get('File_Paths', 'pia_credentials'))) as f:
        user, pw = [line.rstrip() for line in f if line]
    with open(expanduser(conf.get('File_Paths', 'pia_client_id'))) as f:
        client_id = [line.rstrip() for line in f if line]
    c_nt = namedtuple("c_nt", ["user",
                               "pw",
                               "client_id",
                               "pia_url",
                               "transmission_rc",
                               "tun_dev",
                               "netrc",
                               "transmission_uid",
                               "transmission_gid",
                               "transmission_command",
                               "openvpn_command"])
    return c_nt(user,
                pw,
                client_id[0],
                conf.get('PIA', 'url'),
                expanduser(conf.get('File_Paths', 'transmission_rc')),
                conf.get('Server', 'tun_device'),
                expanduser(conf.get('File_Paths', 'netrc')),
                conf.get('Server', 'transmission_uid'),
                conf.get('Server', 'transmission_gid'),
                conf.get('Server', 'transmission_command'),
                conf.get('Server', 'openvpn_command'))


def ip_check(conf):
    """Check IP of tun device. Check 5 times until the IP exists then return
    it or return false.
    """
    count = 5
    while count:
        try:
            ip = Popen(["ip", "addr", "show", conf.tun_dev],
                       stdout=PIPE).communicate()[0].decode()
            ip = ip.split('inet')[1].split()[0]
            return ip
        except IndexError:
            # If tun doesn't exist
            print("IP for tun not available at {}".format(datetime.now()))
            sleep(5)
            count -= 1
    return False


def port_check(conf):
    """Submit a request to PIA port forwarding API. The call should return
    something like: {"port": 12345}. The function returns False or an integer
    port number.
    """
    ip = ip_check(conf)
    if ip is False:
        return False
    data = {"user": conf.user, "pass": conf.pw, "client_id": conf.client_id,
            "local_ip": ip}
    data = urlencode(data)
    count = 5
    while count:
        try:
            req = Request(conf.pia_url, data.encode())
            out = urlopen(req).read().decode()
            port = ast.literal_eval(out)["port"]
        except KeyError:
            print("Key 'port' not found in response: {}".format(out))
            port = False
        except URLError as e:
            port = False
            print("Failed to open PIA port url: [{}] {}".format(type(e), e))
        finally:
            if port:
                return port
            sleep(5)
            count -= 1
    return False


def service_start_stop(name, status, conf):
    """Stop or start a command
    Args: name - the full command string to run
          status - 'start' or 'stop'
          conf - configuration namedtuple
    """
    if status not in ("start", "stop"):
        raise Exception("Invalid service status")
    if 'transmission' not in name:
        uid = gid = 0
    else:
        uid = conf.transmission_uid
        gid = conf.transmission_gid
    cmd = shlex.split(name)
    if status == "start":
        process = Popen(cmd, preexec_fn=_demote(uid, gid), stdout=PIPE)
        print("Started {} at {}".format(cmd[0], datetime.now()))
    elif status == "stop":
        process = Popen(["pkill", "-f", cmd[0]], stdout=PIPE)
        print("Stopped {} at {}".format(cmd[0], datetime.now()))
    process.wait()


def _demote(user_uid, user_gid):
    """Local function to call setgid and setuid on a command when passing to
    Popen's preexec_fn
    """
    def result():
        os.setgid(int(user_gid))
        os.setuid(int(user_uid))
    return result


def restart_vpn(conf):
    """Restarts openvpn and transmission. Updates the transmission bind address
    after openvpn restarts.
    """
    service_start_stop(conf.transmission_command, "stop", conf)
    sleep(5)
    control = False
    while control is False:
        # Continue restarting openvpn until we have a good IP address
        service_start_stop(conf.openvpn_command, "stop", conf)
        sleep(5)
        service_start_stop(conf.openvpn_command, "start", conf)
        sleep(10)
        control = bind_addr_update(conf)
        if control is True:
            service_start_stop(conf.transmission_command, "start", conf)
            sleep(5)


def port_update(conf):
    """Update the port number in transmission.
    """
    port = port_check(conf)
    if port is False:
        return False
    # Update the port and make sure port forwarding is set. Authentication from
    # netrc file
    args = shlex.split("transmission-remote --netrc {} -p {} -m".format(conf.netrc, port))
    Popen(args, stdout=PIPE).communicate()
    print("Updated port to {} at {}".format(port, datetime.now()))
    # print("Testing port {} at {}".format(port, datetime.now()))
    # args = shlex.split("transmission-remote --netrc {} -pt".format(conf.netrc))
    # Popen(args, stdout=PIPE).communicate()


def bind_addr_update(conf):
    """Update the bind address in transmission when it changes. Daemon must not
    be running.
    """
    ip = ip_check(conf)
    port = port_check(conf)
    if ip is False:
        return False
    perms = os.stat(conf.transmission_rc)
    if str(ip) not in open(conf.transmission_rc).read():
        for line in fileinput.input(conf.transmission_rc, inplace=1):
            if "bind-address-ipv4" in line:
                line = '    "bind-address-ipv4": "{}",'.format(ip)
            sys.stdout.write(line)
    os.chown(conf.transmission_rc, perms.st_uid, perms.st_gid)
    print("Updated bind IP to {} at {}".format(ip, datetime.now()))
    return True


def daily():
    """Thread to count one day
    """
    sleep(86400)


def hourly():
    """Thread to count 10 min
       Sleep 10 min. The call to the PIA API should be at least once per hour.
    """
    sleep(1800)


def check_running(conf):
    """Check the processes *_command from the config file to see if they are
    running.
    """
    procs = [shlex.split(i[1])[0] for i in conf._asdict() if
             i[0].endswith("_command")]
    for proc in procs:
        res = Popen(["pgrep", "-f", proc], stdout=PIPE).communicate()[0]
        print(res)
        if not res:
            return False
    return True


def run():
    conf = get_config()
    day = Thread(target=daily)
    hour = Thread(target=hourly)
    while True:
        if not day.isAlive():
            # Restart the VPN once per day
            print("Daily restart of VPN at {}".format(datetime.now()))
            restart_vpn(conf)
            day = Thread(target=daily)
            day.start()
        if not hour.isAlive():
            # do port_update every 10 min, unless connection problems, then try
            # every 30 seconds.
            try:
                port_update(conf)
            except URLError:
                print("Port update failed: restarting "
                      "VPN at {}".format(datetime.now()))
                restart_vpn(conf)
                sleep(30)
            else:
                hour = Thread(target=hourly)
                hour.start()
        sleep(10)
        if not check_running(conf):
            restart_vpn(conf)


if __name__ == "__main__":
    run()
