import sys
import string
import requests
import socket
import threading
import os.path 
import os
import time
import random
import pickle
import pc

proxyPort = pc.port
cache_time = pc.ctime
timer = pc.timeout
Max_con = pc.max_con
max_cache_size = pc.max_cache
cache_dir = pc.directory

website_blacklist = pc.website_bl
host_blacklist = pc.host_bl

recvbuf = 8192
lowbound = 1
highbound = 1000000

cache_size = 0
cache_dict = {}
connections = set()

#class for parsing request
class HandleRequest():
	try:
		def __init__(self, x):
			sep = '\r\n'
			subs = x.split(sep)
		
			self.command = subs[0].split(' ')[0]
			self.path = subs[0].split(' ')[1]
			self.version = subs[0].split(' ')[2]
		
			del subs[0]
			heads = dict()
			for i in subs:
				tmp = i.split(': ')
				if len(tmp) == 2:
					heads[tmp[0].lower()] = tmp[1]
		
			self.headers = heads
	except:
		pass

def errorResponse():
	res = 'HTTP/1.1 200 OK\r\nDate: Mon, 27 Jul 2019 12:28:53 GMT\r\nServer: Apache/2.2.14 (Win32)\r\nLast-Modified: Wed, 22 Jul 2009 19:15:56 GMT\r\nContent-Length: 128\r\nContent-Type: text/html\r\nConnection: Closed\r\n\r\n'

	sep = '\r\n'
	headers = res.split(sep)
	t = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
	#print(t)
	headers[1] = ("Date: " + t)
	error_res = sep.join(headers)
	return error_res.encode()
	
def conditional_get(browserSocket, hostname, request, filename, url):
	global cache_size
	sep = '\r\n'
	headers = request.split(sep.encode())
	t = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(os.path.getatime(filename)))
	n = len(headers)
	headers[n-2] = ("If-Modified-Since: " + t).encode()
	headers.append(''.encode())
	mod_req = sep.encode().join(headers)
	webserverSocket = connect_to_webserver(hostname)
	try :
        	webserverSocket.sendall(mod_req)
	except :
        	webserverSocket.close()
        	return
	browser_response = webserverSocket.recv(8192)
	if int(browser_response.split(' '.encode())[1]) != 200:
		flag = 1
	else:
		flag = 0
		if(len(browser_response) > 0):
			browserSocket.send(browser_response)
		cache_data_pickle = []
		cache_data_pickle.append(browser_response)
		while 1 :	#wait for some time to receive and keep appending the response
			try:
				webserverSocket.settimeout(timer)
				browser_response = webserverSocket.recv(8192)
				cache_data_pickle.append(browser_response)
			except socket.timeout:
				break

			if(len(browser_response) > 0):
				browserSocket.send(browser_response)
			else :
				break
		minus = os.path.getsize(filename)	
		cache_up = open(filename, 'wb+')
		pickle.dump(cache_data_pickle, cache_up)
		cache_size = (cache_size - minus) + os.path.getsize(filename)
		cache_up.close()	
	webserverSocket.close()
	return flag
#connects to the hostname's webserver and returns the web server socket
def connect_to_webserver(hostname):
	try :
		host_ip = socket.gethostbyname(hostname)
	except :
		return
	#establish connection to the IP
	try :
		webserverSocket = createTCPsocket()
	except:
		return
	try:
		webserverSocket.connect((host_ip, 80))
		return webserverSocket
	except :
        	webserverSocket.close()
        	return
#cache response is saved into a file
def dump_response_into_file(cache_data_pickle, url) :
	global cache_size
	try:	
		cache_dict[str(url)] = rnum(cache_dir) 
		cache_file = open(cache_dir + '/' + cache_dict[str(url)], 'wb+')
		pickle.dump(cache_data_pickle, cache_file)
		cache_size = cache_size + os.path.getsize(cache_dir + '/' + cache_dict[str(url)])
		cache_file.close()
		return cache_file
	except Exception as e:
		print(e)

def rnum(dirt):
	while True:
		num = random.randint(lowbound, highbound)
		if os.path.isfile(dirt + str(num)) == False:
			return str(num)

def createTCPsocket():
    try:
        newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return newsocket
    except:
        print('Failed to create a socket')

