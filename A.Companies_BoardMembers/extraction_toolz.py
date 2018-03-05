# -*- coding: utf-8 -*-
from itertools import product
import requests
from bs4 import BeautifulSoup


class Tofes(object):
    def __init__(self, link_info):

        self.valid_report_num = True
        self._type1_reports = ['ת091', 'ת093', 'ת304', 'ת306']
        self._type2_reports = ['ת090', 'ת307']

        self._action_title = link_info['action']
        self._company_name = link_info['company_name']
        self._maya_link = link_info['maya_link']
        self._tofes_link = link_info['tofes_link']
        self._status = True
        self._html = None
        self._report_num = None
        self._date_published = None
        self._fullname = None
        self._job_title = None
        self._job_desc = None
        self._starting_date = None
        self._education = None
        self._prior_jobs = None
        self._gender = None

        self.extract()

    def extract(self):
        self._set_html_()
        self._set_report_num_()
        self._set_date_published_()
        self._set_fullname_()
        self._set_job_title_()
        # self._set_job_desc_()
        self._set_starting_date_()
        self._set_education_()
        self._set_prior_jobs_()
        self._set_gender_()

    def print_results(self):
        print('report type - {0}'.format(self.report_num))
        print('date published - {0}'.format(self.date_published))
        print('action - {0}'.format(self._action_title))
        print('company - {0}'.format(self._company_name))
        print('fullname - {0}'.format(self.fullname))
        print('job - {0} / {1}'.format(self.job_title, self.job_desc))
        print('starting date - {0}'.format(self.starting_date))
        for tup in self.education:
            print(tup[0], tup[1], tup[2])
        for tup in self.prior_jobs:
            print(tup[0], tup[1], tup[2])

    # GETTERS
    @property
    def extracted_info(self):
        return [
            self.fullname,
            self.job_title,
            # self.job_desc,
            self.starting_date,
            self._company_name,
            ','.join(self.prior_jobs),
            self._action_title,
            self.report_num,
            self.date_published,
            self._tofes_link]

    def extracted_info_slim(self):
        yield [
            self.fullname,
            self.gender,
            self.job_title,
            self.starting_date,
            self._company_name,
            self._tofes_link
        ]

        for prior_job_tuple in self.prior_jobs:
            parts = prior_job_tuple[1:-1].split('##')

            job_desc, company, years = parts
            yield [
                self.fullname,
                self.gender,
                job_desc,
                years,
                company,
                self._tofes_link]

    @property
    def status(self):
        return self._status

    @property
    def html(self):
        return self._html

    @property
    def report_num(self):
        return self._report_num

    @property
    def date_published(self):
        return self._date_published

    @property
    def fullname(self):
        return self._fullname

    @property
    def gender(self):
        return self._gender

    @property
    def job_title(self):
        return self._job_title

    @property
    def job_desc(self):
        return self._job_desc

    @property
    def starting_date(self):
        return self._starting_date

    @property
    def education(self):
        return self._education

    @property
    def prior_jobs(self):
        return self._prior_jobs

    # SETTERS
    def _set_html_(self):
        res = requests.get(self._tofes_link)

        if res.status_code != 200:
            print(res.status_code)
            self._status = False
        else:
            page_text = res.content
            self._html = BeautifulSoup(page_text, 'html.parser')

    def _set_report_num_(self):
        self._report_num = self._html.find('span', {'fieldalias': 'MisparTofes'}).contents[0]
        if self._report_num not in self._type1_reports + self._type2_reports:
            self.valid_report_num = False

    def _set_date_published_(self):
        self._date_published = self._html.find('span', {'fieldalias': 'HeaderSendDate'})\
                                              .parent.contents[-1].replace('\r', '').replace('\n', '').replace('\t', '')

    def _set_fullname_(self):
        if not self.valid_report_num:
            self._fullname = None
        else:
            for shem in ['Shem', 'ShemPratiVeMishpacha', 'ShemPriatiVeMishpacha', 'ShemMishpahaVePrati',
                         'ShemRoeCheshbon', 'ShemRoehHeshbon']:
                try:
                    self._fullname = self._html.find('textarea', {'fieldalias': shem}).contents[0]
                    break
                except:
                    pass

    def _set_gender_(self):
        if not self.valid_report_num:
            self._gender = None
        else:
            for gen in ['Gender', 'Min', 'gender']:
                try:
                    gender = self._html.find('span', {'fieldalias': gen}).contents[0]
                    self._gender = 'man' if 'זכר' in gender else 'female'
                    break
                except:
                    pass

    def _set_job_title_(self):
        if self.report_num in self._type2_reports:
            self._job_title = u'רואה חשבון'
        elif not self.valid_report_num:
            self._job_title = None
        else:
            job_titles = ['Tafkid', 'Misra', 'HaTafkidLoMuna']
            for job_ttl in job_titles:
                try:
                    self._job_title = self._html.find('span', {'fieldalias': job_ttl}).contents[0]
                    break
                except:
                    pass

            if self.job_title is  None or ':' in self.job_title or 'אחר' in self.job_title:
                job_descs = ['TeurTafkid', 'LeloTeur', 'TeurHaTafkidLoMuna']
                for desc in job_descs:
                    try:
                        self._job_title = self._html.find('textarea', {'fieldalias': desc}).contents[0]
                        break
                    except:
                        pass

    def _set_job_desc_(self):
        if self.report_num in self._type2_reports:
            self._job_desc = u''
        elif not self.valid_report_num:
            self._job_desc = None
        else:
            job_descs = ['TeurTafkid', 'LeloTeur', 'TeurHaTafkidLoMuna']
            for desc in job_descs:
                try:
                    self._job_desc = self._html.find('textarea', {'fieldalias': desc}).contents[0]
                    break
                except:
                    pass

    def _set_starting_date_(self):
        if not self.valid_report_num:
            self._starting_date = None
        else:
            starting_dates = ['TaarichTchilatHaCehuna', 'TaarichTchilatCehuna', 'TaarichTehilatCehuna',
                              'TaarichTchilatHaKehuna', 'TaarichTchilatKehuna', 'TaarichTehilatKehuna']
            for date in starting_dates:
                try:
                    self._starting_date = self._html.find('span', {'fieldalias': date}).contents[0]
                    break
                except:
                    pass

    def _set_education_(self):
        if not self.valid_report_num:
            self._education = []
        else:
            education = ['Toar', 'ToarAcademi']
            kind = ['Tehum', 'Tchum']
            institute = ['ShemHamosadHaakademi', 'ShemHamosadHaacademi', 'ShemHaMosadHaAkademi', 'ShemHaMosadHaAcademi',
                         'ShemMosadAcademy', 'ShemMosadAcademi', 'ShemMosadAkademi', 'ShemMosadAkademy',
                         'ShemHamosadHaakademy', 'ShemHamosadHaacademy', 'ShemHaMosadHaAkademy', 'ShemHaMosadHaAcademy']
            degrees = []
            for ed in education:
                try:
                    toars = self._html.find_all('span', {'fieldalias': ed})
                    for x, t in enumerate(toars):
                        toar = t.contents[0]
                        toar_type = ''
                        for k in kind:
                            for tag in ['span', 'textarea']:
                                try:
                                    toar_type = self._html.find_all(tag, {'fieldalias': k})[x].contents[0]
                                except:
                                    pass
                        mosad = ''
                        for i in institute:
                            try:
                                mosad = self._html.find_all('textarea', {'fieldalias': i})[x].contents[0]
                            except:
                                pass
                        degrees.append((toar, toar_type, mosad))
                except:
                    pass
            self._education = degrees

    def _set_prior_jobs_(self):
        if not self.valid_report_num:
            self._prior_jobs = []
        else:
            job_titles = ['Tapkid', 'HaTafkidSheMila', 'Tafkid']
            job_places = ['MekomHaAvoda', 'MekomAvoda', 'MekomAvodah']
            job_periods = ['MeshechZmanSheMilaBaTafkid', 'MeshechZman', 'MeshechHaZmanSheMilaTafkid']
            jobs = []
            for job in job_titles:
                try:
                    prior_jobs = self._html.find_all('textarea', {'fieldalias': job})
                    for x, prior in enumerate(prior_jobs):
                        job = prior.contents[0]
                        job_place = ''
                        for p in job_places:
                            for tag in ['span', 'textarea']:
                                try:
                                    job_place = self._html.find_all(tag, {'fieldalias': p})[x].contents[0]
                                except:
                                    pass
                        job_period = ''
                        for z in job_periods:
                            for tag in ['span', 'textarea']:
                                try:
                                    job_period = self._html.find_all(tag, {'fieldalias': z})[x].contents[0]
                                except:
                                    pass

                        jobs.append(u'({}##{}##{})'.format(job, job_place, job_period))
                except:
                    pass
            self._prior_jobs = jobs


