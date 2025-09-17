from collections import deque

INITIAL_STATE = (
  "bar",  # Waiter location: "bar", "table1", "table2", "table3", "table4"
  False,  # Waiter tray: False, True
  (),  # Waiter inventory: (("tableX", "cold"|"hot"), ...)
  (("table1", "cold"), ("table2", "hot")),  # Orders: (("tableX", "cold"|"hot"), ...)
  (),  # Prepared drinks: (("tableX", "cold"|"hot"), ...)
  ("table3", "table4"),  # Tables to clean: ("tableX", ...)
)

# Distances between locations [meters]
LOCATIONS_DISTANCE = {
  ("bar", "table1"): 2,
  ("bar", "table2"): 2,
  ("bar", "table3"): 3,
  ("bar", "table4"): 3,
  ("table1", "table2"): 1,
  ("table2", "table3"): 1,
  ("table3", "table4"): 1,
  ("table4", "table1"): 1,
}


def get_distance(location1, location2):
  if location1 == location2:
    return 0

  if (location1, location2) in LOCATIONS_DISTANCE:
    return LOCATIONS_DISTANCE[(location1, location2)]

  if (location2, location1) in LOCATIONS_DISTANCE:
    return LOCATIONS_DISTANCE[(location2, location1)]

  return 1  # fallback


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
  if location == "bar":
    for i, drink in enumerate(orders):
      drink_kind = drink[1]
      cost = 3 if drink_kind == "cold" else 5
      new_orders = orders[:i] + orders[i + 1 :]  # Remove from orders
      new_prepared = prepared + (drink,)  # Add to prepared
      new_state = (location, tray, inventory, new_orders, new_prepared, tables_to_clean)
      result.append((new_state, f"prepare drink: {drink}", cost))

  # 2. Waiter can walk to another location
  possible_locations = ["bar", "table1", "table2", "table3", "table4"]
  for new_location in possible_locations:
    if new_location != location:
      speed = 1 if tray else 2
      dist = get_distance(location, new_location)
      cost = dist / speed
      new_state = (new_location, tray, inventory, orders, prepared, tables_to_clean)
      result.append((new_state, f"go: {new_location}", cost))

  # 3. Waiter can take or return the tray
  if location == "bar" and not tray:
    new_state = (location, True, inventory, orders, prepared, tables_to_clean)
    result.append((new_state, "take tray", 1))
  if location == "bar" and tray:
    new_state = (location, False, inventory, orders, prepared, tables_to_clean)
    result.append((new_state, "return tray", 1))

  # 4. Waiter can pickup drinks from the bar without a tray
  if location == "bar" and not tray and len(inventory) == 0:
    for i, drink in enumerate(prepared):
      new_prepared = prepared[:i] + prepared[i + 1 :]
      new_inventory = inventory + (drink,)
      new_state = (location, tray, new_inventory, orders, new_prepared, tables_to_clean)
      result.append((new_state, f"pickup drink: {drink}", 1))

  # 5. Waiter can pickup drinks from the bar with a tray
  if location == "bar" and tray and len(inventory) < 3:
    pass

  # 6. Waiter can deliver drinks if he is at the right table
  if len(inventory) > 0:
    for i, drink in enumerate(inventory):
      table, kind = drink
      if location == table:
        new_inventory = inventory[:i] + inventory[i + 1 :]
        new_state = (location, tray, new_inventory, orders, prepared, tables_to_clean)
        result.append((new_state, f"deliver drink:{drink}", 1))

  # 7. Waiter can clean dirty tables
  if not tray and len(inventory) == 0:
    for i, table in enumerate(tables_to_clean):
      if location == table:
        new_tables = tables_to_clean[:i] + tables_to_clean[i + 1 :]
        new_state = (location, tray, inventory, orders, prepared, new_tables)
        result.append((new_state, f"clean table: {table}", 1))
        break

  return result


def BFS(initial_state):
  queue = deque()
  queue.append((initial_state, [], 0))  # (state, actions steps, total cost)

  visited = set()  # Visited nodes

  while queue:
    state, actions, total_cost = queue.popleft()

    if goal(state):
      return visited, actions, total_cost

    if state in visited:
      continue

    visited.add(state)

    for new_state, new_action, new_cost in state_actions(state):
      queue.append((new_state, actions + [new_action], total_cost + new_cost))

  return None


def main():
  visited, actions, cost = BFS(INITIAL_STATE)

  print(f"Visited nodes: {len(visited)}")
  print(f"Total Cost: {cost}")

  print("Steps:")
  for step in actions:
    print(f" - {step}")


if __name__ == "__main__":
  main()
