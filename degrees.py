import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target, True)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

checkedPeople = {}

def shortest_path(source, target, debug = False):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # START MY CODE
    # depth first search without utils
    # neighbors = neighbors_for_person(source)
    # if debug:
    #     print(neighbors)
    # neighbors = list(filter(lambda x: not x[1] in checkedPeople, neighbors))
    # if len(neighbors) == 0:
    #     return None
    
    # path = []
    # for neighbor in neighbors:
    #     checkedPeople[neighbor[1]] = True
    #     if neighbor[1] == target:
    #         return [neighbor]
    #     else:
    #         current_path = shortest_path(neighbor[1], target)
    #         if current_path and (len(path) == 0 or len(current_path) < len(path)):
    #             path = [neighbor] + current_path
    # return None if len(path) == 0 else path

    #breadth first search
    neighbors = neighbors_for_person(source)
    frontier = QueueFrontier()
    source_node = Node(source, None, None)
    for neighbor in neighbors:
        if not neighbor[1] in checkedPeople:
            if neighbor[1] == target:
                return [neighbor]
            frontier.add(Node(neighbor[1], source_node, neighbor[0]))
        checkedPeople[neighbor[1]] = True
    break_outer = False
    while True:
        if frontier.empty():
            return None
        else:
            if break_outer:
                break
            current_node = frontier.remove()
            if current_node.state == target:
                break
            else:
                node_neighbors = neighbors_for_person(current_node.state)
                for neighbor in node_neighbors:
                    if not neighbor[1] in checkedPeople:
                        new_node = Node(neighbor[1], current_node, neighbor[0])
                        # commented line below added to frontier, but should check if node is target before adding to save time
                        #frontier.add(Node(neighbor[1], current_node, neighbor[0]))
                        frontier.add(new_node)
                        if new_node.state == target:
                            current_node = new_node
                            break_outer = True
                            break
                    checkedPeople[neighbor[1]] = True
    pair_list = []
    while current_node:
        pair_list = [(current_node.action, current_node.state)] + pair_list
        current_node = current_node.parent
    return pair_list[1:]

    # END MY CODE




def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
