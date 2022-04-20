# %%
# Berechnungsscript zur Auslegung von Ausblaseschalldämpfern (ehemals Excelfile)

# viele Variablen- & Funktionsnamen wurden direkt aus dem ursprünglichen Excelfile direkt übernommen und gehorchen daher nicht den Python Namenskonventionen

# %%
# externe Module
import math
import cmath

# interne Konstanten Files
import const_gas
import const_diam
import const_bombe
import const_material
import const_festigkeit
import const_directivity
import const_oktspektrum

# %%
#Input-Parameter
def get_input(ext_input_list):
    if __name__ == "__main__":
    # #---------------
        get_input.flow            = 50    #Flow Rate   kg/s
        get_input.p_valve         = 10   #Inlet Pressure   bara
        get_input.t_valve         = 800   #Temperature   °C

        get_input.p_inl           = 15    #Inlet Pressure   bara
        get_input.LwA_input       = 120   #Sound power level   dB(A)
        get_input.LpA_input       = 100   #Sound pressure level   dB(A)
        get_input.d_tocasing      = 1     #Distance to casing   m

        get_input.p_design        = 20    #Design pressure   bara
        get_input.t_design        = 500   #Design temperature   °C
        get_input.d_wall          = 12    #Wallthickness   mm
        get_input.d_inl           = 711   #Inlet pipe chosen   mm

    if __name__ != "__main__":
        pass
        get_input.flow = ext_input_list[0]
        get_input.p_valve  = ext_input_list[1]
        get_input.t_valve = ext_input_list[2]

        get_input.p_inl = ext_input_list[3]
        get_input.LwA_input = ext_input_list[4]
        get_input.LpA_input = ext_input_list[5]
        get_input.d_tocasing = ext_input_list[6]

        get_input.p_design = ext_input_list[7]
        get_input.t_design = ext_input_list[8]
        get_input.d_wall = ext_input_list[9]
        get_input.d_inl = ext_input_list[10]

    #-------------
    # angeschlossene Variablendefinitionen:

    # hilfreiche Umbenennung zu Namen wie im Ursprungs-Excelfile
    m   = get_input.flow
    get_input.t1  = get_input.t_valve
    get_input.p1  = get_input.p_valve
    get_input.h1  = h_d(get_input.p_valve,get_input.t_valve)
    get_input.ts1 = ts(get_input.p_valve)
    get_input.v1  = v_d(get_input.p_valve,get_input.t_valve)

    get_input.d_St1 = get_input.d_inl       # Einführung der "fixed Parameter" d_St1 & p_St1 aus reiner Namensanalogie, an sich nicht notwendig
    get_input.p_St1 = get_input.p_inl


    #Berechnung normierter Volumenstrom V_b
    get_input.V_b = get_input.flow*v_d(p_atm,t_Bereich(p_atm,get_input.h1))

    # Berechnung "fixed Parameter" t_e für alle Bautypen
    if(h_d(p_atm,ts(p_atm))>get_input.h1): get_input.t_e=ts(p_atm)
    else: get_input.t_e=t_Bereich(p_atm,get_input.h1)

    # Berechnung der "fixed Parameter" h_sd & t & v für alle Stufen 1
    get_input.h_sd_St1 = h_d(get_input.p_inl,ts(get_input.p_inl))
    if(get_input.h_sd_St1>get_input.h1): get_input.t_St1=ts(get_input.p_inl)
    else: get_input.t_St1=t_Bereich(get_input.p_inl,get_input.h1)
    get_input.v_St1 = v_d(get_input.p_inl,get_input.t_St1)

    # Auswahl der "fixed Parameter" t_d und p_d
    get_input.t_d = max([get_input.t_design,get_input.t_St1])
    get_input.p_d = max([get_input.p_design,get_input.p_inl])

    #Berechnung kappa (==k) und Schallgeschwindigkeit c:
    if(round(get_input.ts1) == round(get_input.t1)): get_input.k_ = 1.135
    else: get_input.k_ = 1.3
    get_input.c_ = (get_input.k_ * 460 * (get_input.t_St1+273))**0.5



# %%
#Backend Input-Parameter
#-----------------------
timeout_tries = 1000        # Anzahl Durchläufe in while Schleifen bevor Error geraised wird

p_atm = 1       #atmosphärischer Druck (Umgebungsdruck)

p_min1 = 1.05
p_min2 = 1.2
p_min3 = 1.3
p_min4 = 1.4
p_min5 = 1.5
p_min6 = 1.6
p_min_list = [p_min1,p_min2,p_min3,p_min4,p_min5,p_min6]    # TBDTBDTBD Nachfragen: soll die Abfrage von p_min integriert werden und wenn ja, korrekter als im Excelfile?

w_max = 150
w_min = 75
a_ = 0.7
a_stufe = 0.8
Ma_Max1 = 0.8
Ma_Max_ = 0.8

vMax_TypA = 80
vMax_TypB = 65
vMax_Absorption = 65

directivity_angle = 90        # Richtungsabhängigkeit Schalleinwirkung (in °)

PED = False             # TÜV Kosten
birdscreen = False      # Vogelschutz Kosten
Splash_Plates = 0       # "Spritzschutz"-Platten (Kosten) (0==nein 1==ja)
Brackets = 'n'          # Brackets ja('y')/nein('n')?
SA_25_75 = 1            # Eine Art Materialauswahl, (nur für =1 implementiert?)
SiAl = 0                # AluSilicon µm -> Dickenauswahl (0-4) (1:25µm außen; 2:50 µm außen, 3:25µm; 4:50 µm)
R3=0        # hier könnte theoretisch das Material manuell ausgewählt werden (not implemented)
code='D'    # Code für Materialauswahl (nur Großschreibung) - A und D möglich

corr_allow = 0          # Korrosionszusatz bei Materialdicke (mm) (most likely not implemented?)
PED_cost = 100           # Kosten TÜV in €
Stundensatz = 40         # Stundensatz in € (pro Stunde)



# %%
def LWAOkt(f,VTyp,m,rho1,rho2,kappa,t,p1,p2,di,q,R):
    Sicherheit = 2              #Sicherheitszuschlag für berechnete Schalleistung 30.03.01
    c = (kappa * R * t)**0.5    #Schallgeschwindigkeit


    # 'In den nachstehenden Konstanten k0 ist berücksichtigt, dass das Terzspektrum
    # 'im Summenpegel nicht auf 0 dB sondern auf ca. 5 dB normiert ist! Z.B. Ventil-
    # 'typ 1: k0 = 93 dB in Gl. 3.2 /1/ und Gl. 72 in Kap. 9 /2/, hier k0 = 88 dB.
    # 'Ventiltyp 5 nur für zusätzliche Berechnung bei eingezogenen Ventilen

    # defacto wird nur VTyp==1 benutzt
    if(VTyp==1):
        k0 = 88 + 5
        x = (p1 - p2) / p2
    if(VTyp==2):
        k0 = 92 + 5
        x = (p1 - p2) / p2
    if(VTyp==3):
        k0 = 80 + 5
        x = (p1 - p2) / p2
    if(VTyp==4):
        k0 = 80 + 5                  #Änderung 6.12.99 von k0=83 auf k0=80
        x = (p1 / p2) ** (1 / m) - 1
    if(VTyp==5):
        k0 = 88 + 5                  #Änderung 1.12.99   überprüfen !!!!
        x = (p1 - p2) / p2   
 
    #------ Summen-Schalleistungspegel ------
    Lw = k0 + 10 * math.log10(q * c ** 2 / (1 + 6 / x ** 2.5))

    #Einfluss der Rohrleitung
    f1 = 1.8 * c / (math.pi * di)
    if( f > f1): Rohr = 0
    else: Rohr = 20 * math.log10(0.77 * f1 / f)
    
    #Gasdichte rho3 zur Berechnung der Querschnittsfläche an Drosselstelle
    if(VTyp < 5):
        if((p1/p2) < 2):
            rho3 = rho1 * (1 - 0.47 * x) ** (1 / kappa)
            v3 = c * x ** 0.5
        else:
            if(kappa <= 1): rho3 = rho1
            if(kappa > 1): rho3 = rho1 * (2 / (kappa + 1)) ** (1 / (kappa - 1))
            v3 = c

    #Normiertes Terz-Spektrum gebildet mit Strouhal-Zahl
    if(VTyp==1 or VTyp==2):
        S2 = math.pi * di ** 2 / 4
        S3 = q / (rho3 * v3)
        if(S3>S2): S3 = S2
        f0 = 3 * 0.2 * v3 / S3 ** 0.5
        if(f<f0): delta = -10 * math.log10(1 + (f0 / f) ** 2.5)
        else: delta = -10 * math.log10(1 + (f / f0))
    if(VTyp==3 or VTyp==4):         #Änderung 6.12.99   Annahmen: Der Lochdurchmesser ist kleiner als 10 mm und drei Löcher wirken zusammen.
        SLL = 3 * math.pi * 0.01 ** 2 / 4 
                                    
        S3 = q / (rho3 * v3)
        if(S3>SLL): S3 = SLL
        f0 = 0.2 * v3 / S3 ** 0.5
        if(f<f0): delta = -10 * math.log10(1 + (f0 / f) ** 2)
        else: delta = -10 * math.log10(1 + (f / f0))
    if(VTyp==5):                     #Neu 1.12.99
        S3 = math.pi * di ** 2 / 4
        v3 = q / (S3 * rho2)
        if(v3>c): v3 = c
        f0 = 0.2 * v3 / S3 ** 0.5
        if(f<f0): delta = -10 * math.log10(1 + (f0 / f) ** 2)
        else: delta = -10 * math.log10(1 + (f / f0))

    #Terz-A-Schalleistungspegel
    result = Lw + Rohr + delta + Sicherheit
    return result
    #=17*LOG(A11)+50*LOG(B11+273)-15
        


# %%
#Berechnung Durchmesser Gehäuse (Typ 1 stufig)
def D_geh(Vb,Dent):
    F58 = Vb/(math.pi/4)
    d_list = [10000]
    compare = 0.1
    for i in range(len(const_diam.Geh_dia)):      #range(len(const_diam.Geh_dia))   36
        test=(const_diam.Geh_dia[i]**2-Dent**2)/1000000
        if(test>compare): compare = test
        d_comp = F58 / compare
        if (d_comp<vMax_TypA): d_list.append(const_diam.Geh_dia[i])
    d_min = min(d_list)
    return d_min

def D_geh_ra(Vb,Dent):
    G58 = Vb/(math.pi/4)
    d_list = [10000]
    compare = 0.1
    for i in range(len(const_diam.Geh_dia)):      #range(len(const_diam.Geh_dia))   36
        test=(const_diam.Geh_dia[i]**2-Dent**2)/1000000
        if(test>compare): compare = test
        d_comp = G58 / compare
        if (d_comp<vMax_TypB): d_list.append(const_diam.Geh_dia[i])
    d_min = min(d_list)
    return d_min

def D_geh_bo(Vb,Dent):
    H58 = Vb/(math.pi/4)
    d_list = [10000]
    compare = 0.1
    for i in range(len(const_diam.Geh_dia)):      #range(len(const_diam.Geh_dia))   36
        test=(const_diam.Geh_dia[i]**2-Dent**2)/1000000
        if(test>compare): compare = test
        d_comp = H58 / compare
        if ((d_comp<vMax_TypA) and (Vb/const_diam.Af_Bo[const_diam.Geh_dia[i]]<=vMax_Absorption)): d_list.append(const_diam.Geh_dia[i])
    d_min = min(d_list)
    return d_min

