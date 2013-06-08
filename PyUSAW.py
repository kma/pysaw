#-*-coding:utf8-*-
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
import tkFileDialog
import tkFont
from time import sleep
from sys import argv

import Image, ImageDraw
from copy import deepcopy


class nfSAW:
    def __init__(self, taille = 600):
        self.root = Tk() 
        
        # Dimensions de la fenêtre
        
        #self.taille = taille
        #self.tailleInitiale = taille
        
        self.pileChemins =[]
        self.antipileChemins =[]
        self.pointZero = (0,0)
 
        # Les menus
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.nouveauSAW)
        filemenu.add_command(label="Open", command=self.openSAW)
        filemenu.add_separator()
        filemenu.add_command(label="Save", command=self.saveSAW)
        filemenu.add_command(label="Export as points list", command=self.exportPointSAW)
        filemenu.add_command(label="Export as image", command=self.exportSAW)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="New origin", command=self.nouvelleOrigine)
        editmenu.add_command(label="Rehersal", command=self.inverse)        
        editmenu.add_command(label="Delete between two points", command=self.supprimeEntreDeux)        
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Describe key", command=self.describeWindow)
        helpmenu.add_command(label="About...", command=self.aboutWindow)
        menubar.add_cascade(label="Help", menu=helpmenu)


        self.root.config(menu=menubar)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (sw, sh))
        self.root.resizable(FALSE,FALSE)
        
        self.taille = self.root.winfo_screenheight()-200
        self.origine = (self.taille/2, self.taille/2)


        # Taille des pas
        self.step = self.taille/10
        
        # Rayon des sommets
        self.rayon = self.step/10

        # Compteur sachant le nombre de clics dans la suppression
        self.nbClicSuppr = 0

        # Le canevas où tracer les SAW
        self.c = Canvas(self.root, height=self.taille, width=self.taille, background='#ffffff') 


        self.chemin = []
        if len(argv)>1:
            fichier = open(argv[-1]).read()
            if '(' in fichier:
                (x,y), self.chemin = eval(fichier)
                self.pointZero = (x,-y)
            else:
                self.chemin = fichier.replace('\n','')
            self.chemin = [int(k) for k in self.chemin]

        self.c.grid(row=0,rowspan=2,column=0) 

        self.frame2 = LabelFrame(self.root, text="Configuration", height=600, border=4, relief=RIDGE)
        self.frame2.grid(row=0, column=1,sticky=W+E+N+S)

        self.tailleChemin = StringVar()
        self.tailleChemin.set("Length: "+str(len(self.chemin)))
        texteLongueur = Label(self.frame2, textvariable=self.tailleChemin)
        texteLongueur.grid(row = 0, column = 0, columnspan=2, sticky=NW)

        self.nbIntersections = StringVar()
        self.nbIntersections.set("Intersections: "+str(len(self.chemin)-len(set(self.decode(self.chemin)))+1))
        texteIntersections = Label(self.frame2, textvariable=self.nbIntersections)
        texteIntersections.grid(row = 1, column = 0, columnspan=2, sticky=NW)

        self.nbNonDepliables = StringVar()
        self.nbNonDepliables.set("Unfoldable: 1")
        texteNonDepliables = Label(self.frame2, textvariable=self.nbNonDepliables)
        texteNonDepliables.grid(row = 2, column = 0, columnspan=2, sticky=NW)


        self.position = StringVar()
        self.position.set("x = 0, y = 0")
        textePosition = Label(self.frame2, textvariable=self.position)
        textePosition.grid(row = 3, column = 0, columnspan=2, sticky=NW)

        self.etendueX = StringVar()
        self.etendueX.set("Etendue en X :")
        texteetendueX = Label(self.frame2, textvariable=self.etendueX)
        texteetendueX.grid(row = 4, column = 0, columnspan=2, sticky=NW)        

        self.etendueY = StringVar()
        self.etendueY.set("Etendue en Y :")
        texteetendueY = Label(self.frame2, textvariable=self.etendueY)
        texteetendueY.grid(row = 5, column = 0, columnspan=2, sticky=NW)  

        self.avecSommet = IntVar()
        self.avecSommet.set(1)
        checkbouton1 = Checkbutton(self.frame2, text="Vertices", variable=self.avecSommet, command = self.activeSommets)
        checkbouton1.grid(row = 6, column = 0, columnspan=2, sticky=NW)

        self.calculDepliage = IntVar()
        self.calculDepliage.set(1)
        self.checkbouton2 = Checkbutton(self.frame2, text="Unfoldable", variable=self.calculDepliage, command = self.dessine)
        self.checkbouton2.grid(row = 7, column = 0, columnspan=2, sticky=NW, padx = 25)

        self.showIntersection = IntVar()
        self.showIntersection.set(1)
        checkbouton3 = Checkbutton(self.frame2, text="Show future intersections", variable=self.showIntersection)
        checkbouton3.grid(row = 8, column = 0, columnspan=2, sticky=NW)

        self.adapte = IntVar()
        self.adapte.set(0)
        checkbouton4 = Checkbutton(self.frame2, text="Figure adaptation", variable=self.adapte, command = self.dessine)
        checkbouton4.grid(row = 9, column = 0, columnspan=2, sticky=NW)
        if len(argv)>1:
            self.adapte.set(1)
        else:
            self.adapte.set(0)
            

        self.axes = IntVar()
        self.axes.set(0)
        checkbouton5 = Checkbutton(self.frame2, text="Show axes", variable=self.axes, command = self.dessine)
        checkbouton5.grid(row = 10, column = 0, columnspan=2, sticky=NW)


        self.intersectionAffiche = StringVar()
        self.texteChemin = Label(self.frame2, textvariable=self.intersectionAffiche, justify=LEFT)
        self.texteChemin.grid(row = 11, column = 0, columnspan=4, sticky=NW, padx = 5)

        self.frame3 = LabelFrame(self.root, border=4, text="Backtracking",relief=RIDGE)
        self.frame3.grid(row=1, column=1,sticky=NE)
        

        texteSpin = Label(self.frame3, text="Deepeness")
        texteSpin.grid(row = 0, column = 0, sticky=NW)


        self.spinbox = Spinbox(self.frame3, from_=1, to=50)
        self.spinbox.grid(row = 0, column = 1, sticky=NW)


        button = Button(self.frame3, text="Launch", command=self.backtracking)
        button.grid(row = 1, column = 1, sticky=NW)


        texteChemin = Label(self.root, text="Relative encoding of the walk:", justify=LEFT)
        texteChemin.grid(row = 2, column = 0, columnspan=4, sticky=W)
        police=tkFont.Font(self.root, size=10, family='Bitstream Vera Sans')
        texteChemin.config(font=police)        


        self.cheminAffiche = StringVar()
        #self.texteChemin = Entry(self.root, textvariable=self.cheminAffiche, width = 120, justify=LEFT)
        self.texteChemin = Label(self.root, textvariable=self.cheminAffiche, justify=LEFT)
        self.texteChemin.grid(row = 3, column = 0, columnspan=4, sticky=W)
        self.texteChemin.config(font=police)        


        self.dessine()
        
        self.root.title('PySAW: folded self-avoiding walks')
        self.root.bind_all('<Control-s>',self.sauveAuto)
        self.root.bind_all('<Control-z>',self.annule)
        self.root.bind_all('<Control-q>',quit)
        self.root.bind_all('<Control-Z>',self.desannule)        
        self.root.bind_all('<BackSpace>',self.retire)

        self.modeRetrace = False
        self.okPourRetracer = False
        self.listeARetracer = []
        self.root.bind('<B1-Motion>',self.retrace)
        self.root.bind('<ButtonRelease-1>',self.detrace)

        self.c.bind("<Button-3>", self.pivot_horaire) 
        self.c.bind("<Motion>", self.getPosition)


        self.root.bind_all('<Key>', self.deplacement)

        self.root.geometry("%dx%d%+d%+d" % (965, 800, 10, 10))
        #self.root.bind("<Configure>", self.resize)                    
        self.root.mainloop()


        
    def retrace(self, event):
        x0,y0 = self.coordonnees((event.x,event.y))
        if (x0,y0) in [self.coordonnees(u) for u in self.decode(self.chemin)] and not self.okPourRetracer:
            self.okPourRetracer = True
            self.ancienC = deepcopy(self.chemin)
            self.nouveauC = []
            self.listeARetracer = [(x0,y0)]
        if self.okPourRetracer:
            if self.listeARetracer[-1] != (x0,y0):
                self.listeARetracer.append((x0,y0))
                X = (self.origine[0]+self.step*x0,self.origine[1]-y0*self.step)
                Y = (self.origine[0]+self.step*self.listeARetracer[-2][0],self.origine[1]-self.step*self.listeARetracer[-2][1])
                self.c.create_line(X[0],X[1],Y[0],Y[1],fill='#777777')
                if (x0,y0) == (self.listeARetracer[-2][0]+1,self.listeARetracer[-2][1]):
                    self.nouveauC.append(0)
                elif (x0,y0) == (self.listeARetracer[-2][0],self.listeARetracer[-2][1]+1):
                    self.nouveauC.append(3)
                elif (x0,y0) == (self.listeARetracer[-2][0]-1,self.listeARetracer[-2][1]):
                    self.nouveauC.append(2)
                elif (x0,y0) == (self.listeARetracer[-2][0],self.listeARetracer[-2][1]-1):
                    self.nouveauC.append(1)

                    


    def detrace(self, event):
        if len(self.listeARetracer)<=1:
            self.pivot_antihoraire(event)
        elif len(self.listeARetracer) == len(set(self.listeARetracer)) and self.listeARetracer[-1] in [self.coordonnees(u) for u in self.decode(self.ancienC)] and len(set([k for k in self.listeARetracer[1:-2]]).intersection(set(self.decode(self.chemin))))==0:
            self.pileChemins.append(self.chemin)
            debut = [self.coordonnees(u) for u in self.decode(self.chemin)].index(self.listeARetracer[0])
            fin = [self.coordonnees(u) for u in self.decode(self.chemin)].index(self.listeARetracer[-1])
            if debut < fin:
                self.chemin = self.chemin[:debut]+self.nouveauC+self.chemin[fin:]
            else:
                self.nouveauC.reverse()                
                nouveauC = []
                for k in self.nouveauC:
                    if k == 0:
                        nouveauC.append(2)
                    elif k==2 :
                        nouveauC.append(0)
                    elif k==1:
                        nouveauC.append(3)
                    else:
                        nouveauC.append(1)
                self.chemin = self.chemin[:fin]+nouveauC+self.chemin[debut:]
            
        self.listeARetracer = []
        self.okPourRetracer = False
        self.dessine()
        

        
    def resize(self,event):
        self.taille = min(self.root.winfo_width()-self.frame2.winfo_width()-2,self.root.winfo_height()-self.texteChemin.winfo_height()-2)
        self.dessine()
        
    def nouveauSAW(self):
        self.pileChemins =[]
        self.antipileChemins =[]        
        self.step = self.taille/10
        self.rayon = self.step/10
        self.chemin = []
        self.origine = (self.taille/2, self.taille/2)
        self.dessine()


    def openSAW(self):
        self.pileChemins =[]
        self.antipileChemins =[]
        
        filename = askopenfilename(filetypes=[("Fichiers texte","*.txt"),("Tous les fichiers", '*')])
        chemin = open(filename).read().replace('\n','')

        if '(' in chemin:
            self.pointZero, self.chemin = eval(chemin)
            self.pointZero = (self.pointZero[0],-self.pointZero[1])

        else:
            self.chemin = chemin.replace('\n','')

        self.chemin = [int(k) for k in list(self.chemin)]
        self.dessine()

    def saveSAW(self):
        filename = asksaveasfilename(filetypes=[("Fichiers texte","*.txt"),("Tous les fichiers", '*')], initialfile = str(len(self.chemin))+'.txt')
        dd = open(filename,'w')
        dd.write(''.join([str(k) for k in self.chemin]))
        dd.close()

    def exportPointSAW(self):
        filename = asksaveasfilename(filetypes=[("Fichiers texte","*.txt"),("Tous les fichiers", '*')], initialfile = str(len(self.chemin))+'_points.txt')
        dd = open(filename,'w')
        dd.write(', '.join([str(self.coordonnees(k)) for k in self.decode(self.chemin)]))
        dd.close()

    def sauveAuto(self,event):
        filename = str(len(self.chemin))+'.txt'
        dd = open(filename,'w')
        dd.write(''.join([str(k) for k in self.chemin]))
        dd.close()

    def exportSAW(self):
        filename = asksaveasfilename(filetypes=[("Png","*.png"),("Jpg","*.jpg"),("Texte","*.txt")], initialfile = str(len(self.chemin))+'.png')
        if filename.endswith('.txt'):
            dd = open(filename,'w')
            dd.write(''.join([str(k) for k in self.chemin]))
            dd.close()
        elif filename.endswith('.png') or filename.endswith('.jpg'):
            self.plot_proteine(nom=filename)





    def inverse(self):
        self.chemin.reverse()
        self.dessine()
        

    def backtracking(self):
        self.backtrack(self.chemin, len(self.chemin)+eval(self.spinbox.get()))



    def alonge(self,P,c):
        if c == 0:
            return (P[0]+self.step,P[1])
        elif c == 1:
            return (P[0],P[1]+self.step)
        elif c == 2:
            return (P[0]-self.step,P[1])
        else :
            return (P[0],P[1]-self.step)




    def backtrack(self,w,n):
        if len(w) >= n:
            self.chemin = w
            self.dessine()
            self.c.update()
            return
        for a in range(4):
            u = self.alonge(self.decode(w)[-1],a)
            if u not in set(self.decode(w)):
                w1 = w+[a]
                self.dessine(w1)
                self.c.update()
                if eval(self.nbNonDepliables.get().split(': ')[1]) == len(w1) + 1 :
                    print "Bingo !",len(w1)+1,w1
                    self.backtrack(w1,n)
                else:
                    self.backtrack(w1,n)
        

        
    def nouvelleOrigine(self):
        self.root.configure(cursor='cross')
        self.c.bind("<Button-1>", self.changementOrigine) 

    def changementOrigine(self, event):
        x0,y0 = event.x, event.y
        self.pointZero = (self.pointZero[0]-self.coordonnees((x0,y0))[0],self.pointZero[1]+self.coordonnees((x0,y0))[1])
        self.origine = (self.origine[0]+self.step*self.coordonnees((x0,y0))[0],self.origine[1]-self.step*self.coordonnees((x0,y0))[1])
        self.c.bind("<Button-1>", self.pivot_antihoraire) 
        self.root.configure(cursor="")        
        self.dessine()


    def supprimeEntreDeux(self):
        self.c.bind("<Button-3>", self.laSuppression)
        
    
    def laSuppression(self,event):
        self.nbClicSuppr += 1
        x0,y0 = event.x, event.y
        if self.nbClicSuppr ==1:
            self.debutSuppr = [self.coordonnees(u) for u in self.decode(self.chemin)].index(self.coordonnees((x0,y0)))
        elif self.nbClicSuppr == 2:
            fin = [self.coordonnees(u) for u in self.decode(self.chemin)].index(self.coordonnees((x0,y0)))
            if self.debutSuppr > fin:
                debut = fin
                fin = self.debutSuppr
            else:
                debut = self.debutSuppr
            self.pileChemins.append(deepcopy(self.chemin))
            self.chemin = self.chemin[:debut]+self.chemin[fin:]
            self.c.bind("<Button-3>", self.pivot_horaire) 
            self.nbClicSuppr = 0
            self.dessine()

                
    def plot_proteine(self, nom = None):
        L = self.decode(self.chemin)
        im=Image.new('RGB',(self.taille,self.taille),(255,255,255))
        draw = ImageDraw.Draw(im)
        for k in L:
            draw.ellipse((k[0]-self.rayon,k[1]-self.rayon,k[0]+self.rayon,k[1]+self.rayon),fill = (0,0,255))
        draw.line(L, fill=(0,0,255), width=2)
        draw.ellipse((L[0][0]-self.rayon,L[0][1]-self.rayon,L[0][0]+self.rayon,L[0][1]+self.rayon),fill = (255,0,0))
        draw.ellipse((L[-1][0]-self.rayon,L[-1][1]-self.rayon,L[-1][0]+self.rayon,L[-1][1]+self.rayon),fill = (0,255,0))        
        im.save(nom)           




    def getPosition(self,event):
        x0, y0 = event.x, event.y
        x, y = self.coordonnees((x0,y0))
        position = (x*self.step+self.origine[0],-y*self.step+self.origine[1])
        if position in self.decode(self.chemin):
            pos = self.decode(self.chemin).index(position)
            self.position.set("x = "+str(x)+", y = "+str(y)+" ("+str(pos)+")")
            if self.showIntersection.get():
                texte = "Future Intersections :\n"
                origine = self.decode(self.chemin)
                depliage1 = self.decode(self.chemin[:pos]+[(u+1)%4 for u in self.chemin[pos:]])
                listePlus = []
                depliage2 = self.decode(self.chemin[:pos]+[(u-1)%4 for u in self.chemin[pos:]])
                listeMoins = []
                for cpt,k in enumerate(depliage1[pos:]):
                    if depliage1.count(k)>1:
                        listePlus.append((origine[pos+cpt],k))
                for cpt, k in enumerate(depliage2[pos:]):
                    if depliage2.count(k)>1:
                        listeMoins.append((origine[pos+cpt],k))
                texte += "-90° : "+", ".join([str(self.coordonnees(k[0], adaptee = True))+'->'+str(self.coordonnees(k[1], adaptee = True)) for k in listePlus])+'\n'
                texte += "+90° : "+", ".join([str(self.coordonnees(k[0], adaptee = True))+'->'+str(self.coordonnees(k[1], adaptee = True)) for k in listeMoins])+'\n'
                self.intersectionAffiche.set(texte)
            else:
                self.intersectionAffiche.set('')
            if self.nbClicSuppr == 1:
                if self.debutSuppr<=pos:
                    self.dessine(enRouge=range(self.debutSuppr,pos+1))
                else:
                    self.dessine(enRouge=range(pos,self.debutSuppr+1))
        else:
            self.position.set("x = "+str(x)+", y = "+str(y))
            self.intersectionAffiche.set('')
            
            


    def coordonnees(self, point, adaptee = False):
        if not adaptee:
            return ((point[0]-self.origine[0]-self.step/2)/self.step+1, -(point[1]-self.origine[1]-self.step/2)/self.step)
        else:
            return ((point[0]-self.origine[0]-self.step/2)/self.step+1-self.pointZero[0], -(point[1]-self.origine[1]-self.step/2)/self.step-self.pointZero[1])

        

    def dessine(self, chemin = '',enRouge=[]):
        if chemin == '':
            chemin = self.chemin
            
        self.c.delete("all")
        if len(chemin)>1:
            self.c.config(width=self.taille, height=self.taille)

        self.nbIntersections.set("Intersections : "+str(len(chemin)-len(set(self.decode(chemin)))+1))
        self.tailleChemin.set("Length: "+str(len(chemin)))
        texte = ''
        for valeur in chemin:
            if len(texte.replace('\n',''))%80 == 0 and len(texte)>0:
                texte += '\n'
            texte += str(valeur)
        self.cheminAffiche.set(texte)

        listePoints = self.decode(chemin)
        etendueXplus = max([k[0] for k in listePoints])
        etendueXmoins = min([k[0] for k in listePoints])
        etendueYplus = max([k[1] for k in listePoints])
        etendueYmoins = min([k[1] for k in listePoints])
        self.etendueX.set("Width: "+str((etendueXplus-etendueXmoins)/self.step))
        self.etendueY.set("Height: "+str((etendueYplus-etendueYmoins)/self.step))

        centre = ((etendueXmoins+etendueXplus)/2, (etendueYmoins+etendueYplus)/2)

        #if etendueXmoins < 0 or etendueXplus > self.taille or etendueYmoins <0 or etendueYplus > self.taille:
        if self.adapte.get()==1 and len(chemin)>5:
            etendueXplus += self.step
            etendueXmoins -= self.step
            etendueYplus += self.step
            etendueYmoins -= self.step
            rapport = float(self.taille)/max(abs(etendueXplus-etendueXmoins),abs(etendueYplus-etendueYmoins))
            self.step = int(self.taille/(max(abs(etendueXplus-etendueXmoins),abs(etendueYplus-etendueYmoins))/self.step))
            self.rayon = self.step/10            
            self.origine = (int(rapport*(self.origine[0]-centre[0]))+self.taille/2, int(rapport*(self.origine[1]-centre[1]))+self.taille/2)
            listePoints = self.decode(chemin)


        self.nonDepliables = 1
        if len(chemin)>0:
            self.nonDepliables = 2

        for k in range(len(listePoints)-1):
            x1,y1 = listePoints[k]
            x2,y2 = listePoints[k+1]
            self.c.create_line(x1,y1,x2,y2,fill='#0000ff')
            if k in enRouge:
                couleur = '#777700'
            elif listePoints.count(listePoints[k])==1:
                couleur = '#0000ff'
            else:
                couleur = '#ff0000'
            if self.avecSommet.get() and k!=0:
                depliage1 = chemin[:k]+[(u+1)%4 for u in chemin[k:]]
                depliage2 = chemin[:k]+[(u-1)%4 for u in chemin[k:]]
                if self.calculDepliage.get():
                    if len(set(self.decode(depliage1))) == len(self.decode(depliage1)) or len(set(self.decode(depliage2))) == len(self.decode(depliage2)):
                        self.c.create_oval(x1-self.rayon,y1-self.rayon,x1+self.rayon,y1+self.rayon,fill=couleur)
                    else:
                        self.c.create_rectangle(x1-self.rayon,y1-self.rayon,x1+self.rayon,y1+self.rayon,fill=couleur)
                        self.nonDepliables += 1
                else:
                    self.c.create_oval(x1-self.rayon,y1-self.rayon,x1+self.rayon,y1+self.rayon,fill=couleur)

        if self.calculDepliage.get():
            self.nbNonDepliables.set("Unfoldables: "+str(self.nonDepliables))
            
        x1,y1 = listePoints[-1]
        if listePoints.count(listePoints[-1])==1:
            couleur = '#00ff00'
        else:
            couleur = '#ffff00'        
        if self.avecSommet.get():
            self.c.create_rectangle(x1-self.rayon,y1-self.rayon,x1+self.rayon,y1+self.rayon,fill=couleur)


        x1,y1 = listePoints[0]
        if listePoints.count(listePoints[-1])==1:
            couleur = '#000000'
        else:
            couleur = '#00ffff'        
        if self.avecSommet.get():
            self.c.create_rectangle(x1-self.rayon,y1-self.rayon,x1+self.rayon,y1+self.rayon,fill=couleur)

        # Axes are drawn
        if self.axes.get():
            self.c.create_line((0,self.origine[1]),(self.taille,self.origine[1]))
            self.c.create_line((self.origine[0],0),(self.origine[0],self.taille))


    def encode(self, points):
        '''
        Transforme une liste de points en son encode NSEW.
        '''
        L=[]
        for k in range(1,len(points)):
            if points[k-1][0]==points[k][0]:
                if points[k-1][1] < points[k][1]:
                    L.append(3)
                else:
                    L.append(1)
            else:
                if points[k-1][0] < points[k][0]:
                    L.append(0)
                else:
                    L.append(2)
        return L


    def decode(self, C):
        L = [(self.origine[0]+self.pointZero[0]*self.step,self.origine[1]+self.pointZero[1]*self.step)]
        for c in C:
            P = L[-1]
            if c == 0:
                L.append((P[0]+self.step,P[1]))
            elif c == 1:
                L.append((P[0],(P[1]+self.step)))
            elif c == 2:
                L.append(((P[0]-self.step),P[1]))
            elif c == 3:
                L.append((P[0],(P[1]-self.step)))
        return L


    def annule(self,event):
        if len(self.pileChemins)>0:
            self.antipileChemins.append(deepcopy(self.chemin))
            self.chemin = self.pileChemins[-1]
            del self.pileChemins[-1]
            self.dessine()

    def desannule(self,event):
        if len(self.antipileChemins) > 0:
            self.pileChemins.append(deepcopy(self.antipileChemins[-1]))
            del self.antipileChemins[-1]
            self.chemin = deepcopy(self.pileChemins[-1])
            self.dessine()
        

    def deplacement(self, event):
        if event.keysym == 'Right':
            self.pileChemins.append(deepcopy(self.chemin))
            self.chemin.append(0)
            self.dessine()
        elif event.keysym == 'Down':
            self.pileChemins.append(deepcopy(self.chemin))
            self.chemin.append(1)
            self.dessine()
        elif event.keysym == 'Left':
            self.pileChemins.append(deepcopy(self.chemin))
            self.chemin.append(2)
            self.dessine()
        elif event.keysym == 'Up':
            self.pileChemins.append(deepcopy(self.chemin))
            self.chemin.append(3)
            self.dessine()
        elif event.keysym == "Delete":
            self.pileChemins.append(deepcopy(self.chemin))
            self.chemin = self.chemin[:-1]
            self.dessine()              
        else:
            pass
            #print event.keysym, event.keycode


    def retire(self, event):
        self.pileChemins.append(deepcopy(self.chemin))
        if self.chemin[0] == 0:
            self.pointZero = (self.pointZero[0]+1,self.pointZero[1])
        elif self.chemin[0] == 1:
            self.pointZero = (self.pointZero[0],self.pointZero[1]+1)
        elif self.chemin[0] == 2:
            self.pointZero = (self.pointZero[0]-1,self.pointZero[1])
        else:
            self.pointZero = (self.pointZero[0],self.pointZero[1]-1)
            
        self.chemin = self.chemin[1:]
        self.dessine()  

    def pivot_horaire(self, event):
        x = (event.x-self.origine[0]-self.step/2)/self.step+1
        y = -(event.y-self.origine[1]-self.step/2)/self.step+1

        if (x*self.step+self.origine[0],-y*self.step+self.origine[1]+self.step) in self.decode(self.chemin):
            point = self.decode(self.chemin).index((x*self.step+self.origine[0],-y*self.step+self.origine[1]+self.step))
            self.pileChemins.append(deepcopy(self.chemin))
            self.chemin = self.chemin[:point]+[(k+1)%4 for k in self.chemin[point:]]
            self.dessine()


    def pivot_antihoraire(self, event):
        x = (event.x-self.origine[0]-self.step/2)/self.step+1
        y = -(event.y-self.origine[1]-self.step/2)/self.step+1

        if (x*self.step+self.origine[0],-y*self.step+self.origine[1]+self.step) in self.decode(self.chemin):
            point = self.decode(self.chemin).index((x*self.step+self.origine[0],-y*self.step+self.origine[1]+self.step))
            self.pileChemins.append(deepcopy(self.chemin))
            self.chemin = self.chemin[:point]+[(k-1)%4 for k in self.chemin[point:]]
            self.dessine()


    def activeSommets(self):
        if self.avecSommet.get():
            self.checkbouton2.configure(state='normal')
        else:
            self.calculDepliage.set(0)
            self.checkbouton2.configure(state='disabled')
        self.dessine()


    def describeWindow(self):
        other = Toplevel()
        other.title('Second Window')
        otherlabel = Label(other, text = 'This is the other window', relief = RIDGE)
        otherlabel.pack(side = TOP, fill = BOTH, expand = YES)

        """
        self.root.bind_all('<Control-s>',self.sauveAuto)
        self.root.bind_all('<Control-z>',self.annule)
        self.root.bind_all('<Control-q>',quit)
        self.root.bind_all('<Control-Z>',self.desannule)        
        self.root.bind_all('<BackSpace>',self.retire)
        #self.root.bind_all('<Control-Button-1>',self.decoupe)

        self.modeRetrace = False
        self.okPourRetracer = False
        self.listeARetracer = []
        self.root.bind('<B1-Motion>',self.retrace)
        self.root.bind('<ButtonRelease-1>',self.detrace)

        self.c.bind("<Button-3>", self.pivot_horaire) 
        self.c.bind("<Motion>", self.getPosition)


        self.root.bind_all('<Key>', self.deplacement)"""            

    def aboutWindow(self):
        other = Toplevel()
        other.title('About PyUSAW')
        otherlabel = Label(other, text = 'Version 0.2\nAuthor: Christophe Guyeux\nEmail: christophe.guyeux@univ-fcomte.fr', relief = RIDGE)
        otherlabel.pack(side = TOP, fill = BOTH, expand = YES)

if __name__ == '__main__':
    nfSAW()
