import QtQuick 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#12151D"

    property string bgSource: config.background || "background.png"
    property string logoSource: config.logo || "logo.png"
    property color accentCol: config.accentColor || "#1A4D8F"
    property color accentHov: config.accentHover || "#4A90E2"
    property color cardBg: config.cardBackground || "#161922"
    property real cardOp: Number(config.cardOpacity) || 0.88
    property color textPrimary: config.textColor || "#FFFFFF"
    property color textSecondary: config.textSecondary || "#B0B5C0"
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0

    function getSessionName(idx) {
        if (!sessionModel || sessionModel.count === 0) return "Plasma (Wayland)";
        var name = sessionModel.data(sessionModel.index(idx, 0), 260);
        if (name && name !== "") return name;
        for (var r = 257; r <= 262; r++) {
            var val = sessionModel.data(sessionModel.index(idx, 0), r);
            if (typeof val === "string" && val.length > 0 && val.indexOf("/") !== 0) return val;
        }
        return "Plasma (Wayland)";
    }

    TextConstants { id: textConstants }

    // Background Image
    Image {
        id: bgImage
        anchors.fill: parent
        source: root.bgSource
        fillMode: Image.PreserveAspectCrop
        smooth: true
        asynchronous: true

        onStatusChanged: {
            if (status == Image.Error && source != "background.png") {
                source = "background.png"
            }
        }
    }

    // Subtle dark overlay to enhance text readability
    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.3
    }

    // Top Clock & Date
    Column {
        id: clockContainer
        anchors.top: parent.top
        anchors.topMargin: Math.max(40, root.height * 0.08)
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 6

        Text {
            id: clockText
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatTime(new Date(), config.clockFormat || "HH:mm")
            color: root.textPrimary
            font.pixelSize: 64
            font.bold: true
            font.family: "Noto Sans"
        }

        Text {
            id: dateText
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatDate(new Date(), config.dateFormat || "dddd, d MMMM yyyy")
            color: root.textSecondary
            font.pixelSize: 18
            font.family: "Noto Sans"
        }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            clockText.text = Qt.formatTime(new Date(), config.clockFormat || "HH:mm")
            dateText.text = Qt.formatDate(new Date(), config.dateFormat || "dddd, d MMMM yyyy")
        }
    }

    // Central Frosted Glass Login Card
    Rectangle {
        id: loginCard
        width: 380
        height: 400
        anchors.centerIn: parent
        radius: 16
        color: root.cardBg
        opacity: root.cardOp
        border.color: Qt.rgba(1, 1, 1, 0.15)
        border.width: 1

        Column {
            id: cardContent
            anchors.fill: parent
            anchors.margins: 28
            spacing: 16

            // User Avatar / Logo
            Item {
                width: 72
                height: 72
                anchors.horizontalCenter: parent.horizontalCenter

                Rectangle {
                    anchors.fill: parent
                    radius: 36
                    color: Qt.rgba(0.1, 0.3, 0.56, 0.3)
                    border.color: root.accentCol
                    border.width: 2

                    Image {
                        id: userAvatar
                        anchors.fill: parent
                        anchors.margins: 10
                        source: root.logoSource
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        onStatusChanged: {
                            if (status == Image.Error) {
                                source = ""
                            }
                        }
                    }

                    Text {
                        anchors.centerIn: parent
                        text: "👤"
                        font.pixelSize: 28
                        visible: userAvatar.status != Image.Ready
                    }
                }
            }

            // User Name Box
            Rectangle {
                width: parent.width
                height: 40
                color: "#1E222D"
                radius: 8
                border.color: userNameInput.activeFocus ? root.accentCol : "#303542"
                border.width: 1

                TextInput {
                    id: userNameInput
                    anchors.fill: parent
                    anchors.margins: 8
                    anchors.leftMargin: 12
                    verticalAlignment: TextInput.AlignVCenter
                    color: root.textPrimary
                    font.pixelSize: 14
                    font.family: "Noto Sans"
                    text: userModel.lastUser || "zelix"
                    clip: true

                    KeyNavigation.tab: passwordInput
                    Keys.onReturnPressed: sddm.login(userNameInput.text, passwordInput.text, root.sessionIndex)
                }

                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Kullanıcı Adı / Username"
                    color: root.textSecondary
                    font.pixelSize: 13
                    font.family: "Noto Sans"
                    visible: !userNameInput.text && !userNameInput.activeFocus
                }
            }

            // Password Field
            Rectangle {
                id: passBg
                width: parent.width
                height: 40
                color: "#1E222D"
                radius: 8
                border.color: passwordInput.activeFocus ? root.accentCol : "#303542"
                border.width: 1

                TextInput {
                    id: passwordInput
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 40
                    anchors.topMargin: 8
                    anchors.bottomMargin: 8
                    verticalAlignment: TextInput.AlignVCenter
                    color: root.textPrimary
                    font.pixelSize: 14
                    font.family: "Noto Sans"
                    echoMode: showPassToggle.checked ? TextInput.Normal : TextInput.Password
                    clip: true
                    focus: true

                    KeyNavigation.backtab: userNameInput
                    KeyNavigation.tab: loginBtn
                    Keys.onReturnPressed: sddm.login(userNameInput.text, passwordInput.text, root.sessionIndex)
                    onTextChanged: errorMessage.visible = false
                }

                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Parola / Password"
                    color: root.textSecondary
                    font.pixelSize: 13
                    font.family: "Noto Sans"
                    visible: !passwordInput.text && !passwordInput.activeFocus
                }

                // Password Show/Hide Toggle
                Rectangle {
                    id: showPassToggle
                    width: 28
                    height: 28
                    radius: 6
                    anchors.right: parent.right
                    anchors.rightMargin: 6
                    anchors.verticalCenter: parent.verticalCenter
                    color: mouseShowPass.containsMouse ? Qt.rgba(1, 1, 1, 0.1) : "transparent"
                    property bool checked: false

                    Text {
                        anchors.centerIn: parent
                        text: showPassToggle.checked ? "👁" : "🔒"
                        font.pixelSize: 13
                    }

                    MouseArea {
                        id: mouseShowPass
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: showPassToggle.checked = !showPassToggle.checked
                    }
                }
            }

            // Error Message Display
            Text {
                id: errorMessage
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                color: "#FF5252"
                font.pixelSize: 12
                font.family: "Noto Sans"
                wrapMode: Text.WordWrap
                visible: false
                text: "Giriş başarısız. Lütfen tekrar deneyin."
            }

            // Login Button
            Rectangle {
                id: loginBtn
                width: parent.width
                height: 42
                radius: 8
                color: mouseLogin.containsMouse ? root.accentHov : root.accentCol

                Text {
                    anchors.centerIn: parent
                    text: "Giriş Yap / Login →"
                    color: "#FFFFFF"
                    font.pixelSize: 14
                    font.bold: true
                    font.family: "Noto Sans"
                }

                MouseArea {
                    id: mouseLogin
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: sddm.login(userNameInput.text, passwordInput.text, root.sessionIndex)
                }
            }
        }
    }

    // Bottom Bar: Session Info & Power Options
    Item {
        id: bottomBar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 24
        height: 48

        // Left: Session indicator & switcher
        Rectangle {
            id: sessionBtn
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            height: 36
            width: sessionRow.implicitWidth + 24
            color: mouseSession.containsMouse ? Qt.rgba(0.12, 0.16, 0.22, 0.95) : Qt.rgba(0.08, 0.1, 0.14, 0.85)
            radius: 8
            border.color: mouseSession.containsMouse ? root.accentCol : "#303542"
            border.width: 1

            Row {
                id: sessionRow
                anchors.centerIn: parent
                spacing: 6

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "🖥"
                    font.pixelSize: 13
                }

                Text {
                    id: sessionText
                    anchors.verticalCenter: parent.verticalCenter
                    text: root.getSessionName(root.sessionIndex)
                    color: mouseSession.containsMouse ? "#FFFFFF" : root.textSecondary
                    font.pixelSize: 12
                    font.family: "Noto Sans"
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "▾"
                    color: root.textSecondary
                    font.pixelSize: 10
                    visible: sessionModel.count > 1
                }
            }

            MouseArea {
                id: mouseSession
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: sessionModel.count > 1 ? Qt.PointingHandCursor : Qt.ArrowCursor
                onClicked: {
                    if (sessionModel.count > 1) {
                        root.sessionIndex = (root.sessionIndex + 1) % sessionModel.count
                    }
                }
            }
        }

        // Right: Power buttons
        Row {
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            // Suspend
            Rectangle {
                width: 38
                height: 38
                radius: 19
                color: mouseSuspend.containsMouse ? root.accentCol : Qt.rgba(0.08, 0.1, 0.14, 0.85)
                border.color: "#303542"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "🌙"
                    font.pixelSize: 14
                }

                MouseArea {
                    id: mouseSuspend
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: sddm.suspend()
                }
            }

            // Reboot
            Rectangle {
                width: 38
                height: 38
                radius: 19
                color: mouseReboot.containsMouse ? root.accentCol : Qt.rgba(0.08, 0.1, 0.14, 0.85)
                border.color: "#303542"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "🔄"
                    font.pixelSize: 14
                }

                MouseArea {
                    id: mouseReboot
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: sddm.reboot()
                }
            }

            // Poweroff
            Rectangle {
                width: 38
                height: 38
                radius: 19
                color: mousePower.containsMouse ? "#E53935" : Qt.rgba(0.08, 0.1, 0.14, 0.85)
                border.color: "#303542"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "⏻"
                    color: mousePower.containsMouse ? "#FFFFFF" : root.textSecondary
                    font.pixelSize: 15
                }

                MouseArea {
                    id: mousePower
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: sddm.powerOff()
                }
            }
        }
    }

    // SDDM Event Handlers
    Connections {
        target: sddm

        function onLoginFailed() {
            errorMessage.text = "Giriş başarısız. Lütfen tekrar deneyin."
            errorMessage.visible = true
            passwordInput.text = ""
            passwordInput.focus = true
        }

        function onLoginSucceeded() {
            errorMessage.visible = false
        }
    }

    Component.onCompleted: {
        passwordInput.focus = true
    }
}
