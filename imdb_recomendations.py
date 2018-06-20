# -*- python version: 2.7 -*-
# -*- coding: utf-8 -*-

import argparse
from pandas import DataFrame
import pandas as pd
import warnings
from collections import Counter
from pandas.core.common import SettingWithCopyWarning

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

# urls
site = 'https://imdb.com/title/{}'
# Paths to tsv files
name_basics = 'data/name.basics.tsv'
title_basics = 'data/title.basics.tsv'
title_crew = 'data/title.crew.tsv'
title_principal = 'data/title.principals.tsv'
# Columns names
primaryName = 'primaryName'
primaryTitle = 'primaryTitle'
originalTitle = 'originalTitle'
startYear = 'startYear'
genres = 'genres'
Count = 'count'
Tconst = 'tconst'
Nconst = 'nconst'
Directors = 'directors'
#

def search(args):
	# Filtering all films by dates,title and genre 
	films = parse_tsv(title_basics)
	films[startYear] = pd.to_numeric(films[startYear], errors='coerce').fillna(0).astype(int)
	check_genre = films[genres].str.contains(''.join(map(lambda x: '(?i)(?=.*'+x+')',args.genre)),na=False)
	title_check = films[primaryTitle].str.contains(' '.join(args.title))|films[originalTitle].str.contains(' '.join(args.title))
	date_check = (films[startYear]> int(args.years_after)) & (films[startYear] < int(args.years_before))
	filtered_films = films[check_genre&title_check&date_check]
	del films
	names = parse_tsv(name_basics)
	if args.actor_name:
		check_actor_name = names[primaryName].str.contains(''.join(map(lambda x: '(?=.*'+x+')',args.actor_name)),na=False)
		actor_filtered_names = names[check_actor_name]
	else:
		actor_filtered_names = names
	if args.director_name:
		check_director_name = names[primaryName].str.contains(''.join(map(lambda x: '(?=.*'+x+')',args.director_name)),na=False)
		director_filtered_names = names[check_director_name]
	else:
		director_filtered_names = names
	actor_nconst = actor_filtered_names.index.values
	director_nconst = director_filtered_names.index.values
	del names
	crew = parse_tsv(title_crew)
	filtered_crew = crew[crew[Directors].isin(director_nconst)]
	# Filtering by director names
	filtered_films_with_crew = pd.merge(filtered_films, filtered_crew, how='left', on=[Tconst])
	if args.director_name:
		filtered_films_with_crew = filtered_films_with_crew[filtered_films_with_crew[Directors].notnull()]
	del crew
	# Filtering by actor names
	principal = parse_tsv(title_principal)
	filtered_principal = principal[principal[Nconst].isin(actor_nconst)]
	filtered_films_with_crew_principal = pd.merge(filtered_films_with_crew,filtered_principal,how='left',on=[Tconst])
	if args.actor_name:
		filtered_films_with_crew_principal = filtered_films_with_crew_principal[filtered_films_with_crew_principal[Nconst].notnull()]
	final_film_list = filtered_films_with_crew_principal
	del principal
	#Printing results, except duplicates
	for index,row in final_film_list[~final_film_list.index.duplicated()].iterrows():
		try:
			directors =  ','.join(parse_tsv(name_basics).loc[row[Directors].split(', ')][primaryName].values)
		except:
			directors = 'None'
		print '\t'.join([row[primaryTitle],str(row[startYear]),directors,site.format(index)])


def statistics(args):
	names = parse_tsv(name_basics)
	check_name = names[primaryName].str.contains(''.join(map(lambda x: '(?=.*' + x + ')',args.name)), na=False)
	filtered_names = names[check_name]
	names = dict(zip(filtered_names.index.values,filtered_names[primaryName].values))
	crew = parse_tsv(title_crew)
	for nconst in names.keys():
		filtered_crew_by_nconst = crew[crew[Directors].str.contains(nconst,na=False)]
		films =list(filtered_crew_by_nconst.index.values)
		principal = parse_tsv(title_principal)
		filtered_principal_by_nconst = principal[principal[Nconst].str.contains(nconst,na=False)]
		films += list(filtered_principal_by_nconst.index.values)
		films = list(set(films))
		films_df = parse_tsv(title_basics)
		films = films_df[films_df.index.str.contains('|'.join(films),na=False)]
		genres_sorted_by_count = films.groupby([genres])[primaryTitle].count().reset_index(name=Count) \
															.sort_values([Count],ascending=False)[genres].values
		print names.get(nconst)
		for genre in genres_sorted_by_count:
			for index,row in films[films[genres] == genre].iterrows():
				print '\t'.join([row[primaryTitle],site.format(index)])


