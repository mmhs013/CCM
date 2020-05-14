# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

hidden_imports = [
    'fiona',
    'gdal',
    'geos',
    'shapely',
    'shapely.geometry',
    'pyproj',
    'rtree',
    'geopandas.datasets',
    'pytest',
    'pandas._libs.tslibs.timedeltas',
]

a = Analysis(['CCMDataProcess.py'],
             pathex=['D:\\PortableCompiler\\WPy-3702\\notebooks\\New folder'],
             binaries=[('D:\\PortableCompiler\\WPy-3702\\notebooks\\spatialindex_c.dll','.')],
             datas=collect_data_files('geopandas', subdir='datasets'),
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='CCMDataProcess',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
