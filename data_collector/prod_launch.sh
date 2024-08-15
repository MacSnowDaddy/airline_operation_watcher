export TARGET="production"
export ENV="ec2"
Xvfb :99 -screen 0 1280x720x16 &
export DISPLAY=:99
sudo timedatectl set-timezone Asia/Tokyo
export PYTHONPATH=/home/ec2-user/.pyenv/versions/3.10.4/lib/python3.10/site-packages:$PYTHONPATH
cd /home/ec2-user/airline-ops/airline_operation_watcher
/home/ec2-user/.pyenv/shims/python3 data_collector/data_collector_caller.py ana prev >> /home/ec2-user/production_launch.log 2>&1 &
PID_ANA=$!
/home/ec2-user/.pyenv/shims/python3 data_collector/data_collector_caller.py jal prev >> /home/ec2-user/production_launch.log 2>&1 &
PID_JAL=$!
/home/ec2-user/.pyenv/shims/python3 data_collector/data_collector_caller.py sky prev >> /home/ec2-user/production_launch.log 2>&1 &
PID_SKY=$!
/home/ec2-user/.pyenv/shims/python3 data_collector/data_collector_caller.py ado prev >> /home/ec2-user/production_launch.log 2>&1 &
PID_ADO=$!

wait $PID_ANA
wait $PID_JAL
wait $PID_SKY
wait $PID_ADO

SNS_TOPIC_ARN=$1

#publish the result
/home/ec2-user/.pyenv/shims/python3 /home/ec2-user/airline-ops/airline_operation_watcher/会社別RJTT2RJCC定時到着率.py | /home/ec2-user/.pyenv/shims/python3 ~/airline-ops/airline_operation_watcher/data_collector/sns_publish_ontime_arr_rate.py $SNS_TOPIC_ARN >> /home/ec2-user/production_launch.log 2>&1

INSTANCE_ID=$2

# Ensure the INSTANCE_ID environment variable is set
if [ -z "$INSTANCE_ID" ]; then
  echo "Error: INSTANCE_ID is not set."
  exit 1
fi

aws ec2 stop-instances --instance-ids $INSTANCE_ID >> /home/ec2-user/production_launch.log 2>&1
