
datafileName = 'Instances_ULS/Toy_Instance.txt'

with open(datafileName, "r") as file:
    line = file.readline()  
    lineTab = line.split()    
    nbPeriodes = int(lineTab[0])
    
    line = file.readline()  
    lineTab = line.split()
    demandes = []
    for i in range(nbPeriodes):
        demandes.append(int(lineTab[i]))
        
    line = file.readline()  
    lineTab = line.split()
    couts = []
    for i in range(nbPeriodes):
        couts.append(int(lineTab[i]))

    line = file.readline()  
    lineTab = line.split()
    cfixes = []
    for i in range(nbPeriodes):
        cfixes.append(int(lineTab[i]))
    
    line = file.readline()  
    lineTab = line.split()    
    cstock = int(lineTab[0])

#print(nbPeriodes)
#print(demandes)
#print(couts)
#print(cfixes)
#print(cstock)

from mip import *
import time


model2 = Model(name="ULS_Mod2", solver_name="CBC")
model2.max_seconds = 180

# Variables
y = [model2.add_var(var_type=BINARY, name=f"y({i})") for i in range(nbPeriodes)]

x = [[
    model2.add_var(var_type=CONTINUOUS, lb=0, name=f"x({i},{j})") if i <= j else None
    for j in range(nbPeriodes)]
    for i in range(nbPeriodes)
]

# Contraintes de satisfaction de la demande
for j in range(nbPeriodes):
    model2 += xsum(x[i][j] for i in range(j + 1)) == demandes[j]

# Contraintes de lien entre x[i][j] et y[i]
for i in range(nbPeriodes):
    for j in range(i, nbPeriodes):
        model2 += x[i][j] <= demandes[j] * y[i]

# Fonction objectif
model2.objective = xsum(
    cfixes[i] * y[i] +
    xsum((couts[i] + cstock * (j - i)) * x[i][j] for j in range(i, nbPeriodes))
    for i in range(nbPeriodes)
)

# Résolution





#model2.write("test.lp")

status = model2.optimize()


print("\n----------------------------------")
if status == OptimizationStatus.OPTIMAL:
    print("Status de la résolution: OPTIMAL")
elif status == OptimizationStatus.FEASIBLE:
    print("Status de la résolution: TEMPS LIMITE et SOLUTION REALISABLE CALCULEE")
elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    print("Status de la résolution: TEMPS LIMITE et AUCUNE SOLUTION CALCULEE")
elif status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
    print("Status de la résolution: IRREALISABLE")
elif status == OptimizationStatus.UNBOUNDED:
    print("Status de la résolution: NON BORNE")

if model2.num_solutions > 0:
    print("Solution calculée")
    print("-> Valeur de la fonction objectif de la solution calculée : ", model2.objective_value)

    print("\nVariables y (setup activé) :")
    for i in range(nbPeriodes):
        if y[i].x > 0.5:
            print(f"  y({i}) = 1")

    print("\nVariables x (production pour demandes futures) :")
    for i in range(nbPeriodes):
        for j in range(i, nbPeriodes):
            if x[i][j].x > 1e-5:
                print(f"  x({i},{j}) = {x[i][j].x:.2f}")
print("Relaxation linéaire :", model2.objective_bound)
print("Meilleure valeur trouvée :", model2.objective_value)
if model2.objective_value is not None and model2.objective_bound != 0:
    ecart = 100 * (model2.objective_value - model2.objective_bound) / model2.objective_value
    print(f"Écart en % : {ecart:.2f} %")
