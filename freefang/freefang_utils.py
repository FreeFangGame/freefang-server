import random, string

def randstring():
	alphabet = list("abcdefghijklmnopqrstuvwxyz")
	return "".join([alphabet[random.randint(0, 25)] for i in range(10)])
