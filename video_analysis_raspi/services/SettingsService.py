from video_analysis_raspi.model.Settings import Settings


class SettingsService:
    settings: Settings

    def __init__(self):
        self.settings = Settings()

    def get_settings(self):
        pass

    def get_setting(self, setting_name):
        pass

    def change_setting(self, setting_name):
        pass
