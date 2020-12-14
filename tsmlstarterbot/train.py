import sys
import argparse
import json
import os.path
import zipfile

import warnings
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore", category=RuntimeWarning)


import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '99' #99
from tsmlstarterbot.cnn_net_model import CNN_Net
from tsmlstarterbot.deep_fc_net import Deep_FC_Net
from tsmlstarterbot.feature_generation import load_parsed
from tsmlstarterbot.parsing import parse
from tsmlstarterbot.common import *

def fetch_data_dir(directory, limit):
    """
    Loads up to limit games into Python dictionaries from uncompressed replay files.
    """
    replay_files = sorted([f for f in os.listdir(directory) if
                           os.path.isfile(os.path.join(directory, f)) ]) #and f.startswith("replay-")

    if len(replay_files) == 0:
        raise Exception("Didn't find any game replays. Please call make games.")

    print("Found {} games.".format(len(replay_files)))
    print("Trying to load up to {} games ...".format(limit))

    loaded_games = 0

    all_data = []
    for r in replay_files:
        full_path = os.path.join(directory, r)
        with open(full_path) as game:
            game_data = game.read()
            game_json_data = json.loads(game_data)
            all_data.append(game_json_data)
        loaded_games = loaded_games + 1

        if loaded_games >= limit:
            break

    print("{} games loaded.".format(loaded_games))

    return all_data

def fetch_data_zip(zipfilename, limit):
    """
    Loads up to limit games into Python dictionaries from a zipfile containing uncompressed replay files.
    """
    all_jsons = []
    with zipfile.ZipFile(zipfilename) as z:
        print("Found {} games.".format(len(z.filelist)))
        print("Trying to load up to {} games ...".format(limit))
        for i in z.filelist[:limit]:
            with z.open(i) as f:
                lines = f.readlines()
                assert len(lines) == 1
                d = json.loads(lines[0].decode())
                all_jsons.append(d)
    print("{} games loaded.".format(len(all_jsons)))
    return all_jsons


def main():
    parser = argparse.ArgumentParser(description="Halite II training")
    parser.add_argument("--model_name", help="Name of the model")
    parser.add_argument("--features_ready", help="If data already preprocessed to features and saved")
    parser.add_argument("--data", help="Data directory or zip file containing uncompressed games")
    parser.add_argument("--cache", help="Location of the model we should continue to train")
    parser.add_argument("--games_limit", type=int, help="Train on up to games_limit games", default=1000)
    parser.add_argument("--seed", type=int, help="Random seed to make the training deterministic")
    parser.add_argument("--bot_to_imitate", help="Name of the bot whose strategy we want to learn")
    parser.add_argument("--dump_features_location", help="Location of hdf file where the features should be stored")
    parser.add_argument("--dump_features_fn", help="File name of file where the features should be stored")

    args = parser.parse_args()

    if args.data.endswith('.zip'):
        raw_data = fetch_data_zip(args.data, args.games_limit)
        data_input, data_output = parse(raw_data, args.bot_to_imitate,
                                        args.dump_features_location, args.dump_features_fn)
    elif args.features_ready:
        data_input, data_output = load_parsed(args.dump_features_location, args.dump_features_fn)
    else:
        raw_data = fetch_data_dir(args.data, args.games_limit)
        data_input, data_output = parse(raw_data, args.bot_to_imitate,
                                        args.dump_features_location, args.dump_features_fn)

    input_data_size = data_input.shape[1:]
    # Make deterministic if needed
    if args.seed is not None:
        np.random.seed(args.seed)

    # Redirect sys.stdout to the file
    # stderr_fn = sys.stderr
    # stdout_fn = sys.stdout
    # sys.stdout = open('./LogSTDOUT.txt', 'w')
    # sys.stdout = open('./LogSTDERR.txt', 'w')


    net = CNN_Net(input_size=input_data_size, output_size=PLANET_MAX_NUM,
                  cached_model=args.cache, cached_model_path="", seed=args.seed)
    # net = Deep_FC_Net(input_size=input_data_size, output_size=PLANET_MAX_NUM,
    #               cached_model=args.cache, cached_model_path="", seed=args.seed)

    # sys.stdout.close()
    # sys.stderr.close()
    # sys.stderr = stderr_fn
    # sys.stdout = stdout_fn
    # os.remove("./LogSTDOUT.txt")
    # os.remove("./LogSTDERR.txt")

    net.train(data_input, data_output, validation_split = 0.2, n_epochs=20,
              batch_size=100, verbose=1, model_version="v0")



if __name__ == "__main__":
    main()
