#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The core functions for the Tvheadend API
"""

import datetime
import simplejson
import requests
import tvheadend_api_lib.config as config

if config.API_IS_SELFSIGNED:
    requests.packages.urllib3.disable_warnings()

verify_ssl = not config.API_IS_SELFSIGNED

def convert_unix_to_date(unix):
    """
    Converts the given unix timestamp to datetime
    """
    return datetime.datetime.fromtimestamp(int(unix))

def convert_date_to_unix(date):
    """
    Converts the given datetime to unix timestamp
    """
    return int(date.strftime("%s"))

def get_prime_time():
    """
    Returns prime time
    """
    now = datetime.datetime.now()
    prime = datetime.datetime(now.year, now.month, now.day, 20, 15, 0)
    if convert_date_to_unix(prime) < convert_date_to_unix(now):
        now += datetime.timedelta(days=1)
        prime = datetime.datetime(now.year, now.month, now.day, 20, 15, 0)

    return prime

def check_if_prime_time(start):
    """
    Checks if given start timestamp ist prime time
    """
    prime = convert_date_to_unix(get_prime_time())
    sec = int(prime - start)
    if sec < 120 and sec > -120:
        return True
    else:
        return False

def get_prime_events():
    """
    Returns all prime events
    """

    events = []
    channels = get_channels()
    for channel in channels:
        get_prime_time()
        epgs = get_events_by_channel(channel["uuid"], 1, 300)

        for epg in epgs:
            if check_if_prime_time(epg["start"]):
                events.append(epg)

    return events

def api_post_call(url, data):
    """
    Makes a POST request to the API
    """

    response = requests.post(config.API_ADDRESS + url, verify=verify_ssl,
                             data=data, auth=(config.API_USER, config.API_PASSWORD))

    resp = simplejson.loads(response.text)
    if "entries" in resp:
        return resp["entries"]
    else:
        return resp

def api_get_call(url, params=None):
    """
    Makes a GET request to the API
    """

    response = requests.get(config.API_ADDRESS + url, verify=verify_ssl,
                            params=params, auth=(config.API_USER, config.API_PASSWORD))

    resp = simplejson.loads(response.text)
    if "entries" in resp:
        return resp["entries"]
    else:
        return resp

def get_channels():
    """
    Returns all the channels
    """
    data = {
        "sort": "number",
        "dir": "ASC",
        "all": "1"
    }
    channels = api_post_call("api/channel/grid", data)
    return channels

def get_tags_from_channel(channel_id):
    """
    Returns all the tags from a channel
    """
    tags = []
    channels = get_channels()

    for channel in channels:
        if channel["uuid"] == channel_id:
            tags = channel["tags"]

    return tags

def get_name_for_tag(tag):
    """
    Returns the name of a tag by id
    """
    tag = api_get_call("api/idnode/load?uuid=" + tag)
    return tag[0]["text"]

def get_named_tags_from_channel(channel_id):
    """
    Returns all the names of the tags from a channel_id
    """

    named_tags = []
    tags = get_tags_from_channel(channel_id)

    for tag in tags:
        named_tags.append(get_name_for_tag(tag))

    return named_tags

def get_upcoming_recordings(start=0, limit=500):
    """
    Returns all upcoming recordings
    """

    data = {
        "sort": "start_real",
        "dir": "ASC",
        "start": start,
        "limit": limit
    }

    items = api_post_call("api/dvr/entry/grid_upcoming", data)
    content = []
    for item in items:
        if item["status"] != "Running":
            content.append(item)

    return content

def get_current_recordings(start=0, limit=500):
    """
    Returns all current recordings
    """

    data = {
        "sort": "start_real",
        "dir": "ASC",
        "start": start,
        "limit": limit
    }

    items = api_post_call("api/dvr/entry/grid_upcoming", data)
    content = []
    for item in items:
        if item["status"] == "Running":
            content.append(item)

    return content

def get_failed_recordings(start=0, limit=500):
    """
    Returns all failed recordings
    """

    data = {
        "sort": "start_real",
        "dir": "ASC",
        "start": start,
        "limit": limit
    }

    return api_post_call("api/dvr/entry/grid_failed", data)

def get_finished_recordings(start=0, limit=500):
    """
    Returns all finished recordings
    """

    data = {
        "sort": "start_real",
        "dir": "ASC",
        "start": start,
        "limit": limit
    }

    return api_post_call("api/dvr/entry/grid_finished", data)

def get_events_by_channel(channel_id, start=0, limit=500):
    """
    Returns all events by channel
    """

    data = {
        "channel": channel_id,
        "start": start,
        "limit": limit
    }

    return api_post_call("api/epg/events/grid", data)

def get_current_event_by_channel(channel_id):
    """
    Returns the current event by channel_id
    """

    event = get_events_by_channel(channel_id, 0, 1)
    if event:
        return event[0]
    else:
        return None

def schedule_recording(event_id):
    """
    Schedules the given event
    """

    data = {
        "event_id": event_id,
        "config_uuid": ""
    }

    resp = api_post_call("api/dvr/entry/create_by_event", data)

    return check_if_scheduled_by_event(event_id)

def get_event_by_title(title, start=0, limit=500):
    """
    Returns an event by the given title
    """

    data = {
        "start": start,
        "limit": limit,
        "title": title
    }

    return api_post_call("api/epg/events/grid", data)

def get_event_by_id(event_id, start=0, limit=500):
    """
    Searches for an event by the given id
    """

    found_event = None

    for channel in get_channels():
        for event in get_events_by_channel(channel["uuid"], start=start, limit=limit):
            if str(event["eventId"]) == str(event_id):
                found_event = event

    return found_event

def get_recording_by_id(dvr_id):
    """
    Returns the recording by the given id
    """

    recordings = []

    for rec in get_upcoming_recordings():
        if rec["uuid"] == dvr_id:
            return rec
        recordings.append(rec)

    for rec in get_current_recordings():
        if rec["uuid"] == dvr_id:
            return rec
        recordings.append(rec)

    for rec in get_failed_recordings():
        if rec["uuid"] == dvr_id:
            return rec
        recordings.append(rec)

    for rec in get_finished_recordings():
        if rec["uuid"] == dvr_id:
            return rec
        recordings.append(rec)

    for rec in recordings:
        if rec["uuid"] == dvr_id:
            return rec

    return None

def cancel_current_recording_by_dvr(dvr_id):
    """
    Cancels the given recording
    """

    data = {
        "uuid": {
            dvr_id
        }
    }

    if get_recording_by_id(dvr_id) is None:
        return False

    api_post_call("api/dvr/entry/cancel", data)
    return not check_if_scheduled_by_dvr(dvr_id)

def delete_recording_by_dvr(dvr_id):
    """
    Deletes the given upcoming recording by dvr
    """

    data = {
        "uuid": {
            dvr_id
        }
    }

    if get_recording_by_id(dvr_id) is None:
        return False

    api_post_call("api/idnode/delete", data)
    return not check_if_scheduled_by_dvr(dvr_id)

def check_if_scheduled_by_event(event_id):
    """
    Checks if the given event is scheduled for recording
    """

    #dvrState
    #dvrUuid

    for rec in get_upcoming_recordings():
        if str(rec["broadcast"]) == str(event_id):
            return True

    for rec in get_current_recordings():
        if str(rec["broadcast"]) == str(event_id):
            return True

    return False

def check_if_scheduled_by_dvr(dvr_id):
    """
    Checks if the given event is scheduled for recording
    """
    for rec in get_upcoming_recordings():
        if rec["uuid"] == dvr_id:
            return True

    for rec in get_current_recordings():
        if rec["uuid"] == dvr_id:
            return True

    return False