def D_geh_TypF(Vb,Dent):
    H58 = Vb/(math.pi/4)
    d_list = [10000]
    compare = 0.1
    for i in range(len(const_diam.Geh_dia)):      #range(len(const_diam.Geh_dia))   36
        test=(const_diam.Geh_dia[i]**2-Dent**2)/1000000
        if(test>compare): compare = test
        d_comp = H58 / compare
        if ((d_comp<vMax_TypB) and (Vb/const_diam.Af_Bo[const_diam.Geh_dia[i]]<=vMax_Absorption)): d_list.append(const_diam.Geh_dia[i])
    d_min = min(d_list)
    return d_min



# Auswahlfunktionen Durchmesser für Inlet Durchmesser Stufe 2 & 3
def dzwei(d_er):
    for i in const_diam.dzwei_dict:
        if(d_er <= i): return const_diam.dzwei_dict[i]
    return 0

def ddrei(d_er):
    for i in const_diam.ddrei_dict:
        if(d_er <= i): return const_diam.ddrei_dict[i]
    return 0

# %%
def BB_zeit(h,D,hRA,N,di,Bo):           #Berechnung Arbeitsaufwand Zeit (h)
    workhours_list = []
    workhours_list.append(Mantel(h,D))
    workhours_list.append(Boden(D,di))
    workhours_list.append(Flansche(D,hRA))
    workhours_list.append(Pratzen(N))
    workhours_list.append(Hebeoesen(D,Bo))
    workhours_list.append(Halteeisen(D,Bo))
    workhours_list.append(Rippen(D))
    workhours_list.append(Mabs(Bo))
    workhours_list.append(Ment(di))
    return (sum(workhours_list)/60)

def Mantel(h,D):
    C34 = 15+2*(math.pi*D+h)/1000*4
    if(h>2000): C35 = 5+15+20*D/1000+15*(h-2000)/1000+5+15+20*D/1000+15*2
    else: C35 = 5+15+20*D/1000+15*h/1000
    if(h>2000): C36 = 60+2*math.pi*D/1000*15
    else: C36 = 0
    if(D>2400): C37 = 3*h/1000*(5+2*15)
    else: C37 = h/1000*(5+2*15)
    C38 = C34+C35+C36+C37
    return C38

def Boden(D,di):
    D34 = 15+(math.pi*(D+di)*5/1000)
    D35 = 15+(math.pi*D/1000*5)
    D36 = 15+2*math.pi*D/1000*15
    if(D>2000): D37 = 15+D/1000*(5+2*15)
    else: D37 = 0
    D38 = D34+D35+D36+D37
    return D38

def Flansche(D,hRA):
    if(hRA==0 and 800<D<1700): E34 = 20
    else: E34 = 0
    if(D>800 and hRA!=0): E35 = (15+math.pi*D/1000*(5+2*15))*2
    elif(D>800): E35 = 15+math.pi*D/1000*(5+2*15)
    else: E35 = 0
    return(E34+E35)

def Pratzen(N):
    if(N>0): return (15+N*(2*260+1*300)/1000*(5+2*15))
    return 0

def Halteeisen(D,Bo):
    if(Bo!=0 and D<960.1): G34 = 4*380/1000*4+15
    elif(Bo!=0 and 960<D<2000): G34 = 4*380/1000*4+15+15+4*640/1000*4
    elif(Bo!=0 and D>2000): G34 = 6*380/1000*4+15+15+6*640/1000*4
    else: G34 = 0
    if(Bo!=0 and D<960.1): G35 = 15+4*150/1000*(5+2*15)+15
    elif(Bo!=0 and 960<D<2000): G35 = 15+4*150/1000*(5+2*15)+4*200/1000*(5+2*15)
    elif(Bo!=0 and D>200): G35 = 15+6*150/1000*(5+2*15)+15+15+6*200/1000*(5+2*15)
    else: G35 = 0
    return (G34+G35)

def Hebeoesen(D,Bo):
    if(D<960): H34 = 15+2*400/1000*4
    elif(D<1550): H34 = 15+4*400/1000*4
    elif(D>1400 and Bo!=0): H34 = 0
    else: H34 = 15+4*400/1000*4
    if(D<960): H35 = 15+4*100/1000*(5+2*15)
    elif(D<1550): H35 = 8*100/1000*(5+2*15)
    elif(D>1400 and Bo!=0): H35 = 0
    else: H35 = 15+8*100/1000*(5+2*15)
    return (H34+H35)

def Rippen(D):
    if(D<2000): I34 = 15+4*800/1000*4
    else: I34 = 15+6*1700/1000*4+15+6*1900/1000*4
    if(D<2000): I35 = 15+4*400/1000*(5+2*15)
    else: I35 = 6*850/1000*(5+2*15)+15+6*950/1000*(5+2*15)
    return (I34+I35)

def Mabs(Bo):
    if(Bo!=0): return 80
    else: return 0

def Ment(di):
    return (30+15+math.pi*di/1000*(5+2*15))

#-------------------------------------

def Bh(D,L):
    if(L==1): return Bh_1(D)
    elif(L==1.5): return Bh1_5(D)
    elif(L==2): return Bh_2(D)
    else: return 0

def Bh_1(D):
    for i in const_bombe.length1m_time_dict:
        if(i==D): return const_bombe.length1m_time_dict[i]
    return 0
    
def Bh1_5(D):
    for i in const_bombe.length15m_time_dict:
        if(i==D): return const_bombe.length15m_time_dict[i]
    return 0

def Bh_2(D):
    for i in const_bombe.length2m_time_dict:
        if(i==D): return const_bombe.length2m_time_dict[i]
    return 0

#------------------------------------

def BB_Mat(h,D,hRA,N,di,Vs,Bo,kp):          # Berechnung Kosten Material (€)
    cost_list=[]
    cost_list.append(MMantel(h,D,kp))
    cost_list.append(MBoden(D,di,kp))
    cost_list.append(MFlansche(D,hRA,Vs,kp))
    cost_list.append(MPratzen(N,kp))
    cost_list.append(MHebeoesen(D,Bo,kp))
    cost_list.append(MHalteeisen(D,Bo,kp))
    cost_list.append(MRippen(D,di,kp))
    cost_list.append(M_RA(D,hRA))
    if(Vs=='j'): cost_list.append(M_VS(D))
    return (sum(cost_list))

def MMantel(h,D,kp):
    result = GMantel(h,D) * kp * 1.3
    return result

def MBoden(D,di,kp):
    result = GBoden(D,0) * kp *1.3
    return result

def MFlansche(D,hRA,Vs,kp):
    result = 3 * kp * GFlansche(D,hRA,Vs)
    return result

def MPratzen(N,kp):
    result = N*26*1.2*kp/1.95583
    return result

def MHebeoesen(D,Bo,kp):
    if(D<960): G15 = 4*100*100/1000**2*8*8
    elif(D<1550): G15 = 4*100*100/1000**2*8*8
    elif(D>1400 and Bo!=0): G15 = 0
    else: G15 = 100*100*4/1000**2*8*8
    result = G15 * 1.3 * kp
    return result

def MHalteeisen(D,Bo,kp):
    if(Bo!=0 and D<960.1): H16 = 4*100*250/1000**2*8*8
    elif(Bo!=0 and 960<D<2000): H16 = 4*100*250/1000**2+4*120*200/1000**2*8*8
    elif(Bo!=0 and D>2000): H16 = 6*100*250/1000**2+6*200*120/1000**2*8*8
    else: H16 = 0
    result = H16 * 1.3 * kp
    return result

def MRippen(D,di,kp):
    if(di<200): res1 = 4*200*150/1000**2*64
    elif(di<350): res1 = 4*350*150/1000**2*64
    elif(di<450): res1 = 4*300*200/1000**2*64
    elif(di<600): res1 = 4*500*200/1000**2*64
    else: res1 = 700*250*6/1000**2*80
    if(D>2000): res2 = 6*700*250/1000**2*80
    else: res2 = 0
    result = (res1 + res2) * 1.3 * kp
    return result

def M_RA(D,hr):
    J14 = math.pi*(D-200)/1000*hr/1000
    J15 = J14*36+math.pi/4*((D/1000)**2-((D-200)/1000)**2)*hr/1000*108*1.2+J14*1.3+6*hr*50/1000**2*2*8*2.3*1.3
    return J15

def M_VS(D):
    K13 = D**2/1000**2
    K14 = K13*38*1.3
    return K14

#---------------------------

def OB_Mat(h,D,hRA,N,di,Vs,Bo,KZ_Zn,KZ_SiAl):           #Berechnung Behälter Preis Oberfläche
    B54 = math.pi*D/1000*h/1000*2
    B55 = math.pi/4*((D+20)/1000)**2*2-math.pi/4*(di/1000)**2
    if(Vs=='j'): B56_1 = math.pi/4*(((D+200)/1000)**2-(D/1000)**2)*2
    else: B56_1 = 0
    if(hRA!=0): B56_2 = math.pi/4*((D/1000)**2-((D-200)/1000)**2)
    else: B56_2 = 0
    if(Vs=='n'): 
        if(D<960): B56_3 = 0
        elif(D<1700): B56_3 = math.pi/4*(((D+60)/1000)**2-(D/1000)**2)
        else: B56_3 = math.pi/4*(((D+200)/1000)**2-(D/1000)**2)
    else: B56_3 = 0
    B56 = (B56_1+B56_2+B56_3)*2
    if(D<960): B57 = 4*100*100/1000**2
    elif(D<1550): B57 = 4*100*100/1000**2
    elif(D>1400 and Bo!=0): B57 = 0
    else: B57 = 100*100*4/1000**2
    B57 *= 2
    if(D<960): B58 = 4*100*100/1000**2
    elif(D<1550): B58 = 4*100*100/1000**2
    elif(D>1400 and Bo!=0): B58 = 0
    else: B58 = 100*100*4/1000**2
    B58 *= 2
    if(di<200): B59_1 = 4*200*150/1000**2
    elif(di<350): B59_1 = 4*350*150/1000**2
    elif(di<450): B59_1 = 4*300*200/1000**2
    elif(di<600): B59_1 = 4*500*200/1000**2
    else: B59_1 = 700*250/1000**2*6
    if(D>2000): B59_2 = 6*700*250/1000**2
    else: B59_2 = 0
    B59 = (B59_1+B59_2)*2
    B60 = B54 + B55 + B56 + B57 + B58 + B59
    B61 = B60*const_material.KZ_Zn_SiAl_dict[KZ_Zn]
    if(KZ_SiAl<1 or KZ_SiAl>4): B62 = 0
    else: B62 = B60* const_material.KZ_Zn_SiAl_dict[KZ_SiAl]
    B63 = B61+B62
    return B63

#-----------------------------------

def Z_RA(D,hr):             #Zeit - RA
    if(hr>0): return((216+math.pi*D/1000*(5+15)+8*hr/1000*5+math.pi/4*(D**2-(D-200)**2)*hr/1000**3*40+math.pi*(D-200)*hr/1000**2*2.5+math.pi*D/1000*5+8*hr/1000*5)/60)
    else: return 0



# %%
def plt(t_plt):
    tk_plt = t_plt + 273.15
    p_return = (0.001019628104*tk_plt^2 -1.167702935*tk_plt +348.25138) * 10
    return p_return

def pruefen(p_pr,t_pr):
    if(p_pr>1000):raise Exception
    if(t_pr<=350): return 1
    if(590<t_pr<799,85): return 1
    if(plt(t_pr)<=p_pr): raise Exception
    else:
        if(t_pr>=799,85):raise Exception
    return 1

