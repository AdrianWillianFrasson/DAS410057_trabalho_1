import heapq
from collections import deque

from constants import (
  TIME_TO_CLEAN_BIG,
  TIME_TO_CLEAN_SMALL,
  TIME_TO_DELIVER,
  TIME_TO_MAKE_COLD,
  TIME_TO_MAKE_HOT,
)


def canonical_state(state):
  """Converts the state to a consistent, hashable format."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  return (
    b_status,
    w_status,
    location,
    tray,
    tuple(sorted(inventory)),
    tuple(sorted(orders)),
    tuple(sorted(prepared)),
    tuple(sorted(tables_to_clean)),
  )


# A* Search ----------------------------------------------------------------------------------------
def A_star(initial_state, goal, get_next_states):
  """Finds the fastest plan using A* search."""

  # Priority queue: (f = g + h, g = elapsed_time, state, path)
  frontier = [(heuristic(initial_state), 0.0, initial_state, [])]
  visited = {canonical_state(initial_state): 0.0}

  while frontier:
    f, g, state, path = heapq.heappop(frontier)

    if goal(state):
      return g, visited, path

    for next_state, next_path in get_next_states(state):
      canon_next_state = canonical_state(next_state)
      next_time = next_state[0]

      if canon_next_state not in visited or visited[canon_next_state] > next_time:
        visited[canon_next_state] = next_time
        h = heuristic(next_state)
        heapq.heappush(frontier, (next_time + h, next_time, next_state, path + [next_path]))

  return float("inf"), None, None


def heuristic(state):
  """Estimates the remaining time to reach the goal from the current state."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  h = 0.0

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
  """Estimates the remaining time to reach the goal from the current state."""
  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  h = len(inventory) + len(orders) + len(prepared) + len(tables_to_clean)

  if (orders or prepared or inventory) and location != "bar":
    h += 1

  return h


def heuristic3(state):
  """Estimates the remaining time to reach the goal from the current state."""

  time, b_status, w_status, location, tray, inventory, orders, prepared, tables_to_clean = state

  h = 0.0

  # Drinks to make
  if orders:
    h += len(orders) * min(TIME_TO_MAKE_COLD, TIME_TO_MAKE_HOT)

  # Drinks to deliver (either already prepared or in inventory)
  total_drinks = len(prepared) + len(inventory)
  if total_drinks > 0:
    h += total_drinks * TIME_TO_DELIVER

  # Tables to clean
  if tables_to_clean:
    # optimistic: assume all small tables
    h += len(tables_to_clean) * min(TIME_TO_CLEAN_BIG, TIME_TO_CLEAN_SMALL)

  return h


# Uniform-Cost Search ------------------------------------------------------------------------------
def UCS(initial_state, goal, get_next_states):
  """Finds the fastest plan using Uniform-Cost Search (UCS)."""

  frontier = [(0.0, initial_state, [])]
  visited = {canonical_state(initial_state): 0.0}

  while frontier:
    total_time, state, path = heapq.heappop(frontier)

    if goal(state):
      return total_time, visited, path

    for next_state, next_path in get_next_states(state):
      canon_next_state = canonical_state(next_state)
      next_time = next_state[0]

      if canon_next_state not in visited or visited[canon_next_state] > next_time:
        visited[canon_next_state] = next_time
        heapq.heappush(frontier, (next_time, next_state, path + [next_path]))

  return float("inf"), None, None


# Breadth-First Search -----------------------------------------------------------------------------
def BFS(initial_state, goal, get_next_states):
  """Finds the fewest action steps using Breadth-First Search (BFS)."""

  frontier = deque()
  frontier.append((initial_state, []))

  visited = {canonical_state(initial_state)}

  while frontier:
    state, path = frontier.popleft()

    if goal(state):
      return state[0], visited, path

    for next_state, next_path in get_next_states(state):
      canon_next_state = canonical_state(next_state)

      if canon_next_state not in visited:
        visited.add(canon_next_state)
        frontier.append((next_state, path + [next_path]))

  return float("inf"), None, None
