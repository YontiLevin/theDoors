from maya import retrieve_links, extract_info_from_links, extract_info_from_links_slim
from toolz import save2disk


if __name__ == "__main__":
    save_links_path = 'data/links/feb22_18'
    save_extractions_path = 'data/extractions/feb24_18/full'
    # links, failures = retrieve_links(starting_at=2017, up2=2018)
    # save2disk(links, failures, save_links_path)
    links = range(2004, 2019)
    extract_info_from_links(links_by_year=links,
                            links_path=save_links_path,
                            save_extractions_path=save_extractions_path)
    # extract_info_from_links_slim(links_by_year=links,
    #                              links_path=save_links_path,
    #                              save_extractions_path=save_extractions_path)
    # save2db()