# %%
def ts(p_ts):
    if(p_ts>220.2): return -1
    p_ts1025 = (p_ts/10)**0.25
    AG11 = p_ts1025**2+p_ts1025*const_gas.Ni3+const_gas.Ni6
    AG12 = const_gas.Ni1* p_ts1025**2+const_gas.Ni4*p_ts1025+const_gas.Ni7
    AG13 = const_gas.Ni2* p_ts1025**2+const_gas.Ni5*p_ts1025+const_gas.Ni8
    AG14 = 2*AG13/(-AG12-(AG12**2-4*AG11*AG13)**0.5)
    AG15 = (((const_gas.Ni10+AG14)-((const_gas.Ni10+AG14)**2-4*(const_gas.Ni9+const_gas.Ni10*AG14))**0.5)/2)-273.15
    return AG15


def t_a(p_10,h_dta):
    h_2000 = h_dta/2000
    t_a_sum = 0
    for i in range(34):
        t_a_sum += const_gas.kna[i]*p_10**const_gas.kla[i]*(h_2000-2.1)**const_gas.gja[i]
    return(t_a_sum)

def t_b(p_10,h_dtb):
    h_2000 = h_dtb/2000
    t_b_sum = 0
    for i in range(38):
        t_b_sum += const_gas.knb[i]*p_10**const_gas.klb[i]*(h_2000-2.6)**const_gas.gjb[i]
    return(t_b_sum)

def t_c(p_10,h_dtc):
    h_2000 = h_dtc/2000
    t_c_sum = 0
    for i in range(23):
        t_c_sum += const_gas.knc[i]*(p_10+25)**const_gas.klc[i]*(h_2000-1,8)**const_gas.gjc[i]
    return(t_c_sum)

# %%
def int_pol(x1,x2,y1,y2,x_des):
    m = (y2-y1)/(x2-x1)
    y_des = (x_des - x1) * m + y1
    return y_des

def staerke_t(dict,t):
    kx_list=list(dict.keys())
    ky_list=list(dict.values())

    if(t<kx_list[0]): return 0
    if(t>kx_list[-1]): return 0
    for i in range(len(kx_list)-1):
        if(kx_list[i] <= t < kx_list[i+1]): return (int_pol(kx_list[i+1],kx_list[i],ky_list[i+1],ky_list[i],t))
    return 0

def t_Zyl_AD(D_Ro,Druck_p,K_Wert,Verschwaechung_v):
    if(K_Wert > 0): result = D_Ro * (Druck_p - 1) / (20 * K_Wert / 1.5 * Verschwaechung_v + (Druck_p - 1))
    else: result = 0
    return result

def t_ASME(D_Ro,Druck_p,K_Wert,Verschwaechung_v):
    result = 0
    if(K_Wert > 0): result = max(((Druck_p-1)/10*D_Ro/2/(K_Wert*Verschwaechung_v-0.6*(Druck_p-1)/10))  ,  ((Druck_p-1)/10*D_Ro/2/(K_Wert*1-0.6*(Druck_p-1)/10)*1.25))
    return result

def t_Platte_AD(D_Ro,Druck_p,K_Wert):
    if(K_Wert>0): return (0.45 * D_Ro * ((Druck_p - 1) * 1.5 / (10 * K_Wert)) ** 0.5)
    else: return 0

def t_Platte_Stufen_AD(D_Ro_1, D_Ro_2,Druck_p,K_Wert):
    if(K_Wert>0): return (0.45 * (D_Ro_2 - D_Ro_1) * ((Druck_p - 1) * 1.5 / (10 * K_Wert)) ** 0.5)
    else: return 0

def t_Platte_ASME(D_Ro,Druck_p,K_Wert):
    if(K_Wert>0): return (D_Ro * (0.33 * (Druck_p - 1) / 10 / K_Wert / 0.65) ** 0.5)
    else: return 0

def t_Platte_Stufen_ASME(D_Ro_1, D_Ro_2,Druck_p,K_Wert):
    if(K_Wert>0): return ((D_Ro_2 - D_Ro_1) / 2 * min([2.5, (3.4 - 2.4 * (D_Ro_2 - D_Ro_1) / 2 * 1 / (math.pi * (D_Ro_2 + D_Ro_1) / 2))]) * 0.33 * (Druck_p - 1) / K_Wert / 0.65)
    else: return 0

# %%
#Berechnung Spez. Enth. h_d
def h_d(p_hd,T_hd):
    p_hd10 = p_hd / 10
    AI12= 540 /(T_hd+273.15)
    AI17= 0
    for i in range(9):    #range(9)
        AI17 += const_gas.kno[i]*const_gas.gjo[i]*AI12**(const_gas.gjo[i]-1)
    for i in range(43):   #range(1,43)
        AI17 += const_gas.zni[i]*p_hd10**const_gas.kli[i]*const_gas.gji[i]*(AI12-0.5)**(const_gas.gji[i]-1)
    AI18 = AI17 * AI12
    return(AI18 * 0.461526 * (273.15 + T_hd))

#Berechnung t_Bereich
def t_Bereich(p_tb,h_dtb):
    p_tb10 = p_tb / 10
    AJ9 = 905.84278514723 - 0.67955786399241 * h_dtb + 0.12809002730136*10**-3 * h_dtb**2
    if(p_tb10>AJ9): temp = t_c(p_tb10,h_dtb)
    elif(p_tb10<4): temp = t_a(p_tb10,h_dtb)
    else: temp = t_b(p_tb10,h_dtb)
    t_Bereich = temp-273.15
    return t_Bereich


#Berechnung spez. Vol. v_d
def v_d(p_vd, t_vd):
    if(pruefen(p_vd,t_vd)): 1
    AH11 = (t_vd+273.15)/647.3
    AH12 = p_vd / 221.2
    AH13 = math.exp(const_gas.kbd*(1-AH11))
    AH14 = ((const_gas.TETA2-AH11)*const_gas.beta1+(AH11-const_gas.TETA1)*const_gas.beta2-const_gas.gL*(const_gas.TETA2-AH11)*(AH11-const_gas.TETA1))/(const_gas.TETA2-const_gas.TETA1)
    AH15 = const_gas.gid1*(AH11/AH12)
    AH16 = 1*AH12**0*(const_gas.gbd11*AH13**13+const_gas.gbd12*AH13**3) + 2*AH12**1*(const_gas.gbd21*AH13**18+const_gas.gbd22*AH13**2+const_gas.gbd23*AH13) + 3*AH12**2*(const_gas.gbd31*AH13**18+const_gas.gbd32*AH13**10) + 4*AH12**3*(const_gas.gbd41*AH13**25+const_gas.gbd42*AH13**14) + 5*AH12**6*(const_gas.gbd51*AH13**32+const_gas.gbd52*AH13**28+const_gas.gbd53*AH13**24)
    AH17 = (4*AH12**-5*(const_gas.gbd61*AH13**12+const_gas.gbd62*AH13**11))/(AH12**-4+const_gas.kbd61*AH13**14)**2 + (5*AH12**-6*(const_gas.gbd71*AH13**24+const_gas.gbd72*AH13**18))/(AH12**-5+const_gas.kbd71*AH13**19)**2 + (6*AH12**-7*(const_gas.gbd81*AH13**24+const_gas.gbd82*AH13**14))/(AH12**-6+(const_gas.kbd81*AH13**54+const_gas.kbd82*AH13**27))**2
    AH18_sum = const_gas.gbd90*AH13**0 + const_gas.gbd91*AH13**1 + const_gas.gbd92*AH13**2 + const_gas.gbd93*AH13**3 + const_gas.gbd94*AH13**4 + const_gas.gbd95*AH13**5 + const_gas.gbd96*AH13**6
    AH18 = AH18_sum * ((AH12/AH14)**10)*11
    AH19 = AH15 - AH16 - AH17 + AH18
    return(AH19*0.00317 )

# %%
def Pstufe(m,p,t,ppn,Dstufe,Hstufe,pp,h_steam):
    if(m==0 or p==0 or t==0 or Dstufe<=0): return 1
    else: H14 = Nloch(Dstufe,Hstufe)
    H15 = max ([0.01,(t+273)**0.5*m*0.0585/H14])
    H20 = ppn+H15   #H16
    H13 = max([h_steam,h_d(H20,ts(ppn))])
    
    #H19 = 0         #H17
    counter = 0
    while(1):    
        #H19 = H19+1     #H18
        H21 = v_d(H20,t_Bereich(H20,H13))
        H22 = m/0.8/ksi(t,ts(p),H20,ppn)/(2*H20*10**5/H21)**0.5/(math.pi/4*0.01**2)
        H20 = H20 + H15 #H23
        if((H22-H14)/H14<=0.01): return(H20)
        counter += 1
        if (counter > timeout_tries): raise     # Abbruch Schutz hinsichtlich unendlicher loops

def Nloch(Dstufe,Hstufe):
    L34 =math.pi*Dstufe
    if(Hstufe<750): L35 = int((Hstufe-30-10)/12.99+1)
    else: L35 = int((Hstufe-30-20-50)/12.99+1)
    L36 = math.pi*(Dstufe-4)-2
    if(L36<1540): L37 = int((L36-80)/15+1)
    elif(L36<3000): L37 = int((L36-110)/15+1)
    else: L37 = int((L36-190)/15+1)
    if(L36>1540): L38 = (int(L37/2)*L35-int(L35/2))*2
    else: L38 = L37*L35-int(L35/2)
    return L38


def p_plus(v,d_i,d,p_a,m,h):
    p_sum=p_a
    d_p=0
    c_ = (m*1000000/(math.pi*h))**2/2*0.0000055
    counter = 0
    while(d > d_i):                         #von Aussendurchmesser d bis Innendurchmesser di
        v = v * (1 - d_p / p_sum)          #spezifisches Volumen bei p_plus des letzen Layers mit Formel ideales Gas
        d_p = c_ * v / d ** 2                #Druckverlust des Layers
        p_sum = p_sum + d_p                 #Akkumulation Druckzunahme
        d= d - 2                            #Reduzierung Durchmesser 1 mm pro Layer = 2 mm Reduzierung Durchmesser
        counter += 1
        if (counter > timeout_tries): raise     # Abbruch Schutz hinsichtlich unendlicher loops
    return p_sum

def aw(pe,pa,sv):
    A8 = 1.3
    if(pa/pe<0.546): A9 = 0.752
    else: A9 = (1.3/(1.3-1)*(1-(pa/pe)**(0.3/1.3)))**0.5
    A10 = 0.97*A9*(2*pe*10**5*sv)**0.5
    return A10
    

def ksi(t_ksi,tsie,pp1,pp2):
    if(t_ksi>tsie):B10=1.3
    else:B10=1.135

    if((pp2/pp1)<0.5457+0*(2/(B10+1)**(B10/(B10-1)))): B11 = (B10/(B10+1))**0.5*(2/(B10+1))**(1/(B10-1))
    else: B11 = (B10/(B10-1))**0.5*((pp2/pp1)**(2/B10)-(pp2/pp1)**((B10+1)/B10))**0.5

    return B11

