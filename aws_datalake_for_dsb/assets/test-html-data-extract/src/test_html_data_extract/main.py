import os
import re
import pandas as pd
from pyquery import PyQuery as pq


def parse_dsb_html_file(filename):
  print(filename)

  html = pq(filename=filename, encoding='iso-8859-1')
  day = html("div.mon_title").text()

  tables = pd.read_html(filename)

  header = tables[0].iat[0, -1]
  last_update = re.split('[Ss]tand:', header)

  tables[1].insert(0, "Stand", last_update[1].strip())
  tables[1].insert(0, "Datum", day.split()[0])
  tables[1].insert(0, "Wochentag", day.split()[1])

  return tables[1]

path = "./temp/20241010-050032_plans/"
results = [parse_dsb_html_file(os.path.join(path, filename)) for filename in os.listdir(path)]

print(pd.concat(results, ignore_index=True, sort=False).sort_values(['Datum', 'Klasse(n)'], ascending = [True, True]))