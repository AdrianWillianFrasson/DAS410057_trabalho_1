import itertools
from time import perf_counter

from constants import (
  LOCATIONS_DISTANCE,
  SPEED_WITH_TRAY,
  SPEED_WITHOUT_TRAY,
  TIME_TO_CLEAN_BIG,
  TIME_TO_CLEAN_SMALL,
  TIME_TO_DELIVER,
  TIME_TO_MAKE_COLD,
  TIME_TO_MAKE_HOT,
  TIME_TO_PICKUP,
  TIME_TO_RETURN_TRAY,
  TIME_TO_TAKE_TRAY,
)
from search_algorithm import BFS, UCS, A_star


def get_distance(location1, location2):
  """Returns the distance between two locations."""

  if location1 == location2:
    return 0

  if (location1, location2) in LOCATIONS_DISTANCE:
    return LOCATIONS_DISTANCE[(location1, location2)]

  if (location2, location1) in LOCATIONS_DISTANCE:
    return LOCATIONS_DISTANCE[(location2, location1)]

  raise ValueError(f"No distance defined between {location1} and {location2}")


def get_next_states(state):
  """Generates all possible successor states from the current state."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  b_action, b_action_data, b_finish_time = b_status
  w_action, w_action_data, w_finish_time = w_status

  # 1. Find the time of the next event -----------------------------------------
  next_event_time = min(
    b_finish_time if b_action != "idle" else float("inf"),
    w_finish_time if w_action != "idle" else float("inf"),
  )

  if next_event_time == float("inf"):
    next_event_time = time

  # 2. Update world state based on events that just finished -------------------
  new_tray = tray
  new_location = location
  new_orders = list(orders)
  new_prepared = list(prepared)
  new_inventory = list(inventory)
  new_tables_to_clean = list(tables_to_clean)

  if b_finish_time == next_event_time:
    # Barista finishes making a drink
    if b_action == "making":
      new_orders.remove(b_action_data)
      new_prepared.append(b_action_data)

  if w_finish_time == next_event_time:
    # Waiter finishes moving
    if w_action == "moving":
      new_location = w_action_data

    # Waiter finishes taking the tray
    elif w_action == "take_tray" or w_action == "return_tray":
      new_tray = w_action_data

    # Waiter finishes picking up a drink
    elif w_action == "picking_up":
      new_prepared.remove(w_action_data)
      new_inventory.append(w_action_data)

    # Waiter finishes delivering a drink
    elif w_action == "delivering":
      new_inventory.remove(w_action_data)

    # Waiter finishes cleaning a table
    elif w_action == "cleaning":
      new_tables_to_clean.remove(w_action_data)

  # 3. Generate new possible tasks for newly free robots -----------------------
  b_is_free = b_finish_time <= next_event_time
  w_is_free = w_finish_time <= next_event_time

  new_state = (
    next_event_time,
    b_status,
    w_status,
    new_location,
    new_tray,
    tuple(new_inventory),
    tuple(new_orders),
    tuple(new_prepared),
    tuple(new_tables_to_clean),
  )

  possible_b_tasks = get_barista_actions(new_state) if b_is_free else [b_status]
  possible_w_tasks = get_waiter_actions(new_state) if w_is_free else [w_status]

  # 4. Create successor states for each combination of tasks -------------------
  successors = []

  for b_task, w_task in itertools.product(possible_b_tasks, possible_w_tasks):
    next_state = (
      next_event_time,
      b_task,
      w_task,
      new_location,
      new_tray,
      tuple(new_inventory),
      tuple(new_orders),
      tuple(new_prepared),
      tuple(new_tables_to_clean),
    )

    next_path = f"{next_event_time:^8} | {f'{b_task[0]}, {b_task[1]}, {b_task[2]}':<35} | {f'{w_task[0]}, {w_task[1]}, {w_task[2]}':<35}"

    successors.append((next_state, next_path))

  return successors


def get_barista_actions(state):
  """Returns a list of possible actions for an idle barista."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  actions = []

  # Barista can make drinks
  for drink in orders:
    drink_table, drink_kind = drink
    cost = TIME_TO_MAKE_COLD if drink_kind == "cold" else TIME_TO_MAKE_HOT
    actions.append(("making", drink, time + cost))

  # Barista can idle if there is nothing else to do
  if len(orders) == 0:
    actions.append(("idle", None, time))

  return actions


def get_waiter_actions(state):
  """Returns a list of possible actions for an idle waiter."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  actions = []

  # Waiter can take or return the tray
  if not tray and location == "bar" and len(inventory) == 0:
    cost = TIME_TO_TAKE_TRAY
    actions.append(("take_tray", True, time + cost))
  if tray and location == "bar" and len(inventory) == 0:
    cost = TIME_TO_RETURN_TRAY
    actions.append(("return_tray", False, time + cost))

  # Waiter can pickup drinks from the bar
  if location == "bar" and ((not tray and len(inventory) == 0) or (tray and len(inventory) < 3)):
    cost = TIME_TO_PICKUP
    for drink in prepared:
      actions.append(("picking_up", drink, time + cost))

  # Waiter can deliver drinks if he is at the right table
  if len(inventory) > 0:
    cost = TIME_TO_DELIVER
    for drink in inventory:
      drink_table, drink_kind = drink
      if drink_table == location:
        actions.append(("delivering", drink, time + cost))

  # Waiter can clean dirty tables
  if location in tables_to_clean and not tray and len(inventory) == 0:
    cost = TIME_TO_CLEAN_BIG if location == "table3" else TIME_TO_CLEAN_SMALL
    actions.append(("cleaning", location, time + cost))

  # Waiter can walk to another location
  relevant = set(["bar"])
  for drink in inventory:
    relevant.add(drink[0])
  for table in tables_to_clean:
    relevant.add(table)

  for destination in ["bar", "table1", "table2", "table3", "table4"]:
    if destination != location and destination in relevant:
      speed = SPEED_WITH_TRAY if tray else SPEED_WITHOUT_TRAY
      dist = get_distance(location, destination)
      cost = dist / speed
      actions.append(("moving", destination, time + cost))

  # Waiter can idle if there is nothing else to do
  if not tray and len(prepared) == 0 and len(inventory) == 0 and len(tables_to_clean) == 0:
    actions.append(("idle", None, time))

  return actions


def goal(state):
  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  return (
    not tray
    and len(orders) == 0
    and len(prepared) == 0
    and len(inventory) == 0
    and len(tables_to_clean) == 0
    and b_status[0] == "idle"
    and w_status[0] == "idle"
  )


def main():
  initial_state = (
    0.0,  # Global time
    ("idle", None, 0.0),  # Barista status: ("idle"|"action", ..., finish_time)
    ("idle", None, 0.0),  # Waiter status: ("idle"|"action", ..., finish_time)
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

  time_start = perf_counter()
  total_time, visited, path = A_star(initial_state, goal, get_next_states)
  # total_time, visited, path = UCS(initial_state, goal, get_next_states)
  # total_time, visited, path = BFS(initial_state, goal, get_next_states)
  time_end = perf_counter()

  print(f"Execution time: {time_end - time_start:.4f} [s]")
  print(f"Number of nodes: {len(visited)}")
  print(f"Path total time: {total_time} [s]")

  print("Steps:")
  print(
    f"{'Time [s]':^8} | {'Barista (act., desc., end time)':<35} | Waiter (act., desc., end time)"
  )
  print("-" * 80)
  for step in path:
    print(step)


if __name__ == "__main__":
  main()
