import pte
import json
import subprocess



def run(configPath, name):
    with open(configPath) as f:
        config = json.load(f)
        pte.logger.info("Executing script (%s: %s)", configPath, name)
        for cmd in config[name]:
            p = subprocess.run(cmd, capture_output = True)
            if len(p.stdout) > 0:
                pte.logger.info(p.stdout.decode("utf-8"))
            if len(p.stderr) > 0:
                pte.logger.error(p.stderr.decode("utf-8"))
        pte.logger.info("Script is executed (%s: %s).", configPath, name)