import random
import json
import os
import matplotlib.pyplot as plt

# Function to generate a random date
def generateDate():
    day = random.randint(1, 31)
    month = random.randint(1, 12)
    year = random.randint(0, 9999)
    return (day, month, year)


# Function to format a date properly
def formatDate(date):
    day, month, year = date
    return f"{day:02d}/{month:02d}/{year:04d}"


# Function to check if a date is valid
def isValidDate(day, month, year):
    if not (1 <= day <= 31 and 1 <= month <= 12):
        return False
    if month in {4, 6, 9, 11} and day > 30:
        return False
    if month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return day <= 29  # Leap year
        else:
            return day <= 28  # Non-leap year
    return True


# Function to categorize a date
def categorizeDate(date):
    day, month, year = date
    if isValidDate(day, month, year):
        if date in [(29, 2, 2020), (30, 4, 2022), (31, 12, 2023)]:
            return "Boundary"
        return "Valid"
    return "Invalid"


# Function to calculate fitness
def fitnessFunction(date, seen_dates):
    category = categorizeDate(date)
    date_str = formatDate(date)

    valid_coverage = 1 if category == "Valid" else 0
    invalid_coverage = 1 if category == "Invalid" else 0
    boundary_coverage = 1 if category == "Boundary" else 0
    redundancy_penalty = -1 if date_str in seen_dates else 0

    seen_dates.add(date_str)

    weights = {"Valid": 5, "Invalid": 5, "Boundary": 10, "Redundancy": 3}
    fitness = (weights["Valid"] * valid_coverage +
               weights["Invalid"] * invalid_coverage +
               weights["Boundary"] * boundary_coverage -
               weights["Redundancy"] * redundancy_penalty)
    return fitness


# Selection process
def rankSelection(population, fitness_scores, num_select):
    sorted_population = sorted(population, key=lambda date: fitness_scores[formatDate(date)], reverse=True)
    return sorted_population[:num_select]


# Crossover function
def crossover(parent1, parent2):
    return (parent1[0], parent2[1], random.choice([parent1[2], parent2[2]]))


# Mutation function
def mutate(date):
    day, month, year = date
    if random.random() < 0.15:
        day = max(1, min(31, day + random.choice([-3, 3])))
        month = max(1, min(12, month + random.choice([-1, 1])))
        year = max(0, min(9999, year + random.choice([-100, 100])))
    return (day, month, year)


# Genetic Algorithm
import matplotlib.pyplot as plt


# Genetic Algorithm with Coverage Tracking and Line Graph Generation
def geneticAlgo():
    popSize, gens = 50, 100
    population = [generateDate() for _ in range(popSize)]
    seen_dates = set()

    # Lists to track coverage percentages over generations
    valid_coverage_list = []
    invalid_coverage_list = []
    boundary_coverage_list = []

    # GA evolution loop
    for gen in range(gens):
        fitness_scores = {formatDate(date): fitnessFunction(date, seen_dates) for date in population}
        selectedParents = rankSelection(population, fitness_scores, popSize // 2)
        nextPopulation = []

        for i in range(0, len(selectedParents), 2):
            if i + 1 < len(selectedParents):
                child1 = crossover(selectedParents[i], selectedParents[i + 1])
                child2 = crossover(selectedParents[i + 1], selectedParents[i])
                nextPopulation.append(mutate(child1))
                nextPopulation.append(mutate(child2))

        population = nextPopulation

        # Calculate coverage for this generation
        valid_count = sum(1 for date in population if categorizeDate(date) == "Valid")
        invalid_count = sum(1 for date in population if categorizeDate(date) == "Invalid")
        boundary_count = sum(1 for date in population if categorizeDate(date) == "Boundary")
        total_count = valid_count + invalid_count + boundary_count or 1  # avoid division by zero

        valid_coverage_list.append((valid_count / total_count) * 100)
        invalid_coverage_list.append((invalid_count / total_count) * 100)
        boundary_coverage_list.append((boundary_count / total_count) * 100)

    # Final fitness calculation after generations
    final_scores = {formatDate(date): fitnessFunction(date, seen_dates) for date in population}
    sorted_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

    valid_cases, invalid_cases, boundary_cases = 0, 0, 0

    print("Best Test Cases:")
    for date, score in sorted_results[:20]:
        category = categorizeDate(tuple(map(int, date.split("/"))))
        if category == "Valid":
            valid_cases += 1
        elif category == "Invalid":
            invalid_cases += 1
        else:
            boundary_cases += 1
        print(f"{date} -> Fitness: {score}, Category: {category}")

    total_cases = valid_cases + invalid_cases + boundary_cases
    print("\nCoverage Summary:")
    print(f"Valid Cases: {valid_cases} ({(valid_cases / total_cases) * 100:.2f}%)")
    print(f"Invalid Cases: {invalid_cases} ({(invalid_cases / total_cases) * 100:.2f}%)")
    print(f"Boundary Cases: {boundary_cases} ({(boundary_cases / total_cases) * 100:.2f}%)")

    # Save top 10 cases to JSON
    topcasesjson(sorted_results)

    # Plot the coverage improvement over generations
    generations = list(range(1, gens + 1))
    plt.figure(figsize=(10, 5))
    plt.plot(generations, valid_coverage_list, label="Valid Cases Coverage", marker="o", linestyle="-")
    plt.plot(generations, invalid_coverage_list, label="Invalid Cases Coverage", marker="s", linestyle="--")
    plt.plot(generations, boundary_coverage_list, label="Boundary Cases Coverage", marker="^", linestyle=":")

    plt.xlabel("Generations")
    plt.ylabel("Coverage Percentage")
    plt.title("Test Coverage Improvement Over Generations")
    plt.legend()
    plt.grid(True)
    plt.savefig("coverage_graph.png")
    plt.show()


# Run the genetic algorithm

filename="topcases"
if not os.path.exists(filename):
    with open(filename, "w") as file:
        json.dump([], file)  # Initialize with an empty list

def topcasesjson(sorted_results):
    top_10_cases = []

    for date, score in sorted_results[:10]:
        category = categorizeDate(tuple(map(int, date.split("/"))))
        top_10_cases.append({"date": date, "category": category, "fitness": score})

    # Write the top 10 test cases to the JSON file
    with open(filename, "w") as json_file:
        json.dump(top_10_cases, json_file, indent=4)


geneticAlgo()

