from collections import deque

a = [1, 2, 3, 4, 5, 6]
b = deque(x for x in a if x % 2 != 0)

c = deque()
c.append(1)
c.append(22)
c.append(33)
print(b)
print(c)



if __name__ == "__main__":
    buffer = deque()
    mutex = BinarySemaphore(1)

    prod_a1 = ProdEvenModulo50()
    prod_a2 = ProdOddModulo50()
    # cons_b1 = ConsEven()
    # cons_b2 = ConsOdd()
    all = [prod_a1,  prod_a2]
    # all = [cons_b2]

    # prod_a1_thread = threading.Thread(target=run, args=(prod_a1, all))
    # prod_a2_thread = threading.Thread(target=run, args=(prod_a2, all))
    # cons_b1_thread = threading.Thread(target=run, args=(cons_b1, all))
    # cons_b2_thread = threading.Thread(target=run, args=(cons_b2, all))


    # prod_a1_thread.start()
    # prod_a2_thread.start()
    # cons_b1_thread.start()
    # cons_b2_thread.start()

    # prod_a1_thread.join()
    # prod_a2_thread.join()
    # cons_b1_thread.join()
    # cons_b2_thread.join()
