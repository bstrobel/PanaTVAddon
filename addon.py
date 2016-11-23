#!
#  -*- coding: utf-8 -*-
import sys
import io
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import panatv
from datetime import datetime
from operator import itemgetter
import requests
import urllib
import urlparse

top_container_id = '0'
top_flag = 'top'
action_save = 'save'
action_save_all = 'save_all'
action_open_container = 'open'
param_parent_container_id = "parent_id"
param_container_id = 'id'
param_action = 'action'
param_video_url = 'video_url'
param_file_name = 'file_name'
param_title = 'title'
param_channel = 'channel'
param_date = 'dateadded'
param_duration = 'duration'
param_genre = 'genre'
param_mediatype = 'mediatype'
param_cdir = 'cdir'
param_ctype = 'ctype'

param_val_ctype_rec = 'rec'
param_val_ctype_other = 'other'

ptva = xbmcaddon.Addon()
record_dir = ptva.getSetting('video_folder')
panatv_hostname = ptva.getSetting('panatv_hostname')

file_ext = 'ts'

xbmc.log("sys.argv[] " + str(sys.argv))

myurl = sys.argv[0]
args = urlparse.parse_qs(sys.argv[2][1:])

addon_handle = int(sys.argv[1])
    
xbmc.log('{0}.handle={1}, myurl={2}'.format(__name__, addon_handle, myurl))


def build_url(query):
    return myurl + '?' + urllib.urlencode(query)
    
    
def mk_file_name(item_props):
    traw = item_props['title'].encode('UTF-8').strip()
    traw = traw.replace(':', ' -')
    traw = traw.replace('/', '-')
    traw = traw.replace('\\', '-')
    traw = traw.replace('"', '')
    traw = traw.replace('*', '#')
    traw = traw.replace('?', '')
    traw = traw.replace('<', '=')
    traw = traw.replace('>', '=')
    traw = traw.replace('|', '+')
    fname = '{0}.{1}'.format(traw, file_ext)
    return os.path.join(record_dir, fname)

    
def get_duration(duration_str):
    if len(duration_str):
        duration_list = duration_str.split(':')
        duration = int(duration_list[-1])
        if len(duration_list) > 1:
            duration += int(duration_list[-2]) * 60
        if len(duration_list) > 2:
            duration += int(duration_list[-3]) * 3600
        return duration
    return 0


def get_date(date_str):
    if len(date_str):
        datetime_l = date_str.split('T')
        date_l = datetime_l[0].split('-')
        time_l = datetime_l[1].split(':')
        return datetime(
            int(date_l[0]),
            int(date_l[1]),
            int(date_l[2]),
            int(time_l[0]),
            int(time_l[1]),
            int(time_l[2])).isoformat(' ')
    return datetime.now().isoformat(' ')


def create_li_params(item_props):
    video_url = item_props['path'].encode('UTF-8').strip()
    params = dict()
    params[param_video_url] = video_url
    params[param_title] = item_props['title'].encode('UTF-8').strip()
    params[param_channel] = item_props['channel_name'].encode('UTF-8').strip()
    params[param_date] = get_date(item_props['date'].encode('UTF-8').strip())
    params[param_mediatype] = 'movie'
    params[param_genre] = '{0}, {1}'.format(params[param_channel], params[param_date])
    params[param_ctype] = param_val_ctype_other
    if item_props['content_source_type'] == 'rec':
        params[param_ctype] = param_val_ctype_rec
        params[param_duration] = get_duration(item_props['duration'].encode('UTF-8').strip())
        params[param_action] = action_save
        params[param_file_name] = mk_file_name(item_props)
    return params


def create_listing(lcdir, cparent_id):
    xbmc.log('Create listing for container_id={0}, parent_id={1}'.format(lcdir, cparent_id))
    try:
        clist, ilist = panatv.get_listing(lcdir, panatv_hostname)
    except requests.RequestException as err:
        infodialog = xbmcgui.Dialog()
        infodialog.ok(
            ptva.getLocalizedString(31000).encode('UTF-8'),
            ptva.getLocalizedString(31001).encode('UTF-8').format(panatv_hostname, err))
        return
    except BaseException as err:
        infodialog = xbmcgui.Dialog()
        infodialog.ok(
            ptva.getLocalizedString(31007).encode('UTF-8'),
            '''
            {0}
            '''.format(err))
        return
    litems = []
    for itemid, item_props in clist.iteritems():
        url = build_url(
            {param_action: action_open_container, param_container_id: itemid, param_parent_container_id: lcdir})
        li = xbmcgui.ListItem(label=item_props['title'], path=url)
        litems.append((url, li, True, get_date('1969-11-23T10:00:00'), 'A'))
    content_source_type = ''
    for itemid, item_props in ilist.iteritems():
        params = create_li_params(item_props)
        content_source_type = params[param_ctype]
        li = xbmcgui.ListItem(label=item_props['title'], path=params[param_video_url])
        if params[param_ctype] == param_val_ctype_rec:
            context_menu = [
                (ptva.getLocalizedString(31002).encode('UTF-8'), 'PlayMedia({0})'.format(build_url(params))),
                (ptva.getLocalizedString(31003).encode('UTF-8'), 'PlayMedia({0})'.format(
                    build_url({param_cdir: lcdir, param_action: action_save_all})))]
            li.addContextMenuItems(context_menu, replaceItems=True)
        li.setInfo('video', params)
        li.setContentLookup(False)  # needed for Panasonic TV because it gets confused by the HEAD requests
        li.setMimeType('video/vnd.dlna.mpeg-tts')  # needed for Panasonic TV because it gets confused by the HEAD req
        litems.append((params[param_video_url], li, False, params[param_date], params[param_title]))
    xbmc.log("Adding directory items: {0}".format(str(litems)))
    if content_source_type == param_val_ctype_rec:
        xbmcplugin.addDirectoryItems(addon_handle, sorted(litems, key=itemgetter(3)))
    else:
        xbmcplugin.addDirectoryItems(addon_handle, sorted(litems, key=itemgetter(4)))
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.setContent(addon_handle, 'movies')
    
    
def create_progress_dialog(progdialog, title, air_date, channel, kb_loaded, str_num_rec=None):
    dtitle = ptva.getLocalizedString(31004).encode('UTF-8')
    if str_num_rec is not None:
        dtitle = ptva.getLocalizedString(31005).encode('UTF-8').format(str_num_rec)
    progdialog.create(
        dtitle,
        ptva.getLocalizedString(31006).encode('UTF-8').format(title, air_date, channel, kb_loaded))


