# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
import json
import execjs
import random
import logging
import requests
import datetime
from copy import deepcopy

import scrapy
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.spidermiddlewares.referer import RefererMiddleware
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet.error import TimeoutError, ConnectionRefusedError, TCPTimedOutError
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat

from public.models import *
from .settings import USER_AGENT_LIST
from twisted.internet.defer import DeferredLock

logger = logging.getLogger(__name__)
ip_parser = lambda x: re.search("""(\d+\.\d+\.\d+\.\d+)""", x).group(1)


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        rand_use = random.choice(USER_AGENT_LIST)
        if rand_use:
            request.headers.setdefault('User-Agent', rand_use)


class PyroadSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class PyroadSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyPoolMiddleware(object):

    def __init__(self, ):
        self.proxy_pool = []
        # 默认自动更新代理池
        self.proxy_pool_auto_update = True
        # 默认自动更新周期为2分钟
        self.proxy_pool_update_cycle = datetime.timedelta(minutes=2)
        # 默认过期时间
        self.proxy_pool_expiration = datetime.datetime.now()

    def update_proxy_pool(self, spider, sql_proxy_available=1):
        valid_period = spider.proxy_pool_update_cycle if hasattr(spider, "proxy_pool_update_cycle") \
            else self.proxy_pool_update_cycle
        if spider.proxy_source == "file":
            if not spider.proxy_file_path:
                raise ValueError("param 'file_path' is required if get proxy from file!")
            # 通过txt文件读取代理
            with open(spider.proxy_file_path, 'rb+') as f:
                ip_list = f.read()
            self.proxy_pool = [spider.proxy_protocol + "://" + item for item in str(ip_list, "utf-8").split()]
            self.proxy_pool_expiration = datetime.datetime.now() + valid_period
            logger.debug("获取高匿https代理：%s个" % len(self.proxy_pool))
        elif spider.proxy_source == "api":
            if not spider.proxy_url:
                raise ValueError("param 'proxy_url' is required if get proxy from api!")
            # 向代理接口请求代理数据
            resp = requests.get(url=spider.proxy_url)
            # 设置代理池、过期时间
            # self.proxy_pool = [spider.proxy_protocol + "://" + item for item in resp.text.split()]
            self.proxy_pool = ["http://" + item for item in resp.text.split()]
            self.proxy_pool_expiration = datetime.datetime.now() + valid_period
            logger.debug("获取代理：\n%s\n过期时间：%s" % (
                "\n".join(self.proxy_pool),
                datetime.datetime.strftime(self.proxy_pool_expiration, "%Y-%m-%d %H:%M:%S")))
        elif spider.proxy_source == "sql":
            # 通过数据库读取
            kwargs = {
                "type__name": spider.proxy_type,
                "protocol__name": spider.proxy_protocol,
                "is_available": sql_proxy_available,
                "is_delete": 0
            }
            # kwargs = {
            #     "address__in": ["120.52.73.105", "60.185.203.91", "118.117.188.196", "182.84.144.111"]
            # }
            if sql_proxy_available is None:
                del kwargs["is_available"]
            proxy_list = list(ProxyPool.objects.filter(**kwargs).annotate(
                proxy=Concat(V(spider.proxy_protocol + "://"), "address", V(":"), "port", output_field=CharField())
            ).values_list("proxy"))
            self.proxy_pool = [proxy[0] for proxy in proxy_list]
            self.proxy_pool_expiration = datetime.datetime.now() + valid_period
            logger.debug("获取代理：%s个, 过期时间：%s" % (
                len(self.proxy_pool), datetime.datetime.strftime(self.proxy_pool_expiration, "%Y-%m-%d %H:%M:%S")))

    def process_exception(self, request, exception, spider):

        proxy = None
        use_proxy = request.meta.get("proxy")
        # 从代理池暂时删除抛出异常的IP
        if hasattr(spider, "use_proxy") and spider.use_proxy:
            if self.proxy_pool:
                for index, item in enumerate(self.proxy_pool):
                    proxy = request.meta.get('proxy')
                    if proxy in item:
                        del self.proxy_pool[index]

            # 是否需要定时更新代理池
            if hasattr(spider, "proxy_pool_auto_update"):
                self.proxy_pool_auto_update = spider.proxy_pool_auto_update
            if self.proxy_pool_auto_update and hasattr(spider, "proxy_pool_update_cycle"):
                self.proxy_pool_update_cycle = spider.proxy_pool_update_cycle

            need_update_proxy_pool = (
                                             self.proxy_pool_auto_update
                                             and datetime.datetime.now() > self.proxy_pool_expiration
                                     ) or not self.proxy_pool

            # 当代理池为空/代理池即将到期时需要进行更新
            if need_update_proxy_pool:
                kwargs = {
                    "spider": spider,
                }
                if hasattr(spider, "sql_proxy_available"):
                    kwargs["sql_proxy_available"] = spider.sql_proxy_available
                self.update_proxy_pool(spider)

            # 加代理前判断代理池是否为空
            if not self.proxy_pool:
                spider.crawler.engine.close_spider(spider, "proxy pool is empty")
                # signals.spider_closed(spider, "proxy pool is empty")
                return request

            # 加代理发送请求
            proxy = random.choice(self.proxy_pool)
            request.meta['proxy'] = proxy

        if "search" in request.url:
            logger.warning(
                f"Timeout! Change Proxy --> {proxy} page: {json.loads(json.dumps(eval(str(request.body, 'utf-8)'))))['pageNo']}")
        else:
            err_type = {
                TunnelError: "Service Unavailable! ",
                TimeoutError: "Timeout! ",
                ConnectionRefusedError: "Connection Refused! ",
                TCPTimedOutError: "TCP Timeout! "
            }
            err = err_type.get(type(exception))
            if not err:
                # logger.warning(f"{type(exception)}: {exception}")
                logger.warning(f"{exception}")
                return request
            if proxy:
                err += f" Change Proxy --> {proxy} pid: {request.url.split('/')[-1]}"
            if use_proxy:
                err += f" Using Proxy --> {use_proxy}"
            logger.warning(err)
        return request