def threadFunc(x, browserSocket, addr):
	try :
		request = HandleRequest(x.decode())
		#check if the website is in whitelist or blacklist
		if request.headers['host'] in website_blacklist :
			#send the message in an html file
			err_res = errorResponse()
			browserSocket.send(err_res)
			html_file = open('html/error.html', 'rb')
			browserSocket.sendfile(html_file)
			browserSocket.close()
			return
		#checking if the response is in the cache or not
		if request.command == 'GET' :
			if request.path in cache_dict.keys():
				filename = cache_dir + '/' + cache_dict[str(request.path)]
				flag = conditional_get(browserSocket, str(request.headers['host']), x, filename, request.path)
				if flag == 1 :
					with open(filename, 'rb+') as pickle_file:
						list_from_cache = pickle.load(pickle_file)
						for i in list_from_cache:
							browserSocket.send(i)
					pickle_file.close()
			else:
		    		servetheresponse(str(request.headers['host']), x, browserSocket, request.path)
		elif request.command == 'POST':
			servetheresponse(str(request.headers['host']), x, browserSocket, request.path)
		
		else:
		    print('Cannot serve ' + request.command +' requests')

	except Exception as e: #socket.timeout :
	    pass
	    #print(e)
	    #print('Closing the browser socket. Problem in thread')

	try:
		connections.remove(addr)
	except:
		pass
	browserSocket.close()
	
#funtion for serving "POST" request without caching
def servetheresponse(hostname, browser_request, browserSocket) :
	try:	
		webserverSocket = connect_to_webserver(hostname)
	except:
		return
	try :
		webserverSocket.sendall(browser_request)
	except :
		webserverSocket.close()
		return
	while 1 :	#wait for some time to receive and keep appending the response
		try:
			webserverSocket.settimeout(timer)
			browser_response = webserverSocket.recv(8192)
		except socket.timeout:
			break
		if(len(browser_response) > 0):
			browserSocket.send(browser_response)
		else :
			break
	webserverSocket.close()
	return

#function to serve the "GET" request with caching
def servetheresponse(hostname, browser_request, browserSocket, url) :
	try:	
		webserverSocket = connect_to_webserver(hostname)
	except:
		return
	try :
		webserverSocket.sendall(browser_request)
	except :
		webserverSocket.close()
		return
	cache_data_pickle = []
	while 1 :	#wait for some time to receive and keep appending the response
		try:
			webserverSocket.settimeout(timer)
			browser_response = webserverSocket.recv(8192)
			cache_data_pickle.append(browser_response)
		except socket.timeout:
			break

		if(len(browser_response) > 0):
			browserSocket.send(browser_response)

		else :
			break                
        #use pickel to save
	cache_file = dump_response_into_file(cache_data_pickle, url)
	webserverSocket.close()
	return

def cleanup_cache(dir_path):
	global cache_size
	while True:
		if cache_size >= max_cache_size:
			#print("CACHE SIZE EXCEEDED!")
			for entry in os.listdir(dir_path):
				if (time.time() - os.path.getatime(os.path.join(dir_path, entry))) > cache_time:
					os.remove(os.path.join(dir_path, entry))
					print('File deleted')
		time.sleep(1800)	
			
def main():
	cleanup = threading.Thread(target = cleanup_cache, args = (cache_dir, ))
	cleanup.start()
	#creating a socket and binding the socket to the port
	proxySocket = createTCPsocket()
	try :
	    proxySocket.bind(('',proxyPort))
	except:
	    print('Error in binding the Proxy socket')
	proxySocket.listen(10)
	while True:
		try:
			if len(connections) < Max_con:
				browserSocket, addr = proxySocket.accept()
				connections.add(addr)
			else:
				print("OOPS! Server busy")
		except:
			pass
		if addr[0] in host_blacklist or pc.checkHostRange == False:
			try:
				connection.remove(addr)
			except:
				pass
			print("Blacklisted "+ addr[0] + " tried to access proxy")
			browserSocket.close()
		else:
			try:
				browserSocket.settimeout(timer)
				x = browserSocket.recv(recvbuf)		#x contains the data i.e the HTTP request message
			except socket.timeout:
				try:
					connections.remove(addr)
				except:
					pass
				browserSocket.close()
			t = addr[1] 	#port number
			t = threading.Thread(target = threadFunc, args=(x, browserSocket, addr)) #define thread
			t.start()				#start thread
	proxySocket.close()
if __name__ == "__main__":
	main()
