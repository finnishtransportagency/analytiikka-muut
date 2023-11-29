import requests
import json
import boto3
import os
import time
from datetime import datetime, timedelta, date

def get_state(bucket, rakenteet, rakenteet_file):
    ''' Get dates after which to get updates for every structure type
        If structure type have not been read from API before get updates after 1900-01-01
        Otherwise after yesterday
        Args:
            - bucket: bucket, where the information of structure types that were read yesterday, is kept
            - rakenteet: structure types to be read from trex api
            - rakenteet_file: file that includes the structure types that were read yesterday from trex api
        Returns:
            - dates: dict where there is a date (yyyy-mm-dd) for every structure type from where to get the updates from trex api
    '''
    print('Get endpoints that have been read yesterday')
    s3 = boto3.client('s3')
    try:
        rak_eilen = s3.get_object(Bucket=bucket, Key=rakenteet_file)['Body'].read().decode('utf-8').split(',')
        dates = {}
        for rakenne in rakenteet.split(','):
            if rakenne in rak_eilen:
                dates[rakenne] = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
            else:
                dates[rakenne] = '1900-01-01'
        print("Dates to read updates after per structure type: " + str(dates))
        # Update rakenteet file
        s3.put_object(Bucket=bucket, Key=rakenteet_file, Body=rakenteet.encode('utf-8'))
        return dates
    except Exception as e:
        print(e)
        # No rakenteet_file exists because the API is read for the first time or something else
        print('Did not find file of engineering structures yesterday. Create file:')
        dates = {}
        for rakenne in rakenteet.split(','):
            dates[rakenne] = '1900-01-01'
        s3.put_object(Bucket=bucket, Key=rakenteet_file, Body=rakenteet.encode('utf-8'))
        print(rakenteet_file + ' containing "' + rakenteet + '"')
        return dates

def get_oids(dates, api_url):
    ''' Read OID's for strucures that have been updated from taitorakennerekisteri API
        Args:
            - dates: dict having structure type and date after which the updates will be read
            - api_url: url to the API
        Returns:
            - oid_lists: dict where there is a list of oid's that have updates for every structure type
    '''
    print('Get OIDs for all structures from API')
    
    oid_lists = {}
    for rakenne, date in dates.items():
        response = requests.get(api_url + 'muutokset/' + rakenne + '?paivamaara=' + date)
        response.raise_for_status()
        oidt = json.loads(response.content.decode('utf-8'))['oidt']
        oid_lists[rakenne] = oidt
    
    print('Oids for all structures ok')
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
    print('Reading kuntotiedot')
    s3 = boto3.client('s3')
    for rakenne in oidt:
        print('Reading kuntotiedot for ' + rakenne)
        try:
            r = requests.get(api_url + 'kunto/' + rakenne)
            if r.status_code == 404:
                # Not all structure types have this API service
                r.raise_for_status()
        except Exception as e:
            # No kunto API for this structure type so move into the next one
            print(e)
            print('No kuntotiedot for ' + rakenne)
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
            print('Kuntotiedot read and written for ' + rakenne)
                
    print('Kunto data written to s3')

def read_yleistiedot(oidt, api_url, bucket):
    ''' Read yleistiedot from API and write to s3 bucket
        Args:
            - oidt: dict having structure type and list of oid's to be read
            - api_url: Url to API
            - bucket: bucket name where to write the results
    '''
    print('Reading yleistiedot')
    
    for rakenne in oidt:
        print('Reading yleistiedot for ' + rakenne)
        yleis_data = ''
        for oid in oidt[rakenne]:
            resp = requests.get(api_url + 'yleistiedot/' + rakenne + '?oid=' + oid)
            resp.raise_for_status()
            data = resp.content.decode('utf-8')
            yleis_data += data + '\n'
        
        s3 = boto3.client('s3')
        key = get_export_key(rakenne, 'yleistiedot')
        s3.put_object(Body=yleis_data.encode('utf-8'), Bucket=bucket, Key=key)
        print(rakenne + ' yleistiedot written to S3.')
    
    print('Yleistiedot data written to s3')

def start_glue_job(job_name, arguments):
    ''' Start Glue Job Run
        Args:
            - job_name: the name of the glue job to be run
            - arguments: list of parameter values to pass to glue job run
                (structure types and dates after which to get updates, target_bucket, api_url)
    '''
    glue = boto3.client('glue')
    parameters = {'--rakenteet': arguments[0], '--target_bucket': arguments[1], '--api_url': arguments[2]}
    job_run = glue.start_job_run(JobName = job_name, Arguments=parameters)
    print('Started glue job.')
    print('Passed parameters: ' + str(parameters))
    print(job_run)


