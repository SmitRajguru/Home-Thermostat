# check if a tmux session is already running
tmux_state=$(tmux ls | grep thermostat)
if [ -n "$tmux_state" ]; then
    echo "Thermostat is already running"
else
    echo "Starting thermostat"
    tmux new-session -d -s thermostat
    tmux send-keys -t thermostat:0 "cd /home/antonpi/Desktop/Home-Thermostat" C-m
    tmux send-keys -t thermostat:0 "python3 thermostat.py" C-m
fi