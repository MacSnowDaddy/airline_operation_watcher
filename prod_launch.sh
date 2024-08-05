export TARGET="production"
export ENV="ec2"
Xvfb :99 -screen 0 1280x720x16 &
export DISPLAY=:99
export PYTHONPATH=/home/ec2-user/.pyenv/versions/3.10.4/lib/python3.10/site-packages:$PYTHONPATH
/home/ec2-user/.pyenv/shims/python3 data_collector_caller.py ana prev >> /home/ec2-user/production_launch.log 2>&1 &
/home/ec2-user/.pyenv/shims/python3 data_collector_caller.py jal prev >> /home/ec2-user/production_launch.log 2>&1 &
/home/ec2-user/.pyenv/shims/python3 data_collector_caller.py sky prev >> /home/ec2-user/production_launch.log 2>&1 &
/home/ec2-user/.pyenv/shims/python3 data_collector_caller.py ado prev >> /home/ec2-user/production_launch.log 2>&1 &