import heapq
from collections import deque


# A* Search ----------------------------------------------------------------------------------------
def A_star(initial_state, goal, state_actions, heuristic):
  frontier = []
  # (f = h + total_cost, total_cost, state, actions_steps)
  heapq.heappush(frontier, (heuristic(initial_state), 0, initial_state, []))

  visited = {}

  while frontier:
    f, total_cost, state, actions = heapq.heappop(frontier)

    if goal(state):
      return total_cost, visited, actions

    if state in visited and visited[state] <= total_cost:
      continue

    visited[state] = total_cost

    for new_cost, new_state, new_action in state_actions(state):
      new_total_cost = total_cost + new_cost
      new_f = heuristic(new_state) + new_total_cost

      heapq.heappush(frontier, (new_f, new_total_cost, new_state, actions + [new_action]))

  return None


def heuristic_v1(state):
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

def heuristic_v2(state):
    location, _, inventory, orders, prepared, tables_to_clean = state
    h = len(inventory) + len(orders) + len(prepared) + len(tables_to_clean)
    if orders or prepared or inventory:
        if location != "bar":
            h += 1
    return h

# Uniform-Cost Search ------------------------------------------------------------------------------
def UCS(initial_state, goal, state_actions):
  frontier = []
  heapq.heappush(frontier, (0, initial_state, []))  # (total_cost, state, actions_steps)

  visited = {}

  while frontier:
    total_cost, state, actions = heapq.heappop(frontier)

    if goal(state):
      return total_cost, visited, actions

    # If we've already seen this state with a lower cost, skip
    if state in visited and visited[state] <= total_cost:
      continue

    visited[state] = total_cost

    for new_cost, new_state, new_action in state_actions(state):
      heapq.heappush(frontier, (total_cost + new_cost, new_state, actions + [new_action]))

  return None


# Breadth-First Search -----------------------------------------------------------------------------
def BFS(initial_state, goal, state_actions):
  queue = deque()
  queue.append((0, initial_state, []))  # (total_cost, state, actions_steps)

  visited = set()  # Visited nodes

  while queue:
    total_cost, state, actions = queue.popleft()

    if goal(state):
      return total_cost, visited, actions

    if state in visited:
      continue

    visited.add(state)

    for new_cost, new_state, new_action in state_actions(state):
      queue.append((total_cost + new_cost, new_state, actions + [new_action]))

  return None

# Depth-Limited Search (DFS com limite)
def DLS(state, goal, state_actions, limit, actions=None, cost=0, visited=None):
    if actions is None:
        actions = []
    if visited is None:
        visited = set()

    if goal(state):
        return cost, visited, actions

    if limit == 0:
        return None  

    visited.add(state)

    for new_cost, new_state, new_action in state_actions(state):
        if new_state not in visited:
            result = DLS(
                new_state,
                goal,
                state_actions,
                limit - 1,
                actions + [new_action],
                cost + new_cost,
                visited,
            )
            if result is not None:
                return result
    return None


def IDDFS(initial_state, goal, state_actions, max_depth=50):
    visited = set()
    for depth in range(1, max_depth + 1):
        result = DLS(initial_state, goal, state_actions, depth, visited=visited)
        if result is not None:
            return result
    return float("inf"), visited, []