import socket
from threading import Thread

default_filestypes = {".css":"text/css",".pdf":"application/pdf",".rar":"application/x-rar-compressed",".ico":"image/x-icon",".js":"application/javascript",".html":"text/html"}

def redirect(url):
	return "<script>window.location.href='"+url+"';</script>"

def template(filename,**kwargs):
	try:
		with open("templates/"+filename,"r") as file:
			data = file.read()
			response = data.format(**kwargs)
			def search(response):
				import_html = response.split("&&&")
				for i in range(len(import_html)):
					if i%2:
						import_html[i] = template(import_html[i],**kwargs)
				response = "".join(import_html)
				return response
			response = search(response)
			return response
	except:
		return ""

def methods(*args):
	def methods_verif(func):
		def verif(user,var=None):
			if user.request.method in args:
				return func(user)
			else:
				if "bad_request" in user.__urls__:
					args = []
					if "user" in func.__code__.co_varnames[:func.__code__.co_argcount]:
						args.append(user)
					if var:
						args.append(var)
					return user.__urls__["bad request"](*args)
				return "Mauvaise methode de requete"
		return verif
	return methods_verif

def need_cookies(*args):
	def methods_verif(func):
		def verif(user,var=None):
			for arg in args:
				if arg not in user.cookies.keys():
					if "bad_cookie" in user.__urls__:
						args = []
						if "user" in func.__code__.co_varnames[:func.__code__.co_argcount]:
							args.append(user)
						if var:
							args.append(var)
						return user.__urls__["bad_cookie"](*args)
					return "Mauvaise methode de requete"
			return func(user)
		return verif
	return methods_verif

def find_file(user,filename):
	try:
		for ending in default_filestypes:
			if filename.endswith(ending):
				user.accept = default_filestypes[ending]
		with open("files/"+filename,"rb") as file:
			data = file.read()
			return data
	except:
		return ""

class Request():

	def __init__(self,method,url,post):
		self.method = method
		self.url = url
		self.form = {}
		self.search_url(url)
		self.search_post(post)

	def search_url(self,url):
		url = url.split("?")
		if len(url) > 1:
			self.set_form(url[1])

	def search_post(self,post):
		if not post == "":
			self.set_form(post)

	def set_form(self,form):
		infos_form = {}
		for variable in form.split("&"):
			variable = variable.split("=")
			infos_form[variable[0]]=variable[1]
		self.form = infos_form

class User:

	def __init__(self,infos,request,__urls__):
		self.infos = infos
		self.request = request
		self.cookies = self.get_cookies()
		self.cookies_to_set = {}
		self.cookies_to_delete = []
		self.accept = self.search_accept(infos)
		self.__urls__ = __urls__

	def set_cookie(self,cookie,value):
		self.cookies_to_set[cookie] = value

	def delete_cookie(self,cookie):
		self.cookies_to_delete.append(cookie)

	def get_cookies(self):
		data = self.infos.split("\r\n")
		data.pop(0)
		cookies = {}
		for i in data:
			if i.startswith("Cookie:"):
				for cookie in i[8:].split("; "):
					cookie = cookie.split("=")
					cookies[cookie[0]] = cookie[1]
				break
		#print(cookies)
		return cookies

	def search_accept(self,infos):
		try:
			zone = infos.split("Accept: ")[1]
			accept = zone.split(",")[0]
		except:
			data = infos.split("\r\n")
			data = data[0].split(" ")
			data = data[1].split(".")
			extension = data[1]
			accept = "text/"+extension
		return accept

