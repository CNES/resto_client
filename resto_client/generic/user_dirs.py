# -*- coding: utf-8 -*-
"""
   Copyright 2019 CNES

   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
   in compliance with the License. You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software distributed under the License
   is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
   or implied. See the License for the specific language governing permissions and
   limitations under the License.
"""
from configparser import ConfigParser
import os
from pathlib import Path
import platform
from typing import Optional, Dict, Tuple

from appdirs import user_data_dir


MSWINDOWS = (platform.system() == 'Windows')
if MSWINDOWS:
    from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx
    REGISTRY_USER_DIRS_KEY = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'

KNOWN_USER_DIRS: Dict[str, Tuple[Optional[str], Optional[str]]]

KNOWN_USER_DIRS = {'AccountPictures': (None, '{008ca0b1-55b4-4c56-b8a8-4de4b299d3be}'),
                   'AdminTools': (None, '{724EF170-A42D-4FEF-9F26-B60E846FBA4F}'),
                   'ApplicationShortcuts': (None, '{A3918781-E5F2-4890-B3D9-A7E54332328C}'),
                   'CameraRoll': (None, '{AB5FB87B-7CE2-4F83-915D-550846C9537B}'),
                   'CDBurning': (None, '{9E52AB10-F80D-49DF-ACB8-4330F5687855}'),
                   'Contacts': (None, '{56784854-C6CB-462b-8169-88E350ACB882}'),
                   'Cookies': (None, '{2B0F765D-C0E9-4171-908E-08A611B84FF6}'),
                   'Desktop': ('XDG_DESKTOP_DIR', '{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}'),
                   'Documents': ('XDG_DOCUMENTS_DIR', '{FDD39AD0-238F-46AF-ADB4-6C85480369C7}'),
                   'DocumentsLibrary': (None, '{7B0DB17D-9CD2-4A93-9733-46CC89022E7C}'),
                   'Downloads': ('XDG_DOWNLOAD_DIR', '{374DE290-123F-4565-9164-39C4925E467B}'),
                   'Favorites': (None, '{1777F761-68AD-4D8A-87BD-30B759FA33DD}'),
                   'GameTasks': (None, '{054FAE61-4DD8-4787-80B6-090220C4B700}'),
                   'History': (None, '{D9DC8A3B-B784-432E-A781-5A1130A75963}'),
                   'ImplicitAppShortcuts': (None, '{BCB5256F-79F6-4CEE-B725-DC34E402FD46}'),
                   'InternetCache': (None, '{352481E8-33BE-4251-BA85-6007CAEDCF9D}'),
                   'Libraries': (None, '{1B3EA5DC-B587-4786-B4EF-BD1DC332AEAE}'),
                   'Links': (None, '{bfb9d5e0-c6a9-404c-b2b2-ae6db6af4968}'),
                   'LocalAppData': (None, '{F1B32785-6FBA-4FCF-9D55-7B8E7F157091}'),
                   'LocalAppDataLow': (None, '{A520A1A4-1780-4FF6-BD18-167343C5AF16}'),
                   'Music': ('XDG_MUSIC_DIR', '{4BD8D571-6D19-48D3-BE97-422220080E43}'),
                   'MusicLibrary': (None, '{2112AB0A-C86A-4FFE-A368-0DE96E47012E}'),
                   'NetHood': (None, '{C5ABBF53-E17F-4121-8900-86626FC2C973}'),
                   'Objects3D': (None, '{31C0DD25-9439-4F12-BF41-7FF4EDA38722}'),
                   'OriginalImages': (None, '{2C36C0AA-5812-4b87-BFD0-4CD0DFB19B39}'),
                   'PhotoAlbums': (None, '{69D2CF90-FC33-4FB7-9A0C-EBB0F0FCB43C}'),
                   'Pictures': ('XDG_PICTURES_DIR', '{33E28130-4E1E-4676-835A-98395C3BC3BB}'),
                   'PicturesLibrary': (None, '{A990AE9F-A03B-4E80-94BC-9912D7504104}'),
                   'Playlists': (None, '{DE92C1C7-837F-4F69-A3BB-86E631204A23}'),
                   'PrintHood': (None, '{9274BD8D-CFD1-41C3-B35E-B13F55A758F4}'),
                   'Programs': (None, '{A77F5D77-2E2B-44C3-A6A2-ABA601054A51}'),
                   'PublicShare': ('XDG_PUBLICSHARE_DIR', None),
                   'QuickLaunch': (None, '{52a4f021-7b75-48a9-9f6b-4b87a210bc8f}'),
                   'Recent': (None, '{AE50C081-EBD2-438A-8655-8A092E34987A}'),
                   'Ringtones': (None, '{C870044B-F49E-4126-A9C3-B52A1FF411E8}'),
                   'RoamingAppData': (None, '{3EB685DB-65F9-4CF6-A03A-E3EF65729F3D}'),
                   'RoamedTileImages': (None, '{AAA8D5A5-F1D6-4259-BAA8-78E7EF60835E}'),
                   'RoamingTiles': (None, '{00BCFC5A-ED94-4e48-96A1-3F6217F21990}'),
                   'SavedGames': (None, '{4C5C32FF-BB9D-43b0-B5B4-2D72E54EAAA4}'),
                   'SavedPictures': (None, '{3B193882-D3AD-4eab-965A-69829D1FB59F}'),
                   'SavedPicturesLibrary': (None, '{E25B5812-BE88-4bd9-94B0-29233477B6C3}'),
                   'SavedSearches': (None, '{7d1d3a04-debb-4115-95cf-2f29da2920da}'),
                   'Screenshots': (None, '{b7bede81-df94-4682-a7d8-57a52620b86f}'),
                   'SearchHistory': (None, '{0D4C3DB6-03A3-462F-A0E6-08924C41B5D4}'),
                   'SearchTemplates': (None, '{7E636BFE-DFA9-4D5E-B456-D7B39851D8A9}'),
                   'SendTo': (None, '{8983036C-27C0-404B-8F08-102D10DCFD74}'),
                   'SidebarParts': (None, '{A75D362E-50FC-4fb7-AC2C-A8BEAA314493}'),
                   'SkyDrive': (None, '{A52BBA46-E9E1-435f-B3D9-28DAA648C0F6}'),
                   'SkyDriveCameraRoll': (None, '{767E6811-49CB-4273-87C2-20F355E1085B}'),
                   'SkyDriveDocuments': (None, '{24D89E24-2F19-4534-9DDE-6A6671FBB8FE}'),
                   'SkyDrivePictures': (None, '{339719B5-8C47-4894-94C2-D8F77ADD44A6}'),
                   'StartMenu': (None, '{625B53C3-AB48-4EC1-BA1F-A1EF4146FC19}'),
                   'Startup': (None, '{B97D20BB-F46A-4C97-BA10-5E3608430854}'),
                   'Templates': ('XDG_TEMPLATES_DIR', '{A63293E8-664E-48DB-A079-DF759E0509F7}'),
                   'UserPinned': (None, '{9E3995AB-1F9C-4F13-B827-48B24B6C7174}'),
                   'UserProgramFiles': (None, '{5CD7AEE2-2219-4A67-B85D-6C9CE15660CB}'),
                   'UserProgramFilesCommon': (None, '{BCBD3057-CA5C-4622-B42D-BC56DB0AE516}'),
                   'Videos': ('XDG_VIDEOS_DIR', '{18989B1D-99B5-455B-841C-AB7C74E4DDFC}'),
                   'VideosLibrary': (None, '{491E922F-5643-4AF4-A7EB-4E7A138D8174}'),
                   }


