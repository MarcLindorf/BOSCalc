# Werte für die Materialien der Kennzahlen(KZ) 1,2,3,4,...,12,13:

# TBD Nachfragen: Warum ist die "Materialpaarung" 5&6 beide Male Blech? Was ist hier besonders?
Mat_list=['Rohr','Bl.','Rohr','Bl.','Bl.','Bl.','Rohr','Bl.','Rohr','Bl.','Rohr','Bl.']

Mat_name_list=[
    'P235GH',
    'P265GH',
    '15Mo3',
    '16Mo3',
    '13CrMo4-5',
    '1.4301',
    'SA106GrB',
    'SA516Gr60',
    'SA335P11',
    'SA335P22',
    'SA387Gr.12',
    'SA387Gr.22',
    'Gestrick'
]

Mat_prices_list=[
    1.30,
    1.20,
    2.50,
    1.60,
    2.80,
    3.10,
    1.60,
    1.50,
    3.60,
    4.10,
    2.80,
    3.50,
    11.00,
]

KZ_dict={
    1:2,
    2:2,
    3:4,
    4:4,
    5:5,
    6:6,
    7:8,
    8:8,
    9:10,
    10:10,
    11:12,
    12:12,
    13:13
}

# Zusatzoptionen Material Kennzahlen

KZ_Zn_SiAl_dict={        #Materialkosten für Zn- und SiAl-Option
1:  3.45,
2:  6.90,
3:  6.90,
4:  13.80
}