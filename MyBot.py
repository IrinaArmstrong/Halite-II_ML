import tsmlstarterbot

import warnings
warnings.filterwarnings("ignore")


# Load the model from the models directory. Models directory is created during training.
# Run "make" to download data and train.
tsmlstarterbot.Bot(location="StarterML_Bot.ckpt", name="MyBot").play()
