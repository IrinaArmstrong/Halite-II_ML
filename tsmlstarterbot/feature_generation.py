import os
import json
from tqdm import tqdm
import numpy as np
import pandas as pd
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '99'

import warnings
warnings.filterwarnings("ignore")

from tsmlstarterbot.common import *

class PlanetFeature:
    owner = 0
    is_active = 1
    health = 2
    production = 3
    radius = 4
    exists = 5
    docked_ships = 6
    remaining_production = 7
    distance_from_center = 8
    friendly_ship_distance = 9
    enemy_ship_distance = 10
    health_weighted_friendly_ship_distance = 11
    health_weighted_enemy_ship_distance = 12
    friendly_gravity = 13
    enemy_gravity = 14

class ShipFeature:
    cooldown = 0
    health = 1
    x = 2
    y = 3
    vel_x = 4
    vel_y = 5
    closest_empty_planet_distance = 6
    closest_friendly_planet_distance = 7
    closest_enemy_planet_distance = 8

class PlayerFeature:
    n_planets_owned = 0
    n_ships_owned = 1
    n_ships_produced = 2
    ships_per_turn = 3
    moving_ships_ratio = 4
    docked_ships_ratio = 5
    total_planets_health = 6
    total_ships_health = 7
    ships_centroid_x = 8
    ships_centroid_y = 9
    ships_centroid_offset = 10
    ships_centroid_std = 11


class RelationFeature:
    enemy_agressive = 0
    friendly_agressive = 1
    n_collapse = 3
    n_turn = 4


def write_features_numpy(save_file, features, outputs):
    np.savez(save_file, features=features, outputs=outputs)


def angle(x, y):
    radians = math.atan2(y, x)
    if radians < 0:
        radians = radians + 2 * math.pi
    return round(radians / math.pi * 180)


def find_winner(data):
    for player, stats in data['stats'].items():
        if stats['rank'] == 1:
            return player
    return -1


def angle_dist(a1, a2):
    return (a1 - a2 + 360) % 360


def fetch_data_dir(directory, limit):
    """
    Loads up to limit games into Python dictionaries from uncompressed replay files.
    """
    replay_files = sorted([f for f in os.listdir(directory) if
                           os.path.isfile(os.path.join(directory, f)) ]) #and f.startswith("replay-")

    if len(replay_files) == 0:
        raise Exception("Didn't find any game replays. Please call make games.")
    if not limit:
        limit = len(replay_files)

    print("Found {} games.".format(len(replay_files)))
    print("Trying to load up to {} games ...".format(limit))

    loaded_games = 0

    all_data = []
    for r in replay_files:
        full_path = os.path.join(directory, r)
        with open(full_path) as game:
            game_data = game.read().strip("b")
            # game_json_data = json.loads(game_data, encoding='ascii', strict=False)
            game_json_data =  json.loads(eval(game_data),strict=False)
            all_data.append(game_json_data)
        loaded_games = loaded_games + 1

        if loaded_games >= limit:
            break
    # {"constants":{"ADDITIONAL_PRODUCTIVITY":6,"BASE_PRODUCTIVITY":6,
    # "BASE_SHIP_HEALTH":255,"DOCKED_SHIP_REGENERATION":0,"DOCK_RADIUS":4.0,
    # "DOCK_TURNS":5,"DRAG":7.0,"EXPLOSION_RADIUS":10.0,"EXTRA_PLANETS":4,
    # "INFINITE_RESOURCES":true,"MAX_ACCELERATION":7.0,"MAX_SHIP_HEALTH":255,
    print("{} games loaded.".format(loaded_games))

    return all_data

