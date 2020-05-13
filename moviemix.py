import json
import os
import random
import hashlib
import shutil
from random import seed
from random import randint
import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip
from datetime import datetime

class Utils:

    @staticmethod
    def log(msg):
        print(msg)

    @staticmethod
    def get_file_contents(file_path = "", parse_json = False):
        contents = ""
        try:
            with open(file_path) as f:
                contents = f.read()
                f.close()
                contents = json.loads(contents) if parse_json else contents
        except:
            raise "[x] Error when parsing file contents at: " + file_path
        return contents

    @staticmethod
    def create_file(file_path = "", default_contents = ""):
        try:
            with open(file_path, "w") as f:
                f.write(default_contents)
                f.close()
        except:
            raise "[x] Error when creating a file at: " + file_path
    
    @staticmethod
    def file_exists(file_path = "", check_readable = False, check_writable = False):
        try:
            exists = False
            exists = os.path.isfile(file_path)
            exists = os.access(file_path, os.R_OK) if exists and check_readable else exists
            exists = os.access(file_path, os.W_OK) if exists and check_writable else exists
            return exists
        except:
            raise "[x] Error when attempting to check file existence at: " + file_path
    
    @staticmethod
    def write_to_file(file_path, contents):
        if not Utils.file_exists(file_path):
            Utils.create_file(file_path, contents)
        else:
            with open(file_path, "w") as f:
                f.write(contents)
                f.close()
    
    @staticmethod
    def create_dir(dir_path, clean=False):
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
            return
        if clean:
            for each_file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, each_file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except:
                    raise "[x] Error encountered when attempting to delete (%s)" % (file_path)
            return
    
    @staticmethod
    def generate_range_seq(start, end, random_order=False):
        r = list(range(start, end))
        if random_order:
            random.shuffle(r)
        return r
    
    @staticmethod
    def shuffle(population_list = False, start = -1, end = -1, population = []):
        r = Utils.in_order(population_list, start, end, population)
        random.shuffle(r)
        return r
    
    @staticmethod
    def in_order(population_list = False, start = -1, end = -1, population = []):
        r = population if population_list else list(range(start, end))
        return r

    @staticmethod
    def reverse(population_list = False, start = -1, end = -1, population = []):
        r = Utils.in_order(population_list, start, end, population)
        r.reverse()

class MixerUtils:
    @staticmethod
    def select_width(clip_a, clip_b):
        return [clip_a.w, clip_a.h] if clip_a.w > clip_b.w else [clip_b.w, clip_b.h]
    
    @staticmethod
    def select_height(clip_a, clip_b):
        return [clip_a.w, clip_a.h] if clip_a.h > clip_b.h else [clip_b.w, clip_b.h]
    
    @staticmethod
    def select_custom(custom_res, _):
        return [custom_res.w, custom_res.h]

    @staticmethod
    def select_def(_, __):
        return [-1, -1]
    
    @staticmethod
    def strategy_select(strategy, clip_a, clip_b):
        picker = {
            Config.ST_STRAT_NONE: MixerUtils.select_def,
            Config.ST_STRAT_WIDTH: MixerUtils.select_width,
            Config.ST_STRAT_HEIGHT: MixerUtils.select_height
        }

        [w, h] = (picker[strategy])(clip_a, clip_b)
        return w, h
    
    @staticmethod
    def new_clip_resolution(w, h):
        class ClipResolution:
            def __init__(self, w, h):
                    self.w = w
                    self.h = h
        return ClipResolution(w, h)



