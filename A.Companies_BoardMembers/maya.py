from datetime import timedelta, date
from tqdm import tqdm
import requests
from time import sleep
from lxml.html import fromstring
import pandas as pd
from extraction_toolz import Tofes
import os


def retrieve_links(starting_at, up2):

    links_by_year = {}
    failures_by_year = {}
    today = date.today()
    this_year = today.year
    if up2 <= starting_at:
        up2 = starting_at + 1
    top_loop = tqdm(range(starting_at, up2), leave=True)
    for year in top_loop:
        top_loop.set_description('year: {}'.format(year))
        start_d = date(year, 1, 1)
        end_d = date(year, 12, 31)
        if year == this_year:
            end_d = today - timedelta(7)

        appointments = []
        carriers = []
        failures = []

        for start, end in tqdm(_daterange(start_d, end_d), leave=False, position=0):
            results = _scrape(start, end, 1)
            page_count = results[2]
            appointments, carriers, failures = _postprocess_scrapes(appointments, carriers, failures,
                                                                    results, start, end)
            for page_num in tqdm(range(2, page_count + 1), desc='{} - {}'.format(start, end), leave=False, position=0):
                results = _scrape(start, end, page_num)
                appointments, carriers, failures = _postprocess_scrapes(appointments, carriers, failures,
                                                                        results, start, end)

        links_by_year[year] = {'appointments': appointments,
                               'carriers': carriers}
        failures_by_year[year] = failures

    return links_by_year, failures_by_year


def extract_info_from_links(links_by_year, links_path, save_extractions_path):

    cols = ['FULLNAME', 'JOB_DESC', 'DATE', 'COMPANY_NAME', 'PRIOR_JOBS', 'FULL_ACTION_DESC', 'FORM_NUM', 'PUB_DATE', 'REF_LINK']
    os.makedirs(save_extractions_path, exist_ok=True)

    for year in tqdm(links_by_year):
        print(f'\nprocessing {year}...')
        data = _get_csv_data('appointments', year, links_path)
        iterator = tqdm(enumerate(data.iterrows()), leave=False, position=0, total=data.shape[0])
        rows = []
        for i, data in iterator:
            sleep(0.5)
            # if i > 3:
            #     break
            item = data[1]
            tofes_link = item.html_link
            if tofes_link == 'nan' or type(tofes_link) != str or len(tofes_link) < 10 or tofes_link.endswith('.pdf') or '<' in tofes_link:
                continue

            item_info = {'year': year,
                         'action': item.action,
                         'company_name': item.company_name,
                         'maya_link': item.maya_link,
                         'tofes_link': tofes_link}

            try:
                tofes = Tofes(item_info)
                if not tofes.status or not tofes.valid_report_num:
                    continue
                tofes._date_published = tofes.date_published or item.date
                rows.append(tofes.extracted_info)
            except:
                iterator.write(tofes_link, end=' ')

        df = pd.DataFrame(rows, columns=cols)
        df.to_csv('{}/{}.csv'.format(save_extractions_path, year))


def extract_info_from_links_slim(links_by_year, links_path, save_extractions_path):
    cols = ['FULLNAME', 'GENDER', 'JOB_DESC', 'DATE', 'COMPANY_NAME', 'REF_LINK']
    os.makedirs(save_extractions_path, exist_ok=True)

    for year in links_by_year:
        print(f'\nprocessing {year}...')
        # df = pd.DataFrame(columns=cols)
        data = _get_csv_data('appointments', year, links_path)
        iterator = tqdm(enumerate(data.iterrows()), leave=False, position=0, total=data.shape[0])
        rows = []
        for i, data in iterator:
            sleep(0.5)
            # if i > 3:
            #     break
            item = data[1]
            tofes_link = item.html_link
            if tofes_link == 'nan' or type(tofes_link) != str or len(tofes_link) < 10 or tofes_link.endswith(
                    '.pdf') or '<' in tofes_link:
                continue

            item_info = {'year': year,
                         'action': item.action,
                         'company_name': item.company_name,
                         'maya_link': item.maya_link,
                         'tofes_link': tofes_link}

            try:
                tofes = Tofes(item_info)
                if not tofes.status or not tofes.valid_report_num:
                    continue
                tofes._date_published = tofes.date_published or item.date
                for row in tofes.extracted_info_slim():
                    rows.append(row)
            except:
                iterator.write(tofes_link, end=' ')

        df = pd.DataFrame(rows, columns=cols)
        df.to_csv('{}/{}.csv'.format(save_extractions_path, year))


