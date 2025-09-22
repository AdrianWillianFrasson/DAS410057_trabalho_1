import heapq
import itertools
from time import perf_counter

# Action Durations
TIME_TO_MAKE_COLD = 3.0
TIME_TO_MAKE_HOT = 5.0
TIME_TO_PICKUP = 1.0
TIME_TO_DELIVER = 1.0

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


def canonical_state(state):
  """Converts the state to a consistent, hashable format."""
  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  return (
    time,
    tuple(sorted(b_status)),
    tuple(sorted(w_status)),
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

  # 1. Find the time of the next event -----------------------------------------
  b_finish_time = b_status[2] if b_status[0] != "idle" else float("inf")
  w_finish_time = w_status[2] if w_status[0] != "idle" else float("inf")
  next_event_time = min(b_finish_time, w_finish_time)

  if next_event_time == float("inf"):
    next_event_time = current_time

  # 2. Update world state based on events that just finished -------------------
  new_prep = list(prepared)
  new_w_loc = location
  new_w_inv = inventory
  # new_delivered = list(delivered)

  if b_status[2] == next_event_time:
    # 2.1 Barista finishes making a drink
    if b_status[0] == "making":
      new_prep.append(b_status[1])

  if w_status[2] == next_event_time:
    # 2.2 Waiter finishes moving
    if w_status[0] == "moving":
      new_w_loc = w_status[1]

    # 2.3 Waiter finishes picking up a drink
    elif w_status[0] == "picking_up":
      new_w_inv = w_status[1]

    # 2.4 Waiter finishes delivering a drink
    # elif w_status[0] == "delivering":
    #   new_delivered.append(w_status[1])
    #   new_w_inv = None

  # 3. Generate new possible tasks for newly free robots -----------------------
  barista_is_free = b_status[2] <= next_event_time
  waiter_is_free = w_status[2] <= next_event_time

  possible_b_tasks = get_barista_actions(next_event_time, orders) if barista_is_free else [b_status]
  possible_w_tasks = (
    get_waiter_actions(next_event_time, new_w_loc, new_w_inv, new_prep)
    if waiter_is_free
    else [w_status]
  )

  # --- 4. Create successor states for each combination of actions ---
  successors = []

  for b_task in possible_b_tasks:
    temp_orders = list(orders)

    if barista_is_free and b_task[0] == "making":
      temp_orders.remove(b_task[1])

    for w_task in possible_w_tasks:
      temp_prep = list(new_prep)

      if waiter_is_free and w_task[0] == "picking_up":
        temp_prep.remove(w_task[1])

      action_desc = (
        f"[Time: {next_event_time:.1f}] "
        f"B:{b_task[0]}({b_task[1] or ''}) "
        f"W:{w_task[0]}({w_task[1] or ''}) @ {new_w_loc}"
      )

      new_state = (
        next_event_time,
        new_w_loc,
        new_w_inv,
        tuple(temp_orders),
        tuple(temp_prep),
        tuple(new_delivered),
        b_task,
        w_task,
      )

      successors.append((new_state, action_desc))

  return successors


def get_barista_actions(current_time, orders):
  """Returns a list of possible actions for an idle barista."""
  if not orders:
    return [("idle", None, current_time)]

  tasks = []
  for drink in orders:  # barista can choose ANY pending order
    prep_time = TIME_TO_MAKE_COLD if drink[1] == "cold" else TIME_TO_MAKE_HOT
    tasks.append(("making", drink, current_time + prep_time))
  return tasks


def get_waiter_actions(current_time, location, inventory, prepared):
  """Returns a list of all possible actions for an idle waiter."""
  actions = []

  # Move
  for dest in ["bar", "table1", "table2"]:
    if location != dest:
      actions.append(("moving", dest, current_time + get_distance(location, dest)))

  # Pick up drink
  if location == "bar" and inventory is None:
    for drink in prepared:
      actions.append(("picking_up", drink, current_time + TIME_TO_PICKUP))

  # Deliver drink
  if inventory is not None and location == inventory[0]:
    actions.append(("delivering", inventory, current_time + TIME_TO_DELIVER))

  # Idle only if truly no task
  if not actions:
    actions.append(("idle", None, current_time))

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
  counter = itertools.count()  # tie-breaker

  frontier = [(0.0, next(counter), initial_state, [])]
  visited = {canonical_state(initial_state)}

  while frontier:
    total_time, _, state, path = heapq.heappop(frontier)

    if goal(state):
      return total_time, visited, path

    for next_state, next_path in get_next_states(state):
      canon_next_state = canonical_state(next_state)

      if canon_next_state not in visited:
        visited.add(canon_next_state)
        next_time = next_state[0]
        heapq.heappush(frontier, (next_time, next(counter), next_state, path + [next_path]))

  return float("inf"), None, None


def main():
  initial_state = (
    0.0,  # Global time
    ("idle", None, 0.0),  # Barista status: ("idle"|"action", ..., remaining_time)
    ("idle", None, 0.0),  # Waiter status: ("idle"|"action", ..., remaining_time)
    "bar",  # Waiter location: "bar", "table1", "table2", "table3", "table4"
    False,  # Waiter tray: False, True
    (),  # Waiter inventory: (("tableX", "cold"|"hot"), ...)
    (
      ("table1", "cold"),
      ("table1", "hot"),
      ("table1", "hot"),
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