def  recomendation(args):
	path = args.path
	with open(path,'r') as  file_film:
		films = map(lambda x: x.strip(),file_film.readlines())
		# Search for favorite genre
		imdb_films = parse_tsv(title_basics)
		check_title = imdb_films[primaryTitle].str.contains('|'.join(map(lambda x: '('+x+')', films)), na=False)
		filtered_films = imdb_films[check_title]
		filtered_films[startYear] = pd.to_numeric(filtered_films[startYear], errors='coerce').fillna(0).astype(int)
		genre_counter = Counter([y for x in map(lambda z: z.split(','),filtered_films[genres].values) for y in x])
		favorite_genre = genre_counter.keys()[genre_counter.values().index(max(genre_counter.values()))]
		# Search for favorite actor
		principal = parse_tsv(title_principal)
		filtered_principal = principal[principal.index.str.contains('|'.join(map(lambda x:'('+x+')',filtered_films.index.values)))]
		principal_counter = Counter(filtered_principal[Nconst].values)
		favorite_actor = principal_counter.keys()[principal_counter.values().index(max(principal_counter.values()))]
		# Search for favorite director
		crew = parse_tsv(title_crew)
		filtered_crew = crew[crew.index.str.contains('|'.join(map(lambda x: '(' + x + ')', filtered_films.index.values)))]
		crew_counter = Counter([y for x in map(lambda z: z.split(','),filtered_crew[Directors].values) for y in x])
		favorite_director = crew_counter.keys()[crew_counter.values().index(max(crew_counter.values()))]
		# Search for favorite years
		years = [x for x in filtered_films[startYear].values if x!=0]
		favorite_years = []
		for year in range(min(years),max(years)-5):
			five_years_films = [x for x in years if x>year and x <year+5]
			favorite_years = five_years_films if len(five_years_films)>len(favorite_years) else favorite_years
		favorite_years = [min(favorite_years),min(favorite_years)+5]
		# Getting names
		names = parse_tsv(name_basics)
		try:
			actor_name = names[names.index == favorite_actor][primaryName].values[0]
		except:
			actor_name=''
		try:
			director_name = names[names.index == favorite_director][primaryName].values[0]
		except:
			director_name=''
		# Search films
		print 'Best matches:'
		search(argparse.Namespace(actor_name=[actor_name],director_name=[director_name],genre=favorite_genre,title='',
		 						  years_after=favorite_years[0],
		 						  years_before=favorite_years[1]))
		print 'Good matches with director, genre and time:'
		search(argparse.Namespace(actor_name=[''], director_name=[director_name], genre=favorite_genre, title='',
		 						  years_after=favorite_years[0],
		 						  years_before=favorite_years[1]))
		print 'Good matches with actor, genre and time:'
		search(argparse.Namespace(actor_name=[actor_name],director_name=[''], genre=favorite_genre, title='',
		 						  years_after=favorite_years[0],
		 						  years_before=favorite_years[1]))
		print 'Good matches with director,actor and time:'
		search(argparse.Namespace(actor_name=[actor_name], director_name=[''], genre='', title='',
								  years_after=favorite_years[0],
								  years_before=favorite_years[1]))
		print 'Good matches with actor, director and genre:'
		search(argparse.Namespace(actor_name=[actor_name], director_name=[''], genre=favorite_genre, title='',
								  years_after=0,
								  years_before=3000))


#def update_db():
#	print args

def parse_tsv(path_to_file):
	df = DataFrame.from_csv(path_to_file, sep='\t', header=0)
	return df

def parse_args():
	parser = argparse.ArgumentParser(description='')
	subparsers = parser.add_subparsers()
	
	parser_search = subparsers.add_parser('search')
	parser_search.add_argument('--title',nargs='*',default='',help='Movie title')
	parser_search.add_argument('--director_name',nargs='*',default='',help='Name of the director')
	parser_search.add_argument('--actor_name',nargs='*',default='',help='Name of the actor')
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
	
#	parser_update = subparsers.add_parser('update',help='Update tsv files')
#	parser_update.set_defaults(func=update_db)
	
	return parser.parse_args()

if __name__ == '__main__': 
	args = parse_args()
	args.func(args)