# INNER TOOLZ

# DATE GENERATOR
def _daterange(d1, d2):
    days = int((d2 - d1).days)
    for delta1 in range(0, days + 7, 7):
        delta2 = delta1 + 7
        if delta2 > days:
            delta2 = days
        st = str(d1 + timedelta(delta1)).replace(' ', 'T')
        ed = str(d1 + timedelta(delta2)).replace(' ', 'T')
        yield st, ed


def _scrape(start_date, end_date, page_num):

    req = _format_req(start_date, end_date, page_num)
    res = requests.get(req)

    if res.status_code != 200:
        sleep(1)
        return [],[], 0, True

    doc = fromstring(res.text)
    if page_num == 1:
        try:
            count = _get_page_count(doc)
        except:
            count = 0
    else:
        count = 0

    feedItems = doc.find_class("feedItem ng-scope")

    apps = []
    carrs = []
    for feedItem in feedItems:
        tmp = _find_class_wrapper(feedItem, "messageContent ng-binding")
        text = tmp.text_content()
        if any(title in text for title in [u'מינוי', u'הנהלה ונושאי משרה']):
            root = tmp.getparent()
            company = _find_class_wrapper(root, "feedItemCompany ng-scope")
            date_el = _find_class_wrapper(root, "feedItemDate")
            maya_link = base_url + tmp.get('href')
            item = {"date": date_el.text_content(),
                    "company_name": company[0][0].text_content(),
                    "action": tmp.get('title'),
                    "maya_link": maya_link,
                    "html_link": _get_html_link(maya_link)}

            if u'מצבת ליום' in text:
                carrs.append(item)
            else:
                apps.append(item)
    sleep(0.01)
    return apps, carrs, count, False


def _postprocess_scrapes(appointments, carriers, failures, results, start, end):
    apps, carrs, page_count, failed = results
    if failed:
        failures.append({'start': start, 'end': end, 'page': 1})
    appointments += apps
    carriers += carrs
    return appointments, carriers, failures


def _format_req(start_date, end_date, page_num):
    formated_req = \
        splash + base_url + page_url + \
        filters["start_date"].format(start_date=start_date) + \
        filters["end_date"].format(end_date=end_date) + \
        filters["page"].format(page_num=page_num) + \
        filters["events"] + \
        wait_time.format(time=1)
    return formated_req


def _find_class_wrapper(src, class_name):
    if src is None:
        return None
    cls = src.find_class(class_name)
    if len(cls):
        return cls[0]
    return None


def _get_page_count(doc):
    pages = _find_class_wrapper(doc, 'feedItem feedPager')
    page_list = _find_class_wrapper(pages, "pagination")
    count = int(page_list[len(page_list) - 6].text_content())
    return count


def _get_html_link(link):
    count = 0
    # why 3? why why?
    while count < 3:
        req = splash + link + wait_time.format(time=0.25+count*0.5)
        res = requests.get(req)
        count += 1
        if res.status_code != 200:
            sleep(0.5)
            continue

        doc = fromstring(res.text)
        msg = _find_class_wrapper(doc, "messageWrap")
        body = _find_class_wrapper(msg, 'messageBody')
        frame = _find_class_wrapper(body, "rptdoc ng-scope")
        if frame is not None:
            return frame.get('src')
        sleep(0.5)


def _get_csv_data(action, year, path2links):
    filename = '{}/{}/{}.csv'.format(path2links, action, year)
    df = pd.read_csv(filename)
    return df

# GLOBALZ

# URL FORMAT
splash = "http://localhost:8050/render.html?url="
base_url = "http://maya.tase.co.il/"
page_url = "reports/company"
filters = {
    "start_date": "?q=%7B%22DateFrom%22:%22{start_date}%22,",
    "end_date": "%22DateTo%22:%22{end_date}%22",
    "page": ",%22Page%22:{page_num}",
    "events": ",%22events%22:%5B600%5D,%22subevents%22:%5B620,605,603,601,602,621,604,606,615,613,611,612,622,614,616%5D%7D"
}
wait_time = '&timeout=10&wait={time}'