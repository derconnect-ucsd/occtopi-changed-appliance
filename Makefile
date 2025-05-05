run: venv/Scripts/activate
	venv/Scripts/python.exe src/data-visualization.py

update_requirements: venv/Scripts/activate
	venv/Scripts/pip.exe freeze > requirements.txt

# Will create a virtual env (venv) and install all requirements to it.
venv/Scripts/activate: requirements.txt
	python -m venv venv
	venv/Scripts/pip.exe install -q -r requirements.txt

clean:
	rmdir /S /Q __pycache__
	rmdir /S /Q venv