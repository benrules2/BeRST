# Behaviour Real-time Spatial Tracking (BeRST)

Track your cats location using CV and simple fiducial markers.

Install Brew:
https://brew.sh/

Install Git:
$ brew install git

brew install opencv
git clone https://github.com/benrules2/cateye.git

cd cateye

python3 -m pip install -r requirements.txt

./detect_cats.py -v --annotate -f ../CatTracking/images/rupert_hd.mov --preview   

