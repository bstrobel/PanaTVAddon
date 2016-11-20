#!
#  -*- coding: utf-8 -*-
from xml.dom.minidom import parseString
import requests
import io


# Some constants
NS_S = "http://schemas.xmlsoap.org/soap/envelope/"
NS_U = "urn:schemas-upnp-org:service:ContentDirectory:1"
NS_DC = "http://purl.org/dc/elements/1.1/"
NS_DLNA = "urn:schemas-dlna-org:metadata-1-0/"
NS_PXN = "urn:schemas-panasonic-com:pxn"
NS_UPNP = "urn:schemas-upnp-org:metadata-1-0/upnp/"
panaUrl = 'http://{0}:55000/dms/control_0'
requestheaders = {
    'SOAPACTION': '"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"',
    'User-Agent': 'Panasonic Android VR-CP UPnP/2.0',
    'Content-Type': 'text/xml; charset="utf-8"'
}
requestxmlraw = '''<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"\
 s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\
<s:Body>\
<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">\
<ObjectID>0</ObjectID>\
<BrowseFlag>BrowseDirectChildren</BrowseFlag>\
<Filter>*</Filter>\
<StartingIndex>0</StartingIndex>\
<RequestedCount>0</RequestedCount>\
<SortCriteria></SortCriteria>\
</u:Browse>\
</s:Body>\
</s:Envelope>\
'''


def save_xml(xml_text, name='res_xml_doc.xml'):
    with io.open(name, 'wt', encoding='UTF-8') as fd:
            fd.write(xml_text)


def get_browse_response(objid, panatv_hostname, starting_index=0, request_count=20):
    req_xml_doc = parseString(requestxmlraw)

    req_body = req_xml_doc.documentElement.getElementsByTagNameNS(NS_S, 'Body')[0]
    req_browse = req_body.getElementsByTagNameNS(NS_U, 'Browse')[0]
    objid_el = req_browse.getElementsByTagName('ObjectID')[0]
    objid_el.childNodes[0].data = objid
    starting_index_el = req_browse.getElementsByTagName('StartingIndex')[0]
    starting_index_el.childNodes[0].data = starting_index
    request_count_el = req_browse.getElementsByTagName('RequestedCount')[0]
    request_count_el.childNodes[0].data = request_count
    req_xml_str = req_xml_doc.documentElement.toprettyxml()
    r = requests.post(panaUrl.format(panatv_hostname), data=req_xml_str, headers=requestheaders)
    # print r.text
    # http://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character-u-xa0-in-position-20
    content = r.text.encode('UTF-8').strip()
    # save_xml(r.text,'response.xml')

    resp_xml_doc = parseString(content)
    body = resp_xml_doc.documentElement.getElementsByTagNameNS(NS_S, 'Body')[0]
    browse_response = body.getElementsByTagNameNS(NS_U, 'BrowseResponse')[0]
    result = browse_response.getElementsByTagName('Result')
    total_matches = browse_response.getElementsByTagName('TotalMatches')[0]
    res_xml_doc = parseString(result[0].childNodes[0].data.encode('UTF-8').strip())
    # print res_xml_doc.toprettyxml()
    # save_xml(res_xml_doc.toprettyxml())
    return res_xml_doc.documentElement, int(total_matches.childNodes[0].data)


# <item id="1-fullseg-s2" parentID="s2" pxn:ContentSourceType="rec" pxn:DriveContainerID="s2" restricted="1">
#    <dc:title>Woodstock</dc:title>
#    <dc:date>2015-09-09T00:05:00</dc:date>
#    <upnp:genre>undefined</upnp:genre>
#    <upnp:class>object.item.videoItem</upnp:class>
#    <upnp:channelName>arte HD</upnp:channelName>
#    <upnp:channelNr>3</upnp:channelNr>
#    <pxn:channelId>0001,03fb,283e</pxn:channelId>
#    <pxn:NotView>0</pxn:NotView>
#    <pxn:GroupId>0</pxn:GroupId>
#    <res
#       duration="03:36:03"
#       protocolInfo="
#           http-get:*:
#           video/vnd.dlna.mpeg-tts:
#           DLNA.ORG_OP=10;
#           DLNA.ORG_CI=0;
#           DLNA.ORG_FLAGS=01100000000000000000000000000000"
#       pxn:ResumePoint="00:17:14"
#       pxn:VgaContentProtocolInfo="
#           http-get:*:video/vnd.dlna.mpeg-tts:
#           DLNA.ORG_PN=AVC_TS_MP_HD_AAC_LTP_T;
#           DLNA.ORG_OP=10;
#           DLNA.ORG_CI=1;
#           DLNA.ORG_FLAGS=81100000000000000000000000000000"
#       pxn:VgaContentUri="http://192.168.188.40:7501/VIDEO-TVGA-H4-1"
#       pxn:VgaContentVideoBitrate="2600">
#       http://192.168.188.40:7501/VIDEO-H4-1
#   </res>
#   <res
#       bitrate="375000"
#       duration="03:36:03"
#       protocolInfo="
#           http-get:*:
#           video/vnd.dlna.mpeg-tts:
#           DLNA.ORG_PN=AVC_TS_MP_HD_AAC_LTP_T;
#           DLNA.ORG_OP=10;DLNA.ORG_CI=1;
#           DLNA.ORG_FLAGS=81100000000000000000000000000000"
#       pxn:ResumePoint="00:17:14"
#       resolution="640x360">
#       http://192.168.188.40:7501/VIDEO-TVGA-H4-1
#   </res>
# </item>

