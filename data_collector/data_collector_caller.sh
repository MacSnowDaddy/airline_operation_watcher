export TARGET="production"
export ENV="ec2"
Xvfb :99 -screen 0 1280x720x16 &
export DISPLAY=:99
export PYTHONPATH=/home/ec2-user/.pyenv/versions/3.10.4/lib/python3.10/site-packages:$PYTHONPATH
/home/ec2-user/.pyenv/shims/python3 data_collector_caller.py $1 $2 >> /home/ec2-user/data_collector_caller.log 2>&1
sudo halt