# -*- coding: utf-8 -*-

import argparse
from pandas import DataFrame

def search(args):
	print args

def statistics(args):
	print args

def  recomendation(args):
	print args

def update_db():
	print args

def parse_tsv(path_to_file):
	df = DataFrame.from_csv(path_to_file, sep='\t', header=0)
	return df

def parse_args():
	parser = argparse.ArgumentParser(description='')
	subparsers = parser.add_subparsers()
	
	parser_search = subparsers.add_parser('search')
	parser_search.add_argument('--title',nargs='*',help='Movie title')
	parser_search.add_argument('--name',nargs='*',help='Name of the actor or director')
	parser_search.add_argument('--date',help='Release date of the film')
	parser_search.add_argument('--genre',nargs='*',help='Genre of the film')
	parser_search.set_defaults(func=search)

	parser_statistics = subparsers.add_parser('statistics')
	parser_statistics.add_argument('name',nargs='*',help='Name of the actor or director')
	parser_statistics.set_defaults(func=statistics)	
	
	parser_recomendation = subparsers.add_parser('recomendation')
	parser_recomendation.add_argument('path',help='Path to file with input data')
	parser_recomendation.set_defaults(func=recomendation)
	
	parser_update = subparsers.add_parser('update',help='Update tsv files')
	parser_update.set_defaults(func=update_db)
	
	return parser.parse_args()

args = parse_args()
args.func(args)