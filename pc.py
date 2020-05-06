#Conf Parser
#port, directory, ctime, max_cache, max_con, timeout, webiste_bl, host_bl func: checkHostRange
f = open("etc/proxy.conf", "r")
lines = f.readlines()
lines = [x.strip() for x in lines]
for x in lines:
	if x == ' ' or x == '' or x == "\n":
		lines.remove(x)
lines = [x.split(" ")[1] for x in lines]

for x in lines:
	if x == '#':
		lines.remove(x)
try:
	port = int(lines[0])
	directory = lines[1]
	ctime = int(lines[2])
	max_cache = int(lines[3])
	max_con = int(lines[4])
	timeout = int(lines[5])

	fw = open(lines[6], "r")
	website_bl = fw.readlines()
	website_bl = [x.strip() for x in website_bl]

	fb = open(lines[7], "r")
	host_bl = fb.readlines()
	host_bl = [x.strip() for x in host_bl]

	hrange = lines[8]

except:
	pass
#returns false if host not in range, true if can connect
def checkHostRange(host):
	for i in range(3):
		if host.split('.')[i] != h.range.split('.')[i]:
			return False
	l = hrange.split('.')[3].split('/')[0]
	h = hrange.split('.')[3].split('/')[1]
	x = host.split('.')[3]
	if  x >= l and x<= h:
		return True
	else:
		return False  

f.close()
fw.close()
fb.close()
