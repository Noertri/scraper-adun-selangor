import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
import re
import csv
from datetime import datetime


main_url = 'http://dewan.selangor.gov.my/dewan-negeri-selangor/'


@dataclass(repr=True)
class Result:
    name: str = ""
    position: str = "Member of the State Legislative Assembly (Ahli Dewan Undangan Negeri) | State Legislative Assembly (Dewan Undangan Negeri), Selangor"
    address: str = ""
    phone: str = ""
    fax: str = ""
    email: str = ""
    facebook: str = ""
    twitter: str = ""
    photo: str = ""


def send_request(sesi: httpx.Client, url: str):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6,ja;q=0.5',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    response = sesi.get(url, headers=headers)

    return response


def scraper(response: httpx.Response):
    print("Start to scrape web...")
    if response is not None:
        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.select(".zoom-anim-dialog")

        address_pattern = re.compile(r"Alamat:\s*(.+)")
        phone_pattern = re.compile(r"Tel:\s*(.+)")
        fax_pattern = re.compile(r"Faks:\s*(.+)")
        email_pattern = re.compile(r"E-mel:\s*(.+)")
        fb_pattern = re.compile(r"Facebook:\s*(.+)")
        twitter_pattern = re.compile(r"Twitter:\s*(.+)")

        results = []
        if items is not None:
            for item in items:
                _name = name.get_text(strip=True, separator=" ") if (name := item.select_one("h4")) is not None else ""
                _name = _name.replace("\u2019", "'").replace("\u2013", "-")
                _photo = photo if (photo := item.select_one(".thumb>img").get("src")) is not None else ""
                
                result = Result(
                    name=_name,
                    photo=_photo
                )

                for p in item.select(".col-sm-5>p"):
                    txt = p.get_text(strip=True, separator=" ")

                    if (_address := address_pattern.match(txt)):
                        result.address = _address.group(1)

                    if (_phone := phone_pattern.match(txt)):
                        result.phone = _phone.group(1)

                    if (_faks := fax_pattern.match(txt)):
                        result.fax = _faks.group(1)

                    if (_email := email_pattern.match(txt)):
                        result.email = _email.group(1)

                    if (_fb := fb_pattern.match(txt)):
                        result.facebook = _fb.group(1)

                    if (_twitter := twitter_pattern.match(txt)):
                        result.twitter = _twitter.group(1)

                results.append(asdict(result))

        file_name = "ADUN_Selangor_{0}.csv".format(datetime.now().strftime("%d%m%Y%H%M%S"))
        print(f"Save to {file_name}")
        with open(file_name, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=("name", "position", "address", "phone", "fax", "email", "facebook", "twitter", "photo"), delimiter=";")
            writer.writeheader()
            writer.writerows(results)
            f.close()
            print("Done!!!")


if __name__ == "__main__":
    with httpx.Client(verify=False) as client:
        r = send_request(client, main_url)
        scraper(r)
