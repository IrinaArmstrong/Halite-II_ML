# Place this before directly or indirectly importing tensorflow
import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '99' #99
import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings('ignore', category=ResourceWarning)
# warnings.simplefilter("ignore", category=ResourceWarning)
from tsmlstarterbot.cnn_net_model import CNN_Net
from tsmlstarterbot.common import PLANET_MAX_NUM, PER_PLANET_FEATURES

import numpy as np
import unittest

EPSILON = 1e-3
SEED = 0


def equal(a, b):
    return abs(a - b) < EPSILON


class TestNeuralNet(unittest.TestCase):
    def test_invariance(self):
        # Redirect sys.stdout to the file
        stderr_fn = sys.stderr
        stdout_fn = sys.stdout
        sys.stdout = open('./log_stdout.txt', 'w')
        sys.stderr = open('./log_stderr.txt', 'w')

        np.random.seed(SEED)

        # Generate random input
        input_data = np.random.rand(1, PLANET_MAX_NUM, PER_PLANET_FEATURES)
        input_data_size = input_data.shape[1:]
        # Create a random network
        nn = CNN_Net(input_size=input_data_size, output_size=PLANET_MAX_NUM,
                     cached_model=True, cached_model_path="../models/cnn_model_v0.hd5",
                     seed=SEED)
        sys.stdout.close()
        sys.stderr.close()
        sys.stderr = stderr_fn
        sys.stdout = stdout_fn

        # Get predictions
        original_predictions = nn.predict(input_data)
        print(f"Predictions shape: {original_predictions.shape}")
        print(f"Predictions: {original_predictions}")

        # Confirm different predictions for planet 0 and 1
        assert not equal(original_predictions[0, 0], original_predictions[0, 1])

        permuted_input_data = input_data.copy()
        # Swap planets 0 and 1
        permuted_input_data[0, 0, :] = input_data[0, 1, :]
        permuted_input_data[0, 1, :] = input_data[0, 0, :]
        print(f"Original input [0, 0, :]: {input_data[0, 0, :]}")
        print(f"Permuted input [0, 0, :]: {permuted_input_data[0, 0, :]}")

        permuted_predictions = nn.predict(permuted_input_data)

        # Confirm the predictions are permuted
        print(f"{original_predictions[0, 0]} - {permuted_predictions[0, 1]} = {original_predictions[0, 0] - permuted_predictions[0, 1]}")
        print(f"{original_predictions[0, 1]} - {permuted_predictions[0, 0]} = {original_predictions[0, 1] - permuted_predictions[0, 0]}")



if __name__ == "__main__":
    unittest.main()
