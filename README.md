# overlay
PoC python, PIL based CLI to quickly overlay one image to a set of other images

### Installation

I didn't feel like putting this up on PyPi so you'll have to install from here. There are other ways to do this but I think this is the most robust way. 

 - If you haven't already, install [`pipx`](https://pypi.org/project/pipx/) system wide
```bash
pip install pipx
```
 - Clone the repo
```bash
git glone https://github.com/Mattwmaster58/overlay.git
```
 - Install with `pipx`
```bash
pipx install -e ./overlay
```
 - `-e` install in development mode, so anytime you may need to pull an upgrade from this repo, a simple git pull _should_ update the app
 - You may be prompted by `pipx` to add its paths to your PATH variable, you will need to do this to ensure `overlay` is available system wide.
