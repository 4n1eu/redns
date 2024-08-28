import socketserver
import handlers
from config import getConfig

if __name__ == "__main__":
	dnsserver = socketserver.ThreadingUDPServer((getConfig().LISTEN_HOST, getConfig().LISTEN_PORT), getattr(handlers, getConfig().PROXY_CLASS))
	dnsserver.serve_forever()