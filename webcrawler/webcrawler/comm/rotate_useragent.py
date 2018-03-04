import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from .useragent_list import user_agent_list


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        super().__init__()
        self.user_agent = user_agent
        self.user_agent_list = user_agent_list

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            request.headers.setdefault('User-Agent', ua)
