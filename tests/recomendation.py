import sys
sys.path.append('../')

import imdb_recomendations
import argparse

imdb_recomendations.recomendation(argparse.Namespace(path = 'films.txt'))