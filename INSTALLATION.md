## Installation
```bash
git clone https://github.com/ronnie-samaroo/bittex-subnet
cd bittex-subnet
python -m pip install -e .
```


### Install Redis
Install Redis on your host system.

Linux [instructions](https://redis.io/docs/install/install-redis/install-redis-on-linux/)

```bash
sudo apt install lsb-release curl gpg

curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get update
sudo apt-get install redis
```

Ensure the local Redis server is started.

```bash
sudo systemctl status redis-server.service
```

You should see output like:
```
● redis-server.service - Advanced key-value store
     Loaded: loaded (/lib/systemd/system/redis-server.service; disabled; vendor preset: enabled)
     Active: active (running) since Thu 2023-11-16 22:35:42 EST; 3min 25s ago
       Docs: http://redis.io/documentation,
             man:redis-server(1)
   Main PID: 31881 (redis-server)
     Status: "Ready to accept connections"
      Tasks: 5 (limit: 38370)
     Memory: 2.9M
        CPU: 387ms
     CGroup: /system.slice/redis-server.service
             └─31881 "/usr/bin/redis-server 127.0.0.1:6379" "" "" "" "" "" "" ""

Nov 16 22:35:42 user systemd[1]: Starting Advanced key-value store...
Nov 16 22:35:42 user systemd[1]: Started Advanced key-value store.
```


### Secure Redis Configuration
In order to securely run a node, whether a miner or validator, you must run ensure your redis instance is secure from the outside internet and is password-protected.

The following steps are **mandatory** for secure communication on the network:

1. Closing the default redis port
1. Password protecting redis
1. Enabling persistence

#### Close external traffic to Redis 
> Note: **EXPOSING THE REDIS PORT IS A MAJOR SECURITY RISK**

This Bash script is designed to configure UFW (Uncomplicated Firewall) to manage access to default Redis port 6379. The script's primary function is to block all external traffic to port 6379, typically used by Redis, while allowing local processes to still access this port.

##### Usage
To run the script, use the following command in the terminal:
```bash
sudo ./scripts/redis/create_redis_firewall.sh
```
Running this script will:
- Check if UFW is installed and active. If UFW is not active, the script will attempt to enable it.
- Set UFW rules to deny all external access to port 6379.
- Set UFW rules to allow all local access to port 6379.
- Apply the changes by reloading UFW.

##### Important Considerations
- **Test Before Production**: Always test the script in a controlled environment before deploying it in a production setting.
- **Existing Rules**: If there are existing rules for port 6379, review the script to ensure compatibility.
- **Firewall Management**: This script is specifically for systems using UFW. If another firewall management tool is in use, this script will not be compatible.

#### Automated Redis Password Configuration
To enhance security, our system now automatically generates a strong password for Redis. This is **REQUIRED**. This is handled by the `set_redis_password.sh` script. Follow these steps to set up Redis with an automated password:

1. **Run the Redis Start Script**: 
    ```bash
    bash scripts/redis/set_redis_password.sh
    ```
    This script generates a secure password for Redis, attempts to shut down any running Redis instances, and then starts Redis with the new password.

2. **Set `REDIS_PASSWORD` Environment Variable**: 
    The script will export the `REDIS_PASSWORD` environment variable. Ensure this variable is set in your environment where the Redis client is running.

   To export your redis password generated in `set_redis_password.sh` as an environment variable at any time, run:
   ```bash
   REDIS_CONF="/etc/redis/redis.conf"
   export REDIS_PASSWORD=$(sudo grep -Po '^requirepass \K.*' $REDIS_CONF)
   ```

3. **Test password successfully enabled**
    Use the provided script `test_redis_require_pass.sh`
    ```bash
    bash ./scripts/redis/test_redis_require_pass.sh
    ```

#### Enable persistence
If persistence is not enabled in your redis instance, it is **CRUCIAL** that this feature is used. Provided script `./scripts/redis/enable_persistence.sh` does exactly this.

```bash
bash ./scripts/redis/enable_persistence.sh
```

You can verify that this was done correctly by running another provided script to test this feature was enabled.
```bash
bash ./scripts/redis/test_persistence.sh
```

> Note these scripts and operations REQUIRE sudo

#### Redis Troubleshooting
If you encounter issues with Redis, follow these steps:

1. **Check for Existing Redis Processes**: 
    Use `lsof` to look for processes using the default Redis port (6379).
    ```bash
    sudo lsof -i:6379
    ```
    If any processes are using this port, they will be listed.

2. **Terminate Unwanted Redis Processes**: 
    Find the PID under the `PID` column and terminate it using `kill`.
    ```bash
    kill -9 <PID>
    # Example: kill -9 961206
    ```

3. **Restart the Redis Service**: 
    If needed, restart the Redis service.
    ```bash
    systemctl restart redis
    ```


### Install PM2
This will allow you to use the process manager `pm2` for easily setting up your miner or validator.

Install nodejs and npm
```bash
sudo apt install nodejs npm
```

Once this completes, install pm2 globally
```bash
sudo npm install pm2 -g
```


### Running a miner
You can run a miner in your base environment like so:

```bash
python neurons/miner.py --wallet.name <NAME> --wallet.hotkey <HOTKEY> --logging.debug
```

However, it is recommended to use a process manager, such as `pm2`. This can be done simply:

```bash
pm2 start <path-to-script> --interpreter <path-to-python-binary> --name <unique-name> -- <program-args..,>
```

For example running a miner:
```bash
pm2 start /home/user/bittex-subnet/neurons/miner.py --interpreter /home/user/miniconda3/envs/bittex/bin/python --name miner -- --netuid 33 --wandb.off --wallet.name default --wallet.hotkey miner  --axon.port 8888 --logging.debug
```

> Make sure to use absolute paths when executing your pm2 command.

#### Options
- `--netuid`: Specifies the chain subnet uid. Default: 33.
- `--miner.name`: Name of the miner, used for organizing logs and data. Default: "bittex-miner".
- `--neuron.device`: Device to run the miner on, e.g., "cuda" for GPUs or "cpu" for CPU. Default depends on CUDA availability.

- `--blacklist.force_validator_permit`: If True, only allows requests from validators. Default: False.
- `--blacklist.allow_non_registered`: If True, allows non-registered hotkeys to mine. Default: False.

- `--wandb.off`: Disables Weight and Biases logging. Default: False.
- `--wandb.project_name`: Project name for WandB logging. Default: "bittex-subnet".
- `--wandb.entity`: WandB entity (username or team name) for the run. Default: "bittex".
- `--wandb.offline`: Runs WandB in offline mode. Default: False.
- `--wandb.notes`: Notes to add to the WandB run. Default: "".

- `--wallet.address`: Wallet address for transactions.
- `--wallet.private_key`: Private key for the wallet.

These options allow you to configure the miner's behavior, blacklist/whitelist settings, priority handling, and integration with monitoring tools like WandB. Adjust these settings based on your mining setup and requirements.


### Running a validator
```bash
python neurons/validator.py --wallet.name <NAME> --wallet.hotkey <HOTKEY>
```

A dummy wallet is automatically configured and used for all encryption on the network as a validator. The registered coldkey is not exposed. 

Run a validator using `pm2`:
```bash
pm2 start /home/user/bittex-subnet/neurons/validator.py --interpreter /home/user/miniconda3/envs/bittex/bin/python --name validator -- --netuid 33 --logging.debug --wallet.name default --wallet.hotkey validator
```

#### Options
- `--netuid`: Specifies the chain subnet uid. Default: 33.
- `--neuron.name`: Specifies the name of the validator neuron. Default: "bittex-validator".
- `--neuron.device`: The device to run the validator on (e.g., "cuda" for GPU, "cpu" for CPU). Default: "cuda" if CUDA is available, else "cpu".
- `--neuron.num_concurrent_forwards`: The number of concurrent forward requests running at any time. Default: 1.
- `--neuron.disable_set_weights`: If set, disables setting weights on the chain. Default: False.
- `--neuron.events_retention_size`: File size for retaining event logs (e.g., "2 GB"). Default: "2 GB".
- `--neuron.dont_save_events`: If set, event logs will not be saved to a file. Default: False.
- `--neuron.vpermit_tao_limit`: The maximum TAO allowed for querying a validator with a vpermit. Default: 500.
- `--neuron.winner_reward_rate`: Specifies the rate at which the winner is rewarded.

- `--wandb.off`: Disables Weight and Biases logging. Default: False.
- `--wandb.project_name`: Project name for WandB logging. Default: "bittex-subnet".
- `--wandb.entity`: WandB entity (username or team name) for the run. Default: "bittex".
- `--wandb.offline`: Runs WandB in offline mode. Default: False.
- `--wandb.notes`: Notes to add to the WandB run. Default: "".

These options allow you to fine-tune the behavior of the validator neuron. Adjust these settings based on your specific requirements and infrastructure.


### Local Subtensor
It is *highly* recommended that all miners and validators run their own local subtensor node. This will resolve the many issues commonly found with intermittent connectivity across all subnets.

To start your miner/validator using your local node, include the flag `--subtensor.network local` into your startup parameters.

Below are two methods to getting local subtensor up and running. Either use docker, or manually install on the hostmachine.

#### Docker installation
For easiest installation, run subtensor inside of the foundation-provided docker container.

For official docker and docker-compose install instructions, see [here](https://docs.docker.com/engine/install/ubuntu/#installation-methods) and [here](https://docs.docker.com/compose/install/linux/#install-using-the-repository), respectively.

```bash
# Install the docker compose plugin
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Clone subtensor
git clone https://github.com/opentensor/subtensor
cd subtensor

# Start the subtensor container on port 9944
sudo docker compose up -d
```

#### Manual Installation
Provided are two scripts to build subtensor, and then to run it inside a pm2 process as a convenience. If you have more complicated needs, see the [subtensor](https://github.com/opentensor/subtensor/) repo for more details and understanding.
```bash
# Installs dependencies and builds the subtensor binary
./scripts/subtensor/build_subtensor_linux.sh

# Runs local subtensor in a pm2 process (NOTE: this can take several hours to sync chain history)
# Make sure the directory is configured properly to run from the built subtensor binary
# This lives in `./subtensor/target/release/node-subtensor`, so if your subtensor repo lives in
# ~/bittex-subnet/subtensor (by default) then you would need to cd in, e.g.:
# cd ~/bittex-subnet/subtensor

# Run the script to start subtensor
./scripts/subtensor/start_local_subtensor.sh
```

You should see output like this in your pm2 logs for the process at startup:

```bash
pm2 logs subtensor

1|subtenso | 2023-12-22 14:21:30 🔨 Initializing Genesis block/state (state: 0x4015…9643, header-hash: 0x2f05…6c03)    
1|subtenso | 2023-12-22 14:21:30 👴 Loading GRANDPA authority set from genesis on what appears to be first startup.    
1|subtenso | 2023-12-22 14:21:30 🏷  Local node identity is: 12D3KooWAXnooHcMSnMpML6ooVLzFwsmt5umFhCkmkxH88LvP5gm    
1|subtenso | 2023-12-22 14:21:30 💻 Operating system: linux    
1|subtenso | 2023-12-22 14:21:30 💻 CPU architecture: aarch64    
1|subtenso | 2023-12-22 14:21:30 💻 Target environment: gnu    
1|subtenso | 2023-12-22 14:21:30 💻 Memory: 62890MB    
1|subtenso | 2023-12-22 14:21:30 💻 Kernel: 5.15.0-1051-aws    
1|subtenso | 2023-12-22 14:21:30 💻 Linux distribution: Ubuntu 20.04.6 LTS    
1|subtenso | 2023-12-22 14:21:30 💻 Virtual machine: no    
1|subtenso | 2023-12-22 14:21:30 📦 Highest known block at #0    
1|subtenso | 2023-12-22 14:21:30 〽️ Prometheus exporter started at 127.0.0.1:9615    
1|subtenso | 2023-12-22 14:21:30 Running JSON-RPC HTTP server: addr=0.0.0.0:9933, allowed origins=["*"]    
1|subtenso | 2023-12-22 14:21:30 Running JSON-RPC WS server: addr=0.0.0.0:9944, allowed origins=["*"]    
1|subtenso | 2023-12-22 14:21:31 🔍 Discovered new external address for our node: /ip4/52.56.34.197/tcp/30333/ws/p2p/12D3KooWAXnooHcMSnMpML6ooVLzFwsmt5umFhCkmkxH88LvP5gm    

1|subtensor  | 2023-12-22 14:21:35 ⏩ Warping, Downloading state, 2.74 Mib (56 peers), best: #0 (0x2f05…6c03), finalized #0 (0x2f05…6c03), ⬇ 498.3kiB/s ⬆ 41.3kiB/s    
1|subtensor  | 2023-12-22 14:21:40 ⏩ Warping, Downloading state, 11.25 Mib (110 peers), best: #0 (0x2f05…6c03), finalized #0 (0x2f05…6c03), ⬇ 1.1MiB/s ⬆ 37.0kiB/s    
1|subtensor  | 2023-12-22 14:21:45 ⏩ Warping, Downloading state, 20.22 Mib (163 peers), best: #0 (0x2f05…6c03), finalized #0 (0x2f05…6c03), ⬇ 1.2MiB/s ⬆ 48.7kiB/s 
```
