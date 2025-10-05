import heapq
from collections import deque


# A* Search ----------------------------------------------------------------------------------------
def A_star(initial_state, goal, state_actions):
  frontier = []
  # (f = h + total_cost, total_cost, state, actions_steps)
  heapq.heappush(frontier, (heuristic(initial_state), 0.0, initial_state, []))

  visited = {}

  while frontier:
    f, total_cost, state, actions = heapq.heappop(frontier)

    if goal(state):
      return total_cost, visited, actions

    if state in visited and visited[state] <= total_cost:
      continue

    visited[state] = total_cost

    for new_cost, new_state, new_action in state_actions(state, total_cost):
      new_total_cost = total_cost + new_cost
      new_f = heuristic(new_state) + new_total_cost

      heapq.heappush(frontier, (new_f, new_total_cost, new_state, actions + [new_action]))

  return None


def heuristic(state):
  location, tray, inventory, orders, prepared, tables_to_clean = state
  h = 0

  # 1. Estimate prep time for pending orders
  for _, kind in orders:
    h += 3 if kind == "cold" else 5

  # 2. Each dirty table cleaning cost
  for table in tables_to_clean:
    h += 4 if table == "table3" else 2

  # 3. If drinks left to deliver or prepare, assume we must move at least once
  if (orders or prepared or inventory) and location != "bar":
    h += 1

  return h


def heuristic2(state):
  location, _, inventory, orders, prepared, tables_to_clean = state
  h = len(inventory) + len(orders) + len(prepared) + len(tables_to_clean)

  if (orders or prepared or inventory) and location != "bar":
    h += 1

  return h


# Uniform-Cost Search ------------------------------------------------------------------------------
def UCS(initial_state, goal, state_actions):
  frontier = []
  heapq.heappush(frontier, (0.0, initial_state, []))  # (total_cost, state, actions_steps)

  visited = {}

  while frontier:
    total_cost, state, actions = heapq.heappop(frontier)

    if goal(state):
      return total_cost, visited, actions

    # If we've already seen this state with a lower cost, skip
    if state in visited and visited[state] <= total_cost:
      continue

    visited[state] = total_cost

    for new_cost, new_state, new_action in state_actions(state, total_cost):
      heapq.heappush(frontier, (total_cost + new_cost, new_state, actions + [new_action]))

  return None


# Breadth-First Search -----------------------------------------------------------------------------
def BFS(initial_state, goal, state_actions):
  queue = deque()
  queue.append((0.0, initial_state, []))  # (total_cost, state, actions_steps)

  visited = set()  # Visited nodes

  while queue:
    total_cost, state, actions = queue.popleft()

    if goal(state):
      return total_cost, visited, actions

    if state in visited:
      continue

    visited.add(state)

    for new_cost, new_state, new_action in state_actions(state, total_cost):
      queue.append((total_cost + new_cost, new_state, actions + [new_action]))

  return None
