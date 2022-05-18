# NFTools

Instruction for installation on debian-based OS machines
-Installed VSCode
-sudo apt update
-sudo apt dist-upgrade
-sudo apt install python3 python3-venv python3-pip

-python3 -m venv venv 

-source ./venv/bin/activate

-python3 -m pip install -r requirements.txt

If there are errors installing pillow (require jpeg etc.)
-sudo apt install libjpeg8-dev zlib1g-dev libtiff-dev libfreetype6 libfreetype6-dev libwebp-dev libopenjp2-7-dev libopenjp2-7-dev -y
and then inside venv:
-python3 -m pip install Pillow
