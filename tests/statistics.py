import sys
sys.path.append('../')

import imdb_recomendations
import argparse

import os
os.chdir(os.path.dirname(os.getcwd()))

print 'Test 1:'
imdb_recomendations.statistics(argparse.Namespace(name = ['John']))

print 'Test 2:'
imdb_recomendations.statistics(argparse.Namespace(name = ['Malu']))
