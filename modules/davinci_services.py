from pathlib import Path
import DaVinciResolveScript as dvr_script
import os


class Davinci:
    def __init__(self, tag):
        self.name_project = tag
        self.folder_path = f"{os.getenv('PATH_SHORT_VIDEOS')}/{tag}/{tag}_videos"
        self.resolve = dvr_script.scriptapp("Resolve")
        self.project_manager = self.resolve.GetProjectManager()

    def create_new_project(self):
        project = self.project_manager.CreateProject(self.name_project)
        if not project:
            raise Exception("Failed to create project!")
        return project

    def import_videos(self, project):
        media_pool = project.GetMediaPool()
        video_files = list(Path(self.folder_path).glob('*.mp4'))

        # Importing each file
        imported_clips = []
        for video_file in video_files:
            clips = media_pool.ImportMedia(str(video_file))
            if clips:
                imported_clips.extend(clips)

        return imported_clips

    def create_timeline(self, project, clips, timeline_name="Merged Timeline"):
        media_pool = project.GetMediaPool()
        timeline = media_pool.CreateEmptyTimeline(timeline_name)
        if not timeline:
            raise Exception("Failed to create timeline!")

        for clip in clips:
            media_pool.AppendToTimeline(clip)

        return timeline

    def render(self, project, save_path):
        render_settings = {
            'TargetDir': save_path,
            'CustomName': self.name_project,
            'Format': 'mp4',
            'VideoCodec': 'H.264',
        }
        project.SetRenderSettings(render_settings)
        project.AddRenderJob()
        project.StartRendering()
        if project.IsRenderingInProgress() == "False":
            print("rendering finish")
        return f"{save_path}/{self.name_project}"
