import os
import time

import requests
from bs4 import BeautifulSoup
import requests.exceptions

from data_import import get_all_sites_domain_names

# all_site_list =[
#     "aac.sfsu.edu",
#     "aapi.sfsu.edu",
#     "aas.sfsu.edu",
#     "academic.sfsu.edu",
#     "academicresources.sfsu.edu",
#     "access.sfsu.edu",
#     "accessalert.sfsu.edu",
#     "act.sfsu.edu",
#     "activities.sfsu.edu",
#     "advservices.sfsu.edu",
#     "advising.sfsu.edu",
#     "advisinghub.sfsu.edu",
#     "advisinglca.sfsu.edu",
#     "affordablelearning.sfsu.edu",
#     "africana.sfsu.edu",
#     "alumni.sfsu.edu",
#     "amed.sfsu.edu",
#     "anthropology.sfsu.edu",
#     "apiabiography.sfsu.edu",
#     "at.sfsu.edu",
#     "autism.sfsu.edu",
#     "basicneeds.sfsu.edu",
#     "budget.sfsu.edu",
#     "bursar.sfsu.edu",
#     "businessjapanese.sfsu.edu",
#     "cad.sfsu.edu",
#     "campusmemo.sfsu.edu",
#     "campusrec.sfsu.edu",
#     "careergrad.sfsu.edu",
#     "childrenscampus.sfsu.edu",
#     "chss.sfsu.edu",
#     "cj.sfsu.edu",
#     "classics.sfsu.edu",
#     "climate.sfsu.edu",
#     "cls.sfsu.edu",
#     "commencement.sfsu.edu",
#     "commons.sfsu.edu",
#     "communicationstudies.sfsu.edu",
#     "conduct.sfsu.edu",
#     "counseling.sfsu.edu",
#     "cpdc.sfsu.edu",
#     "cregs.sfsu.edu",
#     "cs.sfsu.edu",
#     "csme.sfsu.edu",
#     "csugis.sfsu.edu",
#     "campussafety.sfsu.edu",
#     "design.sfsu.edu",
#     "develop.sfsu.edu",
#     "gatorsmartstart.sfsu.edu",
#     "docfilm.sfsu.edu",
#     "docusign.sfsu.edu",
#     "dos.sfsu.edu",
#     "undocugators.sfsu.edu",
#     "tornado.sfsu.edu",
#     "ecse.sfsu.edu",
#     "edd.sfsu.edu",
#     "edelman.sfsu.edu",
#     "eed.sfsu.edu",
#     "ehs.sfsu.edu",
#     "elsit.sfsu.edu",
#     "em.sfsu.edu",
#     "engineering.sfsu.edu",
#     "eop.sfsu.edu",
#     "equity.sfsu.edu",
#     "erm.sfsu.edu",
#     "esn.sfsu.edu",
#     "ethnicstudies.sfsu.edu",
#     "facaffairs.sfsu.edu",
#     "facilities.sfsu.edu",
#     "familyproject.sfsu.edu",
#     "www.foundation.sfsu.edu",
#     "fellowships.sfsu.edu",
#     "cfsd.sfsu.edu",
#     "financialaid.sfsu.edu",
#     "flagship.sfsu.edu",
#     "future.sfsu.edu",
#     "gallery.sfsu.edu",
#     "gatorgreats.sfsu.edu",
#     "you.sfsu.edu",
#     "coe.sfsu.edu",
#     "geog.sfsu.edu",
#     "gis.sfsu.edu",
#     "globalclassroom.sfsu.edu",
#     "govrel.sfsu.edu",
#     "grad.sfsu.edu",
#     "graymatterlab.sfsu.edu",
#     "gsp.sfsu.edu",
#     "hackathon.sfsu.edu",
#     "health.sfsu.edu",
#     "healthequity.sfsu.edu",
#     "history.sfsu.edu",
#     "home.sfsu.edu",
#     "housing.sfsu.edu",
#     "hr.sfsu.edu",
#     "ia.sfsu.edu",
#     "iac.sfsu.edu",
#     "ibhequity.sfsu.edu",
#     "icce.sfsu.edu",
#     "instructionalcontinuity.sfsu.edu",
#     "investiture.sfsu.edu",
#     "ir.sfsu.edu",
#     "jewish.sfsu.edu",
#     "journalism.sfsu.edu",
#     "kin.sfsu.edu",
#     "ltns.sfsu.edu",
#     "liberalstudies.sfsu.edu",
#     "longmore.sfsu.edu",
#     "maethnicstudies.sfsu.edu",
#     "magazine.sfsu.edu",
#     "maps.sfsu.edu",
#     "math.sfsu.edu",
#     "meis.sfsu.edu",
#     "metro.sfsu.edu",
#     "mobility.sfsu.edu",
#     "morrison.sfsu.edu",
#     "museumstudies.sfsu.edu",
#     "www.musicdance.sfsu.edu",
#     "mystory.sfsu.edu",
#     "nagpra.sfsu.edu",
#     "navigator.sfsu.edu",
#     "news.sfsu.edu",
#     "www.nursing.sfsu.edu",
#     "oes.sfsu.edu",
#     "oip.sfsu.edu",
#     "olli.sfsu.edu",
#     "recruitment.sfsu.edu",
#     "pace.sfsu.edu",
#     "parking.sfsu.edu",
#     "pays.sfsu.edu",
#     "pbk.sfsu.edu",
#     "philosophy.sfsu.edu",
#     "physics.sfsu.edu",
#     "plan.sfsu.edu",
#     "planning.sfsu.edu",
#     "poetry.sfsu.edu",
#     "politicalscience.sfsu.edu",
#     "president.sfsu.edu",
#     "procurement.sfsu.edu",
#     "psm.sfsu.edu",
#     "psychology.sfsu.edu",
#     "caps.sfsu.edu",
#     "pt.sfsu.edu",
#     "publichealth.sfsu.edu",
#     "qaservices.sfsu.edu",
#     "queercinemaproject.sfsu.edu",
#     "research.sfsu.edu",
#     "reslife.sfsu.edu",
#     "retire.sfsu.edu",
#     "rfsa.sfsu.edu",
#     "rivers.sfsu.edu",
#     "recdept.sfsu.edu",
#     "rrs.sfsu.edu",
#     "safezone.sfsu.edu",
#     "westernnoyce.sfsu.edu",
#     "convocation.sfsu.edu",
#     "seo.sfsu.edu",
#     "sete.sfsu.edu",
#     "sfamp.sfsu.edu",
#     "sfbaynerr.sfsu.edu",
#     "reclaimingnature.sfsu.edu",
#     "sfsuais.sfsu.edu",
#     "sierra.sfsu.edu",
#     "slhs.sfsu.edu",
#     "socwork.sfsu.edu",
#     "sped.sfsu.edu",
#     "sss.sfsu.edu",
#     "studentsuccess.sfsu.edu",
#     "sustain.sfsu.edu",
#     "techgovernance.sfsu.edu",
#     "titleix.sfsu.edu",
#     "transfer.sfsu.edu",
#     "transforms.sfsu.edu",
#     "tutoring.sfsu.edu",
#     "tviomfriends.sfsu.edu",
#     "ucorp.sfsu.edu",
#     "univpark.sfsu.edu",
#     "upd.sfsu.edu",
#     "uwa.sfsu.edu",
#     "veterans.sfsu.edu",
#     "viprogram.sfsu.edu",
#     "vpsaem.sfsu.edu",
#     "cease.sfsu.edu",
#     "wgsdept.sfsu.edu",
#     "businessanalytics.sfsu.edu",
#     "msa.sfsu.edu",
#     "erp.sfsu.edu",
#     "sustainablemba.sfsu.edu",
#     "execed.sfsu.edu",
#     "marketing.sfsu.edu",
#     "management.sfsu.edu",
#     "mba.sfsu.edu",
#     "finance.sfsu.edu",
#     "ds.sfsu.edu",
#     "labor-studies.sfsu.edu",
#     "nicemba.sfsu.edu",
#     "vista.sfsu.edu",
#     "accounting.sfsu.edu",
#     "vista-room.sfsu.edu",
#     "biotechmba.sfsu.edu",
#     "gbp.sfsu.edu",
#     "economics.sfsu.edu",
#     "ibus.sfsu.edu",
#     "htm.sfsu.edu",
#     "vistaroom.sfsu.edu",
#     "emba.sfsu.edu",
#     "cob.sfsu.edu",
#     "is.sfsu.edu",
#     "itsecurity.sfsu.edu",
#     "itpolicy.sfsu.edu",
#     "adminfin.sfsu.edu",
#     "policiesandpracticedirectives.sfsu.edu",
#     "advance.sfsu.edu",
#     "www.art.sfsu.edu",
#     "art.sfsu.edu",
#     "martinwong.sfsu.edu",
#     "www.beca.sfsu.edu",
#     "ksfs.sfsu.edu",
#     "tvcenter.sfsu.edu",
#     "biology.sfsu.edu",
#     "beca.sfsu.edu",
#     "biology.sfsu.edu",
#     "climatehq.sfsu.edu",
#     "busops.sfsu.edu",
#     "riskandsafetyservices.sfsu.edu",
#     "ctfd.sfsu.edu",
#     "qlt.sfsu.edu",
#     "qolt.sfsu.edu",
#     "wac.sfsu.edu",
#     "ceetl.sfsu.edu",
#     "cpage.sfsu.edu",
#     "prehealth.sfsu.edu",
#     "sfsummer.sfsu.edu",
#     "ali.sfsu.edu",
#     "www.cpage.sfsu.edu",
#     "www.cel.sfsu.edu",
#     "cel.sfsu.edu",
#     "meetings.sfsu.edu",
#     "ces.sfsu.edu",
#     "summerconf.sfsu.edu",
#     "biochemistry.sfsu.edu",
#     "chembiochem.sfsu.edu",
#     "chemistry.sfsu.edu",
#     "cinema.sfsu.edu",
#     "humcwl.sfsu.edu",
#     "complit.sfsu.edu",
#     "afm.sfsu.edu",
#     "gtac.sfsu.edu",
#     "cose.sfsu.edu",
#     "pinc.sfsu.edu",
#     "cssc.sfsu.edu",
#     "emfimage.sfsu.edu",
#     "catalyze.sfsu.edu",
#     "merl.sfsu.edu",
#     "creativewriting.sfsu.edu",
#     "greenhouse.sfsu.edu",
#     "csld.sfsu.edu",
#     "career.sfsu.edu",
#     "careerservices.sfsu.edu",
#     "sfcall.sfsu.edu",
#     "bold.thinking.sfsu.edu",
#     "developmentalstudies.sfsu.edu",
#     "www.docfilm.sfsu.edu",
#     "drc.sfsu.edu",
#     "earth.sfsu.edu",
#     "tpw.sfsu.edu",
#     "matesol.sfsu.edu",
#     "english.sfsu.edu",
#     "linguistics.sfsu.edu",
#     "cmls.sfsu.edu",
#     "etc.sfsu.edu",
#     "rtc.sfsu.edu",
#     "eoscenter.sfsu.edu",
#     "riptides.sfsu.edu",
#     "eos.sfsu.edu",
#     "imes.sfsu.edu",
#     "marineops.sfsu.edu",
#     "safety.sfsu.edu",
#     "sfstatefacilities.sfsu.edu",
#     "foundation.sfsu.edu",
#     "sfsufdn.sfsu.edu",
#     "tax.sfsu.edu",
#     "financialservices.sfsu.edu",
#     "fiscaff.sfsu.edu",
#     "www.flagship.sfsu.edu",
#     "hotshots.sfsu.edu",
#     "mentalhealthcheckup.sfsu.edu",
#     "gatorhealth.sfsu.edu",
#     "righttoknow.sfsu.edu",
#     "humanities.sfsu.edu",
#     "americanstudies.sfsu.edu",
#     "humanitiesliberalstudies.sfsu.edu",
#     "latinamericanstudies.sfsu.edu",
#     "southasianstudies.sfsu.edu",
#     "internationalrelations.sfsu.edu",
#     "irgrad.sfsu.edu",
#     "cids.sfsu.edu",
#     "ids.sfsu.edu",
#     "askhr.sfsu.edu",
#     "doit.sfsu.edu",
#     "tech.sfsu.edu",
#     "its.sfsu.edu",
#     "drupal.sfsu.edu",
#     "latino.sfsu.edu",
#     "lca.sfsu.edu",
#     "artshumanities.sfsu.edu",
#     "ica.sfsu.edu",
#     "arts.sfsu.edu",
#     "cats.sfsu.edu",
#     "www.creativearts.sfsu.edu",
#     "creativestate.sfsu.edu",
#     "www.library.sfsu.edu",
#     "library.sfsu.edu",
#     "m.library.sfsu.edu",
#     "longmoreinstitute.sfsu.edu",
#     "puboff.sfsu.edu",
#     "marcomm.sfsu.edu",
#     "logo.sfsu.edu",
#     "www.persian.sfsu.edu",
#     "japanese.sfsu.edu",
#     "persian.sfsu.edu",
#     "chinese.sfsu.edu",
#     "italian.sfsu.edu",
#     "mllab.sfsu.edu",
#     "mll.sfsu.edu",
#     "french.sfsu.edu",
#     "spanish.sfsu.edu",
#     "german.sfsu.edu",
#     "fllab.sfsu.edu",
#     "russian.sfsu.edu",
#     "foreign.sfsu.edu",
#     "museum.sfsu.edu",
#     "musicdance.sfsu.edu",
#     "music.sfsu.edu",
#     "newstudentprograms.sfsu.edu",
#     "newstudentguide.sfsu.edu",
#     "nursing.sfsu.edu",
#     "studyabroad.sfsu.edu",
#     "onecard.sfsu.edu",
#     "onecardonline.sfsu.edu",
#     "baypass.sfsu.edu",
#     "outreach.sfsu.edu",
#     "www.physics.sfsu.edu",
#     "president-search.sfsu.edu",
#     "developmentalpsych.sfsu.edu",
#     "psyservs.sfsu.edu",
#     "www.pt.sfsu.edu",
#     "queercinemainstitute.sfsu.edu",
#     "cms.sfsu.edu",
#     "registrar.sfsu.edu",
#     "www.registrar.sfsu.edu",
#     "testing.sfsu.edu",
#     "efh.sfsu.edu",
#     "rpt.sfsu.edu",
#     "secondaryed.sfsu.edu",
#     "senate.sfsu.edu",
#     "sfbuild.sfsu.edu",
#     "sxs.sfsu.edu",
#     "sociology.sfsu.edu",
#     "socsxs.sfsu.edu",
#     "comdis.sfsu.edu",
#     "theatredance.sfsu.edu",
#     "theatre.sfsu.edu",
#     "www.theatre.sfsu.edu",
#     "ueap.sfsu.edu",
#     "lac.sfsu.edu",
#     "carp.sfsu.edu",
#     "exco.sfsu.edu",
#     "ugs.sfsu.edu",
#     "wasc.sfsu.edu",
#     "universityenterprises.sfsu.edu",
#     "realestate.sfsu.edu",
#     "red.sfsu.edu",
#     "ue.sfsu.edu",
#     "efh.sfsu.edu",
#     "aspire.sfsu.edu",
#     "fina.sfsu.edu",
#     "gcoe.sfsu.edu",
#     "wellness.sfsu.edu",
#     "air.sfsu.edu",
#
# ]

