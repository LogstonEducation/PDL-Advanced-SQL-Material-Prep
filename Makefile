data:
	date
	python main.py "sqlite:///data.sqlite3"
	date

clean:
	rm data.sqlite3