class Config:
    config_path = "./config.json"

    # -- Constants: Mix mode
    MX_MULTI = "multi"
    MX_SINGLE = "single"
    MX_DEF = MX_MULTI

    # -- Constants: Transition mode
    T_STATIC = "static"
    T_DEF = T_STATIC
    
    # -- Constants: Ordering
    ORD_RANDOM = "random"
    ORD_INORDER = "inorder"
    ORD_REVERSE = "reverse"
    ORD_DEF = ORD_INORDER

    # -- Constants: Clipping mode & compilation
    C_CLIP = "clip"
    C_FULL = "full"
    C_DEF = C_FULL
    COMP_UNQ = "unique"
    COMP_GEN = "gen"
    COMP_DEF = COMP_GEN

    # -- Constants: Duration & bounds
    DUR_MIN_DEF = -1
    DUR_MAX_DEF = -1
    START_DEF = -1
    END_DEF = -1

    # -- Constants: Export & formats
    OUT_PREFIX_DEF = "moviemixed-"
    FMT_MP4 = "mp4"
    FMT_DEF = FMT_MP4

    # -- Constants: Iterations & stitch behavior
    ITER_DEF = 1
    ST_MIN_DEF = -1
    ST_MAX_DEF = -1
    
    FILL_LOOP = "looping"
    FILL_TRIM = "trim"
    FILL_DEF = FILL_LOOP
    
    ST_STRAT_WIDTH = "width"
    ST_STRAT_HEIGHT = "height"
    ST_STRAT_CUSTOM = "custom"
    ST_STRAT_NONE = "none"
    ST_STRAT_DEF = ST_STRAT_NONE
    
    ST_BITRATE_DEF = "5000k"

    ST_STRAT_H_DEF = -1
    ST_STRAT_W_DEF = -1


    # -- Constants: Other stitch behaviors
    ST_FPS_DEF = 50
    

    def __init__(self):
        Utils.log("Loading configuration")
        self.config = Utils.get_file_contents(Config.config_path, parse_json = True)
    
    def mode(self):
        return self.config["mix_mode"] if "mix_mode" in self.config else Config.MX_DEF

    def transition(self):
        return self.config["transition"] if "transition" in self.config else Config.T_DEF
    
    def order(self):
        return self.config["ordering"] if "ordering" in self.config else Config.ORD_DEF
    
    def clipping_mode(self):
        return self.config["clipping"]["mode"] if "clipping" in self.config and "mode" in self.config["clipping"] else Config.C_DEF
    
    def compile_pattern(self):
        return self.config["clipping"]["compile"] if "clipping" in self.config and "compile" in self.config["clipping"] else Config.COMP_DEF
    
    def min_duration(self):
        return self.config["clipping"]["duration"]["min"] if "clipping" in self.config and "duration" in self.config["clipping"] and "min" in self.config["clipping"]["duration"] else Config.DUR_MIN_DEF
    
    def max_duration(self):
        return self.config["clipping"]["duration"]["max"] if "clipping" in self.config and "duration" in self.config["clipping"] and "max" in self.config["clipping"]["duration"] else Config.DUR_MAX_DEF
    
    def start_at(self):
        return self.config["clipping"]["bounds"]["start"] if "clipping" in self.config and "bounds" in self.config["clipping"] and "start" in self.config["clipping"]["bounds"] else Config.START_DEF

    def end_at(self):
        return self.config["clipping"]["bounds"]["end"] if "clipping" in self.config and "bounds" in self.config["clipping"] and "end" in self.config["clipping"]["bounds"] else Config.END_DEF

    def output_prefix(self):
        return self.config["output_prefix"] if "output_prefix" in self.config else Config.OUT_PREFIX_DEF
    
    def format(self):
        return self.config["format"] if "format" in self.config else Config.FMT_DEF
    
    def iterations(self):
        return self.config["iterations"] if "iterations" in self.config else Config.ITER_DEF

    def min_stitch_duration(self):
        return self.config["stitch"]["duration"]["min"] if "stitch" in self.config and "duration" in self.config["stitch"] and "min" in self.config["stitch"]["duration"] else Config.ST_MIN_DEF

    def max_stitch_duration(self):
        return self.config["stitch"]["duration"]["max"] if "stitch" in self.config and "duration" in self.config["stitch"] and "max" in self.config["stitch"]["duration"] else Config.ST_MAX_DEF
    
    def stitch_strategy(self):
        return self.config["stitch"]["resolution"]["strategy"] if "stitch" in self.config and "resolution" in self.config["stitch"] and "strategy" in self.config["stitch"]["resolution"] else Config.ST_STRAT_DEF
    
    def stitch_res_custom(self):
        strategy = self.stitch_strategy()
        if strategy != Config.ST_STRAT_CUSTOM:
            raise "[x] Attempted to get custom res when the strategy was not custom. Defined strategy: %s" % (strategy)
        w = self.config["stitch"]["resolution"]["w"] if "stitch" in self.config and "resolution" in self.config["stitch"] and "w" in self.config["stitch"]["resolution"] else Config.ST_STRAT_W_DEF
        h = self.config["stitch"]["resolution"]["h"] if "stitch" in self.config and "resolution" in self.config["stitch"] and "h" in self.config["stitch"]["resolution"] else Config.ST_STRAT_H_DEF
        return w, h

    def fps(self):
        return self.config["stitch"]["frames"]["fps"] if "stitch" in self.config and "frames" in self.config["stitch"] and "fps" in self.config["stitch"]["frames"] else Config.ST_FPS_DEF
    
    def bitrate(self):
        return self.config["stitch"]["frames"]["bitrate"] if "stitch" in self.config and "frames" in self.config["stitch"] and "bitrate" in self.config["stitch"]["frames"] else Config.ST_BITRATE_DEF

    def filler(self):
        return self.config["filler"] if "filler" in self.config else Config.FILL_DEF

    def export_stitch(self, resolution = None):
        exp = {}
        exp["strategy"] = self.stitch_strategy()
        exp["min_duration"] = self.min_stitch_duration()
        exp["fps"] = self.fps()
        exp["bitrate"] = self.bitrate()
        exp["resolution"] = {}
        exp["resolution"]["w"] = Config.ST_STRAT_W_DEF
        exp["resolution"]["h"] = Config.ST_STRAT_H_DEF
        if self.stitch_strategy() == Config.ST_STRAT_CUSTOM:
            exp["resolution"]["w"], exp["resolution"]["h"] = self.stitch_res_custom()
        elif resolution is not None:
            exp["resolution"]["w"], exp["resolution"]["h"] = resolution.w, resolution.h
        return exp