spider_template = """
import os

import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from pydispatch import dispatcher
from scrapy import signals

from ..box_handler import get_box_contents


class {class_name}(scrapy.Spider):
    name = '{name}'
    start_urls = ['https://{site_url}']
    output_folder = r'C:\\Users\\913678186\\Box\\ATI\\PDF Accessibility\\SF State Website PDF Scans\\{save_folder}'


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super({class_name}, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def __init__(self):

        self.matched_links = []  # Store matched links
        self.pdf_links = []  # Store PDF links
    

    def parse(self, response):

        # Regular expression pattern for URLs within access.sfsu.edu domain
        access_url_pattern = re.compile(r'https://{site_url}/.*')
        # Pattern specifically for box.com links
        box_url_pattern = re.compile(r'https?://sfsu.box.com/s/.*')

        pdf_pattern = re.compile(r'.*\.pdf$', re.IGNORECASE)  # Pattern to match .pdf files

        # Extract URLs from href attributes
        extracted_links = response.css('a::attr(href)').getall()

        # Filter links and delegate accordingly

        for link in extracted_links:
            absolute_url = response.urljoin(link)

            # Check for access.sfsu.edu links
            if access_url_pattern.match(absolute_url):
                if pdf_pattern.match(absolute_url):
                    self.pdf_links.append((absolute_url, response.url))
                else:
                    yield response.follow(absolute_url, self.parse)

            # Special handling for box.com links
            elif box_url_pattern.match(absolute_url):
                history = response.meta.get('history', [])
                history.append(response.url)

                yield response.follow(absolute_url, self.parse_box_link, meta={{'history': history}})

    def parse_box_link(self, response):
        # Implement special handling for box.com links here
        # For example, extracting direct download URLs, if available

        pdf = get_box_contents(response.url)
        if pdf:

            self.pdf_links.append((pdf, response.meta.get('history', [])[0] ))

        print('Handling a Box.com link:', response.url)
        # Add any specific logic for Box.com links

    def spider_closed(self, spider):
        # Ensure the output folder exists
        os.makedirs(self.output_folder, exist_ok=True)

        # Define the output file path
        output_file_path = os.path.join(self.output_folder, 'scanned_pdfs.txt')

        # Open the file and write each PDF link
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for link in self.pdf_links:
                file.write(f"{{link[0]}} {{link[1]}}\\n")

        print("PDF LINKS saved to", self.output_folder)
"""


