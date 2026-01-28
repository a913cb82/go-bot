#!/usr/bin/env python3
import os
import subprocess
import sys

MODELS_DIR = "models"
HUMAN_MODEL_URL = "https://github.com/lightvector/KataGo/releases/download/v1.15.0/b18c384nbt-humanv0.bin.gz"
MAIN_MODEL_URL = "https://media.katagotraining.org/uploaded/networks/models/kata1/kata1-b28c512nbt-s12192929536-d5655876072.bin.gz"


def download_file(url: str, dest_path: str) -> None:
    if os.path.exists(dest_path):
        print(f"{dest_path} already exists. Skipping.")
        return

    print(f"Downloading {url} to {dest_path}...")
    try:
        # Try curl first
        subprocess.run(["curl", "-L", "-o", dest_path, url], check=True)
        print("Done.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fallback to wget
            subprocess.run(["wget", "-O", dest_path, url], check=True)
            print("Done.")
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            sys.exit(1)


def main() -> None:
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    human_model_path = os.path.join(MODELS_DIR, "human_model.bin.gz")
    download_file(HUMAN_MODEL_URL, human_model_path)

    main_model_path = os.path.join(MODELS_DIR, "main_model.bin.gz")
    # Clean up the previous bad download if it exists and is small
    if os.path.exists(main_model_path):
        if os.path.getsize(main_model_path) < 1000000:
            print("Removing invalid/small main model file...")
            os.remove(main_model_path)

    download_file(MAIN_MODEL_URL, main_model_path)

    # Create a robust human config based on best practices
    config_path = os.path.join(MODELS_DIR, "human.cfg")
    # Always overwrite to ensure correctness
    with open(config_path, "w") as f:
        f.write(
            """# Config for Human SL with KataGo v1.15+
# Based on gtp_human5k_example.cfg

logDir = gtp_logs
logAllGTPCommunication = true
logSearchInfo = true
logSearchInfoForChosenMove = false
logToStderr = false

rules = japanese

allowResignation = true
resignThreshold = -0.99
resignConsecTurns = 20
resignMinScoreDifference = 40
resignMinMovesPerBoardArea = 0.4

# Max visits 40 is good for pass/resign judgment.
# For pure imitation, this is sufficient if humanSLChosenMoveProp = 1.0.
maxVisits = 40
numSearchThreads = 1
lagBuffer = 1.0

delayMoveScale = 2.0
delayMoveMax = 10.0

# ===========================================================================
# HUMAN SL PARAMETERS
# ===========================================================================

# Default profile. Can be overridden via command line: -override-config humanSLProfile=rank_1d
humanSLProfile = rank_5k

# Probability to play a HUMAN-like move vs KataGo's move.
humanSLChosenMoveProp = 1.0

# Ignore human SL pass choice, rely on KataGo.
humanSLChosenMoveIgnorePass = true

# Suppress human moves KataGo hates. Large number = disabled.
humanSLChosenMovePiklLambda = 100000000

# Exploration settings (disabled by default for pure imitation config)
humanSLRootExploreProbWeightless = 0.0
humanSLRootExploreProbWeightful = 0.0
humanSLPlaExploreProbWeightless = 0.0
humanSLPlaExploreProbWeightful = 0.0
humanSLOppExploreProbWeightless = 0.0
humanSLOppExploreProbWeightful = 0.0

humanSLCpuctExploration = 0.50
humanSLCpuctPermanent = 0.2

# ===========================================================================
# OTHER USEFUL PARAMETERS FOR HUMAN PLAY ADJUSTMENT
# ===========================================================================

chosenMoveTemperatureEarly = 0.85
chosenMoveTemperature = 0.70
chosenMoveTemperatureHalflife = 80
chosenMoveTemperatureOnlyBelowProb = 0.01
chosenMoveSubtract = 0
chosenMovePrune = 0

nnCacheSizePowerOfTwo = 17
nnMutexPoolSizePowerOfTwo = 14

# ===========================================================================
# PARAMETERS CHANGED FROM DEFAULT TO MAKE SURE HUMAN SL USAGE WORKS WELL
# ===========================================================================

# Do NOT ignore history for human play.
ignorePreRootHistory = false
analysisIgnorePreRootHistory = false

# Average 2 neural net samples at the root.
rootNumSymmetriesToSample = 2
useLcbForSelection = false

winLossUtilityFactor = 1.0
staticScoreUtilityFactor = 0.30
dynamicScoreUtilityFactor = 0.00

useUncertainty = false
subtreeValueBiasFactor = 0.0
useNoisePruning = false
"""
        )
    print(f"Created robust human config at {config_path}")


if __name__ == "__main__":
    main()
