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

Download [`zips/repository.maybepanic/repository.maybepanic-0.2.0.zip`](zips/repository.maybepanic/repository.maybepanic-0.2.0.zip),
then in Kodi: *Add-ons → Install from zip file*. Plex Uno and the skins then install from *Install from repository →
Maybe Panic*, and update from there.

## Publishing

```
python build.py --uno <path to the script.plexmod-uno checkout>
git add -A && git commit && git push
```

`build.py` zips `addons/*` and Plex Uno's committed `HEAD` into `zips/`, and rewrites `zips/addons.xml` and its `.md5`.
A version that's already published is never rebuilt, so bump an add-on's version in its `addon.xml` before publishing
a change to it. Older versions stay listed (Kodi can roll back to them) until their zips are deleted.

`addons/` holds the sources of the skins and the repository add-on. Plex Uno's source lives in its own repository.