# <?xml version="1.0" ?>
# <DIDL-Lite
#   xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"
#   xmlns:arib="urn:schemas-arib-or-jp:elements-1-0/"
#   xmlns:dc="http://purl.org/dc/elements/1.1/"
#   xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/"
#   xmlns:pxn="urn:schemas-panasonic-com:pxn"
#   xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/">
#     <item
#       id="LiveView_1"
#       parentID="0"
#       pxn:ContentSourceType="tuner"
#       pxn:LiveView="1"
#       pxn:LiveViewUpdateID="1"
#       pxn:ParentRefID="t-dvbc-all"
#       refID="2-tuner-t-dvbc-all"
#       restricted="1">
#         <dc:title>[LiveView] ZDF HD</dc:title>
#         <dc:date>2016-07-22T08:31:23</dc:date>
#         <upnp:genre>undefined</upnp:genre>
#         <upnp:class>object.item.videoItem</upnp:class>
#         <upnp:channelName>ZDF HD</upnp:channelName>
#         <upnp:channelNr>2</upnp:channelNr>
#         <pxn:channelId>0001,0437,2b66</pxn:channelId>
#         <res
#           protocolInfo="
#               http-get:*:video/vnd.dlna.mpeg-tts:
#               DLNA.ORG_CI=0;
#               DLNA.ORG_FLAGS=85100000000000000000000000000000"
#           pxn:VgaContentProtocolInfo="
#               http-get:*:video/vnd.dlna.mpeg-tts:
#               DLNA.ORG_PN=AVC_TS_MP_HD_AAC_LTP_T;
#               DLNA.ORG_CI=1;DLNA.ORG_FLAGS=85100000000000000000000000000000"
#           pxn:VgaContentUri="http://192.168.188.40:7501/TUNER-TVGA-LV-0005-0001-0437-2b66-1194"
#           pxn:VgaContentVideoBitrate="2600">
#               http://192.168.188.40:7501/TUNER-LV-0005-0001-0437-2b66-1194
#         </res>
#         <res
#           bitrate="375000"
#           protocolInfo="
#               http-get:*:video/vnd.dlna.mpeg-tts:
#               DLNA.ORG_PN=AVC_TS_MP_HD_AAC_LTP_T;
#               DLNA.ORG_CI=1;DLNA.ORG_FLAGS=85100000000000000000000000000000"
#           resolution="640x360">
#               http://192.168.188.40:7501/TUNER-TVGA-LV-0005-0001-0437-2b66-1194
#         </res>
#     </item>
#     <container id="s2" parentID="0" restricted="1">
#         <dc:title>Passport AV 107B</dc:title>
#         <upnp:class>object.container</upnp:class>
#         <pxn:DTCPContents>No</pxn:DTCPContents>
#         <pxn:ContainerSourceType>rec</pxn:ContainerSourceType>
#     </container>
#     <container id="t" parentID="0" restricted="1">
#         <dc:title>Tuner</dc:title>
#         <upnp:class>object.container</upnp:class>
#         <pxn:DTCPContents>Yes</pxn:DTCPContents>
#         <pxn:ContainerSourceType>tuner</pxn:ContainerSourceType>
#     </container>
# </DIDL-Lite>


def get_listing(parent_id='0', panatv_hostname='COM-MID1'):
    starting_index = 0
    total_matches = 10000
    container_list = dict()
    item_list = dict()
    while starting_index < total_matches:
        resp, total_matches = get_browse_response(parent_id, panatv_hostname, starting_index)
        starting_index += 20
        containers = resp.getElementsByTagName('container')
        items = resp.getElementsByTagName('item')
        if len(containers) > 0:
            for container in containers:
                title = container.getElementsByTagNameNS(NS_DC, 'title')[0].childNodes[0].data
                container_source_type = container.getElementsByTagNameNS(
                    NS_PXN, 'ContainerSourceType')[0].childNodes[0].data
                itemid = container.getAttribute('id')
                container_list[itemid] = {
                    'title': title,
                    'container_source_type': container_source_type
                }
        if len(items) > 0:
            for item in items:
                content_source_type = item.getAttributeNS(NS_PXN, 'ContentSourceType')
                title = item.getElementsByTagNameNS(NS_DC, 'title')[0].childNodes[0].data
                date = item.getElementsByTagNameNS(NS_DC, 'date')[0].childNodes[0].data
                channel_name = item.getElementsByTagNameNS(NS_UPNP, 'channelName')[0].childNodes[0].data
                duration = item.getElementsByTagName('res')[0].getAttribute('duration')
                # <res> contains mostly 2 elements with the URL
                # URL in res can contain -TVGA-, -NO-TVGA-, or sometimes an URL without these sub strings
                # We just take the first <res> element and remove -NO-TVGA or -TVGA from it.
                path = item.getElementsByTagName('res')[0].childNodes[0].data
                path = path.replace('-NO-TVGA-', '-')
                path = path.replace('-TVGA-', '-')
                itemid = item.getAttribute('id')
                item_list[itemid] = {
                    'content_source_type': content_source_type,
                    'title': title,
                    'date': date,
                    'channel_name': channel_name,
                    'path': path,
                    'id': itemid
                }
                if len(duration):
                    item_list[itemid]['duration'] = duration
    return container_list, item_list


def list_all(container_id='0', container_title='root', level=0):
    clist, ilist = get_listing(container_id)
    print '#', level, '############################ Items in container', container_title, container_id, '####'
    for itemid, item_props in ilist.iteritems():
        print '#', level, '#', item_props['title'], ':', itemid
        print '#', level, '#', 'Date:', item_props['date']
        print '#', level, '#', 'Channel:', item_props['channel_name']
        print '#', level, '#', 'URL:', item_props['path']
    for contid, cont_props in clist.iteritems():
        list_all(contid, cont_props['title'], level+1)

if __name__ == '__main__':
    list_all()
    print '### done ###'
