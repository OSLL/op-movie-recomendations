import sys
sys.path.append('../')

import imdb_recomendations
import argparse

import os
os.chdir(os.path.dirname(os.getcwd()))

imdb_recomendations.recomendation(argparse.Namespace(path = 'tests/films.txt'))