def t_u_func(N,Dia,h):
    if(Dia<490): Rand=100
    else: Rand=150
    L = math.pi * Dia - Rand #entspricht gelochtem Umfang
    if(h<=750): A = 100 - h
    else: A = 150 - h
    t_u = int(L / (2 * N) + ((L / (2 * N)) ** 2 - (A * L / N / 0.866))**0.5 - 1)
    h_hilf = ((N / L * t_u) - 1) * 0.866 * t_u
    if(h_hilf>750): h_hilf = h_hilf + 150
    else: h_hilf = h_hilf + 100
    counter = 0
    while(h<h_hilf):
        h_hilf = ((N / L * t_u) - 1) * 0.866 * t_u
        if(h_hilf>750): h_hilf = h_hilf + 150
        else: h_hilf = h_hilf + 100
        t_u = t_u - 1
        if(t_u<18): return 18
        counter += 1
        if (counter > timeout_tries): raise     # Abbruch Schutz hinsichtlich unendlicher loops
    return t_u

def Hent(D_,Anz,tu):
    D9 = math.pi*D_
    if(D9<490):D10=100
    else:D10=150
    D11=round((Anz/(D9-D10)*tu)-1)*0.866*tu
    if(D11>750): D12=D11+150
    else: D12=D11+100
    return D12

def MatER(ter,tdes,Ner,code):
    E9=max([ter,tdes])
    E10=0
    E11=0
    E12=0
    E13=0
    if(code=="D" and Ner<300):
        if(E9<450):E10=1
        elif(E9<530):E10=3
        elif(E9<570):E10=5
        else:pass
    if(code=="D" and Ner>=300):
        if(E9<480):E11=2
        elif(E9<530):E11=4
        elif(E9<570):E11=5
        else:pass 
    if(code=="A" and Ner<300):
        if(E9<450):E12=10
        elif(E9<530):E12=12
        elif(E9<570):E12=14
        else:pass
    if(code=="A" and Ner>=300):
        if(E9<480):E13=11
        elif(E9<530):E13=13
        elif(E9<570):E13=15
        else:pass
    E14=E10+E11+E12+E13
    return E14

def h_gestrick(h_input):
    if(h_input<=230):
        if(h_input<=110): return 100
        elif(h_input<=140): return 130
        elif(h_input<=170): return 160
        elif(h_input<=200): return 190
        else: return 220
    else: return (round(h_input/50)*50)

# Berechnung Höhe Lochfeld (einige "ungenutzte" Nebenloops/Iterationen der Excelfile-Variante gekürzt)
def H_total(h_min,h_max,D_Ro_1,D_Ro_2,D_Ro_3,D_Ro_4,D_Ro_5,D_Ro_6,flow,h1,p1,p_1,t1,ts1,t_1,v_1,D_B_1,tu):
    if(h_min<100): return((h_max+h_min)/2)
    h_Ent = h_gestrick(h_min)
    
    counter = 0
    while(1):
        if(h_Ent>h_max): return 10000
        p_help = p_plus(v_d(p_atm,t_1),D_Ro_1,D_Ro_2,p_atm,get_input.flow,h_Ent)
        Anz1 = round(get_input.flow/(0.7 * ksi(t1,ts1,p_1,p_help)*(2*p_1*10**5/v_1)**0.5)/(math.pi/4*(D_B_1/1000)**2))
        Hent_ = Hent(D_Ro_1,Anz1,tu)
        if(Hent_<h_Ent): return h_Ent
        if(Anz1<100 and Hent_>h_max): return Hent_
        if (h_Ent<230): h_Ent += 30
        else: h_Ent += 50
        counter += 1
        if (counter > timeout_tries): raise     # Abbruch Schutz hinsichtlich unendlicher loops



# %%
# Behälterbau - Gewicht
def G_SD(h,D,hRA,N,di,VS,Bo):
    G_list = []
    G_list.append(GMantel(h,D))
    G_list.append(GBoden(D,di))
    G_list.append(GFlansche(D,hRA,VS))
    G_list.append(GHebeösen(D,Bo))
    G_list.append(GHalteeisen(D,Bo))
    G_list.append(GRippen(D))
    G_list.append(GRA(D,hRA))
    return (sum(G_list))

def GMantel(h,D):
    g_temp = 0
    if(D<=1550): g_temp = 4
    elif(1550<D<=2000): g_temp = 6
    elif(2000<D<=3000): g_temp = 6
    elif(3000<D<=5000): g_temp = 8
    else: g_temp = 0
    return(g_temp*1.2*math.pi*D/1000*h/1000*8)

def GBoden(D,di):
    g_temp = 0
    if(D<=1550): g_temp = 8
    elif(1550<D<=2000): g_temp = 10
    elif(2000<D<=3000): g_temp = 12
    elif(3000<D<=5000): g_temp = 15
    else: g_temp = 0
    return(g_temp*math.pi/4*((D+20)/1000)**2*8)

def GFlansche(D,hRA,VS):
    g_temp = 0
    if(D<=2000): g_temp = 80
    elif(2000<D<=3000): g_temp = 100
    elif(3000<D<=5000): g_temp = 150
    else: g_temp = 0
    if(hRA!=0): g_temp2 = math.pi/4*((D/1000)**2-((D-g_temp)/1000)**2)*8*8
    else: g_temp2 = math.pi/4*(((D+g_temp)/1000)**2-(D/1000)**2)*8*8
    if(VS!=0): g_temp2 *= 2
    return g_temp2

def GHebeösen(D,Bo):
    if(D<960): return(4*100*100/1000**2*8*8)
    elif(D<1550): return(4*100*100/1000**2*8*8)
    elif(D>1400 and Bo!=0): return(0)
    else: return(100*100*4/1000**2*8*8)

def GHalteeisen(D,Bo):
    if(Bo!=0 and D<960.1): return(4*100*250/1000**2*8*8)
    elif(Bo!=0 and D>960 and D<2000): return(4*100*250/1000**2+4*120*200/1000**2*8*8)
    elif(Bo!=0 and D>2000): return(6*100*250/1000**2+6*200*120/1000**2*8*8)
    else: return 0

def GRippen(D):
    if(D<2000): return(4*150*150/1000**2*8*8)
    else: return(6*500*250/1000**2*8*8+6*700*250/1000**2*8*8)

def GRA(D,hr):
    g_temp = math.pi*(D-200)/1000*hr/1000
    return(g_temp*1.5*8+math.pi/4*((D/1000)**2-((D-200)/1000)**2)*hr/1000*90+6*hr*50/1000**2*2*8)

#-----------------------

def GAbs(D,L):
    if(L==0): return 0
    elif(L==1): return G_1(D)
    elif(L==1.5): return G1_5(D)
    elif(L==2): return G_2(D)
    else: return 0

def G_1(D):
    for i in const_bombe.length1m_weight_dict:
        if(i==D): return const_bombe.length1m_weight_dict[i]
    return 0
    
def G1_5(D):
    for i in const_bombe.length15m_weight_dict:
        if(i==D): return const_bombe.length15m_weight_dict[i]
    return 0

def G_2(D):
    for i in const_bombe.length2m_weight_dict:
        if(i==D): return const_bombe.length2m_weight_dict[i]
    return 0

#-------------------------

def BDM(D,L):
    if(L==0): return 0
    elif(L==1): return BK_1(D)
    elif(L==1.5): return BK1_5(D)
    elif(L==2): return BK_2(D)
    else: return 0

def BK_1(D):
    for i in const_bombe.length1m_matcost_dict:
        if(i==D): return const_bombe.length1m_matcost_dict[i]
    return 0
    
def BK1_5(D):
    for i in const_bombe.length15m_matcost_dict:
        if(i==D): return const_bombe.length15m_matcost_dict[i]
    return 0

def BK_2(D):
    for i in const_bombe.length2m_matcost_dict:
        if(i==D): return const_bombe.length2m_matcost_dict[i]
    return 0

# %%
def De_gestrick(f,tm,vm,wm,dm,sigma,dvbw,struktur,kappa):
    F31 = (kappa*461*(273.15+tm))**0.5
    F32 = wm*1/vm*dvbw
    F33 = 1.35*kappa*1000*sigma/2/math.pi/f*vm
    F34 = (complex(kappa-1,0)/complex(1,-F33)).real
    F35 = (complex(kappa-1,0)/complex(1,-F33)).imag
    F36 = 1+F34
    F37 = F35
    F38 = (cmath.sqrt(complex(1 , -F32*sigma*vm/struktur/2/math.pi/f))).real
    F39 = (cmath.sqrt(complex(1 , -F32*sigma*vm/struktur/2/math.pi/f))).imag
    F40 = (complex(struktur*kappa,0)/complex(F36,F37)).real
    F41 = (complex(struktur*kappa,0)/complex(F36,F37)).imag
    F42 = (cmath.sqrt(complex(F40,F41))).real
    F43 = (cmath.sqrt(complex(F40,F41))).imag
    F44 = (complex(0,2*math.pi*f/F31)*complex(F42,F43)).real
    F45 = (complex(0,2*math.pi*f/F31)*complex(F42,F43)).imag
    F46 = (complex(F44,F45)*complex(F38,F39)).real
    F47 = -8.68*dm*F46
    return F47

def SG_Bo(t,w,A):          # Strömungsrauschen Bo
    C11 = v_d(1,t)
    C12 = 60*math.log10(w)+10*math.log10(A)-25*math.log10((t+273.15)/273.15)+8.6*math.log10(1/1.28/C11)
    return C12

