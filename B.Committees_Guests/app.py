# IMPORTS
import os
import pandas as pd
import re
from tqdm import tqdm
from datetime import date
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
    rows = {str(y): [] for y in range(2004, 2019)}
    cols = ['full_name', 'job_title', 'company', 'meeting_id', 'meeting_title', 'meeting_date', 'reference_link']
    for meeting_id, meeting_file_path in tqdm(_get_files_path(protocols_path)):
        committee_id, meeting_date, meeting_title, session_content, reference, year = _get_meeting_info(meetings_info, meeting_id)
        if committee_id is None:
            continue
        meeting_title = meeting_title if type(meeting_title) is str else session_content
        guests = _get_meeting_guests(meeting_file_path)
        # TODO extract knesset members in committee
        for full_name, job_title, work_place in guests:
            guest_tuple = (full_name, job_title, work_place, meeting_id, meeting_title, meeting_date, reference)
            rows[year].append(guest_tuple)
    for year in rows:
        df = pd.DataFrame(rows[year], columns=cols)
        save_guests_path = 'data/guests/{}'.format(date.today().__str__())
        os.makedirs(save_guests_path, exist_ok=True)
        df.to_csv(save_guests_path+'/{}.csv'.format(year))





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
    year = meeting_info[24][-4:]
    return meeting_info[1], meeting_info[24], meeting_info[3], meeting_info[4], meeting_info[31], year


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
    guests = [g for g in _parse_rows(guests_rows)]
    return guests


def _parse_rows(guests_rows):
    for row in guests_rows:
        row_parts = re.split(r',| - ', row)
        full_name, valid, job_title = _parse_full_name(row_parts[0])
        if not valid or len(row_parts) == 1:
            continue
        # TODO verify if workplace in companies file
        work_place = row_parts[-1]
        if len(row_parts) > 2:
            job_title = row_parts[1]

        yield full_name, job_title, work_place


def _parse_full_name(full_name_raw):
    parts = re.split('\s+', full_name_raw)
    valid = False
    full_name = None
    job_title = None
    first_name = []
    last_name = []
    for p in parts:
        if p in first_names and not len(first_name):
            first_name = [p]
            valid = True
        elif p in last_names or '-' in p:
            last_name.append(p)
        else:
            job_title = p
    if valid:
        full_name = ' '.join(first_name + last_name)

    return full_name, valid, job_title

if __name__ == '__main__':
    path2meetings_info = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/committee-meetings.csv'
    path2firstnames = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/lexicons/firstnames.txt'
    path2lastnames = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/lexicons/lastnames.txt'
    path2companies = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/lexicons/companies.csv'
    _load_globals(path2meetings_info, path2firstnames, path2lastnames, path2companies)

    path2protocols = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/committees_csvs'
    extract_guests_from_meetings(path2protocols, path2meetings_info)
