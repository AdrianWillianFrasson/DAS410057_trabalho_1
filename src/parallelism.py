import heapq
import itertools

# --- Define Constants ---
# Action Durations
TIME_TO_MAKE_COLD = 3.0
TIME_TO_MAKE_HOT = 5.0
TIME_TO_PICKUP = 1.0
TIME_TO_DELIVER = 1.0

# Waiter Movement
TRAVEL_TIMES = {
  ("bar", "table1"): 2.0,
  ("bar", "table2"): 3.0,
  ("table1", "table2"): 1.0,
}


def get_travel_time(loc1, loc2):
  if loc1 == loc2:
    return 0.0
  if (loc1, loc2) in TRAVEL_TIMES:
    return TRAVEL_TIMES[(loc1, loc2)]
  return TRAVEL_TIMES[(loc2, loc1)]


def canonical_state(state):
  """Converts the state to a consistent, hashable format."""
  time, w_loc, w_inv, orders, prep, delivered, b_status, w_status = state
  return (
    time,
    w_loc,
    w_inv,
    tuple(sorted(orders)),
    tuple(sorted(prep)),
    tuple(sorted(delivered)),
    b_status,
    w_status,
  )


def get_next_states(state):
  """Generates all possible successor states from the current state."""
  current_time, w_loc, w_inv, orders, prep, delivered, b_status, w_status = state

  # --- 1. Find the time of the next event ---
  b_finish_time = b_status[2] if b_status[0] != "idle" else float("inf")
  w_finish_time = w_status[2] if w_status[0] != "idle" else float("inf")
  next_event_time = min(b_finish_time, w_finish_time)

  if next_event_time == float("inf"):
    next_event_time = current_time

  # --- 2. Update world state based on events that just finished ---
  new_prep = list(prep)
  new_w_loc = w_loc
  new_w_inv = w_inv
  new_delivered = list(delivered)

  # Barista finishes making a drink
  if b_status[0] == "making" and b_status[2] == next_event_time:
    new_prep.append(b_status[1])

  # Waiter finishes moving
  if w_status[0] == "moving" and w_status[2] == next_event_time:
    new_w_loc = w_status[1]

  # Waiter finishes picking up a drink
  if w_status[0] == "picking_up" and w_status[2] == next_event_time:
    new_w_inv = w_status[1]

  # Waiter finishes delivering a drink
  if w_status[0] == "delivering" and w_status[2] == next_event_time:
    new_delivered.append(w_status[1])
    new_w_inv = None

  # --- 3. Generate new possible tasks for newly free robots ---
  successors = []
  barista_is_free = b_status[2] <= next_event_time
  waiter_is_free = w_status[2] <= next_event_time

  possible_b_tasks = get_barista_actions(next_event_time, orders) if barista_is_free else [b_status]
  possible_w_tasks = (
    get_waiter_actions(next_event_time, new_w_loc, new_w_inv, new_prep)
    if waiter_is_free
    else [w_status]
  )

  # --- 4. Create successor states for each combination of actions ---
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
      actions.append(("moving", dest, current_time + get_travel_time(location, dest)))

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


def ucs_search(initial_state, all_orders):
  """Finds the fastest plan using Uniform-Cost Search (UCS)."""
  counter = itertools.count()  # tie-breaker
  frontier = [(0.0, next(counter), initial_state, [])]
  visited = {canonical_state(initial_state)}

  while frontier:
    total_time, _, current_state, path = heapq.heappop(frontier)

    time, w_loc, w_inv, orders, prep, delivered, b_status, w_status = current_state

    # --- Goal condition ---
    if set(delivered) == set(all_orders) and not w_inv:
      return path, total_time

    for next_state, action_desc in get_next_states(current_state):
      canon_next_state = canonical_state(next_state)
      if canon_next_state not in visited:
        visited.add(canon_next_state)
        next_time = next_state[0]
        heapq.heappush(frontier, (next_time, next(counter), next_state, path + [action_desc]))

  return None, float("inf")


# --- Main execution ---
if __name__ == "__main__":
  # State: (time, w_loc, w_inv, orders, prepared, delivered, b_status, w_status)
  initial_orders = (("table1", "hot"), ("table2", "cold"), ("table1", "hot"))
  initial_state = (
    0.0,  # time
    "bar",  # waiter location
    None,  # waiter inventory
    initial_orders,  # orders
    (),  # prepared drinks
    (),  # delivered drinks
    ("idle", None, 0.0),  # barista status
    ("idle", None, 0.0),  # waiter status
  )

  print(f"Starting with orders: {initial_orders}\n")

  plan, total_time = ucs_search(initial_state, initial_orders)

  if plan:
    print("Fastest plan found:")
    for step in plan:
      print(f"  - {step}")
    print(f"\nTotal time: {total_time:.1f} seconds.")
  else:
    print("Could not find a plan.")
