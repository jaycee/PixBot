PY := bin/python
PIP := bin/pip
FLASK := lib/python2.7/site-packages/flask/__init__.py
TELEGRAM := lib/python2.7/site-packages/telegram/__init__.py

.PHONY: sysdeps
sysdeps:
	sudo apt install python-virtualenv

$(PY):
	virtualenv .

$(PIP): $(PY)

$(TELEGRAM): $(PIP)
	$(PIP) install -r requirements.txt

$(FLASK): $(PIP)
	$(PIP) install -r requirements.txt

.PHONY: deps
deps: $(FLASK) $(TELEGRAM)

.PHONY: clean
clean:
	- rm -rf lib include local bin build src
	- rm pip-selfcheck.json
