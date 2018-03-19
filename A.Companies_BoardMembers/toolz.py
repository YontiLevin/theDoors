import pandas as pd


def save2disk(links, failures, parent_path):
    import os

    for folder in ['appointments', 'carriers', 'failures']:
        path2folder = '{}/{}'.format(parent_path, folder)
        os.makedirs(path2folder, exist_ok=True)

    for year in links:
        apps = links[year]['appointments']
        carrs = links[year]['carriers']
        print("from {} to {} - current count: apps:{} , carrs: {}".format(year, year+1, len(apps), len(carrs)))

        columns = ["date", "company_name", "action", "maya_link", "html_link"]
        appointments_df = pd.DataFrame(apps, columns=columns)
        appointments_df.drop_duplicates(subset=['html_link'])
        appointments_df.to_csv('{dir}/appointments/{year}.csv'.format(dir=parent_path, year=year))

        carriers_df = pd.DataFrame(carrs, columns=columns)
        carriers_df.drop_duplicates(subset=['html_link'])
        carriers_df.to_csv('{dir}/carriers/{year}.csv'.format(dir=parent_path, year=year))

    for year in failures:
        fails = failures[year]

        columns = ["start_date", "end_date", "page_num"]
        failures_df = pd.DataFrame(fails, columns=columns)
        failures_df.to_csv('{dir}/failures/{year}.csv'.format(dir=parent_path, year=year))