class Storage:
    config_path = "./store.json"
    def __init__(self):
        Utils.log("Loading storage")
        if not Utils.file_exists( file_path = Storage.config_path, check_writable=True):
            Utils.create_file( file_path = Storage.config_path, default_contents = "{}")
        self.config = Utils.get_file_contents(Storage.config_path, True)
    
    def export(self):
        Utils.write_to_file(Storage.config_path, json.dumps(self.config))
    
    def store(self, k, v):
        self.config[k] = v
        self.export()

    def key_exists(self, k):
        return k in self.config


class Tailor:
    CLIP_PREFIX = "tailor_clip-"

    @staticmethod
    def resize_patch(strategy, clip, to):
        if to.w == -1 or to.h == -1:
            return clip
        if strategy == Config.ST_STRAT_HEIGHT:
            return clip.resize(height = to.h)
        if strategy == Config.ST_STRAT_WIDTH:
            return clip.resize(width = to.w)
        return clip

    @staticmethod
    def cut_patches(clip_config, temp_dir):
        Utils.log(" [Tailor] Cutting patch from (%s)" % ( clip_config["name"]))
        ffmpeg_extract_subclip(
            clip_config["name"], 
            clip_config["start_at"], clip_config["end_at"],
            targetname = temp_dir + "/" + Tailor.CLIP_PREFIX + clip_config["name"]
        )

    @staticmethod
    def stitch_patches(
        clips_config, temp_dir, expected_duration, export_config, output_name, output_dir = "."):
        
        Utils.log(" [Tailor] Stitching together patches")

        resolution_strategy = export_config["strategy"]
        preferred_resolution = MixerUtils.new_clip_resolution(export_config["resolution"]["w"], ["h"])
        min_duration = export_config["min_duration"]
        fps = int(export_config["fps"])
        bitrate = export_config["bitrate"]

        patches = [temp_dir + "/" + Tailor.CLIP_PREFIX + i["name"] for i in clips_config]
        
        # now if we are short of the min duration, then we need to loop & add till 
        # we satisfy the min length requirement
        if min_duration != Config.ST_MIN_DEF:
            i = 0
            Utils.log(" [Tailor] Ensuring your attire is of appropriate length")
            while expected_duration < min_duration:
                # Utils.log("i is %d and exp dur is: %d and min dur is %d" % (i, expected_duration, min_duration))
                patches.append(temp_dir + "/" + Tailor.CLIP_PREFIX + clips_config[i]["name"])
                expected_duration = expected_duration + clips_config[i]["duration"]
                i = (i+1) % len(clips_config)
            Utils.log(" [Tailor] ...done, This combination should look perfect!")

        Utils.log(" [Tailor] Ensuring the best get up for you")
        patches = [Tailor.resize_patch(resolution_strategy, VideoFileClip(i), preferred_resolution) for i in patches]
        cloth_piece = mp.concatenate_videoclips(patches, method="compose")
        
        Utils.log(" [Tailor] Adding final touches")
        cloth_piece.write_videofile(
            output_dir + "/" + output_name, 
            codec="mpeg4",
            audio=False, verbose=False, 
            preset="ultrafast", 
            fps=fps,
            bitrate=bitrate
        )
        
        Utils.log(" [Tailor] Its done!")
        cloth_piece.close()