def user_download_dir() -> Path:
    """

    :returns: the user download directory depending on the system (linux or windows)
    """
    return user_dir('Downloads')


def user_dir(directory_type: str) -> Path:
    """

    """
    if directory_type not in KNOWN_USER_DIRS:
        msg = 'User directory type "{}" is unknown. Please choose one from {}'
        raise IndexError(msg.format(directory_type, list(KNOWN_USER_DIRS.keys())))
    if MSWINDOWS:
        windows_guid = KNOWN_USER_DIRS[directory_type][1]
        if windows_guid is None:
            msg = 'User directory type "{}" is unknown as a Windows Known Directory'
            raise NotADirectoryError(msg.format(directory_type))
        with OpenKey(HKEY_CURRENT_USER, REGISTRY_USER_DIRS_KEY) as key:
            registry_user_dir = QueryValueEx(key, windows_guid)[0]
        return Path(registry_user_dir)

    # LINUX case

    cfg_parser = ConfigParser()
    cfg_dirs_path = Path.home() / '.config' / 'user-dirs.dirs'
    with open(cfg_dirs_path) as file_desc:
        cfg_parser.read_string("[XDG_DIRS]\n" + file_desc.read())
    linux_id = KNOWN_USER_DIRS[directory_type][0]
    if linux_id is None:
        msg = 'User directory type "{}" is undefined for Linux XDG standard'
        raise NotADirectoryError(msg.format(directory_type))
    download_dir = cfg_parser['XDG_DIRS'][linux_id].strip('"')
    return Path(os.path.expandvars(download_dir))


def user_config_dir(app_author: str ='unknown_author', app_name: str ='unknwon_app') -> Path:
    """
    Return the user configuration directory to be used by an application and create it if needed.

    :param app_author: the author name of the application (a company, a person, ...)
    :param app_name: the name of one application produced by the author.
    :returns: Path to the user configuration directory for the application
    """
    config_dir = Path(user_data_dir(app_name, app_author))
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
    return config_dir
