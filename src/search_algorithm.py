import heapq
from collections import deque


# Breadth-First Search
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


# Uniform-Cost Search
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
