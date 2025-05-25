# minimal pokemon scaffold for LLMs

the others have way too many training wheels. How do the LLMs do in the cold hard real world?

# setup

install python 3.12

probably get in your python venv, for me that's
```bash
python3 -m venv venv # first time, to create
source venv/bin/activate # every time, to enter the venv
```

`pip install -r requirements.txt`

create `keys.py` and put in whichever API keys you intend to use like so:
```py
ANTHROPIC_API_KEY="your key"
```

you may also need to install tkinter manually, even though it's supposed to be bundled with python. I did on Ubuntu 24.04 (just do `sudo apt-get install python3-tk`)

# run

python3 main.py
