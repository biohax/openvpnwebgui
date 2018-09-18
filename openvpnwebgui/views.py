import datetime
import glob
import os
import re
import select
import subprocess
from enum import Enum

from django.http import JsonResponse
from django.shortcuts import render

TIMEOUT = 30000 #msec


def start_vpn(request):
    vpn = request.GET.get('vpn', None)

    # Kill previous processes
    #TODO sudo killall openvpn


    os.chdir("/etc/openvpn/")

    cmd = "sudo openvpn /etc/openvpn/{vpn}".format(vpn=vpn) #TODO dir as var

    process_start = datetime.datetime.now()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    console_output = ""
    poll_obj = select.poll()
    poll_obj.register(process.stdout, select.POLLIN)

    Status = Enum('Status', 'success failed timeout')
    state = None
    time_left = lambda: (process_start + datetime.timedelta(milliseconds=TIMEOUT)) > datetime.datetime.now()

    while not state:
        poll_result = poll_obj.poll(0)
        if poll_result:
            line = process.stdout.readline().decode("utf-8")
            console_output += line
            print(line)
            if "Initialization Sequence Completed" in line: state = Status["success"]
            elif not time_left(): state = Status["timeout"]
            elif "ERROR" in line: state = Status["failed"]

    status_code = 200 if state == Status["success"] else 500

    data = {
        'status': state.name,
        'console': console_output,
    }
    return JsonResponse(data, status=status_code)


def vpns(request):
    path="/etc/openvpn/"  # insert the path to your directory
    vpn_file_list = glob.glob(path + '*.ovpn')


    vpn_list = []
    for vpn in vpn_file_list:
        vpn = os.path.basename(vpn)   # Only filename
        #print(vpn)
        regex = r"([a-z-_]+)([0-9]+)(\..+\.)([a-z]+)([0-9]+)"
        regex = r"([^0-9]+)([0-9]+)\.(.+)\.([a-z]+)([0-9]+)"
        #print(re.findall(regex, vpn, re.I)[0])
        country, nr, kaka, protocol, port = re.findall(regex, vpn, re.I)[0]
        vpn_list.append({
            "url": vpn,
            "country": country,
            "nr": nr,
            "protocol": protocol,
            "port": port
        })

    return render(request, 'vpns.html', {'vpns': vpn_list})