# %%
class daempfer():

    def __init__(self,Stufenanzahl,Gestrick_list) -> None:
        # Aufbau Daempfer:
        self.Stufen = Stufenanzahl
        self.Gestrick_list = Gestrick_list

        # Erstellen/Instanzieren der Stufen & Gestrick
        self.realSt_list=[]
        self.St_list=[]
        self.St1=Stufe(1,False)
        self.St1_Gestr=Stufe('1_Gestr',True)
        self.St2=Stufe(2,False)
        self.St2_Gestr=Stufe('2_Gestr',True)
        self.St3=Stufe(3,False)
        self.St3_Gestr=Stufe('3_Gestr',True)
        self.St_atm=Stufe('atm',False)
        
        # Aufbau des jeweiligen Typs in St_list eintragen:
        self.St_list.append(self.St1)
        self.realSt_list.append(self.St1)
        if(self.Gestrick_list[0]==1):
            self.St_list.append(self.St1_Gestr)
        if(self.Stufen>=2):
            self.St_list.append(self.St2)
            self.realSt_list.append(self.St2)
            if(self.Gestrick_list[1]==1):               
                self.St_list.append(self.St2_Gestr)
        if(self.Stufen>=3):            
            self.St_list.append(self.St3)
            self.realSt_list.append(self.St3)
            if(self.Gestrick_list[2]==1):                
                self.St_list.append(self.St3_Gestr)
        self.St_list.append(self.St_atm)
        self.Typ_name = len(self.St_list)-1

        # Ausfüllen der jeweiligen Stufendurchmesser
        self.St1.D_Ro = get_input.d_inl
        if(self.Stufen >=2): self.St2.D_Ro = dzwei(get_input.d_inl)
        if(self.Stufen >=3): self.St3.D_Ro = ddrei(get_input.d_inl)
        if(len(self.Gestrick_list)>=2 and self.Gestrick_list[0] == 1): self.St1_Gestr.D_Ro = self.St2.D_Ro -8      #Abzug 2*4mm Wandstärke für Gestrickdurchmesser
        if(len(self.Gestrick_list)>=3 and self.Gestrick_list[1] == 1): self.St2_Gestr.D_Ro = self.St3.D_Ro -8      #Abzug 2*4mm Wandstärke für Gestrickdurchmesser
        if(self.Gestrick_list[-1]==1):      # Finden der "letzten" Stufe (vor Atm) und dort Gestrick anders hinzufügen, da andere Beschränkungen
            self.last_St = self.St_list[-2]
            self.last_St.D_Ro = self.St_list[-3].D_Ro +100

        # Befüllung mit "fixed Parameter" (notwendig für Druckberechnung)
        self.St1.p = get_input.p_inl
        self.St1.h_sd = get_input.h_sd_St1
        self.St1.t = get_input.t_St1
        self.St1.v=v_d(self.St1.p,self.St1.t)
        self.St_atm.calc_St_atm(self)           # Berechnen der "äußersten" Stufe bei Atmosphäre
        self.St1.w = round(get_input.flow*self.St1.v/(math.pi/4*((get_input.d_inl-2*get_input.d_wall)/1000)**2))
        self.St1.D_B = 12

        self.h_min = int(get_input.V_b/(math.pi*self.last_St.D_Ro/1000*w_max)*1000)
        self.h_max = int(get_input.V_b/(math.pi*self.last_St.D_Ro/1000*w_min)*1000)
        self.H_ges = h_gestrick(H_total(self.h_min,self.h_max,self.St1.D_Ro,self.St1_Gestr.D_Ro,self.St2.D_Ro,self.St2_Gestr.D_Ro,self.St3.D_Ro,self.St3_Gestr.D_Ro,get_input.flow,get_input.h1,get_input.p1,self.St1.p,get_input.t1,get_input.ts1,self.St1.t,self.St1.v,self.St1.D_B,18))

        # Berechnen der Drücke in den Stufen und der zugehörigen Parameter t, h_sd, v, w:
        for i in range(len(self.St_list)-2):        # Alle Drücke berechnen außer dem ersten und letzten, da diese bekannt/gegeben sind
            if(self.St_list[-i-2].is_Gestrick==True):
                self.St_list[-i-2].p = p_plus(self.St_list[-i-1].v,self.St_list[-i-3].D_Ro,self.St_list[-i-2].D_Ro,self.St_list[-i-1].p,get_input.flow,self.H_ges)
            else:
                self.St_list[-i-2].p = Pstufe(get_input.flow,get_input.p1,get_input.t1,self.St_list[-i-1].p,self.St_list[-i-1].D_Ro,self.H_ges,get_input.p_inl,get_input.h1)
            self.St_list[-i-2].h_sd = h_d(self.St_list[-i-2].p,ts(self.St_list[-i-2].p))
            if(self.St_list[-i-2].h_sd>get_input.h1): self.St_list[-i-2].t = ts(self.St_list[-i-2].p)
            else: self.St_list[-i-2].t = t_Bereich(self.St_list[-i-2].p,get_input.h1)
            self.St_list[-i-2].v = v_d(self.St_list[-i-2].p,self.St_list[-i-2].t)
            if(self.St_list[-i-2].is_Gestrick==True):
                self.St_list[-i-2].w = get_input.V_b/(self.St_list[-i-2].D_Ro/1000*math.pi*self.H_ges/1000)
            else:
                self.St_list[-i-2].w = aw(self.St_list[-i-2].p,self.St_list[-i-1].p,self.St_list[-i-2].v)

        for i in range(len(self.realSt_list)):
            if(i==0): self.realSt_list[i].D_B = 12
            else: self.realSt_list[i].D_B = 10

        for i in range(len(self.St_list)-1):
            if(self.St_list[i].is_Gestrick==False):         # Wenn es kein Gestrick sondern eine reale Stufe ist --> Abschwächungsfaktor & Anzahl berechnen
                self.St_list[i].f = self.St_list[i+1].p/self.St_list[i].p       # Abschwächung

                # Anzahl Löcher
                if(i==0 and self.St_list[i+1].is_Gestrick==True): self.St_list[i].Anz = round(get_input.flow/(a_*ksi(get_input.t1,get_input.ts1,self.St_list[i].p,self.St_list[i+1].p)*(2*self.St_list[i].p*10**5/self.St_list[i].v)**0.5)/(math.pi/4*(self.St_list[i].D_B/1000)**2))    # Auf die erste Stufe folgt Gestrick ( Verwenden von 'a_=0,7')
                elif(i==0 and self.St_list[i+1].is_Gestrick==False): self.St_list[i].Anz = round(get_input.flow/(a_stufe*ksi(get_input.t1,get_input.ts1,self.St_list[i].p,self.St_list[i+1].p)*(2*self.St_list[i].p*10**5/self.St_list[i].v)**0.5)/(math.pi/4*(self.St_list[i].D_B/1000)**2))        # Auf die erste Stufe folgt KEIN Gestrick ( Verwenden von 'a_stufe=0,8')
                else: self.St_list[i].Anz = Nloch(self.St_list[i].D_Ro,self.H_ges)      # Berechnung der Lochanzahl für Stufen 2/3
                
        for i in range(len(self.realSt_list)):    
            if(i==0): self.realSt_list[i].t_u = t_u_func(self.realSt_list[i].Anz,self.realSt_list[i].D_Ro,self.H_ges)
            else: self.realSt_list[i].t_u = 15
            self.realSt_list[i].t_l=int(self.realSt_list[i].t_u*0.866)
            if (i==0): self.realSt_list[i].H=Hent(self.realSt_list[i].D_Ro,self.realSt_list[i].Anz,self.realSt_list[i].t_u)

        self.St1.KZ = MatER(self.St1.t,max([get_input.t_design,self.St1.t]),self.St1.Anz,code)          # 1. Kennzahl festlegen
        for i in self.St_list[1:-1]:          # 1. Kennzahl wird in der Zeile drüber bestimmt, Atm-Stufe hat keine KZ, daher [1:-1]
            if(i.is_Gestrick==True): i.KZ = 13          # Gestrick hat jetzt Kennzahl 13 (im Gegensatz zu Excelfile mit ehemals 9)
            else: i.KZ = const_material.KZ_dict[self.St1.KZ]

        self.Kopfpl_KZ=const_material.KZ_dict[self.St1.KZ]
        self.Ringpl_KZ=const_material.KZ_dict[self.St1.KZ]

        for i in range(len(self.realSt_list)):
            self.realSt_list[i].Mat=const_material.Mat_list[self.realSt_list[i].KZ-1]
            if(i==0): self.realSt_list[i].gew = get_input.d_wall

            if(self.realSt_list[i].KZ<=10): v_calc=2*(self.realSt_list[i].t_u-self.realSt_list[i].D_B)/(1.75*self.realSt_list[i].t_u)
            else: v_calc=((1/math.cos(30*math.pi/180))**2+1-(1/math.cos(30*math.pi/180))/(self.realSt_list[i].t_u/self.realSt_list[i].D_B)*(3+(1/math.cos(30*math.pi/180))**2)**0.5)/(0.015+0.005*(1/math.cos(30*math.pi/180))**2)/100
            self.realSt_list[i].verschw=v_calc
            
        self.Stufen_LwA_total_list = None       # Summenpegel der Schallintensität nach Durchlaufen aller Stufen & Gestrick (wird später gesondert berechnet)

        # Erstellen/Instanzieren der verschieden Bauweisen
        self.Bauweise_list = []
        self.A=Bauweise('A',self)
        self.Bauweise_list.append(self.A)
        self.B=Bauweise('B',self)
        self.Bauweise_list.append(self.B)
        self.C=Bauweise('C',self)
        self.Bauweise_list.append(self.C)
        self.D=Bauweise('D',self)
        self.Bauweise_list.append(self.D)
        self.E=Bauweise('E',self)
        self.Bauweise_list.append(self.E)
        self.F=Bauweise('F',self)
        self.Bauweise_list.append(self.F)
        #self.Bauweise_list = [self.A,self.B,self.C,self.D,self.E,self.F]
    
    def get_weight_sum(self,Typ):
        return Typ.weight_sum

    def d_max_sum(self):        # Bestimmung Maximum & Summe der Durchmesser über alle Stufen
        self.d_max = max([self.St1.D_Ro,self.St2.D_Ro,self.St3.D_Ro,self.St1_Gestr.D_Ro,self.St2_Gestr.D_Ro,self.St3_Gestr.D_Ro,])
        self.d_sum = self.St1.D_Ro+self.St2.D_Ro+self.St3.D_Ro+self.St1_Gestr.D_Ro+self.St2_Gestr.D_Ro+self.St3_Gestr.D_Ro

    def calc_diam(self,Typ):        # Berechnung aller Durchmesser der verschiedenen Bautypen
        self.A.calc_diam_(Typ)
        self.B.calc_diam_(Typ)
        self.C.calc_diam_(Typ)
        self.D.calc_diam_(Typ)
        self.E.calc_diam_(Typ)
        self.F.calc_diam_(Typ)
    
    def calc_height(self):      # Berechnung aller Höhen der verschiedenen Bautypen
        self.A.calc_height_()
        self.B.calc_height_()
        self.C.calc_height_()
        self.D.calc_height_()
        self.E.calc_height_()
        self.F.calc_height_()

    def calc_weight(self):      # Berechnung aller Gewichte der verschiedenen Bautypen
        self.A.calc_weight_()
        self.B.calc_weight_()
        self.C.calc_weight_()
        self.D.calc_weight_()
        self.E.calc_weight_()
        self.F.calc_weight_()

    # Berechnung der Staerkenwerte des Typs
    def calc_staerke(self):
        for i in range(len(self.St_list)-1):
            if(self.St_list[i].is_Gestrick==False):
                p_Stufe = self.St_list[i].p
                if(i==0): p_Stufe = max([get_input.p_d,p_Stufe])

                self.St_list[i].staerke_list=[]
                self.St_list[i].staerke_zyl=[]
                
                for j in range(len(const_festigkeit.Mat_name_dict_list)):
                    staerke_temp = staerke_t(const_festigkeit.Mat_name_dict_list[j],get_input.t_d)
                    if(j>=6): staerke_temp = staerke_temp/14.5*10**5/1000
                    self.St_list[i].staerke_list.append(staerke_temp)

                    st_zyl=t_Zyl_AD(self.St_list[i].D_Ro,p_Stufe,staerke_temp,self.St_list[i].verschw)+2+2*corr_allow
                    if(j>=6): st_zyl = t_ASME(self.St_list[i].D_Ro,p_Stufe,staerke_temp,self.St_list[i].verschw)+2+2*corr_allow
                    self.St_list[i].staerke_zyl.append(st_zyl)
                self.St_list[i].s_Zy = self.St_list[i].staerke_zyl[self.St_list[i].KZ-1]
                if(i>0): self.St_list[i].gew = math.ceil(self.St_list[i].s_Zy/2)*2      # 1. Stufe hat "fixes" 'gew' durch Inputparameter und wird daher übersprungen
            else: pass  # keine Berechnung für Gestrick

        self.Kopfpl_list=[]
        self.Ringpl_list=[]
        for i in range(len(const_festigkeit.Mat_name_dict_list)):
            staerke_temp = staerke_t(const_festigkeit.Mat_name_dict_list[i],get_input.t_d)
            if(i<6): Kopfpl_temp = t_Platte_AD(self.St1.D_Ro,get_input.p_d,staerke_temp)+2+2*corr_allow
            else: Kopfpl_temp = t_Platte_ASME(self.St1.D_Ro,get_input.p_d,staerke_temp)+2+2*corr_allow
            self.Kopfpl_list.append(Kopfpl_temp)

            if(i<6): Ringpl_temp = t_Platte_Stufen_AD(self.St1.D_Ro,self.St_list[1].D_Ro,self.St_list[1].p,staerke_temp)+2+2*corr_allow
            else: Ringpl_temp = t_Platte_Stufen_ASME(self.St1.D_Ro,self.St_list[1].D_Ro,self.St_list[1].p,staerke_temp)+2+2*corr_allow
            self.Ringpl_list.append(Ringpl_temp)

        Kopfpl_d = self.Kopfpl_list[self.St1.KZ-1]
        Ringpl_d = self.Ringpl_list[self.St1.KZ-1]
        self.Kopfpl_d_chosen = math.ceil(max([Kopfpl_d,20])/2)*2        # Dicke RKopflatte auf sinnvolle mm-Stärke runden (und wenigstens 20mm)
        self.Ringpl_d_chosen = math.ceil(max([Ringpl_d,10])/2)*2          # Dicke Ringplatte auf sinnvolle mm-Stärke runden (und wenigstens 10mm)

    # Berechnung Preis/Gewicht der jeweiligen Stufen:
    def calc_costweight(self):
        self.mat_naming_list=['Kopfpl','Ringpl']
        self.mat_prices_list=[const_material.Mat_prices_list[self.Kopfpl_KZ-1],const_material.Mat_prices_list[self.Ringpl_KZ-1]]
        for i in self.St_list[:-1]:
            self.mat_naming_list.append(i.St_index)
            self.mat_prices_list.append(const_material.Mat_prices_list[i.KZ-1])
        
        # Berechnung Gewicht der jew. "Stufe"
        self.mat_weight_list=[
            math.pi/4*(self.d_max+20)**2/1000**2*self.Kopfpl_d_chosen*7.85,                     # Gewicht Kopfplatte
            math.pi/4*((self.d_max+20)**2-(self.St1.D_Ro+20)**2)/1000**2*self.Ringpl_d_chosen*7.85      # Gewicht Ringplatte
        ]
        for i in range(len(self.St_list)-1):     # über alle Stufen/Gestrick loopen (ohne St_atm)
            if(i==0): self.mat_weight_list.append(math.pi*self.St_list[i].D_Ro*(self.H_ges+400)/1000**2*self.St_list[i].gew*7.85)     # Gewicht Stufe 1 (Aufschlag +400 auf H_ges)
            elif(self.St_list[i].is_Gestrick==False): self.mat_weight_list.append(math.pi*self.St_list[i].D_Ro*(self.H_ges)/1000**2*self.St_list[i].gew*7.85)   # Gewicht Stufe 2/3
            else: self.mat_weight_list.append((self.St_list[i].D_Ro**2-self.St_list[i-1].D_Ro**2)*0.533*math.pi/4*self.H_ges/952800)        # Gewicht eines Gestricks

        # Berechnung Kosten der jew. "Stufe"
        self.mat_cost_list=[
            (self.d_max+20)**2/1000**2*self.Kopfpl_d_chosen*7.85*1.5*self.mat_prices_list[0],       # Material-Kosten Kopfplatte
            (self.d_max+20)**2/1000**2*self.Ringpl_d_chosen*7.85*1.5*self.mat_prices_list[1]                # Material-Kosten Ringplatte
        ]
        for i in range(len(self.St_list)-1):     # über alle Stufen/Gestrick loopen (ohne St_atm)
            if(self.St_list[i].is_Gestrick==False): self.mat_cost_list.append(self.mat_weight_list[i+2]*1.5*self.mat_prices_list[i+2])      # Material-Kosten einer Stufe
            else: self.mat_cost_list.append(self.mat_weight_list[i+2]*self.mat_prices_list[i+2])        # Material-Kosten eines Gestricks

        if(self.Kopfpl_d_chosen>30): self.mat_cost_list[1] *= 2             # ausgelagerte if-Bedingung des Excel-files (Extrakosten bei Kopfplatte_d > 30 für Ringplatte)
        if(PED): self.mat_cost_list.append(PED_cost)                        # potentieller Kostenzusatz für TÜV
        self.OF_cost = (2*math.pi/4*(self.d_max+20)**2/1000**2+math.pi*(self.d_max)*self.H_ges/1000**2+math.pi*self.St1.D_Ro/1000*0.5)*30          # Oberflächen-Kosten
        self.mat_cost_list.append(self.OF_cost)

        # Berechnung Arbeitsaufwand in Minuten für jew. "Stufe"
        self.mat_work_list=[
            15+math.pi*((self.d_max+20)/1000)*8,                # Arbeitsaufwand Kopfplatte (min)
            15+math.pi*((self.d_max/1000+0.02)*2+math.pi*(self.St1.D_Ro/1000))*6        # Arbeitsaufwand Ringplatte (min)
        ]
        for i in range(len(self.St_list)-1):     # über alle Stufen/Gestrick loopen (ohne St_atm)
            if(i==0): self.mat_work_list.append(15+(2*(self.H_ges+400)/1000+2*math.pi*(self.St_list[i].D_Ro-self.St_list[i].gew)/1000)*4+5+(2*(self.H_ges+400)/1000+2*math.pi*(self.St_list[i].D_Ro-self.St_list[i].gew)/1000)*2.5+15+15+(self.H_ges+400)/1000*20+25+(math.pi*(self.St_list[i].D_Ro-self.St_list[i].gew)/1000)*20,)        # Arbeitsaufwand Stufe 1 (Aufschlag +400 auf H_ges & andere kleine Formelabweichungen) (min)
            elif(self.St_list[i].is_Gestrick==False): self.mat_work_list.append(15+(2*(self.H_ges)/1000+2*math.pi*(self.St_list[i].D_Ro-self.St_list[i].gew)/1000)*4+5+(2*(self.H_ges)/1000+2*math.pi*(self.St_list[i].D_Ro-self.St_list[i].gew-2)/1000)*2.5+15+15+(self.H_ges)/1000*20)    # Arbeitsaufwand Stufen 2/3 (min)
            else: self.mat_work_list.append(30+(self.St_list[i].D_Ro-self.St_list[i-1].D_Ro)/2/1.25*0.7,) # Arbeitsaufwand Gestrick (min)
        
        self.mat_work_list[-1] += 30             # letzte Gestrickstufe dauert 30min länger (ausgelagerte if-Bedingung) (womöglich 30 min Puffer allgemein?)
        self.mat_work_list.append(15+math.pi*40/1000*(self.d_sum))   # Berechnung Montagekosten "Rohr-Durchmesser"

        self.weight_sum = sum(self.mat_weight_list)             # Gewicht aufsummiert
        self.cost_sum = sum(self.mat_cost_list)                 # Kosten aufsummiert (ohne Arbeit)
        self.work_sum = sum(self.mat_work_list)/60              # Arbeitsaufwand aufsummiert in Stunden umgerechnet

        self.cost = self.cost_sum + self.work_sum*Stundensatz           # Gesamtkosten für Material und Arbeit
        self.cost_per_weight = round(self.cost/self.weight_sum)         # gemittelte Material-Kosten in 1€/kg

    # Berechnung des Schalls in den Stufen
    def calc_sound_Stufen(self):       
        # Berechnung Strömungsgeräusch:
        self.area_entspanner = math.pi*self.d_max/1000*self.H_ges/1000
        self.L_flow = 20*math.log10(get_input.flow*get_input.c_**2)
        self.L_area = -10*math.log10(self.area_entspanner)
        self.L_enth = 10*math.log10((1.3*10**-3)**2*10**12/(get_input.k_*101300*get_input.c_))
        self.L_total = self.L_flow + self.L_area + self.L_enth
        self.L_Okt = -10*math.log10(8)

        # feste Listen für Pegelberechnung:
        LwA_general_list=[]
        for i in range(len(const_oktspektrum.Okt_Freq_Spektrum_list)):
            LwA_general_list.append(LWAOkt(const_oktspektrum.Okt_Freq_Spektrum_list[i],1,1,1/get_input.v1,1/get_input.v_St1,get_input.k_,(get_input.t1+273),get_input.p1,get_input.p_inl,(get_input.d_inl-2*get_input.d_wall)/1000,get_input.flow,461) - const_oktspektrum.Korr_Term_Okt_Freq_Spektrum_list[i])

        # Berechnung Schallpegel für Stufen&Gestrick:
        for j in range(len(self.St_list)-1):
            self.St_list[j].Daempfung_list=[0,0,0,0,0,0,0,0]
            self.St_list[j].Rauschen_summe = 85+10*math.log10(get_input.flow*(1.31*461*(get_input.t_St1+273)))-10*math.log10(1+6*(self.St_list[j+1].p/(self.St_list[j].p-self.St_list[j+1].p))**2.5)

            if(j==0): self.St_list[j].LwA_total_list = LwA_general_list         # Initialisierungsliste der Schleife
            else: self.St_list[j].LwA_total_list = self.St_list[j-1].LwA_total_list         # Übernahme des vorigen Schall-Ergebnisses
            for i in range(len(const_oktspektrum.Okt_Freq_Spektrum_list)):
                if(self.St_list[j].is_Gestrick==False):
                    self.St_list[j].Daempfung_list[i] = (-10*math.log10(1+15/(1+1.5*(self.St_list[j+1].p/(self.St_list[j].p-self.St_list[j+1].p))**0.5)))       # ein Dämpfungswert nur abhängig von den anliegenden Drücken
                    self.St_list[j].Daempfung_LwA_list[i] = (self.St_list[j].LwA_total_list[i] + self.St_list[j].Daempfung_list[i])
                    self.St_list[j].Rauschen_LwA_list[i] = (self.St_list[j].Rauschen_summe + const_oktspektrum.Rauschen_Gestrick_DeltaL_list[i] + const_oktspektrum.Korr_Term_VDI_list[i])
                    self.St_list[j].LwA_total_list[i] = (10*math.log10(10**(self.St_list[j].Daempfung_LwA_list[i]/10)+10**(self.St_list[j].Rauschen_LwA_list[i]/10)))
                if(self.St_list[j].is_Gestrick==True):
                    self.St_list[j].Daempfung_list[i] = De_gestrick(const_oktspektrum.Okt_Freq_Spektrum_list[i],self.St_list[j].t,self.St_list[j].v,get_input.flow*self.St_list[j].v/(math.pi*self.St_list[j].D_Ro*self.H_ges/1000**2),(self.St_list[j].D_Ro-self.St_list[j-1].D_Ro)/2000,0.89,550,1,1.3)
                    self.St_list[j].Daempfung_LwA_list[i] = self.St_list[j].Daempfung_list[i] + self.St_list[j].LwA_total_list[i]
                    self.St_list[j].Rauschen_LwA_list[i] = self.L_total + self.L_Okt + const_oktspektrum.Rauschen_Gestrick_DeltaL_list[i]
                    self.St_list[j].LwA_total_list[i] = 10*math.log10(10**(self.St_list[j].Daempfung_LwA_list[i]/10)+10**(self.St_list[j].Rauschen_LwA_list[i]/10))
            #print(self.St_list[j].LwA_total_list)
            self.Stufen_LwA_total_list = self.St_list[j].LwA_total_list
        #print('---')            
        return self.St_list[j].LwA_total_list



