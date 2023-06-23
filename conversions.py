import math

def position_from_count(count):
        
        spalte = count%6 + 1
        reihe = math.ceil((count-spalte)/6) + 1
        
        return spalte,reihe
    
def count_from_position(spalte,zeile):
    
    return ((zeile - 1) * 6 + spalte - 1)