output_dir = "sf_state_pdf_scan/sf_state_pdf_scan/spiders"
os.makedirs(output_dir, exist_ok=True)

all_sites = get_all_sites_domain_names()
failed = []

for site in all_sites:
    time.sleep(0.1)
    try:
        response = requests.get("https://" + site)
    except requests.exceptions.SSLError:
        failed.append(site)
        continue

    except requests.exceptions.ConnectionError:
        failed.append(site)
        continue

    soup = BeautifulSoup(response.content, 'html.parser')

    site_name_tag = soup.find('span', class_='site-name')
    if site_name_tag and site_name_tag.find('a'):
        site_name = site_name_tag.find('a').text.strip()
    else:
        site_name = 'SiteNameNotFound'

    # Clean the site name for the class name by replacing spaces with underscores
    site_name_cleaned_for_class = ''.join(word.capitalize() for word in ''.join(e if e.isalnum() or e.isspace() else ' ' for e in site_name).split())
    # Keep the site name as is for the spider name, but remove non-alphanumeric characters (spaces are kept)
    site_name_cleaned_for_name = ''.join(e if e.isalnum() or e.isspace() else '' for e in site_name)

    site_name_cleaned_for_file_title = ''.join(e if e.isalnum() or e.isspace() else '' for e in site_name).replace(' ', '_')

    save_folder = site.replace('.', '-').lower()

    class_name = f"{site_name_cleaned_for_class}Spider"
    spider_code = spider_template.format(class_name=class_name,
                                         name=f"{site_name_cleaned_for_name.lower().replace(' ','_')}_spider",
                                         site_url=site,
                                         spider_name=site_name_cleaned_for_name.lower(),
                                         save_folder=save_folder)

    file_path = os.path.join(output_dir, f"{site_name_cleaned_for_file_title.lower()}_spider.py")

    with open(file_path, 'w') as file:
        file.write(spider_code)
    print(f"Generated spider for {site}: {file_path}")


print("FAILED", failed)



