#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib, urllib2
import time,datetime, re, json
import ConfigParser, logging

def getUrlDiscriptionByUrl(sectionUrl, resourcePattern, resourceDetailPattern):

	logging.info("sectionUrl:", sectionUrl);
	logging.info("resourcePattern:", resourcePattern);
	logging.info("resourceDetailPattern:", resourceDetailPattern);

	content=urllib2.urlopen(sectionUrl).read()
	resourcePatternMatch=re.compile(resourcePattern)
	siteUrls=re.findall(resourcePatternMatch, content)

	if sectionUrl.endswith('/') :
		sectionUrl = sectionUrl[:-1]

	result = []
	print siteUrls
	for asite in siteUrls:
		print asite
		curSiteUrl = sectionUrl + asite;
		print curSiteUrl

		resourceDetailPatternMatch=re.compile(resourceDetailPattern)
		contentDetail=urllib2.urlopen(curSiteUrl).read()
		titleDetail=re.findall(resourceDetailPatternMatch, contentDetail)
		print titleDetail
		titleDetail=titleDetail[0].replace("‘","'")
		titleDetail=titleDetail.replace("“","\"")
		titleDetail=titleDetail.replace("；", ",.;")

		result.append('{0}:\n{1}'.format(titleDetail, curSiteUrl))

	return result;

def getAllMessageToSend():
	conf = ConfigParser.ConfigParser()
	conf.read('spider.ini')
	items = conf.get("COUNT", "ITEMS")
	if items <= 0:
		sys.exit("no valid data was found!");

	urlDiscriptionList = []
	for index in range(0, int(items)):
		section ="COUNT_" + '%d' % (index + 1);
		sectionUrl = conf.get(section, "REQUEST_URL");
		resourcePattern = conf.get(section, "RESOURCE_PATTERN");
		logging.info("sectionUrl", sectionUrl);
		logging.info("resourcePattern", resourcePattern);

		if len(sectionUrl) == 0 or len(resourcePattern) == 0:
			continue;

		resourceDetailPattern = conf.get(section, "RESOURCE_DETAIL_PATTERN");
		logging.info("resourceDetailPattern", resourceDetailPattern);

		resourcePattern = resourcePattern.replace('${YEAD}', datetime.datetime.now().strftime("%Y"))
		resourcePattern = resourcePattern.replace('${MONTH}', datetime.datetime.now().strftime("%m"))
		resourcePattern = resourcePattern.replace('${DAY}', datetime.datetime.now().strftime("%d"))

		logging.info("sectionUrl=%s,resourcePattern=%s,resourceDetailPattern=%s", sectionUrl, resourcePattern, resourceDetailPattern);

		urlDiscription = getUrlDiscriptionByUrl(sectionUrl, resourcePattern, resourceDetailPattern);
		urlDiscriptionList.extend(urlDiscription)
	return urlDiscriptionList;

def sendMessage(accessToken, messsageText):
	posturl = "https://oapi.dingtalk.com/robot/send?access_token=" + accessToken
	data = {"msgtype": "markdown", "markdown": {"text":messsageText,"title":"Jenkins","isAtAll": "false"}}
	sendDingDingMessage(posturl, data)


#send Dingding message
def sendDingDingMessage(url, data):
	req = urllib2.Request(url)
	req.add_header("Content-Type", "application/json; charset=utf-8")
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	response=opener.open(req,json.dumps(data))
	print response.read()


tokenText="e31ce0a3f8eaffe79f5e0dad5345ddb2c0a6f148c3a07a3dc6aeecd2a5bb1fed";
if __name__ == '__main__':
	messageList = getAllMessageToSend();
	for aMessage in messageList:
		logging.info("aMessage:%s", aMessage);
		sendMessage(tokenText, aMessage)
