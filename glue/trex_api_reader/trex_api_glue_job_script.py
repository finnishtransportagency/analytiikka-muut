import requests
import json
import boto3
import sys
import time
from datetime import datetime, timedelta, date
from awsglue.utils import getResolvedOptions


###### Functions ######
def log_print(message):
    ''' Print message with timestamp information
        Args:
            - message: string to print to output log
    '''
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + ' - ' + message)

def get_oids(rakenteet, api_url):
    ''' Read OID's for strucures that have been updated from taitorakennerekisteri API
        Args:
            - rakenteet: dict having structure type and date after which the updates will be read
            - api_url: url to the API
        Returns:
            - oid_lists: dict where there is a list of oid's that have updates, for every structure type
    '''
    log_print('Get OIDs for all structures from API')
    
    oid_lists = {}
    for rakenne, date in rakenteet.items():
        response = requests.get(api_url + 'muutokset/' + rakenne + '?paivamaara=' + date)
        response.raise_for_status()
        oidt = json.loads(response.content.decode('utf-8'))['oidt']
        oid_lists[rakenne] = oidt
    
    log_print('Oids for all structures ok')
    return oid_lists

def current_milli_time():
    """ Generates timestamp strings.
    Returns:
        Current time in milliseconds.
    """
    return str(int(round(time.time() * 1000)))

def get_export_key(rakenne, endpoint):
    ''' Generate export file name in ADE format
        Args:
            - rakenne: The structure type
            - endpoint: E.g. yleistiedot or kunto
        Returns:
            - export_key: key in format ADE_entity/table.ADE_entity.currenttime.batch.currenttime.fullscanned.true.json
    '''
    milli_time = current_milli_time()
    entity = 'trex_' + rakenne + '_' + endpoint
    export_key = entity + '/table.' + entity + '.' + milli_time + '.batch.' + milli_time + '.fullscanned.true.json'
    return export_key

def read_kuntotiedot(oidt, api_url, bucket):
    ''' Read kunto tiedot from API and write them to s3 bucket
        Args:
            - oidt: dict having structure type and list of oid's to be read
            - api_url: Url to API
            - bucket: bucket name where to write the results
    '''
    log_print('Reading kuntotiedot')
    s3 = boto3.client('s3')
    for rakenne in oidt:
        log_print('Reading kuntotiedot for ' + rakenne)
        try:
            r = requests.get(api_url + 'kunto/' + rakenne)
            if r.status_code == 404:
                # Not all structure types have this API service
                r.raise_for_status()
        except Exception as e:
            # No kunto API for this structure type so move into the next one
            log_print(str(e))
            log_print('No kuntotiedot for ' + rakenne)
            continue
        else:
            kunto_data = ''
            for oid in oidt[rakenne]:
                resp = requests.get(api_url + 'kunto/' + rakenne + '?oid=' + oid)
                resp.raise_for_status()
                data = resp.content.decode('utf-8')
                kunto = '{"oid":"' + oid + '","kuntotiedot":' + data + '}'
                kunto_data += kunto + '\n'

            key = get_export_key(rakenne, 'kunto')
            s3.put_object(Body=kunto_data.encode('utf-8'), Bucket=bucket, Key=key)
            log_print('Kuntotiedot read and written for ' + rakenne)
                
    log_print('Kunto data written to s3')

def read_yleistiedot(oidt, api_url, bucket):
    ''' Read yleistiedot from API and write to s3 bucket
        Args:
            - oidt: dict having structure type and list of oid's to be read
            - api_url: Url to API
            - bucket: bucket name where to write the results
    '''
    log_print('Reading yleistiedot')
    
    for rakenne in oidt:
        log_print('Reading yleistiedot for ' + rakenne)
        yleis_data = ''
        for oid in oidt[rakenne]:
            resp = requests.get(api_url + 'yleistiedot/' + rakenne + '?oid=' + oid)
            resp.raise_for_status()
            data = resp.content.decode('utf-8')
            yleis_data += data + '\n'
        
        s3 = boto3.client('s3')
        key = get_export_key(rakenne, 'yleistiedot')
        s3.put_object(Body=yleis_data.encode('utf-8'), Bucket=bucket, Key=key)
        log_print(rakenne + ' yleistiedot written to S3.')
    
    log_print('Yleistiedot data written to s3')


###### Script #######
args = getResolvedOptions(sys.argv, ['rakenteet', 'target_bucket', 'api_url'])
log_print('Get arguments from lambda: ' + str(args))
target_bucket = args['target_bucket']
api_url = args['api_url']
rakenteet = json.loads(args['rakenteet'])

oidt = get_oids(rakenteet, api_url)

read_yleistiedot(oidt, api_url, target_bucket)
read_kuntotiedot(oidt, api_url, target_bucket)

log_print('API read done.')
