export TARGET="test"
export ENV="ec2"
touch /home/ec2-user/test_launch_called.log
Xvfb :99 -screen 0 1280x720x16 &
export DISPLAY=:99
python3 daily_aviation_analyzer.py
