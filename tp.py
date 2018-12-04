#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame,os,sys,time,math,argparse
from pygame.locals import *
import random as r
from pygame import gfxdraw

# ------------------------------
#  Crear/Leer Grafos
# ------------------------------

# Crea un grafo tipo manta.

def crear_manta(n):
    V = [str(i) for i in range(1,n*n + 1)]
    E = []
    for v in V:
        if (int(v)%n)!=0:
            E.append([v,str(int(v)+1)])
        if int(v)<=(n*n - n):
            E.append([v,str(int(v)+n)])
    return [V,E]

# Crea un grafo aleatorio con cantN vertices y cantA aristas.

def crear_grafo_aleatorio(cantN, cantA):
    G = [[],[]]
    for i in range(cantN):
        G[0].append(str(i+1))
    for i in range(len(G[0])):
        for j in range(i+1,len(G[0])):
            a = G[0][i-1]
            b = G[0][j-1]
            G[1].append([a,b])    
    r.shuffle(G[1])
    G[1] = G[1][0:cantA]
    return G

# Lee un grafo desde un archivo y lo retorna.

def leer_grafo(nombre):
    G = [[],[]]
    fObject = open(nombre,"r")
    grafo = fObject.read()
    grafo = grafo.split()
    n = int(grafo[0])
    for i in range(1,n+1):
        G[0].append(grafo[i])
    for i in range(n+1,len(grafo),2):
        G[1].append([grafo[i],grafo[i+1]])
    return G

# Toma un grafo (compuesto por clases) y lo exporta a un archivo.

def exportar_grafo(G,nombre):
	D = {}
	fObject = open(nombre,"w+")
	r = str(len(G[0])) + "\n"
	for n,v in enumerate(G[0]):
		D[v.nombre] = str(n+1) 
		r+= str(n+1) + "\n"
	for e in G[1]:
		r+= D[e.a.nombre] + " " + D[e.b.nombre] + "\n"
	r+="\n"
	#print(r)
   	fObject.write(r)
   	fObject.close()

# ------------------------------
#  Operaciones con Vectores
# ------------------------------

def resta(a,b):
	return [a[0]-b[0],a[1]-b[1]]

def suma(a,b):
    return [a[0]+b[0],a[1]+b[1]]    

def modulo(a):
    return math.sqrt(a[0]**2 + a[1]**2)

def producto(x,a):
    return [x*a[0],x*a[1]]

# -----------
#  Clases
# -----------

class Nodo:
    nombre = ''
    color = (0,0,255)
    # Radio 
    r = 0
    # Estado: 
    # 	- 0 : Libre
    # 	- 1 : Cursor por encima
    # 	- 2 : Seleccionado.
    estado = 0

    def __init__(self,nombre,color,x,y,r):
        self.nombre = nombre
        self.color = color
        self.pos = [x,y]
        self.desp = [0,0]
        self.r = r

class Arista:
    color = (0,0,255)
    def __init__(self,color,a,b,g):
        self.color = color
        self.a = a
        self.b = b
        self.g = g