def find_target_planet(bot_id, current_frame, planets, move):
    """
    Find a planet which the ship tried to go to. We try to find it by looking at the angle that the ship moved
    with and the angle between the ship and the planet.
    :param bot_id: id of bot to imitate
    :param current_frame: current frame
    :param planets: planets data
    :param move: current move to analyze
    :return: id of the planet that ship was moving towards
    """

    if move['type'] == 'dock':
        # If the move was to dock, we know the planet we wanted to move towards
        return move['planet_id']
    if move['type'] != 'thrust':
        # If the move was not "thrust" (i.e. it was "undock"), there is no angle to analyze
        return -1

    ship_angle = move['angle']
    ship_data = current_frame['ships'][bot_id][str(move['shipId'])]
    ship_x = ship_data['x']
    ship_y = ship_data['y']

    optimal_planet = -1
    optimal_angle = -1
    for planet_data in planets:
        planet_id = str(planet_data['id'])
        if planet_id not in current_frame['planets'] or current_frame['planets'][planet_id]['health'] <= 0:
            continue

        planet_x = planet_data['x']
        planet_y = planet_data['y']
        a = angle(planet_x - ship_x, planet_y - ship_y)
        # We try to find the planet with minimal angle distance
        if optimal_planet == -1 or angle_dist(ship_angle, a) < angle_dist(ship_angle, optimal_angle):
            optimal_planet = planet_id
            optimal_angle = a

    return optimal_planet


def find_best_bot(all_games_json_data):
    players_games_count = {}
    for json_data in all_games_json_data:
        w = find_winner(json_data)
        p = json_data['player_names'][int(w)]
        if p not in players_games_count:
            players_games_count[p] = 0
        players_games_count[p] += 1

    with open("../players_rating.json", "w") as fp:
        json.dump(players_games_count , fp)

    bot_to_imitate = max(players_games_count, key=players_games_count.get)
    print("Bot to imitate: {}.".format(bot_to_imitate))
    return bot_to_imitate


def separate_planets(planets, bot_to_imitate_index):
    planets_empty = []
    planets_friendly = []
    planets_enemies = []
    for planet_id, planet in planets.items():
        if planet.get('owner') is None:
            planets_empty.append((int(planet_id), planet))
        elif planet.get('owner')== bot_to_imitate_index:
            planets_friendly.append((int(planet_id), planet))
        else:
            planets_enemies.append((int(planet_id), planet))
    return planets_friendly, planets_enemies, planets_empty


def separate_ships(all_ships, bot_to_imitate_index):
    ships_friendly = []
    ships_enemies = []
    for owner_id, ships in all_ships.items():
        if owner_id == bot_to_imitate_index:
            ships_friendly.extend([(ship_id, ship) for ship_id, ship in ships.items()])
        else:
            ships_enemies.extend([(ship_id, ship) for ship_id, ship in ships.items()])
    return ships_friendly, ships_enemies


def find_closest_ship_distance(planet, ships):
    if len(ships) == 0:
        return 1000, None
    distances = [distance(ship[1].get("x"), ship[1].get("y"),
                          planet.get("x"),  planet.get("y")) for ship in ships]
    return np.min(distances), ships[np.argmin(distances)]


def find_gravity(planet, ships):
    gravity = 0
    ships_health = 0
    health_weighted_ship_distance = 0
    for ship in ships:
        d = distance(ship[1].get("x"), ship[1].get("y"),
                     planet.get("x"),  planet.get("y"))
        ships_health += ship[1].get("health")
        health_weighted_ship_distance += d * ship[1].get("health")
        gravity += ship[1].get("health") / (d * d)

    if len(ships) > 0:
        health_weighted_ship_distance = health_weighted_ship_distance / ships_health
    return gravity, health_weighted_ship_distance


def create_players_features(friendly_planets, enemies_planets,
                            empty_planets, planets_general_data,
                            ships_friendly, ships_enemies,
                            center_coords):
    """
    Independent features:
        n_planets_owned = 0
        n_ships_owned = 1
        n_ships_produced = 2
        ships_per_turn = 3
        moving_ships_ratio = 4
        docked_ships_ratio = 5
        total_planets_health = 6
        total_ships_health = 7
        ships_centroid_x = 8
        ships_centroid_y = 9
        ships_centroid_offset = 10
        ships_centroid_std = 11
    """
    ret_features = np.zeros((28, 15))
    # for player in


