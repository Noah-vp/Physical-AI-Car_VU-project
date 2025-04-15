import matplotlib.pyplot as plt

#plot the stats from the population stats.txt file
with open("stats.txt", "r") as f:
    #read the stats with 2 decimal places
    stats = f.read().strip().split(",")
    #remove empty strings
    stats = [x for x in stats if x]

#convert the stats in the list to 2 decimal places
stats = [round(float(x), 2) for x in stats]

#plot the stats with some formatting and labels
plt.plot(stats)
plt.title("Fitness of the population over generations")
plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.show()

