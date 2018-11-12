#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import os
import sys
import random as r
import time
import math
from pygame import gfxdraw

# -----------
#  Clases
# -----------

class Nodo:
    nombre = ''
    color = (0,0,255)
    r = 0
    fijo = 0

    def __init__(self,nombre,color,x,y,z,r):
        self.nombre = nombre
        self.color = color
        self.pos = [x,y,z]
        self.desp = [0,0,0]
        self.r = r

class Arista:
    color = (0,0,255)
    g = 1
    def __init__(self,color,a,b,g):
        self.color = color
        self.a = a
        self.b = b
        self.g = g

# ------------
#  Constantes
# ------------

ANCHO = 800
ALTO = 800

Y = 400
X = 400
Ac = 0
Td = 1

# ------------------------------
#  Crear/Leer Grafos
# ------------------------------

def crear_manta(n):
    V = [str(i) for i in range(1,n*n + 1)]
    E = []
    for v in V:
        if (int(v)%n)!=0:
            E.append([v,str(int(v)+1)])
        if int(v)<=(n*n - n):
            E.append([v,str(int(v)+n)])
    return [V,E]

def crear_grafo(G,mX,mY):
    Gf = [[],[]]
    V = G[0]
    E = G[1]
    D = {}
    i = 0
    for v in V:
        Gf[0].append(Nodo(v,(0,0,200),r.randint(90,mX), r.randint(90,mY),r.randint(90,mY), 7))
        D[v] = i 
        i += 1

    for e in E:
        a = Gf[0][D[e[0]]]
        b = Gf[0][D[e[1]]]
        Gf[1].append(Arista((0,0,0),a,b,2))  

    return Gf

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
    print(G)
    return crear_grafo(G,ANCHO-50,ALTO-50)


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


# ------------------------------
#  Dibujar
# ------------------------------


def dibujar_nodo(screen,nodo):
    pygame.draw.circle(screen,nodo.color,(nodo.pos[0],nodo.pos[1]), nodo.r, 0)

def dibujar_nodo_calidad(screen,nodo):
    pygame.gfxdraw.filled_circle(screen,nodo.pos[0],nodo.pos[1], nodo.r, nodo.color)

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
    for nodo in nodos:
        dibujar_nodo(screen,nodo)
    for arista in aristas:
        dibujar_arista(screen,arista)
    for nodo in nodos:
        dibujar_nombre(screen,nodo)


# ------------------------------
#  Vectores
# ------------------------------

def resta(a,b):
    return [a[0]-b[0],a[1]-b[1],0]

def suma(a,b):
    return [a[0]+b[0],a[1]+b[1],0]    

def modulo(a):
    return math.sqrt(a[0]**2 + a[1]**2)

def producto(x,a):
    return [x*a[0],x*a[1],0]

def resta3d(a,b):
    return [a[0]-b[0],a[1]-b[1],a[2]-b[2]]

def suma3d(a,b):
    return [a[0]+b[0],a[1]+b[1],a[2]+b[2]]    

def modulo3d(a):
    return math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)

def producto3d(x,a):
    return [x*a[0],x*a[1],x*a[2]]

# ------------------------------
# Funcion principal 
# ------------------------------

def fa(x,k):
    return (x**2)/k
def fr(x,k):
    return -(k**2)/x

def iteracion_fruchterman(G,k,W,L,t):
    vertices = G[0]
    aristas = G[1]

    for v in vertices:
        v.desp = [0,0,0]
        for u in vertices:
            if(not (u.nombre == v.nombre)):
                dif = resta(u.pos,v.pos)
                mod = modulo(dif)
                if mod == 0:
                    mod = 1
                v.desp = suma(v.desp,producto((1/mod)*fr(mod,k),dif))

        if Ac:
            dif = resta([X,Y],v.pos)
            mod = modulo(dif)
            if mod == 0:
                mod = 1
            v.desp = suma(v.desp,producto((1/mod)*fr(mod,k)*10,dif))

        dif = resta([ANCHO/2,ALTO/2],v.pos)
        mod = modulo(dif)
        if mod == 0:
            mod = 1
        v.desp = suma(v.desp,producto((1/mod)*fa(mod,k),dif))

    for e in aristas:
        dif = resta(e.a.pos,e.b.pos)
        mod = modulo(dif)
        if mod == 0:
            mod = 1
        e.a.desp = resta(e.a.desp,producto((1/mod)*fa(mod,k),dif))
        e.b.desp = suma(e.b.desp,producto((1/mod)*fa(mod,k),dif))

    for v in vertices:
        if modulo(v.desp) > 8:
            modMax = min(modulo(v.desp),t)
            v.pos = suma(v.pos, producto(modMax/modulo(v.desp),v.desp))

            v.pos[0] = round(min(W,max(0,v.pos[0])))
            v.pos[1] = round(min(L,max(0,v.pos[1])))


    #t-= 0.0001
    return t

def iteracion_fruchterman3d(G,k,W,L,t):
    vertices = G[0]
    aristas = G[1]

    for v in vertices:
        v.desp = [0,0,0]
        for u in vertices:
            if(not (u.nombre == v.nombre)):
                dif = resta3d(u.pos,v.pos)
                mod = modulo3d(dif)
                if mod == 0:
                    mod = 1
                v.desp = suma3d(v.desp,producto3d((1/mod)*fr(mod,k),dif))

        if Ac:
            dif = resta3d([X,Y,Y],v.pos)
            mod = modulo3d(dif)
            if mod == 0:
                mod = 1
            v.desp = suma3d(v.desp,producto3d((1/mod)*fr(mod,k)*10,dif))

        dif = resta3d([ANCHO/2,ALTO/2,ALTO/2],v.pos)
        mod = modulo3d(dif)
        if mod == 0:
            mod = 1
        v.desp = suma3d(v.desp,producto3d((1/mod)*fa(mod,k),dif))

    for e in aristas:
        dif = resta3d(e.a.pos,e.b.pos)
        mod = modulo3d(dif)
        if mod == 0:
            mod = 1
        e.a.desp = resta3d(e.a.desp,producto3d((1/mod)*fa(mod,k),dif))
        e.b.desp = suma3d(e.b.desp,producto3d((1/mod)*fa(mod,k),dif))

    for v in vertices:
        if modulo3d(v.desp) > 8:
            modMax = min(modulo3d(v.desp),t)
            v.pos = suma3d(v.pos, producto3d(modMax/modulo3d(v.desp),v.desp))

            v.pos[0] = round(min(W,max(0,v.pos[0])))
            v.pos[1] = round(min(L,max(0,v.pos[1])))
            v.pos[2] = round(min(L,max(0,v.pos[2])))


    #t-= 0.0001
    return t


def main():
    pygame.init()
    
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Fruchterman")

    A = crear_grafo(crear_grafo_aleatorio(5,10),ANCHO-50,ALTO-50)
    B = crear_grafo(crear_manta(10),ANCHO-50,ALTO-50)

    G = leer_grafo("ejemplos/" + sys.argv[1])  

    area = ANCHO * ALTO
    k = 0.3*math.sqrt(area/len(G[0]))

    t = 1

    global X, Y, Ac, Td

    while True:

        screen.fill((255,255,255))
        dibujar_grafo(screen,G)
        if Td :
            t = iteracion_fruchterman3d(G,k,ANCHO,ALTO,t)
        else:
            t = iteracion_fruchterman(G,k,ANCHO,ALTO,t)
        pygame.display.flip()
        time.sleep(0.01)
        

        X,Y = pygame.mouse.get_pos()

        # Posibles entradas del teclado y mouse
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    k = max(0,k-10)
                if event.key == pygame.K_UP:
                    k += 10
                if event.key == pygame.K_LEFT:
                    Ac = (Ac+1)%2
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                if event.key == pygame.K_RIGHT:
                    Td = (Td+1)%2
            if event.type == pygame.QUIT:
                sys.exit()


if __name__ == "__main__":
    main()