def save_video(largs, show_blocking_dialogs=True, largs_value_is_array=True, str_num_rec=None):
    xbmc.log('save_video({0})'.format(str(largs)))
    video_url = largs[param_video_url]
    file_name = largs[param_file_name]
    title = largs[param_title]
    air_date = largs[param_date]
    channel = largs[param_channel]
    # every param string that went throug the args mechanism becomes an array
    if largs_value_is_array:
        video_url = largs[param_video_url][0]
        file_name = largs[param_file_name][0]
        title = largs[param_title][0]
        air_date = largs[param_date][0]
        channel = largs[param_channel][0]
    r = requests.get(video_url, stream=True)
    infodialog = xbmcgui.Dialog()
    # Make Umlaut filenames work properly
    if os.path.supports_unicode_filenames:
        file_name = file_name.decode('UTF-8').encode('latin_1')

    xbmc.log('Saving ' + file_name)
    if os.path.exists(file_name):
        yesno = False
        if show_blocking_dialogs:
            yesno = infodialog.yesno(
                ptva.getLocalizedString(31008).encode('UTF-8'),
                ptva.getLocalizedString(31009).encode('UTF-8').format(title, air_date, channel))
        if not yesno:
            xbmc.log('Download of "{0}" from channel "{2}" recorded on {1} skipped.'.format(title, air_date, channel))
            return False
    progdialog = xbmcgui.DialogProgress()
    canceled = False
    downloaded = 0
    try:
        with io.open(file_name, 'wb') as fd:
            chunk_size_kb = 100
            create_progress_dialog(progdialog, title, air_date, channel, downloaded, str_num_rec)
            for chunk in r.iter_content(1024 * chunk_size_kb):
                if progdialog.iscanceled():
                    progdialog.close()
                    yesno = infodialog.yesno(ptva.getLocalizedString(31010).encode('UTF-8'),
                                             ptva.getLocalizedString(31011).encode('UTF-8').format(title).encode('UTF-8').strip())
                    if yesno:
                        canceled = True
                        break
                    else:
                        create_progress_dialog(progdialog, title, air_date, channel, downloaded, str_num_rec)
                fd.write(chunk)
                downloaded += chunk_size_kb
                progdialog.update(0, line3='{0:,} kByte loaded'.format(downloaded))
            progdialog.close()
        if canceled:
            xbmc.log('Download canceled. Deleting file.')
            os.remove(file_name)
            return False
        else:
            if show_blocking_dialogs:
                infodialog.ok(
                    ptva.getLocalizedString(31012).encode('UTF-8'),
                    ptva.getLocalizedString(31013).encode('UTF-8').format(title, file_name, downloaded))
            return True
    except IOError as ierr:
        infodialog.ok(
            ptva.getLocalizedString(31014).encode('UTF-8'),
            ptva.getLocalizedString(31015).encode('UTF-8').format(title, file_name, ierr.strerror))
    return False


def save_all_videos(largs):
    lcdir = largs[param_cdir][0]
    xbmc.log('Saving all videos for container_id={0}'.format(lcdir))
    try:
        clist, ilist = panatv.get_listing(lcdir, panatv_hostname)
    except requests.RequestException as err:
        infodialog = xbmcgui.Dialog()
        infodialog.ok(
            ptva.getLocalizedString(31016).encode('UTF-8'),
            ptva.getLocalizedString(31017).encode('UTF-8').format(panatv_hostname, err))
        return
    except BaseException as err:
        infodialog = xbmcgui.Dialog()
        infodialog.ok(
            ptva.getLocalizedString(31007).encode('UTF-8'),
            '''
            {0}
            '''.format(err))
        return
    num = 1
    num_downloaded = 0
    for itemid, item_props in ilist.iteritems():
        str_num_rec = "{0}/{1}".format(num, len(ilist))
        num += 1
        params = create_li_params(item_props)
        if save_video(params, show_blocking_dialogs=False, largs_value_is_array=False, str_num_rec=str_num_rec):
            num_downloaded += 1
    infodialog = xbmcgui.Dialog()
    infodialog.ok(
        ptva.getLocalizedString(31019).encode('UTF-8'),
        ptva.getLocalizedString(31020).encode('UTF-8').format(num_downloaded, len(ilist))
    )


if __name__ == '__main__':
    action = args.get(param_action, None)
    xbmc.log('Action={0}'.format(action))
    if action is None:
        xbmc.log('Listing root directory')
        create_listing(top_container_id, top_flag)
    elif action[0] == action_open_container:
        cdir = args.get(param_container_id, None)
        if cdir:
            cdir = cdir[0]
        parent_id = args.get(param_parent_container_id, None)
        if parent_id:
            parent_id = parent_id[0]
        xbmc.log('Listing container {0}'.format(cdir))
        create_listing(cdir, parent_id)
    elif action[0] == action_save:
        save_video(args)
    elif action[0] == action_save_all:
        save_all_videos(args)