def create_planets_features(friendly_planets, enemies_planets,
                            empty_planets, planets_general_data,
                            ships_friendly, ships_enemies,
                            center_coords):
    """
    Independent features:
        owner = 0, is_active = 1, health = 2
        production = 3, radius = 4, exists = 5
        docked_ships = 6, remaining_production = 7
        distance_from_center = 8
    Dependent:
        friendly_ship_distance = 9
        enemy_ship_distance = 10
        health_weighted_friendly_ship_distance = 11
        health_weighted_enemy_ship_distance = 12
        friendly_gravity = 13
        enemy_gravity = 14
    """
    ret_features = np.zeros((28, 15))

    for f_planet in friendly_planets:
        ret_features[f_planet[0], PlanetFeature.owner] = 1 # me
        ret_features[f_planet[0], PlanetFeature.is_active] = 1 if (len(f_planet[1].get('docked_ships'))
                                                                   < planets_general_data[f_planet[0]].get("docking_spots")) else 0
        ret_features[f_planet[0], PlanetFeature.health] = f_planet[1].get('health')
        ret_features[f_planet[0], PlanetFeature.production] = planets_general_data[f_planet[0]].get("production")
        ret_features[f_planet[0], PlanetFeature.exists] = 1 if planets_general_data[f_planet[0]].get("health") > 0 else 0
        ret_features[f_planet[0], PlanetFeature.docked_ships] = len(f_planet[1].get('docked_ships'))
        ret_features[f_planet[0], PlanetFeature.remaining_production] = f_planet[1].get('remaining_production')
        ret_features[f_planet[0], PlanetFeature.distance_from_center] = distance(planets_general_data[f_planet[0]].get("x"),
                                                                                 planets_general_data[f_planet[0]].get("y"),
                                                                                 center_coords[0],
                                                                                 center_coords[1])
        fdist, _ = find_closest_ship_distance(planets_general_data[f_planet[0]], ships_friendly)
        ret_features[f_planet[0], PlanetFeature.friendly_ship_distance] = fdist
        edist, _ = find_closest_ship_distance(planets_general_data[f_planet[0]], ships_enemies)
        ret_features[f_planet[0], PlanetFeature.enemy_ship_distance] = edist
        fgravity, health_weighted_fdist = find_gravity(planets_general_data[f_planet[0]], ships_friendly)
        ret_features[f_planet[0], PlanetFeature.health_weighted_friendly_ship_distance] = fgravity
        ret_features[f_planet[0], PlanetFeature.friendly_gravity] = fgravity
        egravity, health_weighted_edist = find_gravity(planets_general_data[f_planet[0]], ships_enemies)
        ret_features[f_planet[0], PlanetFeature.enemy_gravity] = egravity
        ret_features[f_planet[0], PlanetFeature.health_weighted_enemy_ship_distance] = egravity


    for f_planet in enemies_planets:
        ret_features[f_planet[0], PlanetFeature.owner] = -1 # not me
        ret_features[f_planet[0], PlanetFeature.is_active] = 1 if (len(f_planet[1].get('docked_ships'))
                                                                   < planets_general_data[f_planet[0]].get("docking_spots")) else 0
        ret_features[f_planet[0], PlanetFeature.health] = f_planet[1].get('health')
        ret_features[f_planet[0], PlanetFeature.production] = planets_general_data[f_planet[0]].get("production")
        ret_features[f_planet[0], PlanetFeature.exists] = 1 if planets_general_data[f_planet[0]].get("health") > 0 else 0
        ret_features[f_planet[0], PlanetFeature.docked_ships] = len(f_planet[1].get('docked_ships'))
        ret_features[f_planet[0], PlanetFeature.remaining_production] = f_planet[1].get('remaining_production')
        ret_features[f_planet[0], PlanetFeature.distance_from_center] = distance(planets_general_data[f_planet[0]].get("x"),
                                                                                 planets_general_data[f_planet[0]].get("y"),
                                                                                 center_coords[0],
                                                                                 center_coords[1])
        fdist, _ = find_closest_ship_distance(planets_general_data[f_planet[0]], ships_friendly)
        ret_features[f_planet[0], PlanetFeature.friendly_ship_distance] = fdist
        edist, _ = find_closest_ship_distance(planets_general_data[f_planet[0]], ships_enemies)
        ret_features[f_planet[0], PlanetFeature.enemy_ship_distance] = edist
        fgravity, health_weighted_fdist = find_gravity(planets_general_data[f_planet[0]], ships_friendly)
        ret_features[f_planet[0], PlanetFeature.health_weighted_friendly_ship_distance] = fgravity
        ret_features[f_planet[0], PlanetFeature.friendly_gravity] = fgravity
        egravity, health_weighted_edist = find_gravity(planets_general_data[f_planet[0]], ships_enemies)
        ret_features[f_planet[0], PlanetFeature.enemy_gravity] = egravity
        ret_features[f_planet[0], PlanetFeature.health_weighted_enemy_ship_distance] = egravity


    for f_planet in empty_planets:
        ret_features[f_planet[0], PlanetFeature.owner] = 0 # no ones
        ret_features[f_planet[0], PlanetFeature.is_active] = 1 if (len(f_planet[1].get('docked_ships'))
                                                                   < planets_general_data[f_planet[0]].get("docking_spots")) else 0
        ret_features[f_planet[0], PlanetFeature.health] = f_planet[1].get('health')
        ret_features[f_planet[0], PlanetFeature.production] = planets_general_data[f_planet[0]].get("production")
        ret_features[f_planet[0], PlanetFeature.radius] = planets_general_data[f_planet[0]].get("r")
        ret_features[f_planet[0], PlanetFeature.exists] = 1 if planets_general_data[f_planet[0]].get("health") > 0 else 0
        ret_features[f_planet[0], PlanetFeature.docked_ships] = len(f_planet[1].get('docked_ships'))
        ret_features[f_planet[0], PlanetFeature.remaining_production] = f_planet[1].get('remaining_production')
        ret_features[f_planet[0], PlanetFeature.distance_from_center] = distance(planets_general_data[f_planet[0]].get("x"),
                                                                                 planets_general_data[f_planet[0]].get("y"),
                                                                                 center_coords[0],
                                                                                 center_coords[1])
        fdist, _ = find_closest_ship_distance(planets_general_data[f_planet[0]], ships_friendly)
        ret_features[f_planet[0], PlanetFeature.friendly_ship_distance] = fdist
        edist, _ = find_closest_ship_distance(planets_general_data[f_planet[0]], ships_enemies)
        ret_features[f_planet[0], PlanetFeature.enemy_ship_distance] = edist
        fgravity, health_weighted_fdist = find_gravity(planets_general_data[f_planet[0]], ships_friendly)
        ret_features[f_planet[0], PlanetFeature.health_weighted_friendly_ship_distance] = fgravity
        ret_features[f_planet[0], PlanetFeature.friendly_gravity] = fgravity
        egravity, health_weighted_edist = find_gravity(planets_general_data[f_planet[0]], ships_enemies)
        ret_features[f_planet[0], PlanetFeature.enemy_gravity] = egravity
        ret_features[f_planet[0], PlanetFeature.health_weighted_enemy_ship_distance] = egravity


    return ret_features


