# IMPORTS


def save2datapackage(path2filesfolder, output_path):
    from datapackage import Package
    package = Package()
    package.infer('/'.join([path2filesfolder, '*.csv']))
    package.save(output_path)


if __name__ == '__main__':
    if __name__ == '__main__':
        # p2ff = '/home/yonti/Projects/theDoors/A.Companies_BoardMembers/data/extractions/feb24_18/full'
        # op = '/home/yonti/Projects/theDoors/A.Companies_BoardMembers/data/packages/maya_full_feb25_18.zip'
        guests_path = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/guests/2018-03-05'
        guests_out = '/home/yonti/Projects/theDoors/B.Committees_Guests/data/guests/2018-03-05.zip'
        save2datapackage(guests_path, guests_out)