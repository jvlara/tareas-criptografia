#!/usr/bin/env python
# coding: utf-8

# # Tarea 1: pregunta 3

# Primero ocuparemos pandas y numpy para leer los mensajes encriptados del csv.

# In[8]:


import pandas as pd
import numpy as np
from pregunta2 import custom_md5
from collections import defaultdict
from otp_utils import xor, print_as_binary, as_integers
df = pd.read_csv("mensajes_p3_custom.csv", header=None, names=["hash", "msj"])
i = 0
msjs = []
msjs = list(df["msj"])


# ### Funciones auxiliares

# In[2]:


def probable_space_count_vector(msj, grupo):
    # Tomamos un mensaje perteneciente a un grupo de mensajes y intentamos adivinar que hay existia un espacio
    # ya que el xor de un espacio con una letra pequeña queda en el rango de 64 y 91
    msj = to_ascii(msj)
    length = len(msj)
    counts = [0]*length
    for c in grupo:
        c = to_ascii(c)
        xd = xor(c, msj)
        res = as_integers(xd)
        
        for idx, val in enumerate(res):
            if val > 64 and val < 91:
                counts[idx] += 1
    return [round(c / len(grupo),4) for c in counts]


def probable_comma_count_vector(msj, grupo):
    # Lo mismo de lo anterior pero para una comma, en este caso 77 y 86
    msj = to_ascii(msj)
    length = len(msj)
    counts = [0]*length
    for c in grupo:
        c = to_ascii(c)
        xd = xor(c, msj)
        res = as_integers(xd)

        for idx, val in enumerate(res):
            if val >= 77 and val <= 86:
                counts[idx] += 1
    return [round(c / len(grupo), 4) for c in counts]

def max_index(i, l):
    # Calculamos el indice donde se encuentra la maxima probabilidad de encontrar un espacio o una coma
    result = 0
    max_value = 0
    for j in range(len(l)):
        if l[j][i] > max_value:
            result = j 
            max_value = l[j][i]
    return result 

def get_max_value(i, j , l):
    # Obtenemos el valor maximo de la lista de listas
    return l[j][i] 

def to_bits(x: int):
    # pasamos un int a un string de bits de minimo 8 bits
    return f"{x:08b}"

def to_baits(x: str):
    # pasamos un string a una lista de bytes de 8 bits
    return [x[8*i: 8*(i+1)] for i in range(0, int(len(x)/8))]

def to_ascii(msj):
    # pasamos un string a letras en codigo ascii
    baits = [msj[8*i: 8*(i+1)] for i in range(0, int(len(msj)/8))]
    ints = [int(bait, 2) for bait in baits]
    letters = [chr(n) for n in ints]
    return "".join(letters)


# ### Función como tal con comentarios

# In[3]:


def break_random_otp(encrypted_messages) -> [str]:
    c_mensajes = len(encrypted_messages)
    # Guardamos en ocupados los mensajes que ya estan asignados a un cluster
    ocupados = []
    orden = {x: i for i, x in enumerate(encrypted_messages)}
    grupos = defaultdict(lambda: [])
    
    current_group = 0
    for j in range(c_mensajes):
        msj = encrypted_messages[j]
        if msj in ocupados:
            # Si ya esta asignado lo saltamos
            continue
        # Inicializamos la probabilidad de estar en el cluster actual
        probability = [0 for i in range(c_mensajes)]
        grupos[current_group].append(msj)
        ocupados.append(msj)

        msj = to_ascii(msj)
        for index, i in enumerate(encrypted_messages):
            
            if i in ocupados:
                continue
            c = 0
            i = to_ascii(i)
            # Hacemos xor de el mensaje representante del cluster (msj) con 
            # los demás mensajes no ocupados.
            res = xor(msj, i)
            res = as_integers(res)
            # Para cada letra del xor tomamos una hipotesis
            # Si esta letra esta entre 1 y 27 entonces la llave se canceló por propiedad del xor,
            # por lo que muy probablemente hagamos xor entre dos letras minusculas o entre una letra minuscula y un espacio, 
            # mientras más hit tengamos más probabilidad
            # le asignaremos.
            # a xor z = 27, a xor b = 1
            # a xor space = 65, z xor space = 90
            for letter in res:
                if (letter <= 27 and letter >= 1) or (letter >= 65 and letter <= 90) :
                    c += 1
            probability[index] = c/len(res)
        probability = np.array(probability)
        # Calculamos los indices de los mensajes con probabilidad mayor a 0.7 de pertenecer al cluster
        indices = np.argwhere(probability > 0.7)
        indices = list(indices.flatten())

        for idx in indices:
            # Añadimos al cluster el mensaje y tambien añadimos el mensaje a ocupados
            grupos[current_group].append(encrypted_messages[idx])
            ocupados.append(encrypted_messages[idx])
        current_group += 1
    # LLave: key, value: listas con los valores encriptados de los mensajes.
    keys_group = {}
    # Listas de tuplas con (msg, index, encripted_key)
    bad_msg = []
    keys = []
    # Para cada grupo calculamos su llave y decriptamos los mensajes que estan dentro
    for key, grupo in grupos.items():
        probables = [probable_space_count_vector(msj, grupo) for msj in grupo]
        probables_c = [probable_comma_count_vector(msj, grupo) for msj in grupo]

        # Maximos valores donde puede estar un espacio
        max_values_at = [max_index(i,probables) for i in range(len(probables[0]))]
        # Maximos valores donde puede estar una coma
        max_values_at_c = [max_index(i,probables_c) for i in range(len(probables_c[0]))]
        # Valores encriptados de un posible espacio
        encrypted_spaces = ""
        # Valores de los mensajes encriptados de un posible espacio o coma
        encrypted_both = ""
        # Espacio y comas concatenados correspondientes a si se uso una coma o un espacio
        boths = ""
        space = f"{ord(' '):08b}"
        c = f"{ord(','):08b}"
        letters = [space, c]
        for i in range(len(max_values_at)):
            space_byte = to_baits(grupo[max_values_at[i]])[i]
            comma_byte = to_baits(grupo[max_values_at_c[i]])[i]
            space_prob = get_max_value(i, max_values_at[i], probables)
            c_prob = get_max_value(i, max_values_at_c[i], probables_c)
            x = [space_prob, c_prob]
            y = [space_byte, comma_byte]
            x = np.array(x)
            idx = np.argmax(x)
            # Añadimos el que tenga más probabilidad de estar en ese lugar, 
            # puede ser la coma o el espacio.
            encrypted_both += y[idx]
            boths += letters[idx]
            # Solo con espacios (sin considerar comas)
            encrypted_spaces += space_byte
            
        spaces = space * len(probables[0])
        # Calculamos dos posibles llaves, dio mejor en la practica usando comas y espacios
        # asi que ocuparemos la probable_key2
        probable_key = xor(to_ascii(encrypted_spaces),to_ascii(spaces))    
        probable_key2 = xor(to_ascii(encrypted_both), to_ascii(boths))
        keys.append(probable_key2)
        keys_group[probable_key2] = []
        # Para cada palabra en el cluster lo decriptaremos con su llave probable
        for word in grupo:
            c = 0
            asciiword = to_ascii(word)
            xorted = xor(asciiword, probable_key2)
            integers = as_integers(xorted)
            # Ocupamos last_letter para saber cuantas veces hemos visto una letra seguida
            # si es mas de 2 entonces lo añadimos a bad_msg
            last_letter = (0, 0)
            for letter in integers:
                # Si el resultado del xor de la palabra con la llave tiene letras pequeñas o espacio
                # entonces es más probable que este correctamente decriptada
                if (letter <= 122 and letter >= 97) or (letter == 32):
                    if last_letter[0] == letter:
                        last_letter = (letter, last_letter[1] + 1)
                    else:
                        last_letter = (letter, 1)
                    if last_letter[1] > 2:
                        c = 0 
                        break
                    c += 1
            # Si tenemos más de 6 significa que probablemente la llave lo decripto decentemente asi que 
            # lo añadimos a full_msg
            if c > 6: 
                keys_group[probable_key2].append(xorted)
            else:
                bad_msg.append((xorted, orden[word], probable_key))

    
    # Para cada mensaje dentro de bad_msg probabmos decriptandolo con otra llave que nos de
    # el mejor resultado posible (por si quedo fuera de un cluster al que pertenecia)
    for encrypted, idx, encrypted_key in bad_msg:
        best_encrypt = ""
        best_c = 0
        best_key = ""
        bad = encrypted_messages[idx]
        bad = to_ascii(bad)
        for key in keys:
            xorted = xor(key, bad)
            integers = as_integers(xorted)
            last_letter = (0, 0)
            for letter in integers:
                if (letter <= 122 and letter >= 97) or (letter == 32):
                    if last_letter[0] == letter:
                        last_letter = (letter, last_letter[1] + 1)
                    else:
                        last_letter = (letter, 1)
                    if last_letter[1] > 2:
                        c = 0
                        break
                    c += 1
            if c > best_c:
                best_c = c
                best_encrypt = xorted
                best_key = key
        keys_group[best_key].append(best_encrypt)
            
    return keys_group


# ### Resultados obtenidos
# Bastante malos :c algo se entiende en algunas llaves, la agrupación no salio bien enalgunos casos.

# In[4]:


result = break_random_otp(msjs)
print(result)


# In[ ]:




