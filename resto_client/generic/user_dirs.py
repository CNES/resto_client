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
from tempfile import mkdtemp
from typing import Optional

from appdirs import user_data_dir
from resto_client.base_exceptions import RestoClientDesignError


MSWINDOWS = (platform.system() == 'Windows')
if MSWINDOWS:
    from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx
    REGISTRY_USER_DIRS_KEY = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'


USER_DIRS_WINDOWS = {'AccountPictures': '{008ca0b1-55b4-4c56-b8a8-4de4b299d3be}',
                     'AdminTools': '{724EF170-A42D-4FEF-9F26-B60E846FBA4F}',
                     'ApplicationShortcuts': '{A3918781-E5F2-4890-B3D9-A7E54332328C}',
                     'CameraRoll': '{AB5FB87B-7CE2-4F83-915D-550846C9537B}',
                     'CDBurning': '{9E52AB10-F80D-49DF-ACB8-4330F5687855}',
                     'Contacts': '{56784854-C6CB-462b-8169-88E350ACB882}',
                     'Cookies': '{2B0F765D-C0E9-4171-908E-08A611B84FF6}',
                     'Desktop': '{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}',
                     'Documents': '{FDD39AD0-238F-46AF-ADB4-6C85480369C7}',
                     'DocumentsLibrary': '{7B0DB17D-9CD2-4A93-9733-46CC89022E7C}',
                     'Downloads': '{374DE290-123F-4565-9164-39C4925E467B}',
                     'Favorites': '{1777F761-68AD-4D8A-87BD-30B759FA33DD}',
                     'GameTasks': '{054FAE61-4DD8-4787-80B6-090220C4B700}',
                     'History': '{D9DC8A3B-B784-432E-A781-5A1130A75963}',
                     'ImplicitAppShortcuts': '{BCB5256F-79F6-4CEE-B725-DC34E402FD46}',
                     'InternetCache': '{352481E8-33BE-4251-BA85-6007CAEDCF9D}',
                     'Libraries': '{1B3EA5DC-B587-4786-B4EF-BD1DC332AEAE}',
                     'Links': '{bfb9d5e0-c6a9-404c-b2b2-ae6db6af4968}',
                     'LocalAppData': '{F1B32785-6FBA-4FCF-9D55-7B8E7F157091}',
                     'LocalAppDataLow': '{A520A1A4-1780-4FF6-BD18-167343C5AF16}',
                     'Music': '{4BD8D571-6D19-48D3-BE97-422220080E43}',
                     'MusicLibrary': '{2112AB0A-C86A-4FFE-A368-0DE96E47012E}',
                     'NetHood': '{C5ABBF53-E17F-4121-8900-86626FC2C973}',
                     'Objects3D': '{31C0DD25-9439-4F12-BF41-7FF4EDA38722}',
                     'OriginalImages': '{2C36C0AA-5812-4b87-BFD0-4CD0DFB19B39}',
                     'PhotoAlbums': '{69D2CF90-FC33-4FB7-9A0C-EBB0F0FCB43C}',
                     'Pictures': '{33E28130-4E1E-4676-835A-98395C3BC3BB}',
                     'PicturesLibrary': '{A990AE9F-A03B-4E80-94BC-9912D7504104}',
                     'Playlists': '{DE92C1C7-837F-4F69-A3BB-86E631204A23}',
                     'PrintHood': '{9274BD8D-CFD1-41C3-B35E-B13F55A758F4}',
                     'Programs': '{A77F5D77-2E2B-44C3-A6A2-ABA601054A51}',
                     'QuickLaunch': '{52a4f021-7b75-48a9-9f6b-4b87a210bc8f}',
                     'Recent': '{AE50C081-EBD2-438A-8655-8A092E34987A}',
                     'Ringtones': '{C870044B-F49E-4126-A9C3-B52A1FF411E8}',
                     'RoamingAppData': '{3EB685DB-65F9-4CF6-A03A-E3EF65729F3D}',
                     'RoamedTileImages': '{AAA8D5A5-F1D6-4259-BAA8-78E7EF60835E}',
                     'RoamingTiles': '{00BCFC5A-ED94-4e48-96A1-3F6217F21990}',
                     'SavedGames': '{4C5C32FF-BB9D-43b0-B5B4-2D72E54EAAA4}',
                     'SavedPictures': '{3B193882-D3AD-4eab-965A-69829D1FB59F}',
                     'SavedPicturesLibrary': '{E25B5812-BE88-4bd9-94B0-29233477B6C3}',
                     'SavedSearches': '{7d1d3a04-debb-4115-95cf-2f29da2920da}',
                     'Screenshots': '{b7bede81-df94-4682-a7d8-57a52620b86f}',
                     'SearchHistory': '{0D4C3DB6-03A3-462F-A0E6-08924C41B5D4}',
                     'SearchTemplates': '{7E636BFE-DFA9-4D5E-B456-D7B39851D8A9}',
                     'SendTo': '{8983036C-27C0-404B-8F08-102D10DCFD74}',
                     'SidebarParts': '{A75D362E-50FC-4fb7-AC2C-A8BEAA314493}',
                     'SkyDrive': '{A52BBA46-E9E1-435f-B3D9-28DAA648C0F6}',
                     'SkyDriveCameraRoll': '{767E6811-49CB-4273-87C2-20F355E1085B}',
                     'SkyDriveDocuments': '{24D89E24-2F19-4534-9DDE-6A6671FBB8FE}',
                     'SkyDrivePictures': '{339719B5-8C47-4894-94C2-D8F77ADD44A6}',
                     'StartMenu': '{625B53C3-AB48-4EC1-BA1F-A1EF4146FC19}',
                     'Startup': '{B97D20BB-F46A-4C97-BA10-5E3608430854}',
                     'Templates': '{A63293E8-664E-48DB-A079-DF759E0509F7}',
                     'UserPinned': '{9E3995AB-1F9C-4F13-B827-48B24B6C7174}',
                     'UserProgramFiles': '{5CD7AEE2-2219-4A67-B85D-6C9CE15660CB}',
                     'UserProgramFilesCommon': '{BCBD3057-CA5C-4622-B42D-BC56DB0AE516}',
                     'Videos': '{18989B1D-99B5-455B-841C-AB7C74E4DDFC}',
                     'VideosLibrary': '{491E922F-5643-4AF4-A7EB-4E7A138D8174}',
                     }


