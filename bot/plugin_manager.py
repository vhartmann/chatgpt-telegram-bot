import json
import os
from typing import Dict, Optional

from plugins.auto_tts import AutoTextToSpeech
from plugins.ddg_image_search import DDGImageSearchPlugin
from plugins.ddg_web_search import DDGWebSearchPlugin
from plugins.dice import DicePlugin
from plugins.gtts_text_to_speech import GTTSTextToSpeech
from plugins.spotify import SpotifyPlugin
from plugins.weather import WeatherPlugin
from plugins.website_content import WebsiteContentPlugin
from plugins.youtube_audio_extractor import YouTubeAudioExtractorPlugin
from plugins.youtube_transcript import YoutubeTranscriptPlugin


class PluginManager:
    """
    A class to manage the plugins and call the correct functions
    """

    def __init__(self, config):
        # enabled_plugins = config.get('plugins', [])
        plugin_mapping = {
            # 'wolfram': WolframAlphaPlugin,
            'weather': WeatherPlugin,
            'ddg_web_search': DDGWebSearchPlugin,
            # 'ddg_translate': DDGTranslatePlugin,
            'ddg_image_search': DDGImageSearchPlugin,
            'spotify': SpotifyPlugin,
            # 'worldtimeapi': WorldTimeApiPlugin,
            'youtube_audio_extractor': YouTubeAudioExtractorPlugin,
            'dice': DicePlugin,
            'gtts_text_to_speech': GTTSTextToSpeech,
            'auto_tts': AutoTextToSpeech,
            # 'whois': WhoisPlugin,
            # 'webshot': WebshotPlugin,
            # 'iplocation': IpLocationPlugin,
            'website_content': WebsiteContentPlugin,
            'youtube_transcript': YoutubeTranscriptPlugin,
        }
        self.plugins = [plugin() for plugin in plugin_mapping.values()]
        # self.plugins = []
        # self.plugins = [plugin_mapping[plugin]() for plugin in enabled_plugins if plugin in plugin_mapping]

    def get_functions_specs(self, query: Optional[str] = None):
        """
        Return the list of function specs that can be called by the model
        """
        use_all_plugins = True
        if query:
            use_all_plugins = query.lower().startswith('z')

        if 'USE_ALL_PLUGINS' in os.environ:
            use_all_plugins = True

        if not use_all_plugins:
            return []

        return [spec for specs in map(lambda plugin: plugin.get_spec(), self.plugins) for spec in specs]

    async def call_function(self, function_name, helper, arguments) -> Dict:
        """
        Call a function based on the name and parameters provided
        """
        plugin = self.__get_plugin_by_function_name(function_name)
        if not plugin:
            return {'error': f'Function {function_name} not found'}

        return await plugin.execute(function_name, helper, **json.loads(arguments))

    def get_plugin_source_name(self, function_name) -> str:
        """
        Return the source name of the plugin
        """
        plugin = self.__get_plugin_by_function_name(function_name)
        if not plugin:
            return ''
        return plugin.get_source_name()

    def __get_plugin_by_function_name(self, function_name):
        return next(
            (
                plugin
                for plugin in self.plugins
                if function_name in map(lambda spec: spec.get('name'), plugin.get_spec())
            ),
            None,
        )
