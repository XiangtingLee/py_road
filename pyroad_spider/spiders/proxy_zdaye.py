import re
from datetime import datetime
import time

import scrapy
import execjs
from ..custom_settings import *
from ..items import ProxyItem


class ProxyZdayeSpider(scrapy.Spider):
    name = 'proxy_zdaye'
    allowed_domains = ['zdaye.com']
    start_urls = ['http://zdaye.com/FreeIPList.html']
    # start_urls = ['https://httpbin.org/get?show_env=1']
    custom_settings = custom_settings_for_proxy_zdaye

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.need_decrypt = False
        self.cb = self.get_js if self.need_decrypt else self.parse
        self.js_url = "https://www.zdaye.com/js/base.js"
        # self.data_url = "https://www.zdaye.com/FreeIPlist.html?pageid=%s"
        self.data_url = "https://www.zdaye.com/free/%s/"
        self.offset = None
        self.current_page_no = 1
        self.resp_time__lt = 1000

    def decrypt(self, data):
        """
        解密偏移量
        :param data:
        :return:
        """
        return str(int("".join(chr(int(v) - int(self.offset)) for v in data)))

    def get_dom_list(self, response):
        # 解析当前html页面中的代理表格
        self.proxy_dom_list = response.xpath("""//table[@id="ipc"]//tbody/tr""")

    def get_total_page_count(self, response):
        try:
            self.total_page_count = int(response.xpath("""//a[@title="最后页"]/text()""")[0])
        except:
            self.total_page_count = 3

    def start_requests(self):
        """
        获取html源码
        :return:
        """
        yield scrapy.Request(self.data_url%self.current_page_no, callback=self.cb)

    def get_js(self, response):
        """
        获取当前html页面对应的js文件
        :param response:
        :return:
        """
        # 解析当前html页面中的代理表格
        self.get_dom_list(response)

        # 处理翻页
        self.get_total_page_count(response)

        # 请求js文件
        yield scrapy.Request(self.js_url, method='get', callback=self.get_token, dont_filter=True)

    def get_token(self, response):
        """
        在js文件中拿到token和ak算出偏移量
        :param response:
        :return:
        """

        # 拿token、mk
        mk = re.search("""var mk = "(.*?)";""", response.text).group(1)
        ak = re.search("""var ak = "(\d+)";""", response.text).group(1)

        # 模拟js
        # js_env = execjs.get()
        # js_compiled = js_env.compile("""
        js_compiled = execjs.compile("""
        function sdfsgfdg(s) {
            var s2 = s.split("m");
            var ts = "";
            for (var n = s2.length - 1; n >= 0; n--) {
                ts = ts + String.fromCharCode(parseInt(s2[n]) - 352)
            }
            return ts
        }

        var rotateLeft = function (lValue, iShiftBits) {
            return (lValue << iShiftBits) | (lValue >>> (32 - iShiftBits));
        }
        var addUnsigned = function (lX, lY) {
            var lX4, lY4, lX8, lY8, lResult;
            lX8 = (lX & 0x80000000);
            lY8 = (lY & 0x80000000);
            lX4 = (lX & 0x40000000);
            lY4 = (lY & 0x40000000);
            lResult = (lX & 0x3FFFFFFF) + (lY & 0x3FFFFFFF);
            if (lX4 & lY4)
                return (lResult ^ 0x80000000 ^ lX8 ^ lY8);
            if (lX4 | lY4) {
                if (lResult & 0x40000000)
                    return (lResult ^ 0xC0000000 ^ lX8 ^ lY8);
                else
                    return (lResult ^ 0x40000000 ^ lX8 ^ lY8);
            } else {
                return (lResult ^ lX8 ^ lY8);
            }
        }
        var F = function (x, y, z) {
            return (x & y) | ((~x) & z);
        }
        var G = function (x, y, z) {
            return (x & z) | (y & (~z));
        }
        var H = function (x, y, z) {
            return (x ^ y ^ z);
        }
        var I = function (x, y, z) {
            return (y ^ (x | (~z)));
        }
        var FF = function (a, b, c, d, x, s, ac) {
            a = addUnsigned(a, addUnsigned(addUnsigned(F(b, c, d), x), ac));
            return addUnsigned(rotateLeft(a, s), b);
        };
        var GG = function (a, b, c, d, x, s, ac) {
            a = addUnsigned(a, addUnsigned(addUnsigned(G(b, c, d), x), ac));
            return addUnsigned(rotateLeft(a, s), b);
        };
        var HH = function (a, b, c, d, x, s, ac) {
            a = addUnsigned(a, addUnsigned(addUnsigned(H(b, c, d), x), ac));
            return addUnsigned(rotateLeft(a, s), b);
        };
        var II = function (a, b, c, d, x, s, ac) {
            a = addUnsigned(a, addUnsigned(addUnsigned(I(b, c, d), x), ac));
            return addUnsigned(rotateLeft(a, s), b);
        };
        var convertToWordArray = function (string) {
            var lWordCount;
            var lMessageLength = string.length;
            var lNumberOfWordsTempOne = lMessageLength + 8;
            var lNumberOfWordsTempTwo = (lNumberOfWordsTempOne - (lNumberOfWordsTempOne % 64)) / 64;
            var lNumberOfWords = (lNumberOfWordsTempTwo + 1) * 16;
            var lWordArray = Array(lNumberOfWords - 1);
            var lBytePosition = 0;
            var lByteCount = 0;
            while (lByteCount < lMessageLength) {
                lWordCount = (lByteCount - (lByteCount % 4)) / 4;
                lBytePosition = (lByteCount % 4) * 8;
                lWordArray[lWordCount] = (lWordArray[lWordCount] | (string.charCodeAt(lByteCount) << lBytePosition));
                lByteCount++;
            }
            lWordCount = (lByteCount - (lByteCount % 4)) / 4;
            lBytePosition = (lByteCount % 4) * 8;
            lWordArray[lWordCount] = lWordArray[lWordCount] | (0x80 << lBytePosition);
            lWordArray[lNumberOfWords - 2] = lMessageLength << 3;
            lWordArray[lNumberOfWords - 1] = lMessageLength >>> 29;
            return lWordArray;
        };
        var wordToHex = function (lValue) {
            var WordToHexValue = "", WordToHexValueTemp = "", lByte, lCount;
            for (lCount = 0; lCount <= 3; lCount++) {
                lByte = (lValue >>> (lCount * 8)) & 255;
                WordToHexValueTemp = "0" + lByte.toString(16);
                WordToHexValue = WordToHexValue + WordToHexValueTemp.substr(WordToHexValueTemp.length - 2, 2);
            }
            return WordToHexValue;
        };
        var uTF8Encode = function (string) {
            string = string.replace("// x0d/x0a/g", "/x0a");
            var output = "";
            for (var n = 0; n < string.length; n++) {
                var c = string.charCodeAt(n);
                if (c < 128) {
                    output += String.fromCharCode(c);
                } else if ((c > 127) && (c < 2048)) {
                    output += String.fromCharCode((c >> 6) | 192);
                    output += String.fromCharCode((c & 63) | 128);
                } else {
                    output += String.fromCharCode((c >> 12) | 224);
                    output += String.fromCharCode(((c >> 6) & 63) | 128);
                    output += String.fromCharCode((c & 63) | 128);
                }
            }
            return output;
        };

        function showm(string) {
            var x = Array();
            var k, AA, BB, CC, DD, a, b, c, d;
            var S11 = 7, S12 = 12, S13 = 17, S14 = 22;
            var S21 = 5, S22 = 9, S23 = 14, S24 = 20;
            var S31 = 4, S32 = 11, S33 = 16, S34 = 23;
            var S41 = 6, S42 = 10, S43 = 15, S44 = 21;
            string = uTF8Encode(string);
            x = convertToWordArray(string);
            a = 0x67452301;
            b = 0xEFCDAB89;
            c = 0x98BADCFE;
            d = 0x10325476;
            for (k = 0; k < x.length; k += 16) {
                AA = a;
                BB = b;
                CC = c;
                DD = d;
                a = FF(a, b, c, d, x[k + 0], S11, 0xD76AA478);
                d = FF(d, a, b, c, x[k + 1], S12, 0xE8C7B756);
                c = FF(c, d, a, b, x[k + 2], S13, 0x242070DB);
                b = FF(b, c, d, a, x[k + 3], S14, 0xC1BDCEEE);
                a = FF(a, b, c, d, x[k + 4], S11, 0xF57C0FAF);
                d = FF(d, a, b, c, x[k + 5], S12, 0x4787C62A);
                c = FF(c, d, a, b, x[k + 6], S13, 0xA8304613);
                b = FF(b, c, d, a, x[k + 7], S14, 0xFD469501);
                a = FF(a, b, c, d, x[k + 8], S11, 0x698098D8);
                d = FF(d, a, b, c, x[k + 9], S12, 0x8B44F7AF);
                c = FF(c, d, a, b, x[k + 10], S13, 0xFFFF5BB1);
                b = FF(b, c, d, a, x[k + 11], S14, 0x895CD7BE);
                a = FF(a, b, c, d, x[k + 12], S11, 0x6B901122);
                d = FF(d, a, b, c, x[k + 13], S12, 0xFD987193);
                c = FF(c, d, a, b, x[k + 14], S13, 0xA679438E);
                b = FF(b, c, d, a, x[k + 15], S14, 0x49B40821);
                a = GG(a, b, c, d, x[k + 1], S21, 0xF61E2562);
                d = GG(d, a, b, c, x[k + 6], S22, 0xC040B340);
                c = GG(c, d, a, b, x[k + 11], S23, 0x265E5A51);
                b = GG(b, c, d, a, x[k + 0], S24, 0xE9B6C7AA);
                a = GG(a, b, c, d, x[k + 5], S21, 0xD62F105D);
                d = GG(d, a, b, c, x[k + 10], S22, 0x2441453);
                c = GG(c, d, a, b, x[k + 15], S23, 0xD8A1E681);
                b = GG(b, c, d, a, x[k + 4], S24, 0xE7D3FBC8);
                a = GG(a, b, c, d, x[k + 9], S21, 0x21E1CDE6);
                d = GG(d, a, b, c, x[k + 14], S22, 0xC33707D6);
                c = GG(c, d, a, b, x[k + 3], S23, 0xF4D50D87);
                b = GG(b, c, d, a, x[k + 8], S24, 0x455A14ED);
                a = GG(a, b, c, d, x[k + 13], S21, 0xA9E3E905);
                d = GG(d, a, b, c, x[k + 2], S22, 0xFCEFA3F8);
                c = GG(c, d, a, b, x[k + 7], S23, 0x676F02D9);
                b = GG(b, c, d, a, x[k + 12], S24, 0x8D2A4C8A);
                a = HH(a, b, c, d, x[k + 5], S31, 0xFFFA3942);
                d = HH(d, a, b, c, x[k + 8], S32, 0x8771F681);
                c = HH(c, d, a, b, x[k + 11], S33, 0x6D9D6122);
                b = HH(b, c, d, a, x[k + 14], S34, 0xFDE5380C);
                a = HH(a, b, c, d, x[k + 1], S31, 0xA4BEEA44);
                d = HH(d, a, b, c, x[k + 4], S32, 0x4BDECFA9);
                c = HH(c, d, a, b, x[k + 7], S33, 0xF6BB4B60);
                b = HH(b, c, d, a, x[k + 10], S34, 0xBEBFBC70);
                a = HH(a, b, c, d, x[k + 13], S31, 0x289B7EC6);
                d = HH(d, a, b, c, x[k + 0], S32, 0xEAA127FA);
                c = HH(c, d, a, b, x[k + 3], S33, 0xD4EF3085);
                b = HH(b, c, d, a, x[k + 6], S34, 0x4881D05);
                a = HH(a, b, c, d, x[k + 9], S31, 0xD9D4D039);
                d = HH(d, a, b, c, x[k + 12], S32, 0xE6DB99E5);
                c = HH(c, d, a, b, x[k + 15], S33, 0x1FA27CF8);
                b = HH(b, c, d, a, x[k + 2], S34, 0xC4AC5665);
                a = II(a, b, c, d, x[k + 0], S41, 0xF4292244);
                d = II(d, a, b, c, x[k + 7], S42, 0x432AFF97);
                c = II(c, d, a, b, x[k + 14], S43, 0xAB9423A7);
                b = II(b, c, d, a, x[k + 5], S44, 0xFC93A039);
                a = II(a, b, c, d, x[k + 12], S41, 0x655B59C3);
                d = II(d, a, b, c, x[k + 3], S42, 0x8F0CCC92);
                c = II(c, d, a, b, x[k + 10], S43, 0xFFEFF47D);
                b = II(b, c, d, a, x[k + 1], S44, 0x85845DD1);
                a = II(a, b, c, d, x[k + 8], S41, 0x6FA87E4F);
                d = II(d, a, b, c, x[k + 15], S42, 0xFE2CE6E0);
                c = II(c, d, a, b, x[k + 6], S43, 0xA3014314);
                b = II(b, c, d, a, x[k + 13], S44, 0x4E0811A1);
                a = II(a, b, c, d, x[k + 4], S41, 0xF7537E82);
                d = II(d, a, b, c, x[k + 11], S42, 0xBD3AF235);
                c = II(c, d, a, b, x[k + 2], S43, 0x2AD7D2BB);
                b = II(b, c, d, a, x[k + 9], S44, 0xEB86D391);
                a = addUnsigned(a, AA);
                b = addUnsigned(b, BB);
                c = addUnsigned(c, CC);
                d = addUnsigned(d, DD);
            }
            var tempValue = wordToHex(a) + wordToHex(b) + wordToHex(c) + wordToHex(d);
            return tempValue.toUpperCase();
        }
        """)
        # 加密后请求偏移量
        js_func = """showm(showm(sdfsgfdg("{mk}") + "beiji" + "{ak}"))""".format(mk=mk, ak=ak)
        token = js_compiled.eval(js_func)
        print("mk:%s\nak:%s\ntoken:%s" % (mk, ak, token))
        offset_url = "https://www.zdaye.com/{mk}_{token}.gif".format(mk=mk, token=token)
        yield scrapy.Request(offset_url, method='get', callback=self.parse, dont_filter=True)

    def parse(self, response):
        """
        拿到偏移量，开始解析页面中的代理
        :param response:
        :return:
        """
        if self.need_decrypt:
            self.offset = response.text
            print("offset:%s" % self.offset)
        else:
            self.get_dom_list(response)
            self.get_total_page_count(response)
        for proxy in self.proxy_dom_list:
            # proxy_info = {}
            proxy_info = ProxyItem()
            # 根据偏移量算出真实IP和端口
            if self.need_decrypt:
                # 有加密时用
                ip_v_list = proxy.xpath("""./td[1]/@v""").extract_first().split("#")[::-1]
                port_v_list = proxy.xpath("""./td[2]/@v""").extract_first().split("#")[::-1]
                proxy_info["address"] = proxy.xpath("""./td[1]/text()""").extract_first().replace("wait",
                                                                                             self.decrypt(ip_v_list))
                proxy_info["port"] = proxy.xpath("""./td[2]/text()""").extract_first().replace("wait",
                                                                                         self.decrypt(port_v_list))
            else:
                # 无加密时用
                proxy_info["address"] = proxy.xpath("""./td[1]/text()""").extract_first()
                proxy_info["port"] = proxy.xpath("""./td[2]/text()""").extract_first()
            # 处理其它字段
            # proxy_info["ip"] = proxy.xpath("""./td[1]/text()""").extract_first().replace("wait",
            #                                                                              self.decrypt(ip_v_list))
            # proxy_info["port"] = proxy.xpath("""./td[2]/text()""").extract_first().replace("wait",
            #                                                                                self.decrypt(port_v_list))
            # proxy_info["anonymous"] = proxy.xpath("""./td[3]/text()""").extract_first()
            # proxy_info["location"] = proxy.xpath("""./td[4]/text()""").extract_first().split(" ")[0]
            # proxy_info["operator"] = proxy.xpath("""./td[4]/text()""").extract_first().split(" ")[1]
            # proxy_info["last_verify"] = proxy.xpath("""./td[5]/text()""").extract_first()
            # proxy_info["support_https"] = True if proxy.xpath("""./td[6]/div/@class""") else False
            # proxy_info["support_post"] = True if proxy.xpath("""./td[7]/div/@class""") else False
            # proxy_info["response_time"] = proxy.xpath("""./td[8]//text()""").extract_first().strip()
            # proxy_info["live_time"] = proxy.xpath("""./td[9]/text()""").extract_first()

            proxy_info["protocol"] = "https" if proxy.xpath("""./td[6]/div/@class""") else "http"
            proxy_info["type"] = proxy.xpath("""./td[3]/text()""").extract_first()
            proxy_info["add_time"] = datetime.now()
            proxy_info["update_time"] = datetime.now()
            proxy_info["is_available"] = 1
            proxy_info["is_delete"] = 0
            try:
                response_time = proxy.xpath("""./td[8]//text()""").extract_first().strip()
                if int(response_time) < self.resp_time__lt:
                    yield proxy_info
            except:
                pass

        # 处理翻页
        if self.current_page_no < self.total_page_count:
            self.current_page_no += 1
            print("crawl page %s/%s" % (self.current_page_no, self.total_page_count))
            time.sleep(9)
            yield scrapy.Request(self.data_url%self.current_page_no, callback=self.cb, dont_filter=True)