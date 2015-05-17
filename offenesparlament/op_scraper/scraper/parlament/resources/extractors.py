import datetime
from django.utils.html import remove_tags
from scrapy import Selector

from parlament.resources import SingleExtractor
from parlament.resources import MultiExtractor
from parlament.resources.util import _clean

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class PRELAW:

    class DESCRIPTION(SingleExtractor):
        XPATH = "//div[contains(concat(' ', normalize-space(@class), ' '), ' c_2 ')]/h3/following-sibling::p/text()"

        @classmethod
        def xt(cls, response):
            try:
                description = response.xpath(cls.XPATH)[0].extract()[0]
            except:
                import ipdb
                ipdb.set_trace()
            return remove_tags(description, 'p')

    class STEPS(MultiExtractor):
        XPATH = '//table'

        @classmethod
        def xt(cls, response):
            steps = []
            raw_table = response.xpath('//table')[1]
            raw_steps = Selector(text=raw_table.extract()).xpath('//tr')
            for index, step in enumerate(raw_steps, start=1):
                step_selector = Selector(text=step.extract())
                title = LAW.PHASES.STEPS.TITLE.xt(step_selector)
                date_str = LAW.PHASES.STEPS.DATE.xt(step_selector)
                date = datetime.datetime.strptime(
                    date_str, "%d.%m.%Y").date()
                protocol_url = LAW.PHASES.STEPS.PROTOCOL.xt(step_selector)
                steps.append({
                    'date': date,
                    'title': title,
                    'sortkey': str(index).zfill(3),
                    'protocol_url': protocol_url
                })
            return steps

    class OPINIONS(MultiExtractor):
        XPATH = '//*[@id="content"]/div[3]/div[2]/div[2]/table//tr'

        @classmethod
        def xt(cls, response):
            ops = []
            raw_ops = response.xpath(cls.XPATH).extract()
            for raw_op in raw_ops[1:]:
                op_sel = Selector(text=raw_op)

                date = op_sel.xpath('//td[1]/text()').extract()
                date = date[0]

                url = op_sel.xpath('//td[2]/a/@href').extract()[0]
                parl_id = u"({})".format(
                    op_sel.xpath('//td[2]/a/text()').extract()[0])

                title = op_sel.xpath('//td[3]/text()').extract()[0]
                if title:
                    title = _clean(title).replace("*", ", ")
                else:
                    title = None

                email = op_sel.xpath('//td[3]/a/@href').extract()
                if email:
                    email = email[0].replace('mailto:', '')
                    title = op_sel.xpath('//td[3]/a/text()').extract()[0]
                else:
                    email = None

                try:
                    date = datetime.datetime.strptime(
                        _clean(date), "%d.%m.%Y").date()
                except:
                    date = None

                ops.append({
                    'date': date,
                    'url': url,
                    'email': email,
                    'title': title,
                    'parl_id': parl_id
                })

            return ops


class OPINION:

    class ENTITY:
        XPATH = '//p[contains(text(),"Stellungnehmende(r):")]/text()'
        XPATH_EMAIL = '//p[contains(text(),"Stellungnehmende(r):")]/a/@href'

        @classmethod
        def xt(cls, response):
            entity_raw = response.xpath(cls.XPATH).extract()
            if entity_raw:
                entity_text = entity_raw[0].replace(
                    u'Stellungnehmende(r):', '')
            else:
                entity_text = u""
            entries = [entry.strip()
                       for entry in entity_text.split(u'\n')
                       if entry.strip()]
            entity = {
                'title_detail': u'',
                'phone': None,
                'email': None
            }
            for entry in entries:
                if u"Tel.:" in entry:
                    entity['phone'] = entry.replace(u'Tel.:', u'')
                else:
                    entity['title_detail'] = u"{} {}".format(
                        entity['title_detail'], entry)
            entity['title_detail'] = entity['title_detail'].replace("*", ", ")
            emaiL_raw = response.xpath(cls.XPATH_EMAIL).extract()
            if emaiL_raw:
                entity['email'] = emaiL_raw[0].replace(u'mailto:', u'')

            return entity

    class STEPS(MultiExtractor):
        XPATH = '//table'

        @classmethod
        def xt(cls, response):
            steps = []
            raw_table = response.xpath('//table')[0]
            raw_steps = Selector(text=raw_table.extract()).xpath('//tr')
            for index, step in enumerate(raw_steps[1:]):
                step_selector = Selector(text=step.extract())
                title = LAW.PHASES.STEPS.TITLE.xt(step_selector)
                date_str = LAW.PHASES.STEPS.DATE.xt(step_selector)
                try:
                    date = datetime.datetime.strptime(
                        date_str, "%d.%m.%Y").date()
                except:
                    import ipdb
                    ipdb.set_trace()
                protocol_url = LAW.PHASES.STEPS.PROTOCOL.xt(step_selector)
                steps.append({
                    'date': date,
                    'title': title,
                    'sortkey': str(index).zfill(3),
                    'protocol_url': protocol_url
                })
            return steps