# %%
class Stufe():

    def __init__(self,index,Gestrick) -> None:
        self.St_index = index           # Stufenindex/-name (Stufennummer & Gestrick? als String)
        self.is_Gestrick = Gestrick     # Ist diese Stufe Gestrick oder nicht?

        self.D_Ro = 0       # Durchmesser Rohe
        self.p=None         # Druck in jeweiliger Stufe
        self.f=None         # Abschwächungsfaktor zur nächsten Stufe
        self.t=None         # Temperatur in jeweiliger Stufe
        self.h_sd=None      # Enthalpie
        self.v=None         # spez. Volumen
        self.Anz=None       # Anzahl Löcher in Stufe
        self.D_B=None       # Durchmesser der Bohrung/Löcher
        self.t_u=None       # Lochaverteilung in Umfang Richtung
        self.t_l=None       # Lochaverteilung in Längen Richtung
        self.verschw=None   # Verschwächungsgrad Materialwand
        self.w=None         # Geschwindigkeit (vom Massenstrom)
        self.H=None         # Höhe Lochfeld (Anteil gelochter Flächenlänge)
        self.KZ=None        # Kennzahl Material (in Tabelle hinterlegt bzgl. Temperatur)
        self.Mat=None       # "Ausgabe" ob Rohr oder Blech (TBD oder Gestrick)
        self.s_Zy=None      # berechnete Dicke Material
        self.gew=None       # gewählte Dicke Material (=aufrunden)

        self.Daempfung_list=[0,0,0,0,0,0,0,0]
        self.Daempfung_LwA_list=[0,0,0,0,0,0,0,0]
        self.Rauschen_LwA_list = [0,0,0,0,0,0,0,0]
        self.LwA_total_list = [0,0,0,0,0,0,0,0]

    def calc_St_atm(self,Typ):
        Typ.St_atm.p=p_atm

        Typ.St_atm.h_sd=h_d(Typ.St_atm.p,ts(Typ.St_atm.p))

        if(Typ.St_atm.h_sd>get_input.h1): Typ.St_atm.t=ts(Typ.St_atm.p)
        else:Typ.St_atm.t=t_Bereich(Typ.St_atm.p,get_input.h1)

        Typ.St_atm.v=v_d(Typ.St_atm.p,Typ.St_atm.t)

