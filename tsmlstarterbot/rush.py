# from hlt.constants import *
# from hlt.entity import *
# import datetime
#
#
# kSafeToDockDistance = 1 * MAX_SPEED
# kShipAttackRadius = 5
# kEnemyShipsClusterRadius = 2 * MAX_SPEED
# kTimePerTurn = 1700  #ms
#
#
# def CheckTimeout(turn_start_time):
#     return (datetime.datetime.utcnow() - turn_start_time).total_seconds() * 1000 > kTimePerTurn
#
# #Hardcode rush formation on turn 0
# def RushFirstTurn(my_ships, enemy_ships):
#     command_queue = list()
#     #determine whether my ships are aligned vertically or horizontally
#     vertically_aligned = abs(my_ships[0].x - my_ships[1].x) < EPS
#     if my_ships[0].x + 1 < enemy_ships[0].x:
#         #i am on the left, opp is on the right
#         if vertically_aligned:
#             command_queue.append("t {} {} {}".format(my_ships[0].id, 3, 290))
#             command_queue.append("t {} {} {}".format(my_ships[1].id, 0, 0))
#             command_queue.append("t {} {} {}".format(my_ships[2].id, 5, 272))
#         else:
#             command_queue.append("t {} {} {}".format(my_ships[0].id, 3, 290))
#             command_queue.append("t {} {} {}".format(my_ships[1].id, 0, 0))
#             command_queue.append("t {} {} {}".format(my_ships[2].id, 5, 272))
#     elif my_ships[0].x - 1 > enemy_ships[0].x:
#         #i am on the right, opp is on the left
#         if vertically_aligned:
#             command_queue.append("t {} {} {}".format(my_ships[0].id, 3, 290))
#             command_queue.append("t {} {} {}".format(my_ships[1].id, 0, 0))
#             command_queue.append("t {} {} {}".format(my_ships[2].id, 5, 272))
#         else:
#             command_queue.append("t {} {} {}".format(my_ships[0].id, 3, 290))
#             command_queue.append("t {} {} {}".format(my_ships[1].id, 0, 0))
#             command_queue.append("t {} {} {}".format(my_ships[2].id, 5, 272))
#     elif my_ships[0].y + 1 < enemy_ships[0].y:
#         #my ships are at the top, opp is at the bottom
#         if vertically_aligned:
#             command_queue.append("t {} {} {}".format(my_ships[0].id, 3, 70))
#             command_queue.append("t {} {} {}".format(my_ships[2].id, 0, 0))
#             command_queue.append("t {} {} {}".format(my_ships[1].id, 5, 88))
#         else:
#             command_queue.append("t {} {} {}".format(my_ships[0].id, 3, 290))
#             command_queue.append("t {} {} {}".format(my_ships[1].id, 0, 0))
#             command_queue.append("t {} {} {}".format(my_ships[2].id, 5, 272))
#     else:
#         #i am at the bottom, opp is at the top
#         if vertically_aligned:
#             command_queue.append("t {} {} {}".format(my_ships[0].id, 3, 290))
#             command_queue.append("t {} {} {}".format(my_ships[1].id, 0, 0))
#             command_queue.append("t {} {} {}".format(my_ships[2].id, 5, 272))
#         else:
#             command_queue.append("t {} {} {}".format(my_ships[0].id, 3, 290))
#             command_queue.append("t {} {} {}".format(my_ships[1].id, 0, 0))
#             command_queue.append("t {} {} {}".format(my_ships[2].id, 5, 272))
#     return command_queue
#
#
# def GameMapCorners(game_map):
#     top_left_corner = Position(0, 0)
#     top_right_corner = Position(game_map.width, 0)
#     bottom_left_corner = Position(0, game_map.height)
#     bottom_right_corner = Position(game_map.width, game_map.height)
#     return (top_left_corner, top_right_corner, bottom_left_corner, bottom_right_corner)
#
#
# def PlanetsCloserToMeThanToEnemy(planets, my_ship, enemy_ship):
#     return [planet for planet in planets if my_ship.calculate_distance_between(planet)
#             < enemy_ship.calculate_distance_between(planet)]
#
# def ClosestAvailablePlanet(ship, game_map, my_ships, my_ships_to_planets_map, enemy_ships):
#     ans = None
#     min_dist = INF
#     for planet in game_map.all_planets():
#         if NearestPlanetCondition(planet, game_map, my_ships, my_ships_to_planets_map, enemy_ships):
#             dist = ship.calculate_distance_between(planet)
#             if dist < min_dist:
#                 min_dist = dist
#                 ans = planet
#     return (ans, min_dist)
#
#
# def NearestPlanetCondition(entity, game_map, my_ships, my_ships_to_planets_map, enemy_ships):
#     return (isinstance(entity, Planet)
#         and  (((not entity.is_owned()) or (entity.owner == game_map.get_me()))
#               and not IsPlanetFull(entity, my_ships_to_planets_map))
#                 and IsSafeToDock(entity, my_ships, enemy_ships))
#
#
# def IsSafeToDock(planet, my_ships, enemy_ships):
#     closest_enemy_ship = ShipClosestToPlanet(planet, enemy_ships)
#     return closest_enemy_ship.calculate_distance_between(planet) > kSafeToDockDistance + planet.radius
#
#
# def IsPlanetFull(planet, my_ships_to_planets_map):
#     return len(planet._docked_ships) + my_ships_to_planets_map[planet.id] >= planet.num_docking_spots
#
#
# def ShipClosestToPlanet(planet, ships):
#     closest_ship = None
#     min_dist = INF
#     for ship in ships:
#         dist = planet.calculate_distance_between(ship)
#         if dist < min_dist:
#             min_dist = dist
#             closest_ship = ship
#     return closest_ship
#
# def CentralPlanets(game_map, planets):
#     map_center = Position(game_map.width / 2, game_map.height / 2)
#     ans = sorted(planets, key = lambda planet: planet.calculate_distance_between(map_center))[0 : min(2, len(planets))]
#     return ans
#
#
# def ClosestCentralPlanet(my_ship, game_map, planets, my_ships, my_ships_to_planets_map, enemy_ships):
#     closest_central_planet = None
#     min_dist = INF
#     central_planets = CentralPlanets(game_map, planets)
#     central_planets.sort(key = lambda planet : my_ships[0].calculate_distance_between(planet))
#     closest_central_planet = central_planets[0]
#     return (closest_central_planet, min_dist)
#
# def NotWorsePlanetClosestToMe(my_ship, reference_planet, planets):
#     not_worse_planet = None
#     min_dist = INF
#     for planet in planets:
#         if planet.num_docking_spots >= reference_planet.num_docking_spots:
#             dist = my_ship.calculate_distance_between(planet)
#             if dist < min_dist:
#                 min_dist = dist
#                 not_worse_planet = planet
#     return (not_worse_planet, min_dist)
#
# def LargePlanetClosestToCenter(my_ship, game_map, planets, my_ships, my_ships_to_planets_map, enemy_ships):
#     game_map_center = Position(game_map.width / 2, game_map.height / 2)
#     closest_planet = None
#     min_dist = INF
#     for planet in planets:
#         if (planet.num_docking_spots >= 3) and NearestPlanetCondition(planet, game_map, my_ships, my_ships_to_planets_map, enemy_ships):
#             dist = game_map_center.calculate_distance_between(planet)
#             if dist < min_dist:
#                 min_dist = dist
#                 closest_planet = planet
#     return (closest_planet, min_dist)
#
# def InitialPlanetChoice2p(game_map, planets, my_ships, my_ships_to_planets_map, enemy_ships):
#     closest_planet, dist_to_closest_planet = ClosestAvailablePlanet(my_ships[0], game_map, my_ships, my_ships_to_planets_map, enemy_ships)
#     target = closest_planet
#     if (closest_planet is not None) and (closest_planet.num_docking_spots >= 5):
#         target = closest_planet
#     else:
#         planets_closer_to_me = PlanetsCloserToMeThanToEnemy(planets, my_ships[0], enemy_ships[0])
#         (closest_central_planet, dist_to_closest_central_planet) = ClosestCentralPlanet(my_ships[0], game_map, planets_closer_to_me, my_ships, my_ships_to_planets_map, enemy_ships)
#         if (closest_central_planet is not None) and (closest_central_planet.num_docking_spots >= 3):
#             (not_worse_planet, dist_to_not_worse_planet) = NotWorsePlanetClosestToMe(my_ships[0], closest_central_planet, planets_closer_to_me)
#             if (not_worse_planet is not None) and (not_worse_planet.num_docking_spots >= 4):
#                 target = not_worse_planet
#             else:
#                 target = closest_central_planet
#         else:
#             (large_planet_closest_to_center, dist_to_large_planet) = LargePlanetClosestToCenter(my_ships[0], game_map, planets_closer_to_me, my_ships, my_ships_to_planets_map, enemy_ships)
#             if large_planet_closest_to_center is not None:
#                 (not_worse_planet, dist_to_not_worse_planet) = NotWorsePlanetClosestToMe(my_ships[0], large_planet_closest_to_center, planets_closer_to_me)
#                 if (not_worse_planet is not None) and (not_worse_planet.num_docking_spots >= 4):
#                     target = not_worse_planet
#                 elif (my_ships[0].calculate_distance_between(closest_central_planet) > not_worse_planet.calculate_distance_between(closest_central_planet)):
#                     target = not_worse_planet
#                 else:
#                     target = closest_central_planet
#             else:
#                 target = closest_central_planet
#     if NearestPlanetCondition(target, game_map, my_ships, my_ships_to_planets_map, enemy_ships):
#         return target
#     return None
#
#
# def RushStrategy(turn, game_map, num_players, planets,
#                 my_ships, my_docked_ships, my_undocked_ships,
#                 enemy_ships, enemy_docked_ships, enemy_undocked_ships,
#                 my_ships_targets, my_ships_positions_next_turn, my_ships_to_planets_map,
#                 turn_start_time, enemy_contact_rush_prev_turn):
#     target = None
#     enemy_contact = CheckEnemyContactRush(my_ships, enemy_ships)
#     if enemy_contact:
#         target = RushEscapeTarget(game_map, my_ships, enemy_ships)
#     else:
#
#         target = ClosestEnemyShipToAllMyShips(my_ships, enemy_ships, False, True)[0]
#         if target is None:
#             target = ClosestEnemyShipToAllMyShips(my_ships, enemy_ships, True, False)[0]
#
#     best_speed = 0
#     best_angle = 0
#     min_dist = INF
#     timeout_flag = False
#     for curr_speed in range(MAX_SPEED + 1):
#         for curr_angle in range(360):
#             if CheckTimeout(turn_start_time):
#                 timeout_flag = True
#                 break
#             found_collision = False
#             curr_angle_in_radians = math.radians(curr_angle)
#             my_ships_positions = {my_ship.id : Position(my_ship.x + curr_speed * math.cos(curr_angle_in_radians), my_ship.y + curr_speed * math.sin(curr_angle_in_radians)) for my_ship in my_ships}
#             for my_ship in my_ships:
#                 for planet in planets:
#                     if CollisionTime(my_ship, my_ships_positions[my_ship.id], planet, planet):
#                         found_collision = True
#                         break
#                 if (not found_collision) and CheckShipCollisionWithMapBorders(my_ships_positions[my_ship.id], game_map):
#                     found_collision = True
#                     break
#             if not found_collision:
#                 curr_dist = min([target.calculate_distance_between(my_ship_position) for my_ship_position in my_ships_positions.values()])
#                 if curr_dist < min_dist:
#                     min_dist = curr_dist
#                     best_speed = curr_speed
#                     best_angle = curr_angle
#         if timeout_flag:
#             break
#     min_dist_to_target = min([target.calculate_distance_between(my_ship) for my_ship in my_ships])
#     if enemy_contact:
#         pass
#     elif (num_players == 2) and (len(my_ships) == 1) and (len(enemy_ships) == 1):
#         pass
#     elif target.docking_status == target.DockingStatus.UNDOCKED:
#         if min_dist_to_target < MAX_SPEED:
#             best_speed = min(MAX_SPEED, int(min_dist_to_target) - 3)
#         elif min_dist_to_target < 2 * MAX_SPEED:
#             best_speed = min(MAX_SPEED, best_speed)
#     else:
#         best_speed = min(MAX_SPEED, int(min_dist_to_target) - 3)
#     best_speed = max(best_speed, 0)
#     command_queue = list()
#     for my_ship in my_ships:
#         command_queue.append("t {} {} {}".format(my_ship.id, best_speed, best_angle))
#     return command_queue
#
#
#
# def CheckEnemyContactRush(my_ships, enemy_ships):
#     for my_ship in my_ships:
#         min_dist_to_enemy_ship = min([my_ship.calculate_distance_between(enemy_ship) for enemy_ship in enemy_ships])
#         if min_dist_to_enemy_ship < kShipAttackRadius:
#             return True
#     return False
#
#
# def RushEscapeTarget(game_map, my_ships, enemy_ships):
#     return EscapeFromEnemyShipsTarget(my_ships[0], game_map, enemy_ships)
#
#
# def EscapeFromEnemyShipsTarget(my_ship, game_map, enemy_ships):
#     escape_position = None
#     escape_angle = 0
#     max_dist_to_closest_enemy = 0
#     speed = MAX_SPEED
#     for angle in range(360):
#         curr_angle_in_radians = math.radians(angle)
#         curr_x = my_ship.x + math.cos(curr_angle_in_radians) * speed
#         curr_y = my_ship.y + math.sin(curr_angle_in_radians) * speed
#         curr_position = Position(curr_x, curr_y)
#         #Prevents getting stuck in the corner when running away from enemy ships
#         if IsOutsideOfGameMap(curr_position, game_map):
#             continue
#         curr_dist_to_closest_enemy = DistToClosestEnemyShip(curr_position, enemy_ships)
#         if curr_dist_to_closest_enemy > max_dist_to_closest_enemy:
#             max_dist_to_closest_enemy = curr_dist_to_closest_enemy
#             escape_angle = angle
#     escape_angle_in_radians = math.radians(escape_angle)
#     escape_x = my_ship.x + math.cos(escape_angle_in_radians) * speed
#     escape_y = my_ship.y + math.sin(escape_angle_in_radians) * speed
#     return Position(escape_x, escape_y)
#
# def DistToClosestEnemyShip(my_ship, enemy_ships):
#     min_dist = INF
#     for enemy_ship in enemy_ships:
#         min_dist = min(min_dist, my_ship.calculate_distance_between(enemy_ship))
#     return min_dist
#
#
# #Checks if given ship position is outside the game map boundaries
# #Is used in EscapeFromEnemy to avoid getting stuck in the corners
# def IsOutsideOfGameMap(ship, game_map):
#     return ((ship.x < SHIP_RADIUS + EPS)
#         or (ship.x > game_map.width - SHIP_RADIUS - EPS)
#         or (ship.y < SHIP_RADIUS + EPS)
#         or (ship.y > game_map.height - SHIP_RADIUS - EPS))
#
#
# def ClosestEnemyShipToAllMyShips(my_ships, enemy_ships, ignore_docked_ships = True, ignore_undocked_ships = True):
#     closest_enemy_ship = None
#     min_dist = INF
#     for enemy_ship in enemy_ships:
#         if ignore_docked_ships and (enemy_ship.docking_status != enemy_ship.DockingStatus.UNDOCKED):
#             continue
#         elif ignore_undocked_ships and (enemy_ship.docking_status == enemy_ship.DockingStatus.UNDOCKED):
#             continue
#         dist = min([enemy_ship.calculate_distance_between(my_ship) for my_ship in my_ships])
#         if dist < min_dist:
#             min_dist = dist
#             closest_enemy_ship = enemy_ship
#     return (closest_enemy_ship, min_dist)
#
#
# def CollisionTime(entity1, target1, entity2, target2):
#     velocity1 = [target1.x - entity1.x, target1.y - entity1.y]
#     velocity2 = [target2.x - entity2.x, target2.y - entity2.y]
#     p = [entity1.x - entity2.x, entity1.y - entity2.y]
#     v = [velocity1[0] - velocity2[0], velocity1[1] - velocity2[1]]
#     a = DotProduct(v, v)
#     b = 2 * DotProduct(p, v)
#     radius1 = hlt.constants.SHIP_RADIUS
#     radius2 = entity2.radius if isinstance(entity2, hlt.entity.Planet) else hlt.constants.SHIP_RADIUS
#     c = DotProduct(p, p) - pow((radius1 + radius2 + kCollisionAdjustmentEpsilon), 2)
#     if abs(a) < kEpsilon:
#         if abs(b) < kEpsilon:
#             return c <= 0
#         t = -c / b
#         return (t >= 0) and (t <= 1)
#     D = b * b - 4 * a * c
#     if D < 0:
#         return False
#     sqrt_D = math.sqrt(D)
#     t0 = (-b - sqrt_D) / (2 * a)
#     t1 = (-b + sqrt_D) / (2 * a)
#     t = min(t0, t1)
#     return (t >= 0) and (t <= 1)