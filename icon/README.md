# Icon assets

The source artwork for the BarTranslateACO app icon lives in `src/translate-tiles-a-zh.svg`.

The icon files used by the app live in `BarTranslate/Assets.xcassets`:

* `AppIcon.appiconset/` provides the application icon selected by the Xcode build setting `ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon`.
* `MenuIcon.imageset/` and `MenuIconMinimal.imageset/` provide the selectable menu bar icons.
* `MenuIconStatus.png` and `MenuIconMinimalStatus.png` are copied as bundled resources for packaged app launch paths that load menu bar icons directly from the app resources.

The inherited upstream app icon exports and prototype icon proposal pages were removed. The app does not load icon files from `docs/`; all runtime icon assets are in the Xcode asset catalog or copied bundle resources listed above.
