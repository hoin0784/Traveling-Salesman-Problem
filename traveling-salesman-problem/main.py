import math, random
import cv2
# cv2 map drawing package

'''
class City:
Means a city and contains the city's coordinates.
'''

class City:
    def __init__(self, x=None, y=None):
        
        self.x = None  # x coordinate of city
        self.y = None  # y coordinate of city
        if x is not None:
            self.x = x
        else:
            self.x = int(random.random() * 200)
        if y is not None:
            self.y = y
        else:
            self.y = int(random.random() * 200)
   
    def getX(self):
        return self.x

    def getY(self):
        return self.y

    # method: find distance between cities
    def distanceTo(self, city): 
        xDistance = abs(self.getX() - city.getX())
        yDistance = abs(self.getY() - city.getY())
        distance = math.sqrt( (xDistance*xDistance) + (yDistance*yDistance) )
        return distance

    def __repr__(self):
        return str(self.getX()) + ", " + str(self.getY())
'''
class TourManager:
'''

# The TourManager class helps travelers plan their trips.
# ㅁAdd city or/ which city exists or/ number of cities

class TourManager:
    destinationCities = []

    def addCity(self, city):
        self.destinationCities.append(city)

    def getCity(self, index):
        return self.destinationCities[index]

    def numberOfCities(self):
        return len(self.destinationCities)


# A class that contains routes connecting all cities, a class that connects cities
# Means the tour path after all

class Tour:
    def __init__(self, tourmanager, tour=None):
        self.tourmanager = tourmanager
        self.tour = []
        self.fitness = 0.0
        self.distance = 0
        if tour is not None:
            self.tour = tour
        else:
            for i in range(0, self.tourmanager.numberOfCities()):
                self.tour.append(None)

    def __len__(self):
        return len(self.tour)

    def __getitem__(self, index):
        return self.tour[index]

    def __setitem__(self, key, value):
        self.tour[key] = value

    def __repr__(self):
        geneString = 'Start -> '
        for i in range(0, self.tourSize()):
            geneString += str(self.getCity(i)) + ' -> '
        geneString += 'End'
        return geneString

    def generateIndividual(self):
        for cityIndex in range(0, self.tourmanager.numberOfCities()):
            self.setCity(cityIndex, self.tourmanager.getCity(cityIndex))
        random.shuffle(self.tour)

    def getCity(self, tourPosition):
        return self.tour[tourPosition]

    def setCity(self, tourPosition, city):
        self.tour[tourPosition] = city
        self.fitness = 0.0
        self.distance = 0

    #fitness is inversely proportional to the distance, the shorter the distance, the higher the score
    def getFitness(self):
        if self.fitness == 0:
            self.fitness = 1/float(self.getDistance())
        return self.fitness

    # Function to calculate the total distance of the tour
    def getDistance(self):
        if self.distance == 0:
            tourDistance = 0
            for cityIndex in range(0, self.tourSize()):
                fromCity = self.getCity(cityIndex)
                destinationCity = None
                if cityIndex+1 < self.tourSize():
                    destinationCity = self.getCity(cityIndex+1)
                else:
                    destinationCity = self.getCity(0)
                tourDistance += fromCity.distanceTo(destinationCity)
            self.distance = tourDistance
        return self.distance

    def tourSize(self):
        return len(self.tour)

    def containsCity(self, city):
        return city in self.tour

# Means a set of travel routes, a collection of tours
# Create a better population by mutating, crossover, and reviving those with high fitness
class Population:
    def __init__(self, tourmanager, populationSize, initialise):
        self.tours = []
        for i in range(0, populationSize):
            self.tours.append(None)
        
        if initialise:
            for i in range(0, populationSize):
                newTour = Tour(tourmanager)
                newTour.generateIndividual()
                self.saveTour(i, newTour)
        
    def __setitem__(self, key, value):
        self.tours[key] = value

    def __getitem__(self, index):
        return self.tours[index]

    def saveTour(self, index, tour):
        self.tours[index] = tour

    def getTour(self, index):
        return self.tours[index]

    def getFittest(self):
        fittest = self.tours[0]
        for i in range(0, self.populationSize()):
            if fittest.getFitness() <= self.getTour(i).getFitness():
                fittest = self.getTour(i)
        return fittest

    def populationSize(self):
        return len(self.tours)


#Core genetic algorithm class

