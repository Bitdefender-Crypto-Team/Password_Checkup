#implementing useful operations in TenSeal for PIR

import tenseal as ts
import numpy as np

#FUNCTII UTILE (PROBABIL MAI MULT PENTRU GENERAREA VECTORILOR DE SELECTIE PENTRU CLIENT
#MOMENTAN VECTORII DE SELECTIE SUNT FIXATI CA IN TOY EXAMPLE

#functie care scrie pe n in baza b, e luata din codul din blogpost
def int2base(n, b):
    if (n < b):
        return [n]
    else:
        return int2base(n // b, b) + [n % b]   # am schimbat putin, vreau pt urm functie sa am lsb la dreapta


#functie care scoate indicii i,j corespunzatori unui k <=m=dimensiunea bazei de date
#k = i*sqrt(n)+j, practic scriu indexul de input k in baza sqrt(n) dar lsb = j tre sa fie la draepta

def indices_of_database_entry(k, m):
    v = int2base(k, np.int64(np.sqrt(m)))
    if len(v) == 1:
        v = v + [0]
    return v

#---------------------TOY EXAMPLE-------------------------------------
#BAZA DE DATE
db = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])  # 16 elem pe 4 biti
#se foloseste in protocol PIR cu 2 DIMENSIUNI BAZA DE DATE STOCATA CA MATRICE sqrt(n)xsqrt(n)
db_enc = db.reshape((4,4))

#CLIENTUL: QUERY
#indexul pe care clientul vrea sa il ceara e encodat ca un vector de selectie, de lungime cat baza de date;
#in cazul de aici, vrea sa selecteze db[k] pt k=1

#pt varianta cu 1 DIMENSIUNE (care e cea mai simpla)
select_vector = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#pt varianta cu 2 DIMENSIUNI adica baza de date e construita ca matrice sqrt(n) * sqrt(n)
#k = 1 = 0*sqrt(n) + 1, deci poz care ne intereseaza din matrice este [i, j] = [0, 1]
#select_vector1 encodeaza i si select_vector2 encodeaza j, amandoi sunt de lungime sqrt(n)
select_vector1 = [1, 0, 0, 0]
select_vector2 = [0, 1, 0, 0]

#-------------------------------------------------------------
#PIR PROTOCOL-LIKE USING CKKS SCHEME
# BUBA LA SCHEMA ASTA E CA LUCREAZA CU NR REALE; DECRIPTARILE RETURNEAZA NR REALE.
#SETUP SCHEMA

context2 = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
context2.generate_galois_keys()
context2.global_scale = 2 ** 40

#1 DIMENSIUNE: clientul da criptarea pt un vector de tip selection_vector, de lungime n, ce encodeaza query-ul k
#QUERY TRIMIS DE CLIENT
query2 = ts.ckks_vector(context2, select_vector)
#RASPUNSUL DE LA SERVER
response2 = query2.dot(db)
#CE EXTRAGE CLIENTUL DIN RASPUNSUL PRIMIT
verdict2 = response2.decrypt()[0] % 2 ** 4    # decrypt returneaza vector cu 1 elem aici, am nevoie de element
print ("clientul a decriptat raspunsul la " + str(verdict2))

#2 DIMENSIUNI: clientul da criptari pt 2 vectori de tip selection_vector, de lungime sqrt(n), ce encodeaza i, j, unde k=i*sqrt(n)+j
#QUERY TRIMIS DE CLIENT
query21 = ts.ckks_vector(context2, select_vector1)
query22 = ts.ckks_vector(context2, select_vector2)
#RASPUNSUL DE LA SERVER
db_transpose = np.transpose(db_enc)
c = query22.matmul(db_transpose)
print ("coloana din matricea-baza de date, cea care contine query-ul"+str(c.decrypt())) #pt verificare
response2_ = c.dot(query21)
#CE EXTRAGE CLIENTUL DIN RASPUNSUL PRIMIT
verdict2_ = response2_.decrypt()[0] % 2 ** 4
print ("clientul a decriptat raspunsul la " + str(verdict2_))

#-----------------------------------------------------------------------
#PIR PROTOCOL-LIKE USING BFV SCHEME
'''
#SETUP SCHEMA
# poly_modulus_degree
n = 4096
# plain_modulus
t = 1032193
context = ts.context(ts.SCHEME_TYPE.BFV, poly_modulus_degree=n, plain_modulus=t)
#QUERY CLIENT
#query = ts.bfv_vector(context, select_vector)
#RASPUNSUL DE LA SERVER
#response = query.dot_product_inplace(db)  #face inmultirea component-wise; PRODUSUL SCALAR (.DOT) SI .MATMUL NU PAR DEFINITE PT BFV:(
#CE EXTRAGE CLIENTUL
#verdict = response.decrypt()
#print (verdict)

#enc_vector = ts.bfv_vector(context, select_vector)

c1 = ts.bfv_vector(context, [1,2,3])
c2 = ts.bfv_vector(context, [3,0,1])

c3 = c1.dot(c2)
print (c3.decrypt())
'''