USER_DIRS_XDG = {'Desktop': 'XDG_DESKTOP_DIR',
                 'Documents': 'XDG_DOCUMENTS_DIR',
                 'Downloads': 'XDG_DOWNLOAD_DIR',
                 'Music': 'XDG_MUSIC_DIR',
                 'Pictures': 'XDG_PICTURES_DIR',
                 'PublicShare': 'XDG_PUBLICSHARE_DIR',
                 'Templates': 'XDG_TEMPLATES_DIR',
                 'Videos': 'XDG_VIDEOS_DIR',
                 }


USER_DIRS_HOME = {'Documents': 'documents',
                  'Downloads': None,
                  }
USER_DIRS_TMP = USER_DIRS_HOME


def _user_dir_get_symbol(directory_type: str, directories_table: dict, unexisting_msg: str) -> str:
    """
    Check that the requested directory type is defined in the selected user directories table
    and return the directory symbol corresponding to this type.

    :param directory_type: the code of some user directory
    :param directories_table: for each directory type, provides its associated symbol
    :param unexisting_msg: part of the exception message raised when directory type is not found
    :raises KeyError: when the directory type is unsupported in the selected configuration
    :returns: the directory symbol to use for this directory type
    """
    if directory_type not in directories_table:
        msg = 'User directory type "{}" is {}. Please choose one from {}.'
        raise KeyError(msg.format(directory_type, unexisting_msg, directories_table))
    return directories_table[directory_type]


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


def user_download_dir(app_name: Optional[str] = None, ensure_exists: bool=False) -> Path:
    """

    :param app_name: name of the application, used when directories cannot be defined by the OS.
    :param ensure_exists: If True, check that the user directory exists before returning its path.
    :returns: the user download directory depending on the system (linux or windows)
    """
    return user_dir('Downloads', app_name=app_name, ensure_exists=ensure_exists)


def user_dir(directory_type: str, app_name: Optional[str]=None, ensure_exists: bool=False) -> Path:
    """
    Returns the well known user directory of some type (download, desktop, documents, ...),
    depending on the Operating System.

    On Windows, these directories are taken from the registry.

    On Linux, 2 situations can be found:

    - if a windowing system is install, we rely on the XDG standard to return these directories,
    - otherwise we use the HOME directory if it exists or TMP otherwise to build a path to a
      limited set of user directories.

    :param directory_type: the code of some user directory (the list of available codes is system
                           dependent)
    :param app_name: name of the application, used when directories cannot be defined by the OS.
    :param ensure_exists: If True, check that the user directory exists before returning its path.
    :returns: the path to the directory in the user environment
    """

    # Windows case
    if MSWINDOWS:
        user_dir_path = _user_dir_windows(directory_type, app_name=app_name)
    else:
        # LINUX case
        user_dir_path = _user_dir_linux(directory_type, app_name=app_name)

    if ensure_exists:
        user_dir_path.mkdir(parents=True, exist_ok=True)
    return user_dir_path


def _user_dir_windows(directory_type: str, app_name: Optional[str]=None) -> Path:
    """
    Returns the path to the requested user directory type on Windows

    :param directory_type: the code of some user directory
    :param app_name: used to insert a sub directory with that name in the user directory path.
    :returns: the path to the directory in the Windows user environment
    """
    directory_id = _user_dir_get_symbol(directory_type, USER_DIRS_WINDOWS, 'unknown on Windows')

    with OpenKey(HKEY_CURRENT_USER, REGISTRY_USER_DIRS_KEY) as key:
        user_dir_registry = QueryValueEx(key, directory_id)[0]

    user_dir_path = Path(user_dir_registry)
    if app_name is not None:
        user_dir_path = user_dir_path / app_name
    return user_dir_path


