# VERSION: 1.1
# AUTHORS: kjjejones44, sabal202

from html.parser import HTMLParser
from urllib.parse import urljoin, urlencode
from helpers import retrieve_url
from novaprinter import prettyPrinter
import json
import re


class bt4g(object):
    url = "https://bt4g.org/"
    name = "bt4g"
    supported_categories = {
        "all": "",
        "movies": "movie/",
        "tv": "movie/",
        "music": "audio/",
        "books": "doc/",
        "software": "app/",
    }

    class MyHTMLParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.is_in_container = False
            self.is_in_entry = False
            self.b_value = ""
            self.container_row_count = 0
            self.temp_result = {}
            self.results = []

        def feed(self, feed: str) -> None:
            super().feed(feed)
            return self.results

        def handle_starttag(self, tag, attrs):
            attr_dict = {x[0]: x[1] for x in attrs}
            if tag == "div":
                if not self.is_in_container and attr_dict.get("class", "") == "container":
                    self.is_in_container = True
            elif tag == "a":
                if self.is_in_container and all(x in attr_dict for x in ["title", "href"]):
                    self.is_in_entry = True
                    self.temp_result.update(attr_dict)
            elif tag == "b":
                if self.is_in_entry:
                    classname = attr_dict.get("class", "")
                    idname = attr_dict.get("id", "")
                    self.b_value = "filesize" if "cpill" in classname else idname

        def handle_endtag(self, tag):
            if tag == "div":
                self.is_in_entry = False

        def handle_data(self, data):
            if self.b_value != "":
                self.temp_result[self.b_value] = data
                if self.b_value == "leechers":
                    self.results.append(self.temp_result)
                    self.temp_result = {}
                self.b_value = ""

    def search(self, term, cat="all"):
        pagenumber = 1
        while pagenumber <= 10:
            result_page = self.search_page(term, pagenumber, cat)
            self.pretty_print_results(result_page)
            if len(result_page) < 15 or int(result_page[-1]["seeders"]) < 1:
                break
            pagenumber += 1

    def search_page(self, term, pagenumber, cat):
        try:
            query = f"{self.url}{self.supported_categories[cat]}search/{term}/byseeders/{pagenumber}"
            parser = self.MyHTMLParser()
            return parser.feed(retrieve_url(query))
        except Exception as e:
            return []

    def download_torrent(self, info):
        if "trackerlist" not in self.__dict__:
            self.trackerlist = json.loads(retrieve_url("https://downloadtorrentfile.com/trackerlist"))
        html = retrieve_url(info)
        magnet_match = re.search(r'(?<=com/hash/)([^"\?]+)\?name=([^"]*)?(?=")', html)
        magnet_hash = magnet_dn = None
        if magnet_match and magnet_match.groups():
            magnet_hash = magnet_match.groups()[0]
            magnet_dn = magnet_match.groups()[1]
            # print(magnet_hash, magnet_dn, info)
        magnet = f"magnet:?xt=urn:btih:{magnet_hash}&dn={magnet_dn}&{urlencode({'tr': self.trackerlist}, doseq=True)}"
        print(f"{magnet} {info}")

    def pretty_print_results(self, results):
        for result in results:
            temp_result = {
                "name": result["title"],
                "size": result["filesize"],
                "seeds": result["seeders"],
                "leech": result["leechers"],
                "engine_url": self.url,
                "link": urljoin(self.url, result["href"]),
            }
            prettyPrinter(temp_result)


if __name__ == "__main__":
    # bt4g().download_torrent("https://bt4g.org/magnet/07f5kZIDw0bvcLUnHv1FwJelosDMMhvWC")
    bt4g().search("how", cat="books")
