
import os,socket,struct,json,re

def str_d(value):
    # Only allow utf-8 characters
    #  https://stackoverflow.com/questions/26541968/delete-every-non-utf-8-symbols-froms-string
    return bytes(value, 'utf-8').decode('utf-8','ignore')

# Removes invalid charaters for ISY Node description
def get_valid_node_name(name):
    # Remove <>`~!@#$%^&*(){}[]?/\;:"'` characters from name
    return re.sub(r"[<>`~!@#$%^&*(){}[\]?/\\;:\"']+", "", str_d(name).lower())

def get_server_data(logger):
    # Read the SERVER info from the json.
    try:
        with open('server.json') as data:
            serverdata = json.load(data)
    except Exception as err:
        logger.error('harmony_hub_funcs:get_server_data: failed to read hubs file {0}: {1}'.format('server.json',err), exc_info=True)
        return False
    data.close()
    # Get the version info
    try:
        version = serverdata['credits'][0]['version']
    except (KeyError, ValueError):
        logger.info('Version not found in server.json.')
        version = '0.0.0.0'
    # Split version into two floats.
    sv = version.split(".");
    v1 = 0;
    v2 = 0;
    if len(sv) == 1:
        v1 = int(v1[0])
    elif len(sv) > 1:
        v1 = float("%s.%s" % (sv[0],str(sv[1])))
        if len(sv) == 3:
            v2 = int(sv[2])
        else:
            v2 = float("%s.%s" % (sv[2],str(sv[3])))
    serverdata['version'] = version
    serverdata['version_major'] = v1
    serverdata['version_minor'] = v2
    return serverdata