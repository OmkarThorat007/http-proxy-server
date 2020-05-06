# # # # HTTP PROXY SERVER # # # #

To run localhost as proxy server: Change HTTP Proxy to "127.0.0.1" and Port to "9999"

To start proxy run : _" python3 proxy3.py "_

All the configurations of the proxy are mentioned in _etc/proxy.conf_
NOTE: Do not add any extra spaces in this file

# The default configs are as follows:
* HTTP port: 9999
* cache directory: cache (in the same folder)
* cache time: 86400 (24 hours) 
* cache memory: 1000000 (1 MB)
* maximum number of connection: 100
* connection timeout: 20	
* host range: 127.0.0.0/3

* Websites to be blocked stored in etc/website_blacklist
* Hosts to be blocked stored in etc/hosts_blacklist

# Caching:
If the cache memory becomes full, the files accessed before 24 hours from current time (i.e. least recently used) are deleted permanently.

# Few http websites for testing
http://malaysiabutterflies.myspecies.info/
http://www.iczn.org/
http://www.lokmat.in

# Website for testing blacklist
http://www.coep.org.in

# For testing host blacklist
Add " 127.0.0.1 " to the host_blacklist.txt

# For testing host range configuration
Change host_range to 127.0.0.2/3


_EESHA KURODE_ & _OMKAR THORAT_
