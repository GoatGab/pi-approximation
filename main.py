from decimal import *
from timeit import default_timer as timer
import math
from multiprocessing.pool import ThreadPool
from multiprocessing import *
from functools import lru_cache
import sys

def arraySum(arr):
    sum = Decimal(0)
    for e in arr:
        sum += e
    return sum

@lru_cache
def factorial(num):
    fact = Decimal(1)
    for i in range(2, num+1):
        fact *= i
    return fact

@lru_cache
def numerator(k):
    six_k_fact = factorial(6 * k)
    n = 1
    if k % 2 == 1: n = -1
    return n * six_k_fact * (Decimal(545140134) * k + Decimal(13591409))

@lru_cache
def denominator_a(k):
    factorial_k = factorial(k)
    return factorial(3 * k) * factorial_k * factorial_k * factorial_k

@lru_cache
def denominator_b (k):
    return Decimal(640320) ** (k * 3)

@lru_cache
def calcConstant(precision):
    getcontext().prec = precision    
    numerator = Decimal(1)
    denominator_a = Decimal(426880)
    denominator_b_squared = Decimal(10005)
    result = numerator / (denominator_a * ((denominator_b_squared) ** Decimal(0.5)))
    return result

@lru_cache
def calcChunkThread(params):
    k0, k1, prec = params[0], params[1], params[2]
    getcontext().prec = prec 
    sum = 0
    if k0 == k1 and k1 == -1:
        return calcConstant(prec)

    for k in range(k0, k1):
        term = (numerator(k) / (denominator_a(k) * denominator_b(k)))
        #print(f"{k}: {term}")
        sum += term
    
    return sum


@lru_cache
def calcThread(k, prec):
    getcontext().prec = prec 
    return (numerator(k) / (denominator_a(k) * denominator_b(k)))


def chudnovskyThreaded(terms, precision, nThreads):
    getcontext().prec = precision
    piResults = []
    
    threadsPool = ThreadPool(processes=nThreads)
    chunkSize = math.floor(terms / nThreads)
    offset = (terms % nThreads)
    
    async_results = []
    chunks = []
    
    for t in range(nThreads+1):
        if t == 0:
            chunks.append((0, chunkSize + offset, precision))
            print(f"{t+1}/{nThreads+1} threads initialized", end='\r')
        elif t == nThreads:
            chunks.append((-1, -1, precision))
            print(f"{t+1}/{nThreads+1} threads initialized", end='\r')
        else: 
            chunks.append((t * chunkSize + offset, (t+1) * chunkSize + offset, precision))
            print(f"{t+1}/{nThreads+1} threads initialized", end='\r')
            
                
    print("") 
    print(">threads initialized")
    piResults = threadsPool.map(calcChunkThread, chunks)
    print(">threads executed")

    const = piResults.pop()

    piInverse = arraySum(piResults)
    print(">completing calculation")
    
    pi = Decimal(1) / (const * piInverse)
    
    return pi
  
def chudnovsky(terms, precision):
    getcontext().prec = precision
    piInverse = 0
   
    for k in range(terms): 
        term = numerator(k) / (denominator_a(k) * denominator_b(k))
        print(f"{k}: {term}")
        piInverse += term
        
    const = calcConstant(precision)
    
    pi = Decimal(1) / (const * piInverse)
    return pi

    
    
  
def main():
    digits = int(input("digits: "))
    threads = int(input("n of threads: "))
    terms = math.ceil(digits/14)
    print(f">calculated: {terms} terms")
    start = timer()
    pi = chudnovskyThreaded(terms, digits, threads)
    #pi = chudnovsky(terms, digits)
    end = timer()
    print(F">finished in: {round((end-start)*1000, 3)} ms / {round((end-start), 3)} s")
    print(">content in digits.txt")
    f = open("digits.txt", "w")
    f.write(str(pi))
    f.close()
    
    
if __name__ == "__main__":
    main()