class ProxyCheckMiddleware(ProxyPoolMiddleware):

    def __init__(self):
        super().__init__()
        self.lock = DeferredLock()
        # 初始化代理池
        # self.update_proxy_pool(datetime.timedelta(seconds=0))
        # self.update_proxy_pool(None)

    def process_request(self, request, spider):
        ...

    def process_response(self, request, response, spider):
        ProxyPool.objects.filter(address=response.text.strip()).update(update_time=datetime.datetime.now(),
                                                                       is_available=1)
        # 代理有效，检查代理池是否有未检测的代理，有则更换代理继续检测
        proxy = random.choice(self.proxy_pool) if self.proxy_pool else None
        logger.info(f"{response.text.strip()} Pass! Change Proxy --> {proxy}")
        if proxy:
            request.meta['proxy'] = proxy
        return request if proxy and self.proxy_pool else response


class PyroadSpiderProxyMiddleware(ProxyPoolMiddleware):

    def __init__(self):
        super().__init__()
        self.lock = DeferredLock()

    def change_proxy(self, request, response, spider):
        # 判断IP是否被封, 被封则逻辑删除该代理IP
        if response.headers.get("Location") and b"forbidden" in response.headers.get("Location"):
            kwargs = {"is_delete": 1, "is_available": 0, "update_time": datetime.datetime.now()}
            ProxyPool.objects.filter(
                address=ip_parser(str(response.headers.get("Location"), encoding="utf8"))
            ).update(**kwargs)

        # 代理池删除被检测到的代理
        for index, item in enumerate(self.proxy_pool):
            proxy = request.meta.get('proxy')
            if proxy in item:
                del self.proxy_pool[index]

        # 判断当前代理池是否还有存活的代理, 没有就更新一次代理池
        if not self.proxy_pool:
            self.update_proxy_pool(spider)
        try:
            # 更换新代理重新请求
            proxy = random.choice(self.proxy_pool)
            request.meta['proxy'] = proxy
            if "search" in request.url:
                logger.warning(
                    f"Change Proxy --> {proxy} page: {spider.form.get('pageNo')}")
            else:
                logger.warning(f"Change Proxy --> {proxy} pid: {request.url.split('/')[-1]}")
            return request
        except IndexError:
            # 触发反爬，代理池无可用代理
            raise IgnoreRequest("proxy pool empty!")

    def process_request(self, request, spider):
        if spider.use_proxy and not request.meta.get("proxy"):
            # 当代理池为空/代理池即将到期时需要进行更新
            if not self.proxy_pool or self.proxy_pool_expiration - datetime.datetime.now() < datetime.timedelta(
                    seconds=5):
                self.update_proxy_pool(spider)

            # 加代理发送请求
            if 'proxy' not in request.meta:
                proxy = random.choice(self.proxy_pool)
                request.meta['proxy'] = proxy
                if "search" in request.url:
                    logger.debug(
                        f"Using Proxy --> {proxy} page: {json.loads(json.dumps(eval(str(request.body, 'utf-8)'))))['pageNo']}")
                else:
                    logger.debug(f"Using Proxy --> {proxy} pid: {request.url.split('/')[-1]}")

    def process_response(self, request, response, spider):
        # 状态码正常，判断是否触发反爬
        if 200 <= response.status < 300:
            try:
                proxy_ip = json.loads(response.text).get("clientIp")
                if proxy_ip:  # 如果爬虫携带代理，并且检测到响应中包含当前代理ip，说明触发了反爬，需要更换代理
                    logger.info(response.text)
                    if "search" in request.url:
                        logger.error(f"Proxy Baned --> {request.meta.get('proxy')} page: {spider.form.get('pageNo')}")
                    else:
                        logger.error(f"Proxy Baned --> {request.meta.get('proxy')} pid: {request.url.split('/')[-1]}")
                    if not spider.use_proxy:
                        raise IgnoreRequest("已触发反爬机制，请添加代理后重试")
                    return self.change_proxy(request, response, spider)

            except:
                # 无需代理则清理meta中的proxy
                if not spider.use_proxy:
                    if "proxy" in request.meta:
                        del request.meta["proxy"]
                    return response

                # 更换代理重新请求
                # return self.change_proxy(request, response, spider)
                return response
        # 状态码异常，默认重定向为封IP
        # if 300 <= response.status < 400:
        else:
            location = str(response.headers.get("Location", ""), "utf-8")
            if re.findall("""(trackMid|verify|login)(?=\.html)""", location):  # 被检测的跳转，需要换代理
                return self.change_proxy(request, response, spider)
            if hasattr(spider, "need_token") and spider.need_token:
                return response
            logger.warning("status code:" + str(response.status))
            # if hasattr(spider, "need_token") and spider.need_token and "__lg_stoken__" not in str(request.headers):
            #     if b"security-check.html" in response.headers["Location"]:                # 正常跳转，获取token即可
            #         self.get_token(request, response)
            #         return request
            return self.change_proxy(request, response, spider)
        # 未触发反爬，正常返回
        return response


class MyRetryMiddleware(RetryMiddleware):

    def process_exception(self, request, exception, spider):
        if (
                isinstance(exception, self.EXCEPTIONS_TO_RETRY)
                and not request.meta.get('dont_retry', False)
        ):
            retry_result = self._retry(request, exception, spider)

            if not retry_result:

                # 判断是否需要自动废弃不可用代理
                if hasattr(spider, "auto_abandon_proxy") and spider.auto_abandon_proxy:
                    ProxyPool.objects.filter(
                        address=ip_parser(request.meta["proxy"])
                    ).update(is_available=0, update_time=datetime.datetime.now())

                if request.meta.get("retry_times") == self.max_retry_times:
                    del request.meta["retry_times"]
            return retry_result


class AutoDisableProxyRetryMiddleware(RetryMiddleware):
    def process_exception(self, request, exception, spider):
        if (
                isinstance(exception, self.EXCEPTIONS_TO_RETRY)
                and not request.meta.get('dont_retry', False)
        ):
            retry_result = self._retry(request, exception, spider)

            if not retry_result:

                # 判断是否需要自动废弃不可用代理
                if spider.proxy_source == 'sql' and hasattr(spider, "auto_abandon_proxy") and spider.auto_abandon_proxy:
                    ProxyPool.objects.filter(
                        address=ip_parser(request.meta["proxy"])
                    ).update(is_available=0, update_time=datetime.datetime.now())

                if request.meta.get("retry_times") == self.max_retry_times:
                    del request.meta["retry_times"]
            return retry_result
