 # Dependencies
 in the following order run
 ```
sudo pacman -S pyenv
pyenv install 3.10
```
or whatever you use to set python version locally. Then switch it to create a venv in my case
```
pyenv local 3.10.18
python -m venv obsidian-latex-ocr-env
```
(note to return back to system do `pyenv local system`)
now do 
```
source obsidian-latex-ocr-env/bin/activate.fish
pip install latex_ocr_server
pip install marker-pdf
```
noting that `latex_ocr_server` requires python 3.10! 
also do `pip install <torch-version-appropriate for you system if the above cant>` eg:
```
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```
for gpu 50 series users who need at least cm120. finally, clone this repo to your home then run with your venv still activated
```
python -m latex_ocr_server start
```
