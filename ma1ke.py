#!/usr/bin/env python

from commands import (GetAudio, SplitFile, PasteFiles, All, Prepare,
                      FrameCount, MatchFrames, TEMP_DIR, Clean)
import os
import sys


def sceneDetect(inFile):
    try:
        with open(f'{inFile}.scenes.csv') as f:
            return f.read().strip()
    except FileNotFoundError:
        from scenedetect.video_manager import VideoManager
        from scenedetect.stats_manager import StatsManager
        from scenedetect.scene_manager import SceneManager
        from scenedetect.detectors import ContentDetector

    videoManager = VideoManager([inFile])
    statsManager = StatsManager()
    sceneManager = SceneManager(statsManager)
    sceneManager.add_detector(ContentDetector())
    baseTimecode = videoManager.get_base_timecode()

    videoManager.start()
    sceneManager.detect_scenes(frame_source=videoManager)
    sceneList = sceneManager.get_scene_list(baseTimecode)

    splitList = [scene[0].get_frames() for scene in sceneList][1:]
    with open(f'{inFile}.scenes.csv', 'w') as f:
        print(','.join(splitList), file=f)
    return splitList


inFile = sys.argv[1]
if not os.path.exists(inFile):
    print("Input file not found. Exiting.")
    exit()
if not os.path.samefile(inFile, os.path.basename(inFile)):
    print("WARNING: input file not in current directory.")
    print("All operations will take place in this directory.")
    print("It is recommended to move the file here.")
splits = sceneDetect(inFile)

commandList = [
    All(),
    Clean(),
    Prepare(splits),
    GetAudio(inFile),
    SplitFile(inFile, splits),
    PasteFiles(splits),
    FrameCount(inFile, os.path.splitext(inFile)[0] + ".fc"),
    FrameCount("%.mkv", "%.fc"),
    MatchFrames(f"{TEMP_DIR}/check/%.match",
                f"{TEMP_DIR}/split/%.fc",
                f"{TEMP_DIR}/encode/%.fc"),
    MatchFrames("verifyOutputFrames", "output.fc",
                os.path.splitext(inFile)[0] + ".fc"), ]

with open('Makefile', 'w') as fo:
    print("# Generated by ma1ke v0.1\n", file=fo)

    for command in commandList:
        print(command.makeCommand(), file=fo)

print("Makefile written.")
