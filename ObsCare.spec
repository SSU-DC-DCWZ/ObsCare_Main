# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


added_file = [('./ui/main.ui','./ui'),
              ('./ui/prev_player.ui','./ui'),
              ('./utils/torch_utils.py','./utils'),
              ('./utils/google_utils.py','./utils'),
              ('./Detect/best.pt','./Detect')]
hiddenimport = [('PyQt5.QtMultimediaWidgets')]
a = Analysis(['ObsCare.py'],
             pathex=[],
             binaries=[],
             datas=added_file,
             hiddenimports=hiddenimport,
             hookspath=[],
             hooksconfig={},
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
          name='ObsCare',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

# Avoid warning
to_remove = ["_AES", "_ARC4", "_DES", "_DES3", "_SHA256", "_counter", "_C"]
for b in a.binaries:
    found = any(
        f'{crypto}.cp39-win_amd64.pyd' in b[1]
        for crypto in to_remove
    )
    if found:
        print(f"Removing {b[1]}")
        a.binaries.remove(b)