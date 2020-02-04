'''
Module created by Astremy
'''

import socket
from threading import Thread
import time

default_filestypes = {".css":"text/css",".pdf":"application/pdf",".rar":"application/x-rar-compressed",".ico":"image/x-icon",".js":"application/javascript",".html":"text/html"}

def execute_func(function,**kwargs):

	'''
	Take the function and the args in parameters,
	and return the result of the function with the good args
	'''

	send = {}

	for var in function.__code__.co_varnames[:function.__code__.co_argcount]:
		if var in kwargs and kwargs[var]:
			send[var] = kwargs[var]
		else:
			send[var] = None

	return function(**send)

def redirect(url):
	
	'''
	Just a script for redirect to an another page
	'''

	return "<script>window.location.href='"+url+"';</script>"

def template(filename,**kwargs):

	'''
	Search a file in 'templates' folder, and return the data.
	Format with the kwargs, and add others files if he contain
	'&&&file.html&&&'
	'''

	try:
		with open("templates/"+filename,"r",encoding="utf-8") as file:
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

	'''
	Decorator, to force the user to use specifics methods
	of request for accessing to the page
	'''

	def methods_verif(func):
		def verif(user,var):
			if user.request.method in args:
				return func(user)
			else:
				if "bad_request" in user.__urls__:
					return execute_func(function=user.__urls__["bad_request"],user=user,var=var)
				return "Mauvaise methode de requete"
		return verif
	return methods_verif

def need_cookies(*args):
	
	'''
	Decorator, to force the user to have specifics cookies
	for accessing to the page
	'''
	
	def methods_verif(func):
		def verif(user,var):
			for arg in args:
				if arg not in user.cookies.keys():
					if "bad_cookie" in user.__urls__:
						return execute_func(function=user.__urls__["bad_cookie"],user=user,var=var)
					return "Mauvaise methode de requete"
			return func(user)
		return verif
	return methods_verif

def find_file(user,filename):
	
	'''
	Find file in 'files' folder.
	Used for search a requested files (ex : files/thing.css)
	'''

	try:
		for ending in default_filestypes:
			if filename.endswith(ending):
				user.accept = default_filestypes[ending]
		with open("files/"+filename,"rb") as file:
			data = file.read()
			return data
	except:
		return b""

class Request():

	def __init__(self,method,url,post):
		self.method = method
		self.url = url
		self.form = {}
		self.search_url(url)
		self.search_post(post)

	def search_url(self,url):

		'''
		Search if the request contain some GET data
		'''

		url = url.split("?")
		if len(url) > 1:
			self.set_form(url[1])

	def search_post(self,post):

		'''
		Search if the request contain some POST data
		'''

		if not post == "":
			self.set_form(post)

	def set_form(self,form):

		'''
		Edit the data of the request
		'''

		for variable in form.split("&"):
			variable = variable.split("=")
			self.form[variable[0]] = variable[1]

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

		'''
		Add a new cookie to the user
		'''

		self.cookies_to_set[cookie] = value

	def delete_cookie(self,cookie):

		'''
		Remove a cookie to the user
		'''

		self.cookies_to_delete.append(cookie)

	def get_cookies(self):

		'''
		Get the cookies of the request
		'''

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

		'''
		Search the good format for the return (text/html, text/css..)
		'''

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

	def __init__(self,page,client,infos,urls,var=None):
		self.page = page
		self.client = client
		self.infos = infos
		self.__urls__ = urls
		self.var = var

	def do(self):

		'''
		Get all infos of the request user, call the function requested,
		and send to the user the return of the function, with the cookies needed,
		or many things like that
		'''

		user = self.create_user()
		cookies = ""

		response = None

		if type(self.page) == str:
			if self.page.startswith("/files/"):
				response = find_file(user,self.page[6:])
		else:

			response = execute_func(function=self.page,user=user,var=self.var)

			for i,j in user.cookies_to_set.items():
				cookies += "Set-Cookie: "+str(i)+"="+str(j)+"\r\n"
			for i in user.cookies_to_delete:
				cookies += "Set-Cookie: "+str(i)+"=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n"



		#print("Reponse : ",response_to_client)
		if response == None:
			print("Aucun retour")
			return

		elif type(response) == type(b""):

			response_to_client = "HTTP/1.0 200 OK\r\nContent-Type: "+user.accept+"\r\n"+cookies+"\r\n"
			self.client.send(response_to_client.encode("latin-1")+response)

		else:
			response_to_client = "HTTP/1.0 200 OK\r\nContent-Type: "+user.accept+"\r\n"+cookies+"\r\n"+str(response)
			self.client.send(response_to_client.encode("latin-1"))

		self.client.close()

		return True

	def create_user(self):

		'''
		Create a user with all data needed
		'''

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

		'''
		When a request was receve, decode, print the request,
		and test if is in the valid urls
		After, try with the urls like that, with {var}
		If no one was found, return a error page
		'''

		connect_client = self.connect_client

		infos = connect_client.recv(33554432)

		if not type(infos) == "str":
			infos = infos.decode()

		if infos == "":
			return

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

		client = Process(self.url["error"],connect_client,infos,self.url,var=None)
		return client.do()

	def test_page(self,request_page,connect_client,infos,var=None):

		'''
		If the page exist, launch the process to return the good page
		'''

		if request_page in self.url:
			print("Result : Okay")
			client = Process(self.url[request_page],connect_client,infos,self.url,var=var)
			return client.do()

		elif request_page.startswith("/files/"):
			print("Result : Okay")
			client = Process(request_page,connect_client,infos,self.url,var=var)
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

		'''
		Create the socket and start the server,
		Use Recv to handle the request, without blocking.
		Detect if the socket was close, to stop the server.
		'''

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((self.host,self.port))
		self.socket.listen(10)

		while self.work:
			try:
				connect_client, nothing = self.socket.accept()
			except OSError:
				self.work = 0
				return
			Recv(self.serv.url,connect_client)

class Server():

	def __init__(self,host,port):

		'''
		Create the server, and add a default path for the favicon
		'''

		self.url = {}
		self.listen = Listening(host,port,self)

		@self.path("/favicon.ico")
		def favicon(user):
			return find_file(user,"favicon.ico")

		@self.path("error")
		def error():
			return "404 Not Found"

	def path(self,adress):

		def add_fonction(function):

			'''
			Decorator for link a fonction tu a Server path.

			If the url adress detection is with {var}, replace by '___'
			for the detection.
			'''

			if adress.format(var="___") != adress:
				self.url[adress.format(var="___")] = function

			else:
				self.url[adress] = function

			return function

		return add_fonction

	def start(self):

		'''
		Start the site, and detect if Ctrl+C is used (To stop the site).
		'''
		
		print("Starting Server")

		self.listen.start()
		self.listen.work = 1

		try:
			while self.listen.work:
				time.sleep(10)
		except KeyboardInterrupt:
			self.stop()

	def stop(self):

		'''
		Stop the site. We can call by the Ctrl+C sensor,
		or by a back-end random function.
		(If we used Thread to start a server without blocking,
		The Ctrl+C sensor doesn't work)
		'''

		if self.listen.socket:
			print("Stopping Server")
			self.listen.socket.close()