def _user_dir_linux(directory_type: str, app_name: Optional[str]=None) -> Path:
    """
    Returns the well known user directory of some type (download, desktop, documents, ...),
    on Linux systems. Two situations can be found:

    - if a windowing system is installed, we rely on the XDG standard to return these directories,
    - otherwise we use the HOME directory if it exists or TMP otherwise to build a path to a
      limited set of user directories.

    :param directory_type: the code of some user directory (the list of available codes is system
                           dependent)
    :param app_name: name of the application, used when directories cannot be defined by the OS.
    :returns: the path to the directory in the user environment
    """
    # Determine if a valid Home is available or not.
    user_home_path = None
    try:
        user_home_path = Path.home()
        if str(user_home_path) == '/':
            # Case where no home dir defined in passward database
            user_home_path = None
    except RuntimeError:
        # Case where pwd is unable to find a home directory
        user_home_path = None

    if user_home_path is None:
        # No user home directory available. Use directories in /tmp.
        return _user_dir_linux_tmp(directory_type, app_name=app_name)

    # User home directory is available
    cfg_dirs_path = user_home_path / '.config' / 'user-dirs.dirs'
    if cfg_dirs_path.exists():
        # XDG available. Try to use it.
        return _user_dir_linux_xdg(directory_type, cfg_dirs_path, app_name=app_name)

    # HOME available but XDG unavailable. Use HOME to create the directory
    return _user_dir_linux_home(directory_type, app_name=app_name)


def _user_dir_linux_xdg(directory_type: str,
                        cfg_dirs_path: Path,
                        app_name: Optional[str]=None) -> Path:
    """
    Returns the path to the requested user directory type on Linux, using XDG.

    :param directory_type: the code of some user directory
    :param cfg_dirs_path: path to the file containing the XDG configuration
    :param app_name: used to insert a sub directory with that name in the user directory path.
    :returns: the path to the directory in the Linux user environment
    """
    directory_id = _user_dir_get_symbol(directory_type, USER_DIRS_XDG, 'undefined by XDG standard')

    cfg_parser = ConfigParser()
    with open(cfg_dirs_path) as file_desc:
        cfg_parser.read_string("[XDG_DIRS]\n" + file_desc.read())
    user_directory = cfg_parser['XDG_DIRS'][directory_id].strip('"')
    user_dir_xdg = os.path.expandvars(user_directory)

    user_dir_path = Path(user_dir_xdg)
    if app_name is not None:
        user_dir_path = user_dir_path / app_name
    return user_dir_path


def _user_dir_linux_home(directory_type: str, app_name: Optional[str]=None) -> Path:
    """
    Returns the path to the requested user directory type on Linux, inside HOME directory.

    :param directory_type: the code of some user directory
    :param app_name: used to insert a sub directory with that name in the user directory path.
    :returns: the path to the directory in the Linux user environment
    :raises RestoClientDesignError: when arguments do not define at least one level of
    directory in home
    """
    directory_id = _user_dir_get_symbol(directory_type, USER_DIRS_HOME, 'forbidden in HOME')

    if app_name is None and directory_id is None:
        msg = 'Cannot create user dir {} with path None in home without specifying app_name'
        raise RestoClientDesignError(msg.format(directory_type))

    if app_name is not None:
        if directory_id is not None:
            user_dir_path = Path.home() / app_name / directory_id
        else:
            user_dir_path = Path.home() / app_name
    else:
        user_dir_path = Path.home() / directory_id
    return user_dir_path


def _user_dir_linux_tmp(directory_type: str, app_name: Optional[str]=None) -> Path:
    """
    Returns the path to the requested user directory type on Linux, inside tmp direectory.

    :param directory_type: the code of some user directory
    :param app_name: used to insert a sub directory with that name in the user directory path.
    :returns: the path to the directory in the Linux user environment
    :raises RestoClientDesignError: when arguments do not define at least one level of
    directory in tmp
    """
    directory_id = _user_dir_get_symbol(directory_type, USER_DIRS_TMP, 'forbidden in TMP')

    if app_name is None and directory_id is None:
        msg = 'Cannot create user dir {} with path None in tmp without specifying app_name'
        raise RestoClientDesignError(msg.format(directory_type))

    if app_name is not None:
        if directory_id is not None:
            user_dir_prefix = '{}_{}_'.format(app_name, directory_id)
        else:
            user_dir_prefix = '{}_'.format(app_name)
    else:
        user_dir_prefix = '{}_'.format(directory_id)
    return Path(mkdtemp(prefix=user_dir_prefix))