def read_public_api(url, bucket):
    ''' Read public api and put file to file load bucket
        Args:
            - url: where to read data from
            - bucket: where to load data
    '''
    print('Read public api and put file to file-load bucket...')
    try:
        r = requests.get(url)
        r.raise_for_status()
        s3 = boto3.client('s3')
        millitime = current_milli_time()
        key = f'trex_silta_avoin/table.trex_silta_avoin.{millitime}.batch.{millitime}.fullscanned.true.delim.comma.skiph.1.csv'
        s3.put_object(Bucket=bucket, Key=key, Body=r.content)
        print(f'{key} written into {bucket}.')
    except Exception as e:
        print(e)


def read_tiira_api(url, bucket):
    ''' Read tiira api and put file into file load bucket
        Args:
            - url: where to read data from
            - bucket: where to load data
    '''
    print('Read tiira api from trex...')
    outdata = []
    url_silta = url + 'rakenteet?tuloksia-per-sivu=5000&sivu='
    page = 1
    total = 1
    last_count = 0
    while last_count < total:
        # in case needed, two retrys for the request
        for i in list(range(3)):
            r = requests.get(url_silta + str(page))
            print(f'Request: {url_silta}{page}, Status code: {r.status_code}')
            if r.status_code == 200:
                data = json.loads(r.content.decode('utf-8'))
                last_count = data['aloitus'] + len(data['tulokset'])
                total = data['lukumaara']
                outdata += data['tulokset']
                break
            else:
                if i == 2:
                    print('No success in three tries...')
                    r.raise_for_status()
                print('Error in api request. Retry after 5 secs.')
                time.sleep(5)
        print(f'Now {len(outdata)} rows gotten from api.')
        page += 1
    
    s3 = boto3.client('s3')
    s3_data = ',\n'.join([json.dumps(x) for x in outdata]) + '\n'
    millitime = current_milli_time()
    key = f'trex_silta_tiira/table.trex_silta_tiira.{millitime}.batch.{millitime}.fullscanned.true.json'
    s3.put_object(Bucket=bucket, Key=key, Body=s3_data.encode('utf-8'))
    print(f'File {key} written into {bucket}.')

    print('Read koodisto from trex tiira api...')
    resp = requests.get(f'{url}koodisto')
    key_koodisto = f'trex_koodisto_tiira/table.trex_koodisto_tiira.{millitime}.batch.{millitime}.fullscanned.true.json'
    try:
        s3.put_object(Bucket=bucket, Key=key_koodisto, Body=resp.content)
        print(f'File {key_koodisto} written into {bucket}.')
    except Exception as e:
        print('-'*100)
        print(e)
        print('-'*100)


def lambda_handler(event, context):
    print('Start')
    print('Get env variables')
    landing_bucket = os.environ['FILE_LOAD_BUCKET']
    api_bucket = os.environ['API_STATE_BUCKET']
    rakenteet = os.environ['RAKENTEET'] # the structure type to be read is controlled in the parameters files
    glue_job_name = os.environ['GLUE_JOB_NAME']
    api_url = os.environ['TREX_API_URL']
    public_api_url = os.environ['PUBLIC_API_URL']
    tiira_api_url = os.environ['TIIRA_API_URL']
    rakenteet_file = 'rakenteet.txt' # structure types that were read yesterday from trex api: 'structure1,strucutre2,...,structure_n'
    print('Env vars gotten')

    read_public_api(public_api_url, landing_bucket)
    read_tiira_api(tiira_api_url, landing_bucket)
    
    # Get dates after which to get updates for every structure type
    dates = get_state(api_bucket, rakenteet, rakenteet_file)
    
    # get list oid's (for those structures that have been updated since the last time reading the API)
    oidt = get_oids(dates, api_url)
    
    # get the number of strucures that have been updated
    total_count = 0
    for key in oidt:
        total_count += len(oidt[key])
    print('Structures updated since last API read in total: ' + str(total_count))
    
    if total_count > 800:
        print('So many structures to get from API that get them by glue to avoid lambda timeout.')
        # Start glue job to get updated structures, pass dates to let the job know which structure types and after which date to get from API, pass also target_bucket and api_url
        start_glue_job(glue_job_name, [json.dumps(dates), landing_bucket, api_url])
    else:
        read_yleistiedot(oidt, api_url, landing_bucket)
        read_kuntotiedot(oidt, api_url, landing_bucket)
    
    print('End')