class LAW:

    class TITLE(SingleExtractor):
        XPATH = '//*[@id="inhalt"]/text()'

    class PARL_ID(SingleExtractor):
        XPATH = '//*[@id="inhalt"]/span/text()'

    class PRELAW_ID(SingleExtractor):
        XPATH = '//h2[@id="tab-VorparlamentarischesVerfahren"]/..'
        XPATH_ID = "//h3[contains(concat(' ', normalize-space(@class), ' '), ' zeigeContentBlock ')]//span/text()"

        @classmethod
        def xt(cls, response):
            raw_section = Selector(text=response.xpath(cls.XPATH).extract()[0])
            prelaw_id = raw_section.xpath(cls.XPATH_ID).extract()[0]
            return prelaw_id

    class KEYWORDS(MultiExtractor):
        XPATH = '//*[@id="schlagwortBox"]/ul//li/a/text()'

    class DOCS(MultiExtractor):
        LI_XPATH = '//*[@id="content"]/div[3]/div[2]/div[2]/div/ul/li'

        @classmethod
        def xt(cls, response):
            docs = []
            raw_docs = response.xpath(cls.LI_XPATH)
            for raw_doc in raw_docs:
                html_url, pdf_url = "", ""
                urls = raw_doc.css('a').xpath('@href').extract()
                for url in urls:
                    if url.endswith('.pdf'):
                        pdf_url = url
                    elif url.endswith('.html'):
                        html_url = url
                title = Selector(text=raw_doc.extract()).xpath(
                    '//a[1]/text()').extract()[0]
                title = title[:title.index('/')].strip()
                docs.append({
                    'title': title,
                    'html_url': html_url,
                    'pdf_url': pdf_url
                })
            return docs

    class STATUS(SingleExtractor):
        XPATH = '//*[@id="content"]/div[3]/div[2]/div[1]/div[1]/p'

        @classmethod
        def xt(cls, response):
            status = remove_tags(
                response.xpath(cls.XPATH).extract()[0], 'em img p')
            status = status.replace('Status: ', '')
            return status

    class CATEGORY(SingleExtractor):
        XPATH = '//*[@id="content"]/div[3]/div[2]/div[2]/h3/text()'

    class DESCRIPTION(SingleExtractor):
        XPATH = '//*[@id="content"]/div[3]/div[2]/div[2]/p[1]'

        @classmethod
        def xt(cls, response):
            description = response.xpath(cls.XPATH).extract()
            if description:
                description = description[0]
            else:
                description = u""
            return remove_tags(description, 'p')

    class PHASES(MultiExtractor):

        XPATH = "//tr[contains(concat(' ', normalize-space(@class), ' '), ' historyHeader ')]/.."

        @classmethod
        def xt(cls, response):
            phases = []
            raw_phases = response.xpath(cls.XPATH)
            for index, raw_phase in enumerate(raw_phases, start=1):
                raw_phase_selector = Selector(text=raw_phase.extract())
                phase_index = str(index).zfill(2)
                title = LAW.PHASES.TITLE.xt(raw_phase_selector)
                steps = LAW.PHASES.STEPS.xt(phase_index, raw_phase_selector)
                phase = {
                    'title': title,
                    'steps': steps
                }
                phases.append(phase)
            return phases

        class TITLE(SingleExtractor):

            XPATH = "//tr[contains(concat(' ', normalize-space(@class), ' '), ' historyHeader ')]//a/text()"

        class STEPS(MultiExtractor):

            XPATH = "/html/body/tbody/tr[not(contains(@class, 'close')) and not(contains(@class, 'historyHeader'))]"

            @classmethod
            def xt(cls, phase_index, selector):
                steps = []
                raw_steps = selector.xpath(cls.XPATH)
                for index, raw_step in enumerate(raw_steps, start=1):
                    step_sortkey = "{}#{}".format(
                        phase_index,
                        str(index).zfill(3))
                    step_selector = Selector(text=raw_step.extract())

                    title = LAW.PHASES.STEPS.TITLE.xt(step_selector)
                    date_str = LAW.PHASES.STEPS.DATE.xt(step_selector)
                    date = datetime.datetime.strptime(
                        date_str, "%d.%m.%Y").date()
                    protocol_url = LAW.PHASES.STEPS.PROTOCOL.xt(step_selector)
                    step = {
                        'sortkey': step_sortkey,
                        'title': title,
                        'date': date,
                        'protocol_url': protocol_url
                    }
                    steps.append(step)
                return steps

            class DATE(SingleExtractor):
                XPATH = "//td[1]/text()"

            class TITLE(SingleExtractor):
                XPATH = "//td[2]/text()"

            class PROTOCOL(SingleExtractor):
                XPATH = "//td[3]/text()"


