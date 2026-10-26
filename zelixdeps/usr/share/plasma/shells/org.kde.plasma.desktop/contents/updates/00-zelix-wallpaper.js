var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {
    var d = allDesktops[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "/usr/share/wallpapers/Zelix/minimalistic.png");
    d.writeConfig("FillMode", 2);
}

var allPanels = panels();
for (var p = 0; p < allPanels.length; p++) {
    var widgets = allPanels[p].widgets();
    for (var w = 0; w < widgets.length; w++) {
        var widget = widgets[w];
        if (widget.type === "org.kde.plasma.kickoff") {
            widget.currentConfigGroup = ["General"];
            widget.writeConfig("icon", "/usr/share/zelix/zelix-icon.png");
            widget.writeConfig("useCustomButtonImage", "true");
        }
        if (widget.type === "org.kde.plasma.icontasks") {
            widget.currentConfigGroup = ["General"];
            widget.writeConfig("launchers", "applications:systemsettings.desktop,applications:org.kde.discover.desktop,applications:org.kde.dolphin.desktop,applications:org.kde.konsole.desktop");
        }
    }
}
