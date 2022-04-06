# Richtcharakteristik (Auswahl über Backend-Inputparameter "directivity"):

angle45_list = [-0,	-0,	-0,	-0,	-0,	-0,	    -0,	    -0]
angle90_list = [-0,	-0,	-0,	-1,	-3,	-5,	    -7,	    -9]
angle120_list =[-0,	-0, -1,	-3,	-6,	-7,	    -11,	-15]
angle150_list =[-0,	-0,	-2,	-5,	-8,	-10,	-13,	-17]
directivity_dict = {
    45:  angle45_list,
    90:  angle90_list,
    120:  angle120_list,
    150:  angle150_list
}

def calc_directivity(angle):
    for i in directivity_dict:
        if(angle <= i):
            return directivity_dict[i]
    return directivity_dict[0]
            