# %%
class Bauweise():                   # Repräsentation der Tabellen A_i-F_i
    def __init__(self,Bautyp,Typ) -> None:
        self.Bautyp = Bautyp        # jeweiliger Bautyp A-F bei Initialisierung festgelegt
        self.Typ = Typ              # jeweiliger "Mutter"-Typ hinsichtlich Stufen&Gestrick
        self.meet_sound_requirements = None     # spätere Variable zum Nachschauen, ob die Schalldämpfungsziele erreicht werden, mit dem jeweiligen Bautyp

        self.t_e = get_input.t_e    # fixed Parameter t_e Temperatur
        self.V_b = get_input.V_b    # fixed parameter V_b Volumenstrom
        self.diam = None            # Durchmesser Rohr
        self.height = None          # Höhe Dämpfer
        self.weight = None          # Gewicht Dämpfer
        self.AF = None              # freie Fläche (Durchmesserfläche Behälter - Fläche der umströmten Bombe)
        self.w = None               # Geschwindigkeit
        self.h = None               # Arbeitsaufwand (h?)
        self.Mat_cost = None        # Kosten Material
        self.CA_Add = 0             # Corrosion Dickenaufschlag (not implemented)
        self.cost = None            # Kosten
        self.SB = 0                 # Staffingbox (not implemented): Vertical & Horizontal Elongation Abfrage (not implemented)
        if(self.t_e<480): self.Beh = 2  #Materialauswahl für Behälter in Abhängigkeit von Temperatur
        else: self.Beh = 4  
        self.SP = Splash_Plates     # Backend-Parameter
        self.Zn = SA_25_75          # Backend-Parameter Oberflächenbehandlungsparam.
        self.SiAl = SiAl            # Backend-Parameter Oberflächenbehandlungsparam.
        self.surface = None         # Oberflächenkosten (€)
        self.Pr = None              # Pratzen
        self.h_v = None             # ? horizontale Elongation ? (not implemented)
        self.s = None               # Staerke
        
        self.LwA_sum = None         # Platzhalter Schallleistungspegel Summe
        self.LpA_sum = None         # Platzhalter Schalldruckpegel Summe
        self.ref_area_Ls = None     # Platzhalter Abzug für Schalldruckabnahme mit Abstand auf Referenzfläche bezogen

        if(self.Bautyp == 'A'): self.Daempfung_list = [0,0,0,0,0,0,0,0]
        if(self.Bautyp == 'B'): self.Daempfung_list = [0,-1,-2,-4,-5,-6,-6,-6]
        if(self.Bautyp == 'C'): self.Daempfung_list = [-1,-3,-6,-14,-21,-30,-25,-18]
        if(self.Bautyp == 'D'): self.Daempfung_list = [-2,-4,-8,-20,-28,-34,-29,-20]
        if(self.Bautyp == 'E'): self.Daempfung_list = [-3,-5,-10,-22,-34,-38,-32,-22]
        if(self.Bautyp == 'F'): self.Daempfung_list = [-3,-6,-12,-26,-39,-44,-38,-28]

        self.Daempfung_LwA_list = [0,0,0,0,0,0,0,0]
        self.flownoise_list = [0,0,0,0,0,0,0,0]
        self.flownoise_LwA_list = [0,0,0,0,0,0,0,0]
        self.directivity_list = const_directivity.calc_directivity(directivity_angle)
        self.directivity_LwA_list = [0,0,0,0,0,0,0,0]
        self.airabsorption_list = [0,0,0,0,0,0,0,0]
        self.airabsorption_LwA_list = [0,0,0,0,0,0,0,0]
        self.LpA_list = [0,0,0,0,0,0,0,0]

    def calc_sound_Bauweise_(self,Typ):          # Berechnung des Schalls für die verschiedenen Bautypen (A-F)
        flownoise_sum = SG_Bo(self.t_e,self.w,self.AF)
        for i in range(len(const_oktspektrum.Okt_Freq_Spektrum_list)):
            self.Daempfung_LwA_list[i] = Typ.Stufen_LwA_total_list[i] + self.Daempfung_list[i]
            self.flownoise_list[i] = flownoise_sum + const_oktspektrum.Korr_Term_flownoise_list[i]
            self.flownoise_LwA_list[i] = 10*math.log10(10**(self.Daempfung_LwA_list[i]/10)+10**(self.flownoise_list[i]/10))
            self.directivity_LwA_list[i] = self.directivity_list[i] + self.flownoise_LwA_list[i]
            self.airabsorption_list[i] = const_oktspektrum.airabsorption_Okt_coeff_list[i] * self.s            
            self.airabsorption_LwA_list[i] = self.airabsorption_list[i] + self.directivity_LwA_list[i]            
            self.LpA_list[i] = self.ref_area_Ls + self.airabsorption_LwA_list[i]            

        help_sum_LwA = 0
        help_sum_LpA = 0
        for i in range(len(const_oktspektrum.Okt_Freq_Spektrum_list)):
            help_sum_LwA += 10**(self.flownoise_LwA_list[i]/10)
            help_sum_LpA += 10**(self.LpA_list[i]/10)
        self.LwA_sum = 10*math.log10(help_sum_LwA)
        self.LpA_sum = 10*math.log10(help_sum_LpA)


    def calc_diam_(self,Typ):            #Berechnung Durchmesser (mm)
        if(self.Bautyp == 'A'): self.diam = D_geh(get_input.V_b,Typ.d_max)
        if(self.Bautyp == 'B'): self.diam = D_geh_ra(get_input.V_b,Typ.d_max)
        if(self.Bautyp == 'C'): self.diam = D_geh_bo(get_input.V_b,Typ.d_max)
        if(self.Bautyp == 'D'): self.diam = D_geh_bo(get_input.V_b,Typ.d_max)
        if(self.Bautyp == 'E'): self.diam = D_geh_bo(get_input.V_b,Typ.d_max)
        if(self.Bautyp == 'F'): self.diam = D_geh_TypF(get_input.V_b,Typ.d_max)

    def calc_height_(self,Typ):          #Berechnung Höhe (mm)
        if(self.Bautyp == 'A'):    
            if(self.diam<=1800): self.height = 1000
            elif(self.diam<=1900): self.height = 1500
            else: self.height = 2000
        if(self.Bautyp == 'B'):
            if(self.diam<=1200): self.height = 1000
            elif(self.diam<=1700): self.height = 1500
            else: self.height = 2000
        if(self.Bautyp == 'C'):
            if(self.diam<=960): self.height = 1500
            else: self.height = math.ceil((Typ.H_ges+1700)/250)*250
        if(self.Bautyp == 'D'):
            if(self.diam<=960): self.height = 1500
            else: self.height = math.ceil((Typ.H_ges+2200)/250)*250
        if(self.Bautyp == 'E'):
            if(self.diam<=960): self.height = 1500
            else: self.height = math.ceil((Typ.H_ges+2700)/250)*250
        if(self.Bautyp == 'F'):
            if(self.diam<=960): self.height = 1500
            else: self.height = math.ceil((Typ.H_ges+2700)/250)*250

    def calc_Pr_(self):         # Berechnung Pratzen/Brackets?
        if((int(self.weight/10)+1)*10>=1000 or self.SB!=0 or Brackets=='y'): self.Pr = 4
        else: self.Pr = 0

    def calc_h_(self,Typ):
        Typ.h_min = int(get_input.V_b/(math.pi*Typ.last_St.D_Ro/1000*w_max)*1000)
        Typ.h_max = int(get_input.V_b/(math.pi*Typ.last_St.D_Ro/1000*w_min)*1000)
        Typ.H_ges = h_gestrick(H_total(Typ.h_min,Typ.h_max,Typ.St1.D_Ro,Typ.St1_Gestr.D_Ro,Typ.St2.D_Ro,Typ.St2_Gestr.D_Ro,Typ.St3.D_Ro,Typ.St3_Gestr.D_Ro,get_input.flow,get_input.h1,get_input.p1,Typ.St1.p,get_input.t1,get_input.ts1,Typ.St1.t,Typ.St1.v,Typ.St1.D_B,18))
    
    def calc_weight_(self,Typ):          # Berechnung Gewicht (kg)
        if(self.Bautyp == 'A'): self.weight = Typ.get_weight_sum(Typ) + G_SD(self.height,self.diam,0,4,get_input.d_inl,birdscreen,0)
        if(self.Bautyp == 'B'): self.weight = Typ.get_weight_sum(Typ) + G_SD(self.height,self.diam,self.height,4,get_input.d_inl,birdscreen,0)
        if(self.Bautyp == 'C'): self.weight = Typ.get_weight_sum(Typ) + G_SD(self.height,self.diam,0,4,get_input.d_inl,birdscreen,0) + GAbs(self.diam,1)
        if(self.Bautyp == 'D'): self.weight = Typ.get_weight_sum(Typ) + G_SD(self.height,self.diam,0,4,get_input.d_inl,birdscreen,0) + GAbs(self.diam,1.5)
        if(self.Bautyp == 'E'): self.weight = Typ.get_weight_sum(Typ) + G_SD(self.height,self.diam,0,4,get_input.d_inl,birdscreen,0) + GAbs(self.diam,2)
        if(self.Bautyp == 'F'): self.weight = Typ.get_weight_sum(Typ) + G_SD(self.height,self.diam,self.height-2100,4,get_input.d_inl,birdscreen,0) + GAbs(self.diam,2)

    def calc_AF_(self):                 # Auswahl Fläche für zueghörigen Durchmesser (m^2)
        if(self.Bautyp == 'A'): self.AF = const_diam.Af_ohne[self.diam]
        if(self.Bautyp == 'B'): self.AF = const_diam.Af_RA[self.diam]
        if(self.Bautyp == 'C'): self.AF = const_diam.Af_Bo[self.diam]
        if(self.Bautyp == 'D'): self.AF = const_diam.Af_Bo[self.diam]
        if(self.Bautyp == 'E'): self.AF = const_diam.Af_Bo[self.diam]
        if(self.Bautyp == 'F'): self.AF = const_diam.Af_Bo[self.diam]
    
    def calc_w_(self):      # Berechnung (Strom)Geschwindigkeit (m/s)
        self.w = get_input.V_b/self.AF

    def calc_work_(self,Typ):          	    # Berechnung Arbeitsaufwand (h)
        if(self.Bautyp == 'A'): self.h = Typ.work_sum + BB_zeit(self.height,self.diam,0,self.Pr,get_input.d_inl,0) + Bh(self.diam,0) + Splash_Plates * 0.8                   #+@hSB($C$10;I45)
        if(self.Bautyp == 'B'): self.h = Typ.work_sum + BB_zeit(self.height,self.diam,self.height,self.Pr,get_input.d_inl,0) + Bh(self.diam,0) + Splash_Plates * 0.8 + Z_RA(self.diam,self.height)         #+@hSB($C$10;I56)
        if(self.Bautyp == 'C'): self.h = Typ.work_sum + BB_zeit(self.height,self.diam,0,self.Pr,get_input.d_inl,1) + Bh(self.diam,1) + Splash_Plates * 0.8 + Z_RA(self.diam,0)                   #+@hSB($C$10;I67)
        if(self.Bautyp == 'D'): self.h = Typ.work_sum + BB_zeit(self.height,self.diam,0,self.Pr,get_input.d_inl,1.5) + Bh(self.diam,1.5) + Splash_Plates * 0.8 + Z_RA(self.diam,0)               #+@hSB($C$10;I78)
        if(self.Bautyp == 'E'): self.h = Typ.work_sum + BB_zeit(self.height,self.diam,0,self.Pr,get_input.d_inl,2) + Bh(self.diam,2) + Splash_Plates * 0.8 + Z_RA(self.diam,0)                   #+@hSB($C$10;I89)
        if(self.Bautyp == 'F'): self.h = Typ.work_sum + BB_zeit(self.height,self.diam,self.height-2100,self.Pr,get_input.d_inl,2) + Bh(self.diam,2) + Splash_Plates * 0.8 + Z_RA(self.diam,self.height-2100)    #+@hSB($C$10;I100))

    def calc_matcost_(self,Typ):            # Berechnung Materialkosten (€)
        if(self.Bautyp == 'A'): self.Mat_cost = Typ.cost_sum + BB_Mat(self.height,self.diam,0,0,get_input.d_inl,'n',0,const_material.Mat_prices_list[self.Beh-1]) +Splash_Plates*14    #+kSB(C$10,I45)
        if(self.Bautyp == 'B'): self.Mat_cost = Typ.cost_sum + BB_Mat(self.height,self.diam,0,0,get_input.d_inl,'n',0,const_material.Mat_prices_list[self.Beh-1]) +Splash_Plates*14    #+kSB(C$10,I56)
        if(self.Bautyp == 'C'): self.Mat_cost = Typ.cost_sum + BB_Mat(self.height,self.diam,0,0,get_input.d_inl,'n',0,const_material.Mat_prices_list[self.Beh-1]) +Splash_Plates*14 + BDM(self.diam,1)   #+kSB(C$10,I67)
        if(self.Bautyp == 'D'): self.Mat_cost = Typ.cost_sum + BB_Mat(self.height,self.diam,0,0,get_input.d_inl,'n',0,const_material.Mat_prices_list[self.Beh-1]) +Splash_Plates*14 + BDM(self.diam,1.5)    #+kSB(C$10,I78)
        if(self.Bautyp == 'E'): self.Mat_cost = Typ.cost_sum + BB_Mat(self.height,self.diam,0,0,get_input.d_inl,'n',0,const_material.Mat_prices_list[self.Beh-1]) +Splash_Plates*14 + BDM(self.diam,2)    #+kSB(C$10,I89)
        if(self.Bautyp == 'F'): self.Mat_cost = Typ.cost_sum + BB_Mat(self.height,self.diam,self.height-2100,0,get_input.d_inl,'n',0,const_material.Mat_prices_list[self.Beh-1]) +Splash_Plates*14 + BDM(self.diam,2)    #+kSB(C$10,I100)

    def calc_cost_(self,Typ):               # Berechnung Gesamtkosten/Preis (€)
        if(Typ.H_ges<10000 and self.diam<10000): self. cost = self.surface+self.h*Stundensatz+self.Mat_cost+self.CA_Add
        else: self.cost = 100000

    def calc_surface_(self,Typ):                    #Berechnung Oberfläche Material Kosten (€?!)
        if(self.Beh ==6 or self.Zn<1 or self.Zn>4): self.surface = 0
        else: self.surface = OB_Mat(self.height,self.diam,0,4,get_input.d_inl,0,0,self.Zn,self.SiAl)+ Typ.OF_cost

    def calc_s_(self):
        if(get_input.d_tocasing == 0): self.s = self.diam/2000+1
        else: self.s = self.diam/2000 + get_input.d_tocasing
        self.ref_area_Ls = -10*math.log10(2*math.pi*self.s**2)

