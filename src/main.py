import time
from search_algorithm import BFS, UCS, A_star


def canonical_state(state):
  location, tray, inventory, orders, prepared, tables_to_clean = state

  return (
    location,
    tray,
    tuple(sorted(inventory)),
    tuple(sorted(orders)),
    tuple(sorted(prepared)),
    tuple(sorted(tables_to_clean)),
  )


# Distances between locations [meters]
LOCATIONS_DISTANCE = {
  ("bar", "table1"): 2,
  ("bar", "table2"): 2,
  ("bar", "table3"): 3,
  ("bar", "table4"): 3,
  ("table1", "table2"): 1,
  ("table1", "table3"): 1,
  ("table1", "table4"): 1,
  ("table2", "table3"): 1,
  ("table2", "table4"): 1,
  ("table3", "table4"): 1,
}


def get_distance(location1, location2):
  if location1 == location2:
    return 0

  if (location1, location2) in LOCATIONS_DISTANCE:
    return LOCATIONS_DISTANCE[(location1, location2)]

  if (location2, location1) in LOCATIONS_DISTANCE:
    return LOCATIONS_DISTANCE[(location2, location1)]

  raise ValueError(f"No distance defined between {location1} and {location2}")


def goal(state):
  location, tray, inventory, orders, prepared, tables_to_clean = state

  return (
    not tray
    and len(orders) == 0
    and len(prepared) == 0
    and len(inventory) == 0
    and len(tables_to_clean) == 0
  )


def state_actions(state):
  location, tray, inventory, orders, prepared, tables_to_clean = state
  result = []

  # 1. Barista can preper drinks (if there is any pending orders)
  for i, drink in enumerate(orders):
    drink_kind = drink[1]
    cost = 3.0 if drink_kind == "cold" else 5.0
    new_orders = orders[:i] + orders[i + 1 :]
    new_prepared = prepared + (drink,)
    new_state = canonical_state(
      (location, tray, inventory, new_orders, new_prepared, tables_to_clean)
    )
    result.append((cost, new_state, f"[{cost}] prepare drink: {drink}"))

  # 2. Waiter can walk to another location
  possible_locations = ["bar", "table1", "table2", "table3", "table4"]
  for new_location in possible_locations:
    if new_location != location:
      speed = 1.0 if tray else 2.0
      dist = get_distance(location, new_location)
      cost = dist / speed
      new_state = canonical_state(
        (new_location, tray, inventory, orders, prepared, tables_to_clean)
      )
      result.append((cost, new_state, f"[{cost}] go: {new_location}"))

  # 3. Waiter can take or return the tray
  if not tray and location == "bar" and len(inventory) == 0:
    cost = 0.0
    new_state = canonical_state((location, True, inventory, orders, prepared, tables_to_clean))
    result.append((cost, new_state, f"[{cost}] take tray"))
  if tray and location == "bar" and len(inventory) == 0:
    cost = 0.0
    new_state = canonical_state((location, False, inventory, orders, prepared, tables_to_clean))
    result.append((cost, new_state, f"[{cost}] return tray"))

  # 4. Waiter can pickup drinks from the bar without a tray
  if location == "bar" and not tray and len(inventory) == 0:
    cost = 1.0
    for i, drink in enumerate(prepared):
      new_prepared = prepared[:i] + prepared[i + 1 :]
      new_inventory = inventory + (drink,)
      new_state = canonical_state(
        (location, tray, new_inventory, orders, new_prepared, tables_to_clean)
      )
      result.append((cost, new_state, f"[{cost}] pickup drink: {drink}"))

  # 5. Waiter can pickup drinks from the bar with a tray
  if location == "bar" and tray and len(inventory) < 3:
    cost = 1.0
    for i, drink in enumerate(prepared):
      new_prepared = prepared[:i] + prepared[i + 1 :]
      new_inventory = inventory + (drink,)
      new_state = canonical_state(
        (location, tray, new_inventory, orders, new_prepared, tables_to_clean)
      )
      result.append(
        (cost, new_state, f"[{cost}] pickup drink (tray - {len(new_inventory)}): {drink}")
      )

  # 6. Waiter can deliver drinks if he is at the right table
  if len(inventory) > 0:
    cost = 1.0
    for i, drink in enumerate(inventory):
      table, kind = drink
      if location == table:
        new_inventory = inventory[:i] + inventory[i + 1 :]
        new_state = canonical_state(
          (location, tray, new_inventory, orders, prepared, tables_to_clean)
        )
        result.append((cost, new_state, f"[{cost}] deliver drink: {drink}"))

  # 7. Waiter can clean dirty tables
  if location in tables_to_clean and not tray and len(inventory) == 0:
    cost = 4.0 if location == "table3" else 2.0
    new_tables = tuple(t for t in tables_to_clean if t != location)
    new_state = canonical_state((location, tray, inventory, orders, prepared, new_tables))
    result.append((cost, new_state, f"[{cost}] clean table: {location}"))

  return result


def main():
  initial_state = canonical_state(
    (
      "bar",  # Waiter location: "bar", "table1", "table2", "table3", "table4"
      False,  # Waiter tray: False, True
      (),  # Waiter inventory: (("tableX", "cold"|"hot"), ...)
      (
        ("table1", "cold"),
        ("table1", "hot"),
        ("table1", "hot"),
      ),  # Orders: (("tableX", "cold"|"hot"), ...)
      (),  # Prepared drinks: (("tableX", "cold"|"hot"), ...)
      ("table3", "table4"),  # Tables to clean: ("tableX", ...)
    )
  )

  time_start = time.perf_counter()
  # cost, visited, actions = A_star(initial_state, goal, state_actions)
  # cost, visited, actions = UCS(initial_state, goal, state_actions)
  cost, visited, actions = BFS(initial_state, goal, state_actions)
  time_end = time.perf_counter()

  print(f"Time: {time_end - time_start:.4f} seconds")
  print(f"Number of nodes: {len(visited)}")
  print(f"Total cost: {cost}")

  print("Steps:")
  for step in actions:
    print(f" - {step}")


if __name__ == "__main__":
  main()
