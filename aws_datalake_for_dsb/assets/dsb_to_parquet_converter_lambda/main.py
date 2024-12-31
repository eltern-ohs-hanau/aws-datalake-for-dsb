import os
import traceback
from datetime import datetime
import re
import pandas as pd
from pyquery import PyQuery as pq

##############################################################
# Sync local temp with S3 data
##############################################################

# mkdir -p ./temp/download
# aws sso login --profile stefan-ohs
# aws s3 sync s3://dsb-data-813986443542/download/ ./temp/download/ --profile stefan-ohs
# aws s3 sync ./temp/parquet/ s3://dsb-data-813986443542/parquet/ --profile stefan-ohs

##############################################################
# SQL for crawled Athena table
##############################################################
# select datum as datum2, max(parse_datetime(stand, 'd.M.yyyy HH:mm')) as max_stand FROM "test"."test-parquet" group by datum limit 100; 

# WITH
#   test_casted AS (
#    SELECT
#    DISTINCT *
#    , CAST(parse_datetime(stand, 'd.M.yyyy HH:mm') AS timestamp) stand_timestamp
#    , CAST(trim(coalesce(element_at(split(stunde, '-'),1),stunde)) AS integer) stunde_start
#    , CAST(trim(coalesce(element_at(split(stunde, '-'),2),stunde)) AS integer) stunde_ende
#    FROM
#      "test"."test-parquet"
# ) 
# , test_max AS (
#    SELECT
#      datum
#    , max(stand_timestamp) stand_max
#    FROM
#      test_casted
#    GROUP BY datum
# ) 
# SELECT test_casted.*, (test_casted.stunde_ende + 1 - test_casted.stunde_start) AS stunde_anzahl
# FROM
#   (test_casted
# LEFT JOIN test_max ON (test_casted.datum = test_max.datum))
# WHERE (stand_max = stand_timestamp)


def parse_dsb_html_file(filename):
    """
    This function creates dataframe from html file of DSB Vertretungsplan
    """

    html = pq(filename=filename, encoding='iso-8859-1')
    title = html("div.mon_title").text()
    date = datetime.strptime(title.split()[0], "%d.%m.%Y")
    weekday = title.split()[1]
    assert weekday in ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

    tables = pd.read_html(filename)
   
    # Check required columns of table
    assert "Klasse(n)" in tables[1].columns
    assert "Art" in tables[1].columns
    assert "Stunde" in tables[1].columns
    assert "Fach" in tables[1].columns
    assert "Raum" in tables[1].columns

    header = tables[0].iat[0, -1]
    last_update = re.split('[Ss]tand:', header)

    tables[1].insert(0, "Wochentag", weekday)
    tables[1].insert(len(tables[1].columns), "Stand", last_update[1].strip())

    # Cast all items to string to avoid conversion errors on columns containing partially integers
    result = tables[1].astype("string")

    result.insert(0, "Datum", date)

    return result

download_path = "./temp/download/"
for path in os.listdir(download_path):
    results = []
    for filename in os.listdir(os.path.join(download_path, path)):
        try:
            results.append(parse_dsb_html_file(os.path.join(download_path, path, filename)))
        except Exception as ex:
            print("ERROR: Could not read {}\n{}\n{}".format(filename, ex, traceback.format_exc()))

    if len(results):
        parquet_fullpath = os.path.join("./temp/parquet/", "{}.gzip".format(path))
        df = pd.concat(results, ignore_index=True, sort=False)
        print("\nTypes of data after conversion:\n", df.dtypes)
        df.to_parquet(parquet_fullpath, engine='fastparquet', compression='gzip')
        print("SUCCESS: Saved parquet {}".format(parquet_fullpath))
    else:
        print("WARNING: Could not find data for {}".format(path))