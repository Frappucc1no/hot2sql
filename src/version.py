"""
版本管理模块

版本号统一管理，所有模块从这里导入。
版本格式: MAJOR.MINOR.PATCH (语义化版本)

更新版本时只需修改此文件。
"""
__version__ = "2.0.0"

VERSION_INFO = {
    'major': 2,
    'minor': 0,
    'patch': 0,
}

def get_version():
    return __version__

def get_version_tuple():
    return (VERSION_INFO['major'], VERSION_INFO['minor'], VERSION_INFO['patch'])
