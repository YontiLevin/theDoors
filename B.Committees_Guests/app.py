# IMPORTS
import os
import pandas as pd
import re
from tqdm import tqdm

# GLOBALS
meetings_info = pd.DataFrame()
first_names = set()
last_names = set()
companies_info = pd.DataFrame()


def _load_globals(path2meetings_info, path2first_names, path2last_names, path2companies_info):
    global meetings_info, first_names, last_names, companies_info
    meetings_info = pd.read_csv(path2meetings_info)
    with open(path2first_names, 'r') as fns:
        first_names = set(fns.read().split('\n'))
    with open(path2last_names, 'r') as lns:
        last_names = set(lns.read().split('\n'))
    # companies_info = pd.read_csv(path2companies_info, encoding='latin-1')


def extract_guests_from_meetings(protocols_path, meetings_info_file):
    for meeting_id, meeting_file_path in tqdm(_get_files_path(protocols_path)):
        committee_id, meeting_date, meeting_title, session_content, reference = _get_meeting_info(meetings_info, meeting_id)
        if committee_id is None:
            continue
        meeting_title = meeting_title if type(meeting_title) is str else session_content
        guest_rows = _get_meeting_guests(meeting_file_path)
        guests = [g for g in _parse_rows(guest_rows)]





# INNER TOOLZ
def _get_files_path(path2parentfolder):
    for folder in os.listdir(path2parentfolder):
        for protocol in os.listdir(os.path.join(path2parentfolder, folder)):
            if protocol.endswith('.csv'):
                committee_id = protocol[:-4]
                yield committee_id, os.path.join(path2parentfolder, folder, protocol)


def _get_meeting_info(meetings_info, meeting_id):
    meeting_info = meetings_info.loc[meetings_info['id'] == int(meeting_id)].values
    if meeting_info.shape[0] == 0:
        return None, None, None
    meeting_info = meeting_info[0]

    return meeting_info[1], meeting_info[24], meeting_info[3], meeting_info[4], meeting_info[31]


def _get_meeting_guests(meeting_file_path):
    df = pd.read_csv(meeting_file_path)
    if 'header' not in df.columns:
        return []
    # get the row with index == מוזמנים
    relevant_row = df.loc[df['header'].isin(['מוזמנים', ':מוזמנים', 'מוזמנים:'])].values
    if relevant_row.shape[0] == 0:
        # No such rows where found
        return []
    text_block = relevant_row[0][1]
    if type(text_block) == float:
        return []
    guests_rows = [gr for gr in text_block.split('\n') if len(gr)]
    return guests_rows


def _parse_rows(guests_rows):
    for row in guests_rows:
        row_parts = re.split(r', | - ', row)
        if _verify_valid_name(row_parts[0]):
            yield row_parts
            continue
        print(row_parts[0])
    pass


def _verify_valid_name(full_name):
    name_parts = re.split('\s+', full_name)
    firstname = None
    lastname= []
    for p in name_parts:
        if p in first_names and firstname is None:
            name_type = 'FIRST'
            firstname = p
        elif p in last_names:
            name_type = 'LAST'
            lastname .append(p)
        else:
            name_type = 'OTHER'
        print(f'{p} is {name_type}')
    lastname = ' '.join(lastname)
    pass

if __name__ == '__main__':
    path2meetings_info = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/committee-meetings.csv'
    path2firstnames = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/lexicons/firstnames.txt'
    path2lastnames = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/lexicons/lastnames.txt'
    path2companies = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/lexicons/companies.csv'
    _load_globals(path2meetings_info, path2firstnames, path2lastnames, path2companies )

    path2protocols = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/committees_csvs'
    extract_guests_from_meetings(path2protocols, path2meetings_info)
