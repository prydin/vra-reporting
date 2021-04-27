import requests
import argparse
from datetime import datetime, timedelta
from urllib.parse import quote
from functools import lru_cache
import csv

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

@lru_cache(1000)
def get_template_name(blueprintId, catalogItemId):
    if not blueprintId or (blueprintId != 'inline-blueprint'):
        response = requests.get(args.url + '/blueprint/api/blueprints/%s' % blueprintId, headers=headers, verify=verify)
    else:
        response = requests.get(args.url + '/catalog/api/items/%s' % catalogItemId, headers=headers, verify=verify)
    if response.status_code != 200:
        return "*UNKNOWN*"
    return response.json()['name']

def get(url):
    response = requests.get(args.url + url, headers=headers, verify=verify)
    if response.status_code != 200:
        raise Exception("Error communicating with server: %d %s" % (response.status_code, response.content.decode()))
    return response.json()



def process_deployments(rng, w, deleted):
    page = 0
    while True:
        deploymentPayload = get('/deployment/api/deployments?createdAt=%s&size=100&page=%d&deleted=%s' % (rng, page, str(deleted).lower()))
        for d in deploymentPayload['content']:
            template = get_template_name(d.get('blueprintId'), d.get('catalogItemId'))
            requestPayload = get('/deployment/api/deployments/%s/requests?size=1000&deleted=%s' % (d['id'], str(deleted).lower()))
            for r in requestPayload['content']:
                w.writerow([template, r['name'], r['requestedBy'], r['status'], r['createdAt'], r['totalTasks'], r['completedTasks']])


        totalPages = int(deploymentPayload['totalPages'])
        if page >= totalPages - 1:
            break
        page += 1


parser = argparse.ArgumentParser(description='report.py');
parser.add_argument('--url', help='The vRA URL', required=True)
parser.add_argument('--token', type=str, help='The vRA API token', required=True)
parser.add_argument('--insecure', help='Skip cert validation', action='store_true')
parser.add_argument('--lookback', help='Number of days to report (default=30)', default='30')
parser.add_argument('--out', help='Output filename', required=True)

args = parser.parse_args()
if args.help:
    parser.print_usage()
    exit(0)
verify=not args.insecure

payload = {
    "refreshToken": args.token
}
response = requests.post(args.url + "/iaas/api/login", json=payload, headers=headers, verify=verify)
headers["Authorization"] = "Bearer " + response.json()["token"]

# List cloud templates
now = datetime.utcnow()
rng = quote('[%s.000Z,%s.000Z]' % ((now-timedelta(days=int(args.lookback))).isoformat('T','seconds'), now.isoformat('T', 'seconds')))

with open(args.out, 'w', newline='') as csvfile:
    w = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, dialect='excel')
    w.writerow(['template', 'type', 'requester', 'status', 'createdAt', 'totalTasks', 'successfulTasks'])
    process_deployments(rng, w, False)
    process_deployments(rng, w, True)