def parce_allocations(current_frame, current_moves, all_planets, bot_to_imitate_id):
    # find % allocation for all ships
    allocations = {}
    ret_allocations = np.zeros((28,), dtype=np.float32)
    all_moving_ships = 0

    # for each planet we want to find how many ships are being moved towards it now
    for ship_id, ship in current_frame['ships'].get(bot_to_imitate_id).items():
        if ship_id in current_moves[bot_to_imitate_id][0]:
            p = find_target_planet(bot_to_imitate_id, current_frame, all_planets,
                                   current_moves[bot_to_imitate_id][0][ship_id])
            planet_id = int(p)
            if planet_id < 0 or planet_id >= PLANET_MAX_NUM:
                continue

            if p not in allocations:
                allocations[p] = 0
            allocations[p] = allocations[p] + 1
            all_moving_ships = all_moving_ships + 1

    if all_moving_ships == 0:
        return ret_allocations

    # Compute what % of the ships should be sent to given planet
    for planet_id, allocated_ships in allocations.items():
        ret_allocations[int(planet_id)] = allocated_ships / all_moving_ships
    return ret_allocations



def parse_replay(replay_data, bot_to_imitate):

    players_names = replay_data['player_names']
    bot_to_imitate_id = str(players_names.index(bot_to_imitate))
    frames = replay_data['frames']
    moves = replay_data['moves']
    width = replay_data['width']
    height = replay_data['height']
    planets_general_data = replay_data['planets']
    center = (width / 2, height / 2)

    game_training_data = []
    game_target_data = []
    # Ignore the last frame, no decision to be made there
    for idx in range(len(frames) - 1):

        current_moves = moves[idx]
        current_frame = frames[idx]

        if (bot_to_imitate_id not in current_frame['ships']
                or len(current_frame['ships'][bot_to_imitate_id]) == 0):
            continue
        # 1) Split planets to friendly, enemies and empty
        # List[Dict[str, Any]] -> list of planets and dict of each features
        planets_friendly, planets_enemies, planets_empty = separate_planets(current_frame['planets'],
                                                                            bot_to_imitate_id)
        # 2) Split ships
        ships_friendly, ships_enemies = separate_ships(current_frame['ships'], bot_to_imitate_id)
        # 3) Create planets features: 15
        planets_features = np.zeros((1, 28, 15))
        planets_features[0] = create_planets_features(planets_friendly, planets_enemies,
                                                   planets_empty, planets_general_data,
                                                   ships_friendly, ships_enemies,
                                                   center)
        game_training_data.append(planets_features)
        # 4) Create player based features
        # TODO
        # 5) Create outputs
        outputs_allocations = parce_allocations(current_frame, current_moves,
                                                planets_general_data, bot_to_imitate_id)
        game_target_data.append(outputs_allocations)

    return np.vstack(game_training_data), np.vstack(game_target_data)


