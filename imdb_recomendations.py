# -*- python version: 2.7 -*-
# -*- coding: utf-8 -*-

import argparse
from pandas import DataFrame
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# Paths to tsv files
name_basics = 'data/name.basics.tsv'
title_basics = 'data/title.basics.tsv'
title_crew = 'data/title.crew.tsv'
title_principal = 'data/title.principals.tsv'


def filter_names_by_args(name):
	names = parse_tsv(name_basics)
	check_name = names['primaryName'].str.contains(''.join(map(lambda x: '(?=.*'+x+')',name)),na=False)
	filtered_names = names[check_name]
	return filtered_names

def search(args):
	# Filtering all films by dates,title and genre 
	films = parse_tsv(title_basics)
	films['startYear'] = pd.to_numeric(films['startYear'], errors='coerce').fillna(0).astype(int)
	check_genre = films['genres'].str.contains(''.join(map(lambda x: '(?=.*'+x+')',args.genre)),na=False)
	title_check = films['primaryTitle'].str.contains(' '.join(args.title))|films['originalTitle'].str.contains(' '.join(args.title))
	date_check = (films['startYear']> int(args.years_after)) & (films['startYear'] < int(args.years_before))
	filtered_films = films[check_genre&title_check&date_check]
	del films
	# Filtering all names 
	filtered_names = filter_names_by_args(args.name)
	nconst = filtered_names.index.values
	# Merging tables
	crew = parse_tsv(title_crew)
	filtered_films_with_crew=pd.merge(filtered_films,crew,how='left',on=['tconst'])
	del crew
	principal = parse_tsv(title_principal)
	principal_names=pd.merge(filtered_films_with_crew,principal,how='left',on=['tconst'])
	del principal
	# Filtering films by names
	filter_name = principal_names['nconst'].str.contains('|'.join(map(lambda x: x,nconst)),na=False)
	final_film_list = principal_names[filter_name]
	#Printing results, except duplicates
	for index,row in final_film_list[~final_film_list.index.duplicated()].iterrows():
		directors =  ','.join(parse_tsv(name_basics).loc[row['directors'].split(', ')]['primaryName'].values)
		print '\t'.join([row['primaryTitle'],str(row['startYear']),directors,'https://imdb.com/title/{}'.format(index)])
	
	
def statistics(args):
	filtered_names = filter_names_by_args(args.name)
	names = dict(zip(filtered_names.index.values,filtered_names['primaryName'].values))
	for nconst in names.keys():
		print names[nconst]
		crew = parse_tsv(title_crew)
		filtered_crew_by_nconst = crew[crew['directors'].str.contains(nconst,na=False)]
		films =list(filtered_crew_by_nconst.index.values)
		principal = parse_tsv(title_principal)
		filtered_principal_by_nconst = principal[principal['nconst'].str.contains(nconst,na=False)]
		films += list(filtered_principal_by_nconst.index.values)
		films = list(set(films))
		films_df = parse_tsv(title_basics)
		films = films_df[films_df.index.str.contains('|'.join(films),na=False)]
		genres_sorted_by_count = films.groupby(['genres'])['primaryTitle'].count().reset_index(name='count') \
															.sort_values(['count'],ascending=False)['genres'].values
		for genre in genres_sorted_by_count:
			for index,row in films[films['genres'] == genre].iterrows():
				print '\t'.join([row['primaryTitle'],'https://imdb.com/title/{}'.format(index)])
				
				
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
	parser_search.add_argument('--title',nargs='*',default='',help='Movie title')
	parser_search.add_argument('--name',nargs='*',default='',help='Name of the actor or director')
	parser_search.add_argument('--years_after',default=1000,help='Release date of the film after')
	parser_search.add_argument('--years_before',default=3000,help='Release date of the film after')
	parser_search.add_argument('--genre',nargs='*',default='',help='Genre of the film')
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

if __name__ == '__main__': 
	args = parse_args()
	args.func(args)