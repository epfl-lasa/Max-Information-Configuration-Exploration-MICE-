#!/bin/sh
python dataProcessingScripts/joint2TaskActual.py
python dataProcessingScripts/joint2TaskDesired.py
python3 dataProcessingScripts/dataProcess.py
python3 dataProcessingScripts/dataVisualise_quick.py