def parse_data(data_path, games_limit=None, bot_to_imitate=None,
                dump_features_location="../train_data", dump_features_fn="train_data.npz"):

    all_games_json_data = fetch_data_dir(data_path, games_limit)

    if not bot_to_imitate:
        bot_to_imitate = find_best_bot(all_games_json_data)

    print("Parsing data...")
    parsed_games = 0

    all_features_data = []
    all_target_data = []
    for json_data in tqdm(all_games_json_data, total=len(all_games_json_data)):

        # For each game see if bot_to_imitate played in it
        players_names = json_data['player_names']
        if bot_to_imitate not in set(players_names):
            continue
        replay_inputs, replay_outputs = parse_replay(json_data, bot_to_imitate)
        all_features_data.append(replay_inputs)
        all_target_data.append(replay_outputs)

        parsed_games = parsed_games + 1

    if parsed_games == 0:
        raise Exception("Didn't find any matching games. Try different bot.")

    write_features_numpy(os.path.join(dump_features_location, dump_features_fn),
                         np.vstack(all_features_data), np.vstack(all_target_data))



def load_parsed(dump_features_location: str = "../train_data",
                dump_features_fn=None):

    if not dump_features_fn:
        dataset_files = sorted([f for f in os.listdir(dump_features_location) if
                               os.path.isfile(os.path.join(dump_features_location, f)) and f.endswith(".npz")])
        if len(dataset_files) == 0:
            raise Exception("Didn't find any datasets. Please call parce raw data.")

        print("Found {} datasets.".format(len(dataset_files)))
        print("Trying to load up datasets ...")

        all_data_inputs = []
        all_data_outputs = []

        for f in tqdm(dataset_files, total=len(dataset_files)):
            full_path = os.path.join(dump_features_location, f)
            data = np.load(full_path)
            features, outputs = data['features'], data['outputs']
            all_data_inputs.append(features)
            all_data_outputs.append(outputs)

        all_data_inputs = np.vstack(all_data_inputs)
        all_data_outputs = np.vstack(all_data_outputs)
        print(f"Full features shape: {all_data_inputs.shape}")
        print(f"Full outputs shape: {all_data_outputs.shape}")

        return all_data_inputs, all_data_outputs

    data = np.load(os.path.join(dump_features_location, dump_features_fn))
    features, outputs = data['features'], data['outputs']
    print(f"Features shape: {features.shape}")
    print(f"Outputs shape: {outputs.shape}")
    return features, outputs


if __name__ == "__main__":
    parse_data(data_path="D:\Data\Halite-2_Replays_19012018_p1",
               bot_to_imitate=None, games_limit=None,
               dump_features_location="../train_data/shummie",
               dump_features_fn="train_data_5.npz") #"Sydriax v17" "shummie v526"