class GA:
    def __init__(self, tourmanager, mutationRate=0.05, tournamentSize=5, elitism=True):
        self.tourmanager = tourmanager
        self.mutationRate = mutationRate
        self.tournamentSize = tournamentSize
        self.elitism = elitism
    #Evolving process
    def evolvePopulation(self, pop):
        newPopulation = Population(self.tourmanager, pop.populationSize(), False)
        elitismOffset = 0
        if self.elitism:
            newPopulation.saveTour(0, pop.getFittest())
            elitismOffset = 1
        
        for i in range(elitismOffset, newPopulation.populationSize()):
            parent1 = self.tournamentSelection(pop)
            parent2 = self.tournamentSelection(pop)
            child = self.crossover(parent1, parent2)
            newPopulation.saveTour(i, child)
        
        for i in range(elitismOffset, newPopulation.populationSize()):
            self.mutate(newPopulation.getTour(i))
        
        return newPopulation
    # performance process
    def crossover(self, parent1, parent2):
        child = Tour(self.tourmanager)
        
        startPos = int(random.random() * parent1.tourSize())
        endPos = int(random.random() * parent1.tourSize())
        
        for i in range(0, child.tourSize()):
            if startPos < endPos and i > startPos and i < endPos:
                child.setCity(i, parent1.getCity(i))
            elif startPos > endPos:
                if not (i < startPos and i > endPos):
                    child.setCity(i, parent1.getCity(i))
        
        for i in range(0, parent2.tourSize()):
            if not child.containsCity(parent2.getCity(i)):
                for ii in range(0, child.tourSize()):
                    if child.getCity(ii) == None:
                        child.setCity(ii, parent2.getCity(i))
                        break

        return child
   # Mutation process
    def mutate(self, tour):
        for tourPos1 in range(0, tour.tourSize()):
            if random.random() < self.mutationRate:
                tourPos2 = int(tour.tourSize() * random.random())
                
                city1 = tour.getCity(tourPos1)
                city2 = tour.getCity(tourPos2)
                
                tour.setCity(tourPos2, city1)
                tour.setCity(tourPos1, city2)

    def tournamentSelection(self, pop):
        tournament = Population(self.tourmanager, self.tournamentSize, False)
        for i in range(0, self.tournamentSize):
            randomId = int(random.random() * pop.populationSize())
            tournament.saveTour(i, pop.getTour(randomId))
        fittest = tournament.getFittest()
        return fittest



if __name__ == '__main__':
    # How many cities will traveler take a trip to?
    n_cities = 20
    # How many populations (tours) to create per generation
    population_size = 50
    # Evolution through 100 generations
    n_generations = 100
    # To generate random cities
    random.seed(100)

    # map.jpg (U.S. map)  plan to take a random city
    map_original = cv2.imread('map.jpg')

    # Setup cities and tour
    tourmanager = TourManager()
    # Add 20 n_cities
    for i in range(n_cities):
        # Cities should not be created anywhere, so put the coordinates in x and y respectively
        x = random.randint(70, 700)        # 70 700
        y = random.randint(70, 700)        # 70 700
        # Add cities
        tourmanager.addCity(City(x=x, y=y))

        # Draw a red dot on the image
        cv2.circle(map_original, center=(x, y), radius=10, color=(0, 0, 255), thickness=-1, lineType=cv2.LINE_AA)

    cv2.imshow('map', map_original)
    cv2.waitKey(0)

    # Initialize population
    pop = Population(tourmanager, populationSize=population_size, initialise=True)
    print("Initial distance: " + str(pop.getFittest().getDistance()))

    # Evolve population
    ga = GA(tourmanager)

    # loop 100 generations
    for i in range(n_generations):
        pop = ga.evolvePopulation(pop)
        # pick the best ones
        fittest = pop.getFittest()

        map_result = map_original.copy()
        # draw the path# draw the path# draw the path
        for j in range(1, n_cities):
            cv2.line(
                map_result,
                pt1=(fittest[j-1].x, fittest[j-1].y),
                pt2=(fittest[j].x, fittest[j].y),
                color=(255, 0, 0),
                thickness=3,
                lineType=cv2.LINE_AA
            )

        cv2.putText(map_result, org=(10, 25), text='Generation: %d' % (i+1), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=0, thickness=1, lineType=cv2.LINE_AA)
        cv2.putText(map_result, org=(10, 50), text='Distance: %.2fkm' % fittest.getDistance(), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=0, thickness=1, lineType=cv2.LINE_AA)
        cv2.imshow('map', map_result)
        if cv2.waitKey(100) == ord('q'):
            break

    # Print final results
    print("Finished")
    print("Final distance: " + str(pop.getFittest().getDistance()))
    print("Solution:")
    print(pop.getFittest())

    cv2.waitKey(0)
