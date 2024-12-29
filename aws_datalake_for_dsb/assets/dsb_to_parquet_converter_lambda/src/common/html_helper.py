from datetime import datetime
import re
import pandas as pd
from pyquery import PyQuery as pq


def parse_dsb_html_file(filename):
    """
    This function creates dataframe from HTML file of DSB Vertretungsplan
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

    tables[1].insert(0, "Datum", date)
    tables[1].insert(0, "Wochentag", weekday)
    tables[1].insert(len(tables[1].columns), "Stand", last_update[1].strip())

    return tables[1]