class Mixer:
    temp_dir = "./tmp_mixer"
    output_dir = "./output"
    def __init__(self):
        Utils.log("-------------------------------------------------------")
        self.config = Config()
        self.storage = Storage()
        self.subjects = []
        self.load_files()
        Utils.log("-------------------------------------------------------")

    def assemble_subjects(self):
        assembler = {
            Config.ORD_INORDER: Utils.in_order,
            Config.ORD_REVERSE: Utils.reverse,
            Config.ORD_RANDOM:  Utils.shuffle
        }
        return (assembler[self.config.order()])(population_list = True, population = self.subjects)

    def load_files(self):
        Utils.log("Loading workspace subjects")
        working_format = self.config.format()
        if working_format.endswith("pyc") or working_format.endswith("py"):
            raise "[x] Invalid format specifier for mixing: (%s)" % (working_format)
        Utils.log(" - Working with format: (%s)" % (working_format))
        for each_file in os.listdir("./"):
            if each_file.endswith(working_format):
                self.subjects.append(each_file)
        
        if len(self.subjects) == 0:
            raise "[x] No valid files with format (%s) found in working dir. Nothing to work on." % (working_format)
        
        if self.config.mode() == Config.MX_SINGLE and len(self.subjects) > 1:
            raise "[x] Too many subjects found (%d) while the mixing mode was (%s)" % (len(self.subjects), Config.MX_SINGLE)

    def generate_sequence(self):
        Utils.log(" - Generating pattern")
        seq = []
        resolution = MixerUtils.new_clip_resolution(-1, -1)
        is_res_custom = self.config.stitch_strategy() == Config.ST_STRAT_CUSTOM
        if is_res_custom:
            resolution.w, resolution.h = self.config.stitch_res_custom()
        total_duration = 0
        max_st_duration = self.config.max_stitch_duration()
        for each_subject in self.subjects:
            seq_body = { "name": each_subject }
            start_at = 0
            end_at = 0
            min_duration = 0
            max_duration = 0
            passes = True

            video_clip = VideoFileClip(each_subject)
            duration = int(video_clip.duration)
            seq_body["duration"] = duration

            # Only if we are in clipping mode, we need to set appropriate bounds
            if self.config.clipping_mode() == Config.C_CLIP:
                start_at = self.config.start_at() if self.config.start_at() != Config.START_DEF else 0
                end_at = self.config.end_at() if self.config.end_at() != Config.END_DEF else duration
                min_duration = duration if self.config.min_duration() != Config.DUR_MIN_DEF else self.config.min_duration()
                max_duration = duration if self.config.max_duration() != Config.DUR_MAX_DEF else min(duration, self.config.max_duration())
                passes = passes and min_duration <= duration
                passes = passes and (end_at - start_at) <= min_duration
            else:
                start_at = 0
                end_at = duration
                min_duration = duration
                max_duration = duration

            if not passes:
                Utils.log(
                    "    [i] Skipping (%s) since its duration checks have failed: Start: (%d), End: (%d), Duration: (%d), Min Duration: (%d), Max Duration: (%d)" % (
                        each_subject,
                        start_at, end_at, duration,
                        min_duration, max_duration
                    )
                )
                seq_body["skip"] = True
            else:
                final_duration = randint(min_duration, max_duration)
                start_at = randint(start_at, end_at - final_duration)
                end_at = start_at + final_duration
                seq_body["start_at"] = start_at
                seq_body["end_at"] = end_at
                seq_body["duration"] = final_duration
                
                # Keep track of a rough estimate of the vid length
                total_duration = total_duration + final_duration
                # Update resolution final data based on strategy
                if not is_res_custom:
                    resolution.w, resolution.h = MixerUtils.strategy_select(self.config.stitch_strategy(), resolution, video_clip)
            seq.append(seq_body)
            if max_st_duration != Config.ST_MAX_DEF and total_duration > max_st_duration:
                break
        
        # Check the stitch & fill behavior
        stitch_check = self.config.min_stitch_duration() != Config.ST_MIN_DEF
        min_stitch_violation = total_duration < self.config.min_stitch_duration()
        min_stitch_filler_non_complaint = self.config.filler() != Config.FILL_LOOP
        if stitch_check and min_stitch_violation and min_stitch_filler_non_complaint:
            raise "[x] Minimum stitch duration violation: Filler policy non complaint! Expected duration: (%d), Min Stitch duration: (%d), Filler: (%s)" % (
                total_duration, self.config.min_stitch_duration(), self.config.filler()
            )
        return seq, total_duration, resolution

    def stitch_sequence(self, seq, expected_duration, resolution):
        if len(seq) >= len(self.subjects):
            raise "[x] Generated sequence length (%d) not equal to the number of subjects (%d)" % (len(seq), len(self.subjects))
        
        Utils.create_dir(Mixer.temp_dir, True)
        Utils.create_dir(Mixer.output_dir)
        for each_seq in seq:
            Tailor.cut_patches(each_seq, Mixer.temp_dir)
        Tailor.stitch_patches(
            seq, Mixer.temp_dir, expected_duration,
            self.config.export_stitch(resolution=resolution),
            Mixer.output_dir + "/" + self.config.output_prefix() + datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + "." + self.config.format()
        )

    def start(self):
        seed()
        Utils.log(">> MovieMix: Starting over (%d) iterations" % (self.config.iterations()))
        for each_iteration in range(0, self.config.iterations()):
            Utils.log("[i] Iteration %d" % (each_iteration))
            Utils.log("")
            
            Utils.log(" ==> Assembling subjects")
            self.subjects = self.assemble_subjects()
            
            # Generate pattern for this subject set
            movie_pattern = {}
            expected_duration = 0
            resolution = None
            if self.config.compile_pattern() == Config.COMP_UNQ:
                while True:
                    movie_pattern, expected_duration, resolution = self.generate_sequence()
                    pattern_hash = hashlib.md5(json.dumps(movie_pattern).encode('utf-8')).hexdigest()
                    if not self.storage.key_exists(pattern_hash):
                        self.storage.store(pattern_hash, True)
                        break
            else:
                movie_pattern, expected_duration, resolution = self.generate_sequence()
            
            Utils.log(" ==> Expected duration to be around ~%d" % (expected_duration))
            Utils.log(" ==> Expected resolution to be around (w,h) %dx%d" % (resolution.w, resolution.h))
            
            # Ready to stitch the seq
            self.stitch_sequence(movie_pattern, expected_duration, resolution)
            
            
        

    
    
m = Mixer()
m.start()