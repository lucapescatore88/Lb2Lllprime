
def get_combinations(vects = []) :

    if len(vects) < 1 : return None
    if len(vects) == 1 : return [ [x] for x in vects[0] ]

    combs = []
    smaller_combs = get_combinations( vects[:-1] )
    for el in vects[-1] :
        for sc in smaller_combs :
            combs.append(sc + [el])

    return combs


