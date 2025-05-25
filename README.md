# minimal pokemon scaffold for LLMs

The others have overlays, custom tools, and developer hints, which is BS.
How do the LLMs do in the cold hard real world?
Screenshots, basic log, and generic scratchpad only.

# setup

1. install python 3.12 (other versions might work but I haven't tested)

2. probably get in your python venv, for me that's
```bash
python3 -m venv venv # first time, to create
source venv/bin/activate # every time, to enter the venv
```

3. `pip install -r requirements.txt`

4. create `keys.py` like so:
```py
ANTHROPIC_API_KEY="your key"
```

5. find a pokemon gameboy rom and put it in the root dir as `pokemon.gb`

6. _(optional)_ you may also need to install tkinter manually, even though it's supposed to be bundled with python. I did on Ubuntu 24.04 (just do `sudo apt-get install python3-tk`)

# run

`python3 main.py`

By default, you are the LLM. To choose a different model, edit the top of `main.py` to change where `get_llm_response` is imported from.
