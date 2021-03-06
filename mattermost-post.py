from contextlib import closing
import http.client
import json
import re
import sublime
import sublime_plugin
import sys


class MattermostPostCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        project_settings = sublime.load_settings("mattermost-post.sublime-settings")

        url = project_settings.get("url")
        team = project_settings.get("team")
        channel = project_settings.get("channel")
        pat = project_settings.get("pat")
        post_fileinfo = project_settings.get("post_fileinfo", False)
        max_lines = project_settings.get("max_lines", 0)
        syntax_map = project_settings.get("syntax_map")

        if url == "" or team == "" or channel == "" or pat == "" or max_lines == 0:
            sublime.error_message("Mattermost Post: Setting missing.")
            return

        if re.match("^[a-z0-9-.]*$", url) is None:
            sublime.error_message(
                "Mattermost Post: Setting url may contain only lowercase letters, numbers, dots and dashes."
            )
            return

        if re.match("^[a-z0-9-]*$", team) is None:
            sublime.error_message(
                "Mattermost Post: Setting team may contain only lowercase letters, numbers and dashes."
            )
            return

        if re.match("^[a-z0-9-]*$", channel) is None:
            sublime.error_message(
                "Mattermost Post: Setting channel may contain only lowercase letters, numbers and dashes."
            )
            return

        with closing(http.client.HTTPSConnection(url)) as conn:
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": "Bearer {}".format(pat),
            }
            try:
                conn.request("GET", "/api/v4/teams/name/{}/channels/name/{}".format(team, channel), "", headers)
            except Exception as e:
                sublime.error_message("Mattermost Post: Trouble with https connection. See console for more info.")
                raise e
            channel_query_response = conn.getresponse()

            if channel_query_response.status != 200:
                sublime.error_message("Mattermost Post: Unable to get mm channel. See console for more info.")
                print("Mattermost Post Error\n---")
                print(channel_query_response.status)
                print(channel_query_response.reason)
                print(channel_query_response.read())
                print("---")
                return

            post = {
                "channel_id": json.loads(channel_query_response.read().decode())['id'],
                "message": ""
            }

            selections = self.view.sel()
            syntax = syntax_map.get(
                self.view.settings().get('syntax'),
                self.view.settings().get('syntax').split("/")[-1].rsplit(".")[0].split(" ")[0].lower()
            )

            full_path = self.view.file_name()
            if full_path is not None and post_fileinfo is True:
                post['message'] += "Filename: {}\n".format(
                    full_path.split("{}/".format(self.view.window().extract_variables()['folder']))[1]
                )

            code_blocks = ""
            for region in selections:
                region_text = self.view.substr(region)

                if len(region_text) < 1:
                    continue

                if len(region_text.splitlines()) > max_lines:
                    sublime.error_message("Mattermost Post: selection lines > {}".format(max_lines))
                    return

                if post_fileinfo is True:
                    beginning_linenumber = self.view.rowcol(region.begin())[0] + 1
                    ending_linenumber = self.view.rowcol(region.end())[0] + 1
                    code_blocks += "Linenumbers: {} - {}\n".format(beginning_linenumber, ending_linenumber)

                code_blocks += "```{}\n".format(syntax)
                code_blocks += "{}\n".format(region_text)
                code_blocks += "```\n"

            if code_blocks == "":
                return

            post['message'] += code_blocks

            if sys.getsizeof(post['message']) > 16300:
                sublime.error_message("Mattermost Post: selections > 16300 bytes")

            try:
                conn.request("POST", "/api/v4/posts", json.dumps(post), headers)
            except Exception as e:
                sublime.error_message("Mattermost Post: Trouble with https connection. See console for more info.")
                raise e

            posts_response = conn.getresponse()
            if posts_response.status != 201:
                sublime.error_message("Mattermost Post: Unable to create mm post. See console for more info.")
                print("Mattermost Post Error\n---")
                print(posts_response.status)
                print(posts_response.reason)
                print(posts_response.read())
                print("---")
                return