#############################################################################
def extras(html):
    birth_date = html.find('span', {'fieldalias': 'TaarichLeida'}).contents[0]
    print(birth_date)

    mispar = ['MisparZihuy', 'MisparZihui']
    posts = ['1', '']
    for misparzihui in product(mispar, posts):
        query_num = ''.join(list(misparzihui))
        try:
            identifier_num = html.find('span', {'fieldalias': query_num}).contents[0]
            query_type = 'Sug{}'.format(query_num)
            identifier_type = html.find('span', {'fieldalias': query_type}).contents[0]
            print(identifier_type, identifier_num)
            break
        except:
            pass

    ezrachut = ['Ezrachut', 'EzrahutSlashEretz1', 'EzrahutSlashEretz']

    for ezrach in ezrachut:
        try:
            citizenship = html.find('span', {'fieldalias': ezrach}).contents[0]
            print(citizenship)
            break
        except:
            pass


if __name__ == '__main__':
    item_info = {'year': 2018,
                 'action': 'appointment',
                 'company_name': 'test',
                 'maya_link': None,
                 'tofes_link': 'http://mayafiles.tase.co.il/RHtm/1079001-1080000/H1079270.htm'}

    tofes = Tofes(item_info)
    for j in tofes.extracted_info_slim():
        print(j)

