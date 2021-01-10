all: data/17819.csv

data/%.csv:
	pipenv run python scripts/scrape.py $* > $@	
