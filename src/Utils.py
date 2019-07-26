'''
工具类
Created By Martin Huang on 2018/5/19
修改记录：
2018/5/16 =》删除不需要的方法
2018/5/29 =》增加获取操作系统平台方法，增加网络连通性检测(后续考虑重构)
2018/6/3 =》网络连通性代码重构
2018/6/10 =》增加配置文件读取方法(可能有IO性能影响，考虑重构)
'''

import IpGetter2
import IpGetter
import platform
import subprocess
import json
#from AcsClientSingleton import AcsClientSing
#from CommonRequestSingleton import CommonRequestSing

class Utils:
	#获取真实公网IP
	def getRealIP(times):
		index = times % len(IpGetter2.getIpList())
		ip = IpGetter2.getIpList()[index]()
		return ip

	#获取真实公网IPv6
	def getRealIPv6():
		url = IpGetter.getIpPageV6()
		ip = IpGetter.getRealIpV6(url)
		return ip

	#获取二级域名的RecordId
	def getRecordId(domain):
		client = Utils.getAcsClient()
		request = Utils.getCommonRequest()
		request.set_domain('alidns.aliyuncs.com')
		request.set_version('2015-01-09')
		request.set_action_name('DescribeDomainRecords')
		request.add_query_param('DomainName', Utils.getConfigJson().get('First-level-domain'))
		response = client.do_action_with_exception(request)
		jsonObj = json.loads(response.decode("UTF-8"))
		records = jsonObj["DomainRecords"]["Record"]
		for each in records:
			if each["RR"] == domain:
				return each["RecordId"], each["Value"]
		return None, None

'''
    #获取CommonRequest
    def getCommonRequest():
	    return CommonRequestSing.getInstance()

    #获取AcsClient
    def getAcsClient():
	    return AcsClientSing.getInstance()

    #获取操作系统平台
    def getOpeningSystem():
	    return platform.system()

    #从config.json中获取配置信息JSON串
    def getConfigJson():
	    with open('/etc/ddns_config.json') as file:
		    jsonStr = json.loads(file.read())
	    return jsonStr
'''
if __name__ == '__main__':
	for i in range(1, 10, 1):
		ip = Utils.getRealIP(i)	
		print (ip)