#!/usr/bin/env python
# coding: utf-8

# # Tarea 1: Pregunta 2

# ### Funciones auxiliares

# In[1]:


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
def custom_md5(msg: str, h0: int = 0x67452301) -> str:
    A = h0 % (pow(2, 32))
    B = 0xEFCDAB89
    C = 0x98BADCFE
    D = 0x10325476

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


# ### Resultados

# In[4]:


custom = custom_md5("hola")
print(custom)


# In[ ]:




