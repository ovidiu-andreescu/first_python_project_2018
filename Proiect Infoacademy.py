"""
    Avem aplicatia care tine stocul unui depozit. Efectuati urmatoarele imbunatatiri:

1. Implementati o solutie care sa returneze o proiectie grafica a intrarilor si iesirilor intr-o
anumita perioada, pentru un anumit produs;	--pygal--

2. Implementati o solutie care sa va avertizeze cand stocul unui produs este mai mic decat o limita
minima, predefinita. Limita sa poata fi variabila (per produs). Preferabil sa transmita un email de
avertizare sefului serviciului aprovizionare;

3. Creati o metoda cu ajutorul careia sa puteti transmite prin email diferite informatii (
de exemplu fisa produsului) ; 	--SMTP--

4. Utilizati Regex pentru a cauta :
    - un produs introdus de utilizator;
    - o tranzactie cu o anumita valoare introdusa de utilizator;	--re--

5. Creati o baza de date care sa cuprinda urmatoarele tabele:	--pymysql--  sau --sqlite3--
    Categoria
        - idc INT NOT NULL AUTO_INCREMENT PRIMARY KEY (integer in loc de int in sqlite3)
        - denc VARCHAR(255) (text in loc de varchar in sqlite3)
    Produs
        - idp INT NOT NULL AUTO_INCREMENT PRIMARY KEY
        - idc INT NOT NULL
        - denp VARCHAR(255)
        - pret DECIMAL(8,2) DEFAULT 0 (real in loc de decimal)
        # FOREIGN KEY (idc) REFERENCES Categoria.idc ON UPDATE CASCADE ON DELETE RESTRICT
    Operatiuni
        - ido INT NOT NULL AUTO_INCREMENT PRIMARY KEY
        - idp INT NOT NULL
        - cant DECIMAL(10,3) DEFAULT 0
        - data DATE

6. Imlementati o solutie cu ajutorul careia sa populati baza de date cu informatiile adecvate.

7. Creati cateva view-uri cuprinzand rapoarte standard pe baza informatiilor din baza de date. --pentru avansati--
pygal
8. Completati aplicatia astfel incat sa permita introducerea pretului la fiecare intrare si iesire.
Pretul produsului va fi pretul mediu ponderat (la fiecare tranzactie se va face o medie intre
pretul produselor din stoc si al celor intrate ceea ce va deveni noul pret al produselor stocate.
Pretul de iesire va fi pretul dpygalin acel moment; --pentru avansati--

""" 
from datetime import datetime
import smtplib
import pygal
import pymysql

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()

server.login("t6575162", "thisisatest")
mail = input('Mail: ')

host = "localhost"
passwd = ""
port = 3306
user = "root"
dbname = "Project"
db = pymysql.connect(host='127.0.0.1', port = 3306, user = user, passwd = passwd, db = dbname)

cursor = db.cursor()
#cursor.execute("CREATE TABLE Categorie (idc INT NOT NULL AUTO_INCREMENT PRIMARY KEY, denc VARCHAR(255))")
#cursor.execute("CREATE TABLE Produs (idp INT NOT NULL AUTO_INCREMENT PRIMARY KEY, idc INT NOT NULL, denp VARCHAR(255), pret DECIMAL(8,2) DEFAULT 0)")
#cursor.execute("CREATE TABLE Operatiuni (ido INT NOT NULL AUTO_INCREMENT PRIMARY KEY, idp INT NOT NULL, cant DECIMAL(10,3) DEFAULT 0, data DATE)")

class Stoc:
    """Tine stocul unui depozit"""

    def __init__(self, prod, categ, um = 'Buc', sold = 0):
        self.prod = prod			# parametri cu valori default ii lasam la sfarsitul listei
        self.categ = categ  		# fiecare instanta va fi creata obligatoriu cu primii trei param.
        self.sold = sold			# al patrulea e optional, soldul va fi zero
        self.um = um
        self.i = {}					# fiecare instanta va avea trei dictionare intrari, iesiri, data
        self.e = {}					# pentru mentinerea corelatiilor cheia operatiunii va fi unica
        self.d = {}

    def intr(self, cant, data = str(datetime.now().strftime('%Y%m%d'))):
        self.data = data
        self.cant = cant
        self.sold += self.cant          # recalculam soldul dupa fiecare tranzactie
        if self.d.keys():               # dictionarul data are toate cheile (fiecare tranzactie are data)
            cheie = max(self.d.keys()) + 1
        else:
            cheie = 1
        self.i[cheie] = self.cant       # introducem valorile in dictionarele de intrari si data
        self.d[cheie] = self.data

    def iesi(self, cant, data = str(datetime.now().strftime('%Y%m%d'))):
        #   datetime.strftime(datetime.now(), '%Y%m%d') in Python 3.5
        self.data = data
        self.cant = cant
        self.sold -= self.cant
        if self.d.keys():
            cheie = max(self.d.keys()) + 1
        else:
            cheie = 1
        self.e[cheie] = self.cant       # similar, introducem datele in dictionarele iesiri si data
        self.d[cheie] = self.data

    def fisap(self):

        print('Fisa produsului ' + self.prod + ': ' + self.um)
        print(40 * '-')
        print(' Nrc ', '  Data ', 'Intrari', 'Iesiri')
        print(40 * '-')
        for v in self.d.keys():
            if v in self.i.keys():
                print(str(v).rjust(5), self.d[v], str(self.i[v]).rjust(6), str(0).rjust(6))
            else:
                print(str(v).rjust(5), self.d[v], str(0).rjust(6), str(self.e[v]).rjust(6))
        print(40 * '-')
        print('Stoc actual:      ' + str(self.sold).rjust(10))
        print(40 * '-' + '\n')

    def fisap_mail(self):
        global Fise
        Fise = []
        for v in self.d.keys():
            if v in self.i.keys():
                Fisa = '\nProdus: {0}\n\
                        Nrc: {1}\n\
                        Data: {2}\n\
                        Intrare: {3}\n\
                        Iesire: {4}\n\
                        Stoc: {5}'.format(self.prod, str(v), self.d[v], str(self.i[v]), str(0), self.sold)
                
            else:
                Fisa = '\nProdus: {0}\n\
                      Nrc: {1}\n\
                      Data: {2}\n\
                      Intrare: {3}\n\
                      Iesire: {4}\n\
                      Stoc: {5}'.format(self.prod, str(v), self.d[v], str(0), str(self.e[v]), self.sold)

            Fise.append(Fisa)

        server.sendmail('t6575162', mail, " ".join(map(" ".join, Fise)))

    def limita(self, lim):
        self.lim = lim
        if self.sold < lim:
            print("Stocul e sub limita pentru: {0}. Stoc actual: {1}".format(self.prod, str(self.sold)))
            msg = "\nStocul e sub limita pentru: {0}. Stoc actual: {1}".format(self.prod, str(self.sold))
            server.sendmail('t6575162', mail, msg)
    
    def graf(self):
        line_chart = pygal.Bar()
        line_chart.title = 'Depozit Intrari si iesiri'
        for v in self.d.keys():
            if v in self.i.keys():
                line_chart.add('Intrari', [self.i[v]])
            else:
                line_chart.add('Iesiri', [self.e[v]])
        line_chart.render_in_browser()
  

fragute = Stoc('fragute', 'fructe', 'kg')       # cream instantele clasei
lapte = Stoc('lapte', 'lactate', 'litru')
ceasuri = Stoc('ceasuri', 'ceasuri')

fragute.sold                    # ATRIBUTE
fragute.prod
fragute.intr(100)
fragute.iesi(73)
fragute.intr(100)
fragute.iesi(85)
fragute.intr(100)
fragute.iesi(101)

fragute.d                       # dictinareele produsului cu informatii specializate
fragute.i
fragute.e

fragute.sold
fragute.categ
fragute.prod
fragute.um


lapte.intr(1500)
lapte.iesi(975)
lapte.intr(1200)
lapte.iesi(1490)
lapte.intr(1000)
lapte.iesi(1200)

fragute.limita(30)
lapte.limita(50)


fragute.graf()
lapte.graf()
ceasuri.graf()


l = [fragute, lapte, ceasuri]

for i in l:
	i.fisap()

fragute.fisap_mail()
db.commit()
server.quit()