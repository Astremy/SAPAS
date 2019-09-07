import socket
from threading import Thread

def redirect(url):
	return "<script>window.location.href='"+url+"'</script>"

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
		def verif(user):
			if user.request.method in args:
				return func(user)
			else:
				return "Mauvaise methode de requete"
		return verif
	return methods_verif

def find_file(filename):
	try:
		with open("files/"+filename,"r") as file:
			data = file.read()
			return data
	except:
		return ""

class Request():

	def __init__(self,method,url,post):
		self.method = method
		self.url = url.split("?")[0]
		self.form = None
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

	def __init__(self,infos,request):
		self.infos = infos
		self.request = request
		self.cookies = self.get_cookies()
		self.cookies_to_set = {}
		self.accept = self.search_accept(infos)

	def set_cookie(self,cookie,value):
		self.cookies_to_set[cookie] = value

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

class Process(Thread):

	def __init__(self,page,client,infos):
		Thread.__init__(self)
		self.page = page
		self.client = client
		self.infos = infos

	def run(self):

		user = self.create_user()
		cookies = ""

		if type(self.page) == str:
			if self.page.startswith("/file/"):
				reponse = find_file(self.page[5:])
		else:
			reponse = self.page(user)
			for i,j in user.cookies_to_set.items():
				cookies += "Set-Cookie: "+str(i)+"="+str(j)+"\r\n"

		response_to_client = "HTTP/1.0 200 OK\r\nContent-Type: "+user.accept+"\r\n"+cookies+"\r\n"+reponse
		#print("Reponse : ",response_to_client)
		self.client.send(response_to_client.encode("UTF-8"))
		self.client.close()

	def create_user(self):
		data = self.infos.split("\r\n")
		#print(data)
		protocol = data[0].split(" ")
		request = Request(protocol[0],protocol[1],data[-1])
		user = User(self.infos,request)
		return user

class Server:

	def __init__(self,host,port):
		self.host = host
		self.port = port
		self.url = {}

	def path(self,adress):

		def add_fonction(function):

			self.url[adress] = function

			return function

		return add_fonction

	def start(self):
		
		self.work = 1
		connect_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connect_main.bind((self.host,self.port))
		connect_main.listen(5)
		print("Server Start")

		while self.work:
			connect_client, nothing = connect_main.accept()
			infos = connect_client.recv(1024).decode("UTF-8")
			data = infos.split("\r\n")
			protocol = data[0].split(" ")
			#print(infos)

			try:
				request_page = protocol[1].split("?")[0]
			except:
				continue

			print("Request : "+request_page)

			if request_page.startswith("/file/"):
				print("Result : Okay")
				client = Process(request_page,connect_client,infos)
				client.start()
			elif request_page in self.url:
				print("Result : Okay")
				client = Process(self.url[request_page],connect_client,infos)
				client.start()
			else:
				print("Result : Not Found")
				connect_client.send("HTTP/1.1 404 Not Found\n\n<html><body><center><h3>Error 404</h3></center></body></html>".encode('utf-8'))

		print("Stopping Server")

	def stop(self):
		self.work = 0
