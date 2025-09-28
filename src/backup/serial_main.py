from time import perf_counter
from serial_search_algorithm import BFS, UCS, A_star


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


def get_desc(time, action, data, cost):
  return f"{time:^8} | {f'{action}, {data}, {time + cost}':<35}"


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


def state_actions(state, time):
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
    result.append((cost, new_state, get_desc(time, "Barista: making", drink, cost)))

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
      result.append((cost, new_state, get_desc(time, "Waiter: moving", new_location, cost)))

  # 3. Waiter can take or return the tray
  if not tray and location == "bar" and len(inventory) == 0:
    cost = 0.0
    new_state = canonical_state((location, True, inventory, orders, prepared, tables_to_clean))
    result.append((cost, new_state, get_desc(time, "Waiter: take_tray", True, cost)))
  if tray and location == "bar" and len(inventory) == 0:
    cost = 0.0
    new_state = canonical_state((location, False, inventory, orders, prepared, tables_to_clean))
    result.append((cost, new_state, get_desc(time, "Waiter: return_tray", False, cost)))

  # 4. Waiter can pickup drinks from the bar without a tray
  if location == "bar" and not tray and len(inventory) == 0:
    cost = 1.0
    for i, drink in enumerate(prepared):
      new_prepared = prepared[:i] + prepared[i + 1 :]
      new_inventory = inventory + (drink,)
      new_state = canonical_state(
        (location, tray, new_inventory, orders, new_prepared, tables_to_clean)
      )
      result.append((cost, new_state, get_desc(time, "Waiter: picking_up", drink, cost)))

  # 5. Waiter can pickup drinks from the bar with a tray
  if location == "bar" and tray and len(inventory) < 3:
    cost = 1.0
    for i, drink in enumerate(prepared):
      new_prepared = prepared[:i] + prepared[i + 1 :]
      new_inventory = inventory + (drink,)
      new_state = canonical_state(
        (location, tray, new_inventory, orders, new_prepared, tables_to_clean)
      )
      result.append((cost, new_state, get_desc(time, "Waiter: picking_up", drink, cost)))

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
        result.append((cost, new_state, get_desc(time, "Waiter: delivering", drink, cost)))

  # 7. Waiter can clean dirty tables
  if location in tables_to_clean and not tray and len(inventory) == 0:
    cost = 4.0 if location == "table3" else 2.0
    new_tables = tuple(t for t in tables_to_clean if t != location)
    new_state = canonical_state((location, tray, inventory, orders, prepared, new_tables))
    result.append((cost, new_state, get_desc(time, "Waiter: cleaning", location, cost)))

  return result


def main():
  initial_state = canonical_state(
    (
      "bar",  # Waiter location: "bar", "table1", "table2", "table3", "table4"
      False,  # Waiter tray: False, True
      (),  # Waiter inventory: (("tableX", "cold"|"hot"), ...)
      (
        ("table4", "cold"),
        ("table4", "cold"),
        ("table1", "cold"),
        ("table1", "cold"),
        ("table3", "hot"),
        ("table3", "hot"),
        ("table3", "hot"),
        ("table3", "hot"),
      ),  # Orders: (("tableX", "cold"|"hot"), ...)
      (),  # Prepared drinks: (("tableX", "cold"|"hot"), ...)
      ("table2",),  # Tables to clean: ("tableX", ...)
    )
  )

  time_start = perf_counter()
  cost, visited, actions = A_star(initial_state, goal, state_actions)
  # cost, visited, actions = UCS(initial_state, goal, state_actions)
  # cost, visited, actions = BFS(initial_state, goal, state_actions)
  time_end = perf_counter()

  print(f"Execution time: {time_end - time_start:.4f} [s]")
  print(f"Number of nodes: {len(visited)}")
  print(f"Path total time: {cost} [s]")

  print("Steps:")
  print(f"{'Time [s]':^8} | {'Robots Actions (act., desc., end time)':<30}")
  print("-" * 60)
  for step in actions:
    print(step)
  print(get_desc(cost, "idle", None, 0.0))


if __name__ == "__main__":
  main()