class PERSON:

    class DETAIL:

        class FULL_NAME(SingleExtractor):
            XPATH = '//*[@id="inhalt"]/text()'

        class PHOTO_URL(SingleExtractor):
            XPATH = "//div[contains(concat(' ', normalize-space(@class), ' '), ' teaserPortraitLarge ')]/a/img/@src"

        class MANDATES:
            XPATH = "//h4[text()='Politische Mandate']/following-sibling::ul[1]/li"

            @classmethod
            def xt(cls, response):
                mandates_raw = response.xpath(cls.XPATH).extract()
                mandates = []
                for mandate in mandates_raw:
                    mandate = _clean(remove_tags(mandate, 'li'))

                    if "<div" in mandate and "</div>" in mandate:
                        mandate = _clean(remove_tags(
                            Selector(text=mandate).xpath("//div").extract()[0],
                            'div'))

                    function = mandate.split(u'<br>')[0].split(',')[0]
                    party = mandate.split(u'<br>')[0].split(',')[1]

                    # Start Date
                    try:
                        start_date = _clean(
                            mandate.split('<br>')[1].split(u'\u2013')[0])

                        start_date = datetime.datetime.strptime(
                            start_date, "%d.%m.%Y").date()
                    except:
                        logger.error(
                            u"Failed to parse mandate start date: {}".format(start_date))
                        start_date = None

                    # End Date
                    try:
                        end_date = mandate.split(
                            '<br>')[1].split(u'\u2013')
                        if len(end_date) > 1 and end_date[1]:
                            end_date = datetime.datetime.strptime(
                                _clean(end_date[1]), "%d.%m.%Y").date()
                        else:
                            end_date = None
                    except:
                        logger.error(
                            u"Failed to parse mandate end date: {}".format(end_date))
                        end_date = None

                    mandates.append({
                        'function': function,
                        'party': _clean(party),
                        'start_date': start_date,
                        'end_date': end_date,
                    })

                return mandates

        class BIO:
            XPATH = "//h3[contains(concat(' ', normalize-space(@class), ' '), ' hidden ') and text()='Lebenslauf']/following-sibling::p"

            @classmethod
            def xt(cls, response):
                bio = {
                    'birthdate': None,
                    'birthplace': '',
                    'deathdate': None,
                    'deathplace': '',
                    'occupation': ''
                }
                bio_data = response.xpath(cls.XPATH).extract()
                if bio_data:
                    bio_data = bio_data[0]
                else:
                    return bio

                # Birth Data
                for data in bio_data.split('<br>'):
                    birth = Selector(text=data)\
                        .xpath("//em[contains(text(),'Geb.')]/parent::*/text()")\
                        .extract()
                    if birth:
                        birth = birth[0]
                        bio['birthdate'] = _clean(birth.split(',')[0])
                        try:
                            bio['birthdate'] = datetime.datetime.strptime(
                                bio['birthdate'], "%d.%m.%Y").date()
                        except:
                            logger.error("Failed to parse birthdate: {}".format(
                                bio['birthdate']))
                            bio['birthdate'] = None
                        if len(birth.split(',')) > 1:
                            bio['birthplace'] = birth.split(',')[1]

                    # Death Data
                    death = Selector(text=data)\
                        .xpath("//em[contains(text(),'Verst.')]/parent::*/text()")\
                        .extract()
                    if death:
                        death = death[0]
                        bio['deathdate'] = _clean(death.split(',')[0])
                        try:
                            bio['deathdate'] = datetime.datetime.strptime(
                                bio['deathdate'], "%d.%m.%Y").date()
                        except:
                            logger.error("Failed to parse deathdate: {}".format(
                                bio['deathdate']))
                            bio['deathdate'] = None
                        if len(death.split(',')) > 1:
                            bio['deathplace'] = death.split(',')[1]

                    # Occupation
                    occupation = Selector(text=data)\
                        .xpath("//em[contains(text(),'Beruf')]/parent::*/text()")\
                        .extract()
                    if occupation:
                        occupation = occupation[0]
                        bio['occupation'] = occupation.split(',')[0]
                return bio

    class PARTY(SingleExtractor):
        XPATH = '//li'
        XPATH_SHORT = '//li/span/text()'
        XPATH_TITLE = '//li/span/@title'

        class SHORT(SingleExtractor):
            XPATH = '//li/span/text()'

        class TITLE(SingleExtractor):
            XPATH = '//li/span/@title'

        @classmethod
        def xt(cls, selector):
            """
            Extract the elements
            """
            parties_raw = cls._xt(selector)
            parties = []
            for party in parties_raw:
                try:
                    party_short = PERSON.PARTY.SHORT.xt(Selector(text=party))
                    party_title = PERSON.PARTY.TITLE.xt(Selector(text=party))
                    parties.append([party_short, party_title])
                except IndexError:
                    pass
            return parties