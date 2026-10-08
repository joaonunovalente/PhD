# Experiment Vibrometer + ORBBEC FEMTO

## Create Container
``` bash
sh docker_run.sh CODE_PATH DATA_PATH

sh docker_run.sh /home/valente/Documents/vscode/PhD-code/Pipeline/exhaustive-grid-search /home/valente/Documents/vscode/PhD-code/Pipeline/data
```

## Pipeline
``` bash
# Capture point clouds
cd /home/valente/Documents/vscode/PhD-code/Pipeline/code
capture_point_clouds.py

# Enter docker container
docker exec -it egs-pipepine-container /bin/bash
cd exhaustive-grid-search/

# Register point clouds
python demo.py  --pc_source_path ../data/test1/depth_1.ply --pc_target_path ../data/test1/depth_2.ply

# Visualize the point clouds
visualize_registration.py 1 1 2
```