class Grafo:

	# Grafo: Lista de vertices y Lista de Aristas.
	G = [[],[]]
	# Último vertice seleccionado.
	S = None
	# Se esta manteniendo apretado el boton del mouse.
	pulsar = 1
	# Ancho y Alto de la pantalla.
	W = 800
	L = 800
	# Radio y color de los nuevos vertices.
	r = 8
	cV = (0,0,200)
	# Color de las nuevas aristas.
	cA = (0,0,0)
	# Diccionario utilizado para acceder a la posicion de los
	# vértices más facilmente.
	D = {}
	# Cantidad de vertices
	i = 0
	# Máximo numero utilizado para nombrar vértices.
	t = 0

	def __init__(self,W,L,r,cV,cA,verbose):
		self.W = W
		self.L = L
		self.r = r
		self.cV = cV
		self.cA = cA
		self.verbose = verbose

	def randomx(self):
		return r.randint(self.r,self.W - self.r)

	def randomy(self):
		return r.randint(self.r,self.L - self.r)

	def fa(self,x,k):
		return (x**2)/k

	def fr(self,x,k):
		return -(k**2)/x

	def agregar_vertice(self,x,y,id = None):
		if(id == None):
			id = str(self.t+1)
		self.G[0].append(Nodo(id,self.cV,x,y,self.r))
		self.D[id] = self.i
		self.i += 1
		self.t += 1
		if self.verbose :
			print("\n-> Nuevo nodo ("+ id +") agregado.")

	def agregar_arista(self,a,b):
		self.G[1].append(Arista(self.cA,a,b,2))  

	def cargar(self,G):
		self.G = [[],[]]
		self.i = 0
		self.t = 0
		self.pulsar = 1
		self.D = {}
		self.S = None

		aux = self.verbose
		self.verbose = False
		V,E = G
		for v in V:
			self.agregar_vertice(self.randomx(),self.randomy(),v)
		for e in E:
			self.agregar_arista(self.G[0][self.D[e[0]]],self.G[0][self.D[e[1]]])
		self.verbose = aux

	def actualizar_fuerza_repulsion(self,k):
		vertices = self.G[0]
		for v in vertices:
			v.desp = [0,0]

		c1 = 0
		while c1 < self.i:
			c2 = c1 + 1
			while (c2 < self.i) and not(c1==c2):
				dif = resta(vertices[c2].pos,vertices[c1].pos)
				mod = modulo(dif)
				if mod == 0:
					mod = 1
				vertices[c1].desp = suma(vertices[c1].desp,producto((1/mod)*self.fr(mod,k),dif))
				vertices[c2].desp = suma(vertices[c2].desp,producto((-1/mod)*self.fr(mod,k),dif))
				c2+=1
			c1+=1

	def actualizar_fuerza_atraccion(self,k):
		aristas = self.G[1]
		for e in aristas:
			dif = resta(e.a.pos,e.b.pos)
			mod = modulo(dif)
			if mod == 0:
				mod = 1
			e.a.desp = resta(e.a.desp,producto((1/mod)*(self.fa(mod,k)),dif))
			e.b.desp = suma(e.b.desp,producto((1/mod)*(self.fa(mod,k)),dif))
		            
	def actualizar_fuerza_gravedad(self,k,gravedad_constante):
		vertices = self.G[0]
		for v in vertices:
			dif = resta([self.W/2,self.L/2],v.pos)
			mod = modulo(dif)
			if mod == 0:
				mod = 1
			if gravedad_constante :
				v.desp = suma(v.desp,producto((1/mod)*20,dif))
			else :
				v.desp = suma(v.desp,producto((1/mod)*self.fa(mod,k),dif))

	def actualizar_posiciones(self,k,x,y,gravedad_constante):
		vertices = self.G[0]
		self.actualizar_fuerza_repulsion(k)
		self.actualizar_fuerza_gravedad(k,gravedad_constante)
		self.actualizar_fuerza_atraccion(k)
		for v in vertices:
			if modulo(v.desp) > 8:
				modMax = min(modulo(v.desp),1)
				v.pos = suma(v.pos, producto(modMax/modulo(v.desp),v.desp))

				v.pos[0] = int(round(min(self.W,max(0,v.pos[0]))))
				v.pos[1] = int(round(min(self.L,max(0,v.pos[1]))))

		if self.pulsar and not(self.S==None):
			self.S.pos[0] = x
			self.S.pos[1] = y


	def p(self):
		self.pulsar = 0

	# Maneja la interacción del mouse y los estados de los vértices.

	def mouse(self,x,y,flag):
		c = [(0,0,255),(0,255,0),(255,0,0)]

		f = True

		for v in self.G[0]:
			if(((x<=v.pos[0]+v.r) and (x>=v.pos[0]-v.r)) and ((y<=v.pos[1]+v.r) and (y>=v.pos[1]-v.r))):
				f = False
				if flag and not (self.pulsar):
					if(self.S==None):
						self.S = v
						v.estado = 2
					else: 
						if(self.S.nombre == v.nombre):
							v.estado = 1
						else :
							self.agregar_arista(self.S,v)
							v.estado = 1
							self.S.estado = 1
						self.S = None
				else :
					if v.estado == 0:
						v.estado = 1
			else:
				if v.estado == 1:
					v.estado = 0

			v.color = c[v.estado]

		if flag and f and not self.S == None:
			self.S.estado = 0
			self.S.color = c[self.S.estado]
			self.S = None

		if flag:
			self.pulsar = 1


	def eliminar(self,x,y):
		aristas = []
		c = 0
		while c < self.i:
			v = self.G[0][c]
			if(((x<=v.pos[0]+v.r) and (x>=v.pos[0]-v.r)) and ((y<=v.pos[1]+v.r) and (y>=v.pos[1]-v.r))):
				if (not self.S == None) and v.nombre == self.S.nombre:
					self.S = None
				for e in self.G[1]:
					if not(e.a.nombre == v.nombre) and not(e.b.nombre == v.nombre):
						aristas.append(e)
				self.G[1] = aristas
				self.G[0] = self.G[0][:c] + self.G[0][c+1:]
				self.i -= 1
				if self.verbose:
						print("\n-> Nodo eliminado("+v.nombre+").")
				break
			c+=1


# ---------------------------------------
#  Funciones para dibujar en pantalla.
# ---------------------------------------

def dibujar_nodo(screen,nodo):
    pygame.draw.circle(screen,nodo.color,(nodo.pos[0],nodo.pos[1]), nodo.r+4, 0)
    pygame.draw.circle(screen,(255,255,255),(nodo.pos[0],nodo.pos[1]), nodo.r, 0)

def dibujar_arista(screen,arista):
    pygame.gfxdraw.line(screen,arista.a.pos[0],arista.a.pos[1],arista.b.pos[0],arista.b.pos[1],arista.color)

