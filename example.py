import math

# Params: 112272535095293 112582705942171 112272535095293 115280095190773 115797848077099 1099726899285419 294975139100397 450958985454453 4508057898454457 364172344003717


def main(x):
    n = int(x)
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True
