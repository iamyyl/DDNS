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
import os
import sys
import json
import time
import signal
import errno
import argparse
import socket
import SocketServer
import logging

from Utils import Utils

from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.acs_exception.exceptions import ClientException

logFilename = None
logPath = None
try:
	logPath = Utils.getLogpath()
	logFilename = logPath + '/DDNS.log'
except:
	logFilename='/tmp/DDNS.log'
	logPath = None
	pass

logging.basicConfig(filename=logFilename,
	format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s:%(message)s'
	, level=logging.INFO)

waitSeconds = 300000
prvIp = ""
isipv6 = None
times = 0
daemonIP, daemonPort = Utils.getDaemonIpPort()
pid = None
FC = '{"failed" : 1}'

def getRealIp(use_v6, times):
	if use_v6: 
		ip = Utils.getRealIPv6()
	else:
		ip = Utils.getRealIP(times)
	return ip

def getIpType(use_v6):
	if use_v6:
		return 'AAAA'
	else:
		return 'A'
	
def DDNS(ip, type):
	client = Utils.getAcsClient()
	recordId, ipOnAli = Utils.getRecordId(Utils.getConfigJson().get('Second-level-domain'))
	if ((not (ip is None)) and ip == ipOnAli):
		logging.warning("DDNS : ip == ipOnAli.")
		return None

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

def getIpOnAli():
	client = Utils.getAcsClient()
	recordId, ipOnAli = Utils.getRecordId(Utils.getConfigJson().get('Second-level-domain'))
	return ipOnAli
	
def send(content):
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sockIp, sockPort = SocketServer.getAddress()
	server_address = (sockIp, sockPort)
	sock.connect(server_address)
	sock.send(content.encode())
	sock.close()
	pass

def timeoutFn():
	global times
	global pid
	pid = os.fork()
	if (pid == 0):
		# Child
		content = None
		try:
			ip = getRealIp(isipv6, times)
			logging.info('getRealIp : times= ' + str(times) + ', ip=' + str(ip))
			content = '{"getrealip" : "'+ str(ip) + '"}'
		except Exception as e:
			logging.warning('Client error : ' + str(e) + ', times=' + str(times))
			content = FC
		finally:
			send(content)
			sys.exit(0)
		pass
	else:
		# Parent
		times += 1
		return
	pass # timeoutFn()

def changeIp(ip):
	global prvIp
	global pid
	if (prvIp == ip):
		logging.info("ip not changed")
		return
	pid = os.fork()
	if (pid == 0):
		#Child
		content = None
		try:
			type = getIpType(isipv6)
			result = DDNS(ip, type)
			content = '{"ddns" : "'+ str(ip) + '"}'
		except Exception as e:
			logging.warning('DDNS error : ' + str(e))
			content = FC
		finally:
			send(content)
			sys.exit(0)
			pass
	else:
		# Parent
		pass
	pass

def recivedFn(content):
	global pid
	global prvIp
	os.waitpid(-1, 0)
	pid = 0
	
	if (content is None):
		logging.info("recieved content is None!")
		return
	
	d = json.loads(content.decode('utf-8'))
	keys = d.keys()
	for key in keys:
		if (key == 'getrealip'):
			changeIp(d[key])
		elif (key == 'ddns'):
			prvIp = d[key] 
			logging.info("Set succ, ip: " + str(d[key]))
		elif (key == 'failed'):
			logging.info("recieved failed.")
		else:
			logging.warning("recived unknown key : " + key)
			pass
	pass

def run():
	global isipv6
	global prvIp
	parser = argparse.ArgumentParser(description='DDNS')
	parser.add_argument('-6', '--ipv6', nargs='*', default=False)
	args = parser.parse_args()
	isipv6 = isinstance(args.ipv6, list)
	
	logging.info("Starting.....")
	if (not SocketServer.initServer(daemonIP, daemonPort)):
		logging.error("Init socket server failed, ip=" + str(daemonIP) + ", port = " + str(daemonPort))
		return	
	
	while(True):
		try:
			prvIp = getIpOnAli()
			break
		except Exception as e:
			logging.error('getIpOnAli failed:' + str(e))
			time.sleep(5*60)
			continue
		
	SocketServer.runServer(timeout=waitSeconds,timeoutFn=timeoutFn, recivedFn=recivedFn)
	
	logging.info("End")

if __name__ == "__main__":
	run()

