# Actions duration [seconds]
TIME_TO_MAKE_COLD = 3.0
TIME_TO_MAKE_HOT = 5.0
TIME_TO_PICKUP = 1.0
TIME_TO_DELIVER = 1.0
TIME_TO_CLEAN_BIG = 4.0
TIME_TO_CLEAN_SMALL = 2.0
TIME_TO_TAKE_TRAY = 0.0
TIME_TO_RETURN_TRAY = 0.0
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
