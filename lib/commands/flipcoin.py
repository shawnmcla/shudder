import random

#Command: !flipcoin

def flip_coin(userName, *args, **kwargs):
    """Simulate a coinflip, return a string representing the result."""
    return ["/me flips a shiny quarter!", "It landed on Heads! ( Kappa )" if random.randint(1,2) == 1 else "It landed on Tails! ( StinkyCheese )"]