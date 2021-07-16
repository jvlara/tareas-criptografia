#!/usr/bin/env python
# coding: utf-8

# # Tarea 1: Pregunta 2

# ### Funciones auxiliares

# In[1]:

import random
import math

def transform_to_raw_binary(msg: str) -> int:
    # Transforma un mensaje en un array de bits
    int_array = bytearray(msg, 'utf-8')
    integer_array = [to_bin_2(x) for x in int_array]
    str_bin = "".join(integer_array)
    return str_bin

def hex_to_str(num):
    # Transforma un numero a hexadecimal
    return f"{num:08x}"

def padding(str_bin: str) -> str:
    # Función de padding de md5
    i_len = len(str_bin) % 512
    pad = ""
    # Dependiendo del largo le añadimos el 1 con su respectivos 0
    # hasta llegar a 448 mod 512
    if i_len < 448:
        pad += "1"
        pad += "0" * (448-i_len-1)
    elif i_len == 448:
        pad += "1"
        pad += "0" * 511
    else:
        x = 512-i_len+448
        pad += "1"
        pad += "0" * (x-1)
    # añadimos el lenght en un largo de 64
    largo = len(str_bin)
    largoencoded = f'{largo:064b}'
    # transformamos a little la representación y lo añadimos al mensaje original
    pad += transform_to_little(largoencoded)
    return str_bin + pad

def to_bin_2(int10: int, with_b: bool = False) -> str:
    # Tomamos un int y lo transformamos en binario representado en 
    # 8 bits
    return f'{int10:08b}' if with_b == False else f'{int10:#08b}'

def transform_to_little(secuencia: str) -> str:
    # Tomamos cada byte y luego los damos vuelta
    # un byte es 8 bits
    if (len(secuencia) % 8) != 0:
        raise Exception
    little = []
    for i in range(0, int(len(secuencia)/8)):
        aux = secuencia[8*i: 8*(i+1)]
        little.append(aux)
    return "".join(little[::-1])

# Funciones auxiliares sacadas de wikipedia en ingles para hacer el hasheo
# &: and, |: or, ~:neg, ^: xor
def F(b, c, d): 
    return (b & c) | (~b & d)
def G(b, c, d): 
    return (b & d) | (c & ~d)
def H(b, c, d): 
    return b ^ c ^ d
def I(b, c, d): 
    return c ^ (b | ~d)
# Suma modulo 2 la 32
def mod_32_sum(a, b): 
    return (a + b) % pow(2, 32)
# Shift left pero con rotación
def left_rotate(x, n): 
    return (x << n) | (x >> (32 - n))


# ### Función md5

# In[2]:


import math

