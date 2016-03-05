# -*- mode: python -*-
a = Analysis(['C:\\Users\\damian\\Documents\\glioblastoma\\csvAnalyst\\csvAnalyst.py'],
             pathex=['C:\\WinPython-64bit-2.7.9.3\\python-2.7.9.amd64\\Scripts'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='csvAnalyst.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='csvAnalyst')
