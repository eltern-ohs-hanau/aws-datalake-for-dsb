from datetime import datetime
import re
import pandas as pd
from pyquery import PyQuery as pq
from aws_lambda_powertools import Logger

logger = Logger()

def parse_dsb_html_file(filename: str):
    """
    This function creates dataframe from HTML file of DSB Vertretungsplan
    """

    html = pq(filename=filename, encoding='iso-8859-1')
    title = html("div.mon_title").text()
    date = datetime.strptime(title.split()[0], "%d.%m.%Y")
    weekday = title.split()[1]
    assert weekday in ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

    tables = pd.read_html(filename, encoding='iso-8859-1')
    header = tables.pop(0).iat[0, -1]
    last_update = re.split('[Ss]tand:', header)

    for table in tables:
        try:
            # Check required columns of table
            assert "Klasse(n)" in table.columns
            assert "Art" in table.columns
            assert "Stunde" in table.columns
            assert "Fach" in table.columns
            assert "Raum" in table.columns

            for column in table.columns:
                table[column] = table[column].astype(str) #TODO Adding .str.decode('iso-8859-1') if there are invalid characters
            #TODO also this might be more elegant https://stackoverflow.com/questions/62016462/pandas-how-to-read-html-and-casting-all-fields-to-string
  
            table.insert(0, "Datum", date)
            table.insert(0, "Wochentag", weekday)
            table.insert(len(table.columns), "Stand", last_update[1].strip())
            return table

        except Exception as e:
            logger.warn("WARN: Skipping invalid table in file {}".format(filename))
            logger.warn(e)
    
    return pd.DataFrame()

def write_parqet_file(filename: str, dataframes: list):
    """
    This function writes list of dataframes to a Parquet file
    """
    try:
        pd.concat(dataframes, ignore_index=True, sort=False).to_parquet(filename, compression='gzip')
    except Exception as e:
        logger.error("ERROR: Writing following dataframes {}".format(dataframes))
        raise(e)
