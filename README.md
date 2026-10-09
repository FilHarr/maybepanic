# Maybe Panic

A Kodi 21+ repository for testing **Plex Uno** (`script.plexmod-uno`), a renamed fork of
[PlexMod for Kodi](https://github.com/pannal/plex-for-kodi) that installs alongside the stock add-on, together with its
Plextuary skins:

| Add-on | For |
| --- | --- |
| `script.plexmod-uno` (Plex Uno) | everything |
| `skin.plextuary-uno` (Plextuary Uno) | most devices |
| `skin.plextuaryce-uno` (Plextuary CoreELEC Uno) | CoreELEC |
| `skin.plextuarycpm-uno` (Plextuary CE Custom Builds Uno) | CoreELEC custom builds (U3k, avdvplus, p3i, CPM) |

The skins are pannal's Plextuary builds from [Don't Panic](https://github.com/pannal/dontpanickodi), plus `font8`,
the Inter 4 fonts and a wrapping notification layout.

## Installing

In Kodi:

1. *Settings → System → Add-ons*: turn on *Unknown sources*
2. *Settings → File manager → Add source*: select *&lt;None&gt;*, enter `https://pm4k.daftegg.uk`, OK, name it
   *maybepanic*, OK
3. *Add-ons → Add-on browser* (the open box icon) *→ Install from zip file → maybepanic*: the `repository.maybepanic`
   zip
4. *Add-on browser → Install from repository → Maybe Panic*: Plex Uno and the Plextuary Uno skin for the device

Or download the repository zip from [pm4k.daftegg.uk](https://pm4k.daftegg.uk) and install it from a local folder.
Plex Uno and the skins then update from the repository.

## Publishing

```
python build.py --uno <path to the script.plexmod-uno checkout>
git add -A && git commit && git push
```

`build.py` zips `addons/*` and Plex Uno's committed `HEAD` into `zips/`, rewrites `zips/addons.xml` and its `.md5`, and puts
the newest repository zip and an `index.html` linking it at the root, which GitHub Pages serves (see `CNAME`).
A version that's already published is never rebuilt, so bump an add-on's version in its `addon.xml` before publishing
a change to it. Older versions stay listed (Kodi can roll back to them) until their zips are deleted.

`addons/` holds the sources of the skins and the repository add-on. Plex Uno's source lives in its own repository.
