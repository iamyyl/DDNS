'''
DDNS 主程序 使用阿里云的SDK发起请求
Created By Martin Huang on 2018/5/20
修改记录：
2018/5/20 => 第一版本
2018/5/26 => 增加异常处理、Requst使用单例模式，略有优化
2018/5/29 => 增加网络连通性检测，只有联通时才进行操作，否则等待
2018/6/10 => 使用配置文件存储配置，避免代码内部修改(需要注意Python模块相互引用问题)
2018/9/24 => 修改失败提示信息
'''
import logging
logging.basicConfig(filename='/mnt/usbhome/log/DDNS.log', level=logging.INFO)
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.acs_exception.exceptions import ClientException
from Utils import Utils
import time
import argparse

waitSeconds = 60
prvIp = ""

def getRealIp(use_v6):
	if use_v6:
		ip = Utils.getRealIPv6()
		type = 'AAAA'
	else:
		ip = Utils.getRealIP()
		type = 'A'
	return ip, type
	
def DDNS(ip, type):
	client = Utils.getAcsClient()
	recordId, ipOnAli = Utils.getRecordId(Utils.getConfigJson().get('Second-level-domain'))

	request = Utils.getCommonRequest()
	request.set_domain('alidns.aliyuncs.com')
	request.set_version('2015-01-09')
	request.set_action_name('UpdateDomainRecord')
	request.add_query_param('RecordId', recordId)
	request.add_query_param('RR', Utils.getConfigJson().get('Second-level-domain'))
	request.add_query_param('Type', type)
	request.add_query_param('Value', ip)
	response = client.do_action_with_exception(request)
	return response

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='DDNS')
	parser.add_argument('-6', '--ipv6', nargs='*', default=False)
	args = parser.parse_args()
	isipv6 = isinstance(args.ipv6, list)

	logging.info("Starting.....")
	while (True):
		#if not Utils.isOnline():
			#logging.info("not online")
			#time.sleep(waitSeconds)
			#continue
		try:
			ip, type = getRealIp(isipv6)
			if (ip is None or prvIp == str(ip)):
				logging.info("ip not changed")
				time.sleep(waitSeconds)
				continue;	
			prvIp = str(ip)
			result = DDNS(ip, type)
			logging.info("Set succ, ip:", str(ip))
		except (ServerException,ClientException) as reason:
			logging.warning("Set Faild, reason:")
			logging.warning(reason.get_error_msg())
		else:
			logging.warning("unknow exception")
		pass #while pass
	logging.info("End")

