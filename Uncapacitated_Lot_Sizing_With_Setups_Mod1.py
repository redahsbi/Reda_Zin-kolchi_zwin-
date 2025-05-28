

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

model = Model(name = "ULS", solver_name="CBC")
model.max_seconds = 180


x = [model.add_var(name=f"x({i})", var_type=CONTINUOUS, lb=0) for i in range(nbPeriodes)]
y = [model.add_var(name=f"y({i})", var_type=BINARY) for i in range(nbPeriodes)]
s = [model.add_var(name=f"s({i})", var_type=CONTINUOUS, lb=0) for i in range(nbPeriodes)]
 


# Bilan des stocks
for i in range(nbPeriodes):
    if i == 0:
        model += x[i] == demandes[i] + s[i]
    else:
        model += x[i] + s[i-1] == demandes[i] + s[i]

# Lien entre production et activation
M = sum(demandes)
for i in range(nbPeriodes):
    model += x[i] <= M * y[i]


model.objective = xsum(couts[i]*x[i] + cfixes[i]*y[i] + cstock*s[i] for i in range(nbPeriodes))



#model.write("test.lp")

status = model.optimize()

print("Relaxation linéaire :", model.objective_bound)
print("Meilleure valeur trouvée :", model.objective_value)
if model.objective_value is not None and model.objective_bound != 0:
    ecart = 100 * (model.objective_value - model.objective_bound) / model.objective_value
    print(f"Écart en % : {ecart:.2f} %")
print("Nombre de nœuds :", model.node_count)
print("Temps de résolution :", model.solve_time, "secondes")


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
    
if model.num_solutions>0:
    print("Solution calculée")
    print("-> Valeur de la fonction objectif de la solution calculée : ",  model.objective_value)
    for i in range(nbPeriodes):
        print(f"Période {i+1} : x = {x[i].x}, y = {int(y[i].x)}, s = {s[i].x}")


    print("\n \t Implémentez l'affichage de la solution !")

