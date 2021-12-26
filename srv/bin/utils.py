#!/usr/bin/python3.8
import os
import json
import packets.packets as packets
import packets.rreq as rreq
dirname = os.path.dirname(__file__)
log_file = os.path.join(dirname, 'log/service.log')

# print(dirname)
# print(log_file)


def prepareRouteRequest(obj):
    """[summary]

    Args:
        obj (dict): objects contains destination, 
    """
    print()
    
    # return
