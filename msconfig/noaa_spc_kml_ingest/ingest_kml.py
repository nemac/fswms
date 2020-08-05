#!/usr/bin/env python

import ogr
import os
import os.path
import shutil
import datetime
import argparse
import subprocess


def build_ogr_url_path(d):
    base_url = 'https://www.spc.noaa.gov/climo/reports/'
    fn_tmpl = '{}_rpts.kmz'
    fmt_date = datetime.datetime.strftime(d, '%y%m%d')
    fn_zip = fn_tmpl.format(fmt_date)
    fn_kml = f'{fmt_date}_rpts.kml'
    p = os.path.join('/vsizip/vsicurl', base_url, fn_zip, fn_kml)
    return p


def get_dates(days_back):
    today = datetime.datetime.today()
    dates = [ today - datetime.timedelta(days=i) for i in range(0, days_back+1) ]
    return dates


def get_report_type_for_layer(name):
    if 'Tornado' in name:
        return 'tornado'
    if 'Wind' in name:
        return 'wind'
    if 'Hail' in name:
        return 'hail'


def process_layer(f, p, layer_index, date):
    # Get the OGR Layer
    layer = f.GetLayerByIndex(layer_index)
    layer_name = layer.GetName()
    layer_type = get_report_type_for_layer(layer_name)

    # Save the layer to an temporary sqlite file
    # Clean up the layer name with -nln to prevent SQL errors
    fn = os.path.basename(p)
    dst_path = './tmp/{}_{}.sqlite'.format(fn.rstrip('.kmz'), layer_type)
    c = 'ogr2ogr -overwrite -f "SQLite" -nln data {0} {1} "{2}"'.format(dst_path, p, layer_name)
    print('\n', c)
    os.system(c)

    # Add a new column for the report type
    c = 'ogrinfo -dialect "SQLITE" ' + \
                '-sql "ALTER TABLE data ADD COLUMN {1} STRING DEFAULT {0};" {2}'.format(
                layer_type, 'report_type', dst_path)
    print('\n', c)
    os.system(c)

    # Add a new column for the date
    # TODO use type Date for the date column
    c = 'ogrinfo -dialect "SQLITE" ' + \
                '-sql "ALTER TABLE data ADD COLUMN {1} STRING DEFAULT {2};" {3}'.format(
                layer_type, 'date', date.strftime('%y%m%d'), dst_path)
    print('\n', c)
    os.system(c)


def process_day_kml(p, d):
    # Open the KML file
    try:
        f = ogr.Open(p)
        layer_count = f.GetLayerCount()
        # For each layer in the file...
        for i in range(2, layer_count):
            process_layer(f, p, i, d)
    except Exception as err:
        print('Error processing file {}'.format(p))
        print(err)

def setup_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('days_back', help='Script fetches KML for this many days back in time from today')
    return parser


def make_tmp_dir():
    if not os.path.exists('./tmp'):
        print('Creating ./tmp directory...')
        os.mkdir('./tmp')

def put_results_in_db():
    '''
    Place contents of intermediate SQLite db into efetac postgis database
    Remove -append if the table does not already exist
    '''
    #c = '''source .env && ogr2ogr -append -skipfailures -f PostgreSQL -nln $TABLE PG:"dbname='$DB_NAME' host='localhost' port='$PG_PORT' user='$PG_USER' password='$PG_PASSWORD'" result.sqlite data'''
    c = './move_result'
    proc = subprocess.Popen(c, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    print(output)


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()
    days_back = int(args.days_back)
    make_tmp_dir()
    dates = get_dates(days_back)
    for d in dates:
        p = build_ogr_url_path(d)
        print('Fetching data from {}'.format(p))
        process_day_kml(p, d)
    # Move the first temp file and use it as the final result
    result_fn = 'result.sqlite'
    data_files = sorted(os.listdir('./tmp'))
    os.rename('./tmp/{}'.format(data_files[0]), result_fn)
    # Start at index 1 since we moved the first file
    for p in data_files[1:]:
        # Append the data
        c = 'ogr2ogr -append -f "SQLite" {} ./tmp/{} data'.format(result_fn, p)
        print('\n', c)
        os.system(c)
    shutil.rmtree('./tmp', ignore_errors=True)
    put_results_in_db()
    os.remove('result.sqlite')


if __name__ == '__main__':
    main()