class Process():

	def __init__(self,page,client,infos,urls={},var=None):
		self.page = page
		self.client = client
		self.infos = infos
		self.__urls__ = urls
		self.var = var

	def do(self):

		user = self.create_user()
		cookies = ""

		if type(self.page) == str:
			if self.page.startswith("/files/"):
				reponse = find_file(user,self.page[6:])
		else:
			args = []
			if "user" in self.page.__code__.co_varnames[:self.page.__code__.co_argcount]:
				args.append(user)
			if self.var:
				args.append(self.var)
			reponse = self.page(*args)
			for i,j in user.cookies_to_set.items():
				cookies += "Set-Cookie: "+str(i)+"="+str(j)+"\r\n"
			for i in user.cookies_to_delete:
				cookies += "Set-Cookie: "+str(i)+"=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n"

		#print("Reponse : ",response_to_client)
		if reponse == None:
			print("Aucun retour")
			return self.client.close()

		elif type(reponse) == type(b""):

			response_to_client = "HTTP/1.0 200 OK\r\nContent-Type: "+user.accept+"\r\n"+cookies+"\r\n"
			self.client.send(response_to_client.encode()+reponse)

		else:
			response_to_client = "HTTP/1.0 200 OK\r\nContent-Type: "+user.accept+"\r\n"+cookies+"\r\n"+str(reponse)
			self.client.send(response_to_client.encode())

		self.client.close()

		return True

	def create_user(self):
		data = self.infos.split("\r\n")
		#print(data)
		protocol = data[0].split(" ")
		request = Request(protocol[0],protocol[1],data[-1])
		user = User(self.infos,request,self.__urls__)
		return user

class Recv(Thread):

	def __init__(self,url,connect_client):
		Thread.__init__(self)
		self.url = url
		self.connect_client = connect_client
		self.start()

	def run(self):
		connect_client = self.connect_client

		infos = connect_client.recv(16777216).decode("utf-8")
		data = infos.split("\r\n")
		protocol = data[0].split(" ")
		#print(infos)

		try:
			request_page = protocol[1].split("?")[0]
		except:
			return

		print("Request : "+request_page)

		if self.test_page(request_page,connect_client,infos):
			return

		tests_pages = request_page.split("/")

		for i in range(len(tests_pages)-1):
			i = i+1
			if i > 1:
				a = "/".join(tests_pages[:-i]+["___"]+tests_pages[-(i-1):])
				if self.test_page(a,connect_client,infos,var=tests_pages[-i]):
					return
			a = "/".join(tests_pages[:-i]+["___"])
			if self.test_page(a,connect_client,infos,var="/".join(tests_pages[-i:])):
				return

		print("Result : Not Found")
		connect_client.send("HTTP/1.1 404 Not Found\n\n<html><body><center><h3>Error 404</h3></center></body></html>".encode('utf-8'))
		return connect_client.close()

	def test_page(self,request_page,connect_client,infos,var=None):
		if request_page in self.url:
			print("Result : Okay")
			client = Process(self.url[request_page],connect_client,infos,self.url,var=var)
			return client.do()
		elif request_page.startswith("/files/"):
			print("Result : Okay")
			client = Process(request_page,connect_client,infos,self.url,var=var)
			return client.do()
		else:
			if "error" in self.url:
				print("Result : Not Found")
				client = Process(self.url["error"],connect_client,infos,self.url,var=var)
				return client.do()


class Listening(Thread):

	def __init__(self,host,port,serv):
		Thread.__init__(self)
		self.serv = serv
		self.host = host
		self.port = port
		self.work = 0
		self.socket = None

	def run(self):

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((self.host,self.port))
		self.socket.listen(10)

		while self.work:
			try:
				connect_client, nothing = self.socket.accept()
			except OSError:
				self.work = 0
				return
			Recv(self.url,connect_client)

class Server():

	def __init__(self,host,port):
		self.url = {}
		self.listen = Listening(host,port,self)

		@self.path("/favicon.ico")
		def favicon(user):
			return find_file(user,"favicon.ico")

	def path(self,adress):

		def add_fonction(function):

			if adress.format(var="___") != adress:
				self.url[adress.format(var="___")] = function

			else:
				self.url[adress] = function

			return function

		return add_fonction

	def start(self):
		
		print("Starting Server")

		self.listen.start()
		self.listen.work = 1

		try:
			while self.listen.work:
				pass
		except KeyboardInterrupt:
			self.stop()

	def stop(self):

		if self.listen.socket:
			print("Stopping Server")
			self.listen.socket.close()
