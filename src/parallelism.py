import heapq
import itertools
from time import perf_counter

# Actions duration [seconds]
TIME_TO_MAKE_COLD = 3.0
TIME_TO_MAKE_HOT = 5.0
TIME_TO_PICKUP = 1.0
TIME_TO_DELIVER = 1.0
TIME_TO_TAKE_TRAY = 0.1
TIME_TO_RETURN_TRAY = 0.1
SPEED_WITH_TRAY = 1.0
SPEED_WITHOUT_TRAY = 2.0

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
  """Returns the distance between two locations."""
  if location1 == location2:
    return 0

  if (location1, location2) in LOCATIONS_DISTANCE:
    return LOCATIONS_DISTANCE[(location1, location2)]

  if (location2, location1) in LOCATIONS_DISTANCE:
    return LOCATIONS_DISTANCE[(location2, location1)]

  raise ValueError(f"No distance defined between {location1} and {location2}")


def canonical_state(state):
  """Converts the state to a consistent, hashable format."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  return (
    time,
    b_status,
    w_status,
    location,
    tray,
    tuple(sorted(inventory)),
    tuple(sorted(orders)),
    tuple(sorted(prepared)),
    tuple(sorted(tables_to_clean)),
  )


def get_next_states(state):
  """Generates all possible successor states from the current state."""

  current_time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = (
    state
  )

  b_action, b_action_data, b_finish_time = b_status
  w_action, w_action_data, w_finish_time = w_status

  # 1. Find the time of the next event -----------------------------------------
  next_event_time = min(
    b_finish_time if b_action != "idle" else float("inf"),
    w_finish_time if w_action != "idle" else float("inf"),
  )

  if next_event_time == float("inf"):
    next_event_time = current_time

  # 2. Update world state based on events that just finished -------------------
  new_tray = tray
  new_location = location
  new_orders = list(orders)
  new_prepared = list(prepared)
  new_inventory = list(inventory)

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

  # 3. Generate new possible tasks for newly free robots -----------------------
  b_is_free = b_action == "idle" or b_finish_time <= next_event_time
  w_is_free = w_action == "idle" or w_finish_time <= next_event_time

  new_state = canonical_state(
    (
      next_event_time,
      b_status,
      w_status,
      new_location,
      new_tray,
      new_inventory,
      new_orders,
      new_prepared,
      tables_to_clean,
    )
  )

  possible_b_tasks = get_barista_actions(new_state) if b_is_free else [b_status]
  possible_w_tasks = get_waiter_actions(new_state) if w_is_free else [w_status]

  # 4. Create successor states for each combination of actions -----------------
  successors = []

  for b_task, w_task in itertools.product(possible_b_tasks, possible_w_tasks):
    temp_orders = list(new_orders)
    temp_prepared = list(new_prepared)
    temp_inventory = list(new_inventory)

    if w_is_free and w_task[0] == "delivering":
      temp_inventory.remove(w_task[1])

    next_state = (
      next_event_time,
      b_task,
      w_task,
      new_location,
      new_tray,
      tuple(temp_inventory),
      tuple(temp_orders),
      tuple(temp_prepared),
      tables_to_clean,
    )

    next_path = (
      f"[Time: {next_event_time}] "
      f"B:{b_task[0]}({b_task[1]}) "
      f"W:{w_task[0]}({w_task[1]}) "
      f"state: {next_state} "
    )

    successors.append((next_state, next_path))

  return successors


def get_barista_actions(state):
  """Returns a list of possible actions for an idle barista."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  actions = [("idle", None, time)]

  # Barista can make drinks
  for drink in orders:
    drink_table, drink_kind = drink
    cost = TIME_TO_MAKE_COLD if drink_kind == "cold" else TIME_TO_MAKE_HOT
    actions.append(("making", drink, time + cost))

  return actions


def get_waiter_actions(state):
  """Returns a list of possible actions for an idle waiter."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  actions = [("idle", None, time)]

  # Waiter can walk to another location
  for destination in ["bar", "table1", "table2", "table3", "table4"]:
    if location != destination:
      speed = SPEED_WITH_TRAY if tray else SPEED_WITHOUT_TRAY
      dist = get_distance(location, destination)
      cost = dist / speed
      actions.append(("moving", destination, time + cost))

  # Waiter can take or return the tray
  # if not tray and location == "bar" and len(inventory) == 0:
  #   cost = TIME_TO_TAKE_TRAY
  #   actions.append(("take_tray", True, time + cost))
  # if tray and location == "bar" and len(inventory) == 0:
  #   cost = TIME_TO_RETURN_TRAY
  #   actions.append(("return_tray", False, time + cost))

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


def UCS(initial_state):
  """Finds the fastest plan using Uniform-Cost Search (UCS)."""

  frontier = [(0.0, canonical_state(initial_state), [])]
  visited = {canonical_state(initial_state)}

  while frontier:
    total_time, state, path = heapq.heappop(frontier)

    if goal(state):
      return total_time, visited, path

    for next_state, next_path in get_next_states(state):
      canon_next_state = canonical_state(next_state)

      if canon_next_state not in visited:
        visited.add(canon_next_state)
        next_time = next_state[0]
        heapq.heappush(frontier, (next_time, next_state, path + [next_path]))

  return float("inf"), None, None


def main():
  initial_state = (
    0.0,  # Global time
    ("idle", None, 0.0),  # Barista status: ("idle"|"action", ..., finish_time)
    ("idle", None, 0.0),  # Waiter status: ("idle"|"action", ..., finish_time)
    "bar",  # Waiter location: "bar", "table1", "table2", "table3", "table4"
    False,  # Waiter tray: False, True
    (),  # Waiter inventory: (("tableX", "cold"|"hot"), ...)
    (
      ("table1", "cold"),
      ("table2", "hot"),
    ),  # Orders: (("tableX", "cold"|"hot"), ...)
    (),  # Prepared drinks: (("tableX", "cold"|"hot"), ...)
    (),  # Tables to clean: ("tableX", ...)
  )

  time_start = perf_counter()
  total_time, visited, path = UCS(initial_state)
  time_end = perf_counter()

  print(f"Time: {time_end - time_start:.4f} seconds")
  print(f"Number of nodes: {len(visited)}")
  print(f"Total time: {total_time}")

  print("Steps:")
  for step in path:
    print(f" - {step}")


if __name__ == "__main__":
  main()
