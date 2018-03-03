import scrapy


class JobSpider(scrapy.Spider):

    name = "jobs"

    def start_requests(self):
        urls = [
            'https://angel.co/directory/jobs/roles',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_more_roles)

    def parse_more_roles(self, response):
        # page = response.url.split("/")[-1]
        self.logger.debug(response.url)
        more_roles = response.xpath("(//div/div/ul/li)[last()]/a")
        follow_links = []
        for role in more_roles:
            role_link = role.css('a::attr(href)').extract_first()
            role_name = role.css('a::text').extract_first()
            follow_links.append((role_name, role_link))
        self.logger.debug("\n------ level 1 ------")
        self.logger.debug(f"more roles: {follow_links}\n")
        for name, link in follow_links:
            yield response.follow(link, callback=self.parse_roles)

    def parse_roles(self, response):
        # page = response.url.split("/")[-1]
        self.logger.debug(response.url)
        roles = response.xpath('//div/ul/li/a')
        follow_links = []
        for role in roles:
            role_link = role.css('a::attr(href)').extract_first()
            role_name = role.css('a::text').extract_first()
            follow_links.append((role_name, role_link))
        self.logger.debug("\n------ level 2 ------")
        self.logger.debug(f'roles: {follow_links}\n')
        for name, link in follow_links:
            yield response.follow(link, callback=self.parse_company)

    def parse_company(self, response):
        self.logger.debug(response.url)
        companies = response.xpath('//h5/a')
        follow_links = []
        for com in companies:
            com_link = com.css('a::attr(href)').extract_first()
            com_name = com.css('a::text').extract_first()
            follow_links.append((com_name, com_link))
        self.logger.debug("\n------ level 3 ------")
        self.logger.debug(f'company: {follow_links}\n')
        for name, link in follow_links:
            yield response.follow(link, callback=self.parse_job,
                                  meta={'company name': name, 'company link': link})

    def parse_job(self, response):
        self.logger.debug(response.url)
        job_groups = response.xpath('//li[div]')
        follow_link = []
        for jg in job_groups:
            job_category = jg.xpath('div/text()').extract_first()
            jobs = jg.xpath('(div[node()])[last()]/div')
            for job in jobs:
                job_title = job.xpath('div/div/a/text()').extract_first()
                job_link = job.xpath('div/div/a/@href').extract_first()
                follow_link.append((job_title, job_link))
        self.logger.debug("\n------ level 4 ------")
        # self.logger.debug(response.meta)
        self.logger.debug(f'job: {follow_link}\n')
        for name, link in follow_link:
            yield response.follow(link, callback=self.parse_job_page,
                                  meta={'job title': name, 'job link': link, 'job category': job_category,
                                        'company name': response.meta['company name'],
                                        'company link': response.meta['company link']})

    def parse_job_page(self, response):
        self.logger.debug(response.url)
        ''' job info contains location and contract type
            e.g. Delhi · Full Time
        '''
        # job_info = response.xpath('//div[1]/div[2]/div[2]/div[1]/div[2]/div[1]').extract_first()
        # company_desp = response.xpath('//div[1]/div[2]/div[2]/div[1]/div[2]/div[2]').extract_first()
        ''' find job description by class value'''
        job_desp = ' '.join(response.css('.job-description *::text').extract())
        self.logger.debug("\n------ level 5 ------")
        # self.logger.debug(f'response: {response.meta}')
        response.meta['job description'] = job_desp
        response.meta['job source'] = response.text
        yield response.meta