def dibujar_nombre(screen,nodo):
    font = pygame.font.SysFont('Comic Sans MS', 25)
    text = nodo.nombre
    text = font.render(text, True, (0,0,255))
    screen.blit(text, (nodo.pos[0]+nodo.r+3, nodo.pos[1]+nodo.r+3))

def dibujar_grafo(screen,G):
    nodos = G[0]
    aristas = G[1]
    for arista in aristas:
        dibujar_arista(screen,arista)
    for nodo in nodos:
        dibujar_nodo(screen,nodo)
    for nodo in nodos:
        dibujar_nombre(screen,nodo)


# ------------------------------
# Funcion principal.
# ------------------------------

def argumentos():
	parser = argparse.ArgumentParser()

	# Verbosidad, opcional, False por defecto.

	parser.add_argument('-v', '--verbose', 
                        action='store_true', 
                        help='Muestra mas informacion.',
                        default=False)

	# Archivo de donde se importa el grafo.

	parser.add_argument('-i','--input',
						help = 'Ruta del archivo con el grafo a importar.',
						default = 'EntradaDefecto.txt')

	# Archivo al que se exporta el grafo creado.

	parser.add_argument('-o','--output',
						help = 'Ruta del archivo para exportar el grafo creado.',
						default = 'SalidaDefecto.txt')

	return parser.parse_args()


def nextFile(filename,directory):
    fileList = os.listdir(directory)
    nextIndex = fileList.index(filename) + 1
    if nextIndex == 0 or nextIndex == len(fileList):
        return fileList[0]
    return fileList[nextIndex]

def main():

	args = argumentos()

	verbose = args.verbose

	directorio_actual = os.path.dirname(os.path.realpath(__file__))

	directorio_grafos = directorio_actual + "/Grafos/"

	archivo_input = directorio_grafos + args.input

	pygame.init()

	if verbose:
		print("\nINFORMACIÓN DE LA EJECUCIÓN:")

	ANCHO = 800
	ALTO = 800

	screen = pygame.display.set_mode((ANCHO, ALTO))
	pygame.display.set_caption("Fruchterman")

	G = Grafo(ANCHO,ALTO,7,(0,0,255),(0,0,0),verbose)

	if os.path.isfile(archivo_input):
		C = leer_grafo(archivo_input)
		if verbose:
			print("\n-> Se cargo el archivo " + archivo_input)
	else :
		C = leer_grafo(directorio_grafos + "EntradaDefecto.txt")
		if verbose:
			print("\n-> No existe archivo " + archivo_input)
			print("\n-> Se cargo en su lugar " + directorio_grafos + "EntradaDefecto.txt")

	G.cargar(C)

	area = ANCHO * ALTO
	k = 0.3*math.sqrt(area/len(G.G[0]))
	gravedad_constante = False

	pressed_up = False
	pressed_down = False

	while True:

		X,Y = pygame.mouse.get_pos()

		screen.fill((255,255,255))
		dibujar_grafo(screen,G.G)
		G.actualizar_posiciones(k,X,Y,gravedad_constante)
		pygame.display.flip()
		time.sleep(0.01)

		
		l,m,r = pygame.mouse.get_pressed()
		
		if r:
			G.eliminar(X,Y) 

		if not l:
			G.p()

		G.mouse(X,Y,l)

		if m:
			G.agregar_vertice(X,Y)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit() 

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					exportar_grafo(G.G,directorio_grafos + args.output) 
					if verbose:
						print("\n-> Se exportó el grafo al archivo " + directorio_grafos + args.output)
						print("\n-> Se cerrará el programa.")
					sys.exit()
				if event.key == pygame.K_UP:    
					pressed_up = True
				if event.key == pygame.K_DOWN:    
					pressed_down = True

				if event.key == pygame.K_RIGHT:
					siguiente = nextFile(args.input,directorio_grafos)
					G.cargar(leer_grafo(directorio_grafos + siguiente))
					args.input = siguiente
					if verbose:
						print("\n-> Se cargo el archivo " + args.input)
					k = 0.3*math.sqrt(area/len(G.G[0]))

				if event.key == pygame.K_g:
					gravedad_constante = not gravedad_constante
					if verbose:
						if gravedad_constante:
							print("\n-> Gravedad Constante.")
						else: 
							print("\n-> Gravedad relativa a la posicion.")

			elif event.type == pygame.KEYUP:            
				if event.key == pygame.K_UP:        
					pressed_up = False
				if event.key == pygame.K_DOWN:        
					pressed_down = False

		if pressed_up :
			k+=1
			if verbose:
				print("\n-> Aumentando constante de repulsión en una unidad k = " + str(k) + ".")

		if pressed_down :
			if verbose:
				if k == 1:
					print("\n-> Mínimo k alcanzado.")
				else :
					print("\n-> Disminuyendo constante de repulsión en una unidad k = " + str(k) + ".")
			k = max(1,k-1)

if __name__ == "__main__":
    main()