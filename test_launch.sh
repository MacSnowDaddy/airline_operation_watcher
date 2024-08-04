export TARGET="test"
export ENV="ec2"
Xvfb :99 -screen 0 1280x720x16 &
export DISPLAY=:99
export PYTHONPATH=/home/ec2-user/.pyenv/versions/3.10.4/lib/python3.10/site-packages:$PYTHONPATH
/home/ec2-user/.pyenv/shims/python3 daily_aviation_analyzer.py >> /home/ec2-user/test_launch.log 2>&1
