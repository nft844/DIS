import pandas as pd

actors = pd.read_csv("movie_actors.csv")
people = pd.read_csv("people.csv")

actors_ids = set(actors["person_id"])
people_ids = set(people["person_id"])

# Hvor mange actors findes også i people?
intersection = actors_ids & people_ids

print("Antal actors:", len(actors_ids))
print("Antal people:", len(people_ids))
print("Overlap:", len(intersection))

# Hvor mange mangler?
missing = actors_ids - people_ids
print("Actors uden navn:", len(missing))

# Vis nogle af dem der mangler
missing_list = list(missing)[:10]
print("Eksempel på manglende IDs:", missing_list)