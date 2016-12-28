#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The core functions for the Tvheadend API
"""

import datetime
import simplejson
import requests
import config

class ApiCore(object):
    """
    ApiCore
    """

    @classmethod
    def convert_unix_to_date(cls, unix):
        """
        Converts the given unix timestamp to datetime
        """
        return datetime.datetime.fromtimestamp(int(unix))

    @classmethod
    def convert_date_to_unix(cls, date):
        """
        Converts the given datetime to unix timestamp
        """
        return int(date.strftime("%s"))

    @classmethod
    def get_prime_time(cls):
        """
        Returns prime time
        """
        now = datetime.datetime.now()
        prime = datetime.datetime(now.year, now.month, now.day, 20, 15, 0)
        if cls.convert_date_to_unix(prime) < cls.convert_date_to_unix(now):
            now += datetime.timedelta(days=1)
            prime = datetime.datetime(now.year, now.month, now.day, 20, 15, 0)

        return prime

    @classmethod
    def check_if_prime_time(cls, start):
        """
        Checks if given start timestamp ist prime time
        """
        prime = cls.convert_date_to_unix(cls.get_prime_time())
        sec = int(prime - start)
        if sec < 120 and sec > -120:
            return True
        else:
            return False

    @classmethod
    def get_prime_events(cls):
        """
        Returns all prime events
        """

        events = []
        channels = cls.get_channels()
        for channel in channels:
            cls.get_prime_time()
            epgs = cls.get_events_by_channel(channel["uuid"], 1, 300)

            for epg in epgs:
                if cls.check_if_prime_time(epg["start"]):
                    events.append(epg)

        return events

    @classmethod
    def api_post_call(cls, url, data):
        """
        Makes a POST request to the API
        """

        response = requests.post(config.API_ADDRESS + url,
                                 data=data, auth=(config.API_USER, config.API_PASSWORD))

        resp = simplejson.loads(response.text)
        if "entries" in resp:
            return resp["entries"]
        else:
            return resp

    @classmethod
    def api_get_call(cls, url, params=None):
        """
        Makes a GET request to the API
        """

        response = requests.get(config.API_ADDRESS + url,
                                params=params, auth=(config.API_USER, config.API_PASSWORD))

        resp = simplejson.loads(response.text)
        if "entries" in resp:
            return resp["entries"]
        else:
            return resp

    @classmethod
    def get_channels(cls):
        """
        Returns all the channels
        """
        data = {
            "sort": "number",
            "dir": "ASC",
            "all": "1"
        }
        channels = cls.api_post_call("api/channel/grid", data)
        return channels

    @classmethod
    def get_tags_from_channel(cls, channel_id):
        """
        Returns all the tags from a channel
        """
        tags = []
        channels = cls.get_channels()

        for channel in channels:
            if channel["uuid"] == channel_id:
                tags = channel["tags"]

        return tags

    @classmethod
    def get_name_for_tag(cls, tag):
        """
        Returns the name of a tag by id
        """
        tag = cls.api_get_call("api/idnode/load?uuid=" + tag)
        return tag[0]["text"]

    @classmethod
    def get_named_tags_from_channel(cls, channel_id):
        """
        Returns all the names of the tags from a channel_id
        """

        named_tags = []
        tags = cls.get_tags_from_channel(channel_id)

        for tag in tags:
            named_tags.append(cls.get_name_for_tag(tag))

        return named_tags

    @classmethod
    def get_upcoming_recordings(cls, start=0, limit=50):
        """
        Returns all upcoming recordings
        """

        data = {
            "sort": "start_real",
            "dir": "ASC",
            "start": start,
            "limit": limit
        }

        return cls.api_post_call("api/dvr/entry/grid_upcoming", data)

    @classmethod
    def get_failed_recordings(cls, start=0, limit=50):
        """
        Returns all failed recordings
        """

        data = {
            "sort": "start_real",
            "dir": "ASC",
            "start": start,
            "limit": limit
        }

        return cls.api_post_call("api/dvr/entry/grid_failed", data)

    @classmethod
    def get_finished_recordings(cls, start=0, limit=50):
        """
        Returns all finished recordings
        """

        data = {
            "sort": "start_real",
            "dir": "ASC",
            "start": start,
            "limit": limit
        }

        return cls.api_post_call("api/dvr/entry/grid_finished", data)

    @classmethod
    def get_events_by_channel(cls, channel_id, start, limit):
        """
        Returns all events by channel
        """

        data = {
            "channel": channel_id,
            "start": start,
            "limit": limit
        }

        return cls.api_post_call("api/epg/events/grid", data)

    @classmethod
    def get_current_event_by_channel(cls, channel_id):
        """
        Returns the current event by channel_id
        """

        event = cls.get_events_by_channel(channel_id, 0, 1)
        if event:
            return event[0]
        else:
            return None

    @classmethod
    def schedule_recording(cls, event_id):
        """
        Schedules the given event
        """

        data = {
            "event_id": event_id,
            "config_uuid": ""
        }

        success = False
        resp = cls.api_post_call("api/dvr/entry/create_by_event", data)
        if not resp:
            success = True

        return success

    @classmethod
    def search_event_by_title(cls, title, start, limit):
        """
        Searches for an event by the given title
        """

        data = {
            "start": start,
            "limit": limit,
            "title": title
        }

        return cls.api_post_call("api/epg/events/grid", data)


    @classmethod
    def cancel_current_recording(cls, recording_id):
        """
        Cancels the given recording
        """

        data = {
            "uuid": {
                recording_id
            }
        }

        success = False

        resp = cls.api_post_call("api/dvr/entry/cancel", data)
        if not resp:
            success = True

        return success

    @classmethod
    def delete_upcoming_recording(cls, recording_id):
        """
        Deletes the given upcoming recording_id
        """

        data = {
            "uuid": {
                recording_id
            }
        }

        success = False
        resp = cls.api_post_call("api/idnode/delete", data)
        if not resp:
            success = True

        return success
