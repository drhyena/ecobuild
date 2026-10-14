class GeneticManager:
    #a class that oversees how genes get passed over. acts as a balancer of sorts. wihtout balance, craetures simply get stronger,faster, longer ranged etc
    def __init__(self,c):

        conversion_dictionary = conversion_dictionary.fromkeys(c.genome,"")
