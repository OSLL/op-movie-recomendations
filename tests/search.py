import sys
sys.path.append('../')

import imdb_recomendations
import argparse

import os
os.chdir(os.path.dirname(os.getcwd()))
# Test search only by actor name
print 'Test 1:'
imdb_recomendations.search(argparse.Namespace(actor_name=['John'], director_name=[''], genre='', title='',
                          years_after=0,
                          years_before=3000))
print 'Test 2:'
# Test search only by director name
imdb_recomendations.search(argparse.Namespace(director_name=['John'], actor_name=[''], genre='', title='',
                          years_after=0,
                          years_before=3000))
print 'Test 3:'
# Test search by director and actor name
imdb_recomendations.search(argparse.Namespace(director_name=['John'], actor_name=['Tommy'], genre='', title='',
                          years_after=0,
                          years_before=3000))
print 'Test 4:'
# Test search only by genre
imdb_recomendations.search(argparse.Namespace(director_name=[''], actor_name=[''], genre='Short', title='',
                          years_after=0,
                          years_before=3000))
print 'Test 5:'
# Test search only by time
imdb_recomendations.search(argparse.Namespace(director_name=[''], actor_name=[''], genre='', title='',
                          years_after=1990,
                          years_before=2000))
print 'Test 6:'
# Test search by name and time
imdb_recomendations.search(argparse.Namespace(director_name=['Jo'], actor_name=[''], genre='', title='',
                          years_after=1990,
                          years_before=2000))
print 'Test 7:'
# Test search by name with regexp
imdb_recomendations.search(argparse.Namespace(director_name=['J.hn'], actor_name=[''], genre='', title='',
                          years_after=1000,
                          years_before=3000))