# Inspirado en wikipedia md5 versión ingles y paper de md5 original
def custom_md5(msg: str, h0: int = 137269462086865085541390238039692956790) -> str:
    A = h0 // pow(2, 32*3)
    B = (h0 // pow(2, 32*2)) % pow(2,32)
    C = (h0 // pow(2, 32)) % pow(2,32)
    D = h0 % pow(2, 32)

    binary_msg = transform_to_raw_binary(msg)
    # Añadimos el padding
    binary_msg = padding(binary_msg)
    len_msg = len(binary_msg)
    # Transformamos a little todas las palabras de 32 bits de largo en el mensaje padeado
    binary_msg = "".join([transform_to_little(binary_msg[32*i:32*(i+1)]) for i in range(0, int(len_msg/32))])
    if len_msg % 512 != 0:
        raise ValueError("largo incorrecto")
    # Separamos los n mensajes de largo 512
    mensajes_512 = [binary_msg[512*i:512*(i+1)] for i in range(0, int(len_msg/512))]
    if len("".join(mensajes_512)) != len(binary_msg):
        raise ValueError("no coincide con el valor del mensaje")
    # inicializamos T con la formula de sen por 2 a la 32
    T = [math.floor(abs(math.sin(i+1))*4294967296) for i in range(0, 64)]
    # Auxiliares
    AA = A
    BB = B
    CC = C
    DD = D
    
    
    for msj in mensajes_512:
        if len(msj) != 512:
            raise ValueError("Largo no puede ser distinto a 512")

        M = []
        # Separamos mensaje en trozos de 32 bits
        for i in range(0, int(len(msj)/32)):
            aux = msj[int(32*i):int(32*(i+1))]
            M.append(aux)
        
        # transformamos str a int 
        M = [int(i, 2) for i in M]
        
        # Tabla s con los numeros de cada paso -> ronda
        S = {0: [7, 12, 17, 22], 1: [5, 9, 14, 20], 2: [4, 11, 16, 23], 3: [6, 10, 15, 21]}
        
        # proceso de hashing, 4 rondas de 16 pasos
        for ronda in range(4*16):
            if 0 <= ronda <= 15:
                f = F(B, C, D)
                paso = 0
                g = ronda
            elif 16 <= ronda <= 31:
                f = G(B, C, D)
                paso = 1
                g = ((5 * ronda) + 1) % 16
            elif 32 <= ronda <= 47:
                f = H(B, C, D)
                paso = 2
                g = ((3 * ronda) + 5) % 16
            elif 48 <= ronda <= 63:
                f = I(B, C, D)
                paso = 3
                g = (7 * ronda) % 16
            f = (f + M[g] + T[ronda] + A) % pow(2,32)
            f = left_rotate(f, S[paso][ronda % 4])
            A = D
            D = C
            C = B
            B = mod_32_sum (B, f)

        AA = mod_32_sum(AA, A)
        BB = mod_32_sum(BB, B)
        CC = mod_32_sum(CC, C)
        DD = mod_32_sum(DD, D)
    # Transformamos a little los registros y los printeamos como hexadecimal
    la = int(transform_to_little(f"{AA:032b}"),2)
    lb = int(transform_to_little(f"{BB:032b}"), 2)
    lc = int(transform_to_little(f"{CC:032b}"), 2)
    ld = int(transform_to_little(f"{DD:032b}"), 2)
    
    digest = "".join([f"{la:0>8x}", f"{lb:0>8x}", f"{lc:0>8x}", f"{ld:0>8x}"])
    return digest


## Tarea 2 
def miller_rabin(n: int, k: int) -> bool:
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # Transformar el n-1
    d = n-1
    r = 0
    while d % 2 == 0:
        r += 1
        d = d // 2
    # n = (2**r)*d +1

    salir = 0
    for i in range(k):
        a = random.randint(2, n-2)
        actual = exp_mod(a, d, n)  # inicial
        if actual == 1 or actual == n-1:
            continue
        # empezamos desde a elevado a d y vamos elevanto hasta llegar a (a ** n-1).
        for _ in range(r-1):
            actual = exp_mod(actual, 2, n)
            if actual == n-1:
                # nos la jugamos por primo
                salir = 1
                break
        if salir == 1:
            salir = 0
            continue
        # Si vimos puros 1 o cualquier cosa distinta a -1 en los r casos entonces llegamos aquí.
        return False
    return True


def generar_primo(l: int) -> int:
    for i in range(3000):
        r1 = expo(10, l-1)
        r2 = expo(10, l) - 1
        a = random.randint(r1, r2)
        if miller_rabin(a, 100):
            return a


# In[2]:


def alg_ext_euclides(a: int, b: int) -> (int, int, int):
    if b > a:
        raise Exception("El primer numero tiene que ser mayor al segundo")
    if a <= 0:
        raise Exception("El primer numero tiene que ser mayor a 0")
    r = [a, b]
    s = [1, 0]
    t = [0, 1]

    while r[1] != 0:
        aux = r[0] // r[1]
        r = [r[1], r[0] - aux * r[1]]
        s = [s[1], s[0] - aux * s[1]]
        t = [t[1], t[0] - aux * t[1]]

    return r[0], s[0], t[0]


def exp_mod(a: int, b: int, n: int) -> int:
    if a < 0 or b < 0 or n <= 0:
        raise Exception("Error de argumentos")
    if b == 0:
        return 1
    elif (b % 2) == 0:
        t = exp_mod(a, b//2, n)
        return (t*t) % n
    else:
        t = exp_mod(a, (b-1) // 2, n)
        return (t*t*a) % n


def exp_mod(a, k, n):
    # Código sacado de https://elbauldelprogramador.com/criptografia-101-fundamentos-matematicos-ii/ ya que el algoritmo que hice recursivo tiraba recursion limit en primos 150 +
    b = 1
    if k == 0:
        return b
    A = a
    if 1 & k:
        b = a
    k = k >> 1
    while k:
        A = (A**2) % n
        if 1 & k:
            b = (b * A) % n
        k = k >> 1
    return b


def expo(a: int, b: int) -> int:
    if b == 0:
        return 1
    elif (b % 2) == 0:
        t = expo(a, b//2)
        return (t*t)
    else:
        t = expo(a, (b-1) // 2)
        return (t*t*a)


# In[3]:


def inverso(a: int, n: int) -> int:
    if n < 2:
        raise Exception("n tiene que ser mayor o igual a 2")
    if a < 2:
        raise Exception("a tiene que ser mayor o igual a 1")
    if a > n:
        mcd, s, t = alg_ext_euclides(a, n)
        if mcd != 1:
            raise Exception("los inputs tienen que ser primos relativos")
        # Si tenemos que el inverso es negativo hay que pasarlo a su positivo en modulo n
        if s < 0:
            s = n + s
        return s
    else:
        mcd, s, t = alg_ext_euclides(n, a)
        if t < 0:
            t = n + t
        if mcd != 1:
            raise Exception("los inputs tienen que ser primos relativos")
        return t


# In[4]:


def generar_clave(l: int):
    p = generar_primo(l)
    q = generar_primo(l)
    n = p * q
    phin = (p-1)*(q-1)
    while True:
        d = random.randint(1, phin)
        mcd, _, _ = alg_ext_euclides(phin, d)
        if mcd == 1:
            break
    e = inverso(d, phin)
    with open("private_key.txt", "w") as file:
        file.write(f"{d}\n")
        file.write(f"{n}\n")
    with open("public_key.txt", "w") as file:
        file.write(f"{e}\n")
        file.write(f"{n}\n")


def enc(m: int) -> int:
    with open("public_key.txt", "r") as file:
        lines = file.readlines()
        e = int(lines[0].strip())
        n = int(lines[1].strip())
    if m >= n:
        raise Exception("el mensaje es más largo que n")
    return exp_mod(m, e, n)


def dec(m: int) -> int:
    with open("private_key.txt", "r") as file:
        lines = file.readlines()
        d = int(lines[0].strip())
        n = int(lines[1].strip())
    if m >= n:
        raise Exception("el mensaje es más largo que n")
    return exp_mod(m, d, n)