# %%
#Instanzierung und Aufbau der jeweiligen Typen
def define_Stufen_Typen():
    Typ1_Stufen = 1
    Typ1_Gestrick_list = [1]
    Typ1 = daempfer(Typ1_Stufen,Typ1_Gestrick_list)

    Typ2_Stufen = 2
    Typ2_Gestrick_list = [0,1]
    Typ2 = daempfer(Typ2_Stufen,Typ2_Gestrick_list)

    Typ3_Stufen = 2
    Typ3_Gestrick_list = [1,1]
    Typ3 = daempfer(Typ3_Stufen,Typ3_Gestrick_list)

    Typ4_Stufen = 3                         # Anzahl physischer Stufen
    Typ4_Gestrick_list = [0,0,1]            # Auswahl ob Gestrick nach einer Stufe? 0==kein Gestrick, 1==Gestrick
    Typ4 = daempfer(Typ4_Stufen,Typ4_Gestrick_list)

    Typ5_Stufen = 3
    Typ5_Gestrick_list = [0,1,1]
    Typ5 = daempfer(Typ5_Stufen,Typ5_Gestrick_list)

    Typ6_Stufen = 3
    Typ6_Gestrick_list = [1,1,1]
    Typ6 = daempfer(Typ6_Stufen,Typ6_Gestrick_list)

    Typ_list = [Typ1,Typ2,Typ3,Typ4,Typ5,Typ6]
    return Typ_list

# %%
def calculate_everything(Typ_list):
    #Typ_list = [Typ1,Typ2,Typ3,Typ4,Typ5,Typ6]           # Liste aller vorhandenen Typen-Objekte

    for Typ in Typ_list:
        Typ.d_max_sum()                     # Bestimmung Maximum und Summe aller Stufen-Durchmesser
        Typ.calc_staerke()                  # Berechnung der Staerken-Tabelle für die Stufen und Kopf-/Ringplatte triggern
        Typ.calc_costweight()               # Berechnung der Kosten/Gewichte triggern
        for Bautyp in Typ.Bauweise_list:
            Bautyp.calc_diam_(Typ)             # Berechnung aller Durchmesser der verschiedenen Bautypen triggern
            Bautyp.calc_height_(Typ)           # Berechnung aller Höhen der verschiedenen Bautypen triggern
            Bautyp.calc_h_(Typ)                # Berechnung der Gesamthöhe triggern
            Bautyp.calc_weight_(Typ)     # Berechnung des Gewichts triggern
            Bautyp.calc_Pr_()               # Berechnung Pratzen triggern
            Bautyp.calc_AF_()           # Berechnung Fläche triggern
            Bautyp.calc_w_()             # Berechnung (Strom)Geschwindigkeit triggern
            Bautyp.calc_work_(Typ)            # Berechnung Arbeitsaufwand triggern
            Bautyp.calc_matcost_(Typ)          # Berechnung Materialkosten für Typ triggern
            Bautyp.calc_surface_(Typ)           # Berechnung Oberfläche Material triggern
            Bautyp.calc_cost_(Typ)              # Berechnung Gesamtkosten triggern
            Bautyp.calc_s_()                    # Berechnung Staerke triggern
            
        Typ.calc_sound_Stufen()                 # Berechnung Schallpegel für Stufen in den verschiedenen Typen triggern
        for Bautyp in Typ.Bauweise_list:
            Bautyp.calc_sound_Bauweise_(Typ)    # Berechnung Schallpegel für verschiedene Bauweisen triggern



# %%
def evaluate_results(Typ_list):
    met_requirements_list=[]
    for i in Typ_list:
        for j in i.Bauweise_list:
            if(get_input.LwA_input>0 and round(j.LwA_sum)<=get_input.LwA_input+0.5):
                j.meet_sound_requirements = True
                met_requirements_list.append(j)
            elif(get_input.LpA_input>0 and round(j.LpA_sum)<=get_input.LpA_input+0.5):
                j.meet_sound_requirements = True
                met_requirements_list.append(j)
            else:
                j.meet_sound_requirements = False

    if(met_requirements_list==[]):
        print('Kein Dämpfer erfüllt die Anforderungen')
    else:
        cost_temp = met_requirements_list[0].cost       # Initialisierung Kostenvergleich mit erstem Kosten-Eintrag der erfolgreichen Dämpferliste
        i_temp = met_requirements_list[0]
        for i in met_requirements_list:
            if(i.cost < cost_temp):                     # Suche nach niedrigsten Kosten unter den erfolgreichen Dämpfern
                cost_temp = i.cost                      # Merken der niedrigsten Kosten
                i_temp = i                              # Merken des billigsten Dämpfers (Bauweise)
        #chosen_Daempfer = i_temp.Typ
        chosen_Bauweise = i_temp
        Gesamttyp = [chosen_Bauweise.Typ.Typ_name , chosen_Bauweise.Bautyp , chosen_Bauweise.Typ.H_ges]
        if __name__ == "__main__":
            print('Results:')
            print('Typ: ',Gesamttyp)
            print('Durchmesser: ', chosen_Bauweise.diam)
            print('Höhe: ', chosen_Bauweise.height)
            print('Gewicht: ', chosen_Bauweise.weight)
            print('Preis: ', chosen_Bauweise.cost)
        
        results_list = [chosen_Bauweise.diam, chosen_Bauweise.height, chosen_Bauweise.weight,Gesamttyp ,chosen_Bauweise.cost]
        results_list[2] = math.ceil(results_list[2]/50)*50       # Aufrunden zum nächst höchsten 50kg-Inkrement (Gewicht)
        results_list[4] = math.ceil(results_list[4]/100)*100     # Aufrunden zum nächst höchsten 100€-Inkrement (Preis)
        return results_list

# %%
if __name__ == "__main__":
    get_input([])
    list_of_all_silencers = define_Stufen_Typen()            # Aufbau der verschiedenen Typen hinsichtlich Stufen & Gestrick
    calculate_everything(list_of_all_silencers)              # alle Parameter der einzelnen Dämpfertypen berechnen
    results = evaluate_results(list_of_all_silencers)                  # Auswertung hinsichtlich erreichter Schalldämmung und bestem Preis --> Ausgabe

# %%
def getData(ext_input_list):
    get_input(ext_input_list)

    list_of_all_silencers = define_Stufen_Typen()            # Aufbau der verschiedenen Typen hinsichtlich Stufen & Gestrick
    calculate_everything(list_of_all_silencers)              # alle Parameter der einzelnen Dämpfertypen berechnen
    results = evaluate_results(list_of_all_silencers)                  # Auswertung hinsichtlich erreichter Schalldämmung und bestem Preis --> Ausgabe
    return results


