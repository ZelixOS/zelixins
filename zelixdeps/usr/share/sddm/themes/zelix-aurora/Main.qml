import QtQuick 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#000000"

    property string bgSource: config.background || "background.png"
    property string logoSource: config.logo || "logo.png"

    // Black & White palette
    property color accentCol:     config.accentColor     || "#FFFFFF"
    property color accentHov:     config.accentHover     || "#E0E0E0"
    property color cardBg:        config.cardBackground  || "#111111"
    property real  cardOp:        Number(config.cardOpacity) || 0.92
    property color textPrimary:   config.textColor       || "#FFFFFF"
    property color textSecondary: config.textSecondary   || "#AAAAAA"
    property color borderNormal:  "#333333"
    property color borderFocus:   "#FFFFFF"
    property color btnHover:      "#222222"
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

    // ─── Background Image ───────────────────────────────────────────────────
    Image {
        id: bgImage
        anchors.fill: parent
        source: root.bgSource
        fillMode: Image.PreserveAspectCrop
        smooth: true
        asynchronous: true
        onStatusChanged: {
            if (status == Image.Error && source != "background.png")
                source = "background.png"
        }
    }

    // Dark overlay — ensures readability on any background
    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.62
    }

    // ─── Top: Clock & Date ───────────────────────────────────────────────────
    Column {
        id: clockContainer
        anchors.top: parent.top
        anchors.topMargin: Math.max(40, root.height * 0.08)
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 4

        Text {
            id: clockText
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatTime(new Date(), config.clockFormat || "HH:mm")
            color: root.textPrimary
            font.pixelSize: 72
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
            dateText.text  = Qt.formatDate(new Date(), config.dateFormat || "dddd, d MMMM yyyy")
        }
    }

    // ─── Center: Login Card ──────────────────────────────────────────────────
    Rectangle {
        id: loginCard
        width: 380
        height: 420
        anchors.centerIn: parent
        radius: 12
        color: root.cardBg
        opacity: root.cardOp

        // Thin white border
        border.color: Qt.rgba(1, 1, 1, 0.18)
        border.width: 1

        Column {
            id: cardContent
            anchors.fill: parent
            anchors.margins: 32
            spacing: 16

            // ── Logo ────────────────────────────────────────────────────────
            Item {
                width: 80
                height: 80
                anchors.horizontalCenter: parent.horizontalCenter

                Rectangle {
                    anchors.fill: parent
                    radius: 40
                    color: "#1A1A1A"
                    border.color: "#FFFFFF"
                    border.width: 1

                    Image {
                        id: userAvatar
                        anchors.fill: parent
                        anchors.margins: 12
                        source: root.logoSource
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        onStatusChanged: {
                            if (status == Image.Error) source = ""
                        }
                    }

                    Text {
                        anchors.centerIn: parent
                        text: "👤"
                        font.pixelSize: 30
                        visible: userAvatar.status != Image.Ready
                    }
                }
            }

            // ── Username field ───────────────────────────────────────────────
            Rectangle {
                width: parent.width
                height: 42
                color: "#0D0D0D"
                radius: 8
                border.color: userNameInput.activeFocus ? root.borderFocus : root.borderNormal
                border.width: 1

                TextInput {
                    id: userNameInput
                    anchors.fill: parent
                    anchors.leftMargin: 14
                    anchors.rightMargin: 14
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
                    anchors.leftMargin: 14
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Kullanıcı Adı / Username"
                    color: root.textSecondary
                    font.pixelSize: 13
                    font.family: "Noto Sans"
                    visible: !userNameInput.text && !userNameInput.activeFocus
                }
            }

            // ── Password field ───────────────────────────────────────────────
            Rectangle {
                id: passBg
                width: parent.width
                height: 42
                color: "#0D0D0D"
                radius: 8
                border.color: passwordInput.activeFocus ? root.borderFocus : root.borderNormal
                border.width: 1

                TextInput {
                    id: passwordInput
                    anchors.fill: parent
                    anchors.leftMargin: 14
                    anchors.rightMargin: 44
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
                    anchors.leftMargin: 14
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Parola / Password"
                    color: root.textSecondary
                    font.pixelSize: 13
                    font.family: "Noto Sans"
                    visible: !passwordInput.text && !passwordInput.activeFocus
                }

                // Password show/hide toggle
                Rectangle {
                    id: showPassToggle
                    width: 30
                    height: 30
                    radius: 6
                    anchors.right: parent.right
                    anchors.rightMargin: 6
                    anchors.verticalCenter: parent.verticalCenter
                    color: mouseShowPass.containsMouse ? "#222222" : "transparent"
                    property bool checked: false

                    Text {
                        anchors.centerIn: parent
                        text: showPassToggle.checked ? "👁" : "🔒"
                        font.pixelSize: 13
                        color: root.textSecondary
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

            // ── Error message ────────────────────────────────────────────────
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

            // ── Login button ─────────────────────────────────────────────────
            Rectangle {
                id: loginBtn
                width: parent.width
                height: 44
                radius: 8
                color: mouseLogin.containsMouse ? root.accentHov : root.accentCol

                Text {
                    anchors.centerIn: parent
                    text: "Giriş Yap / Login →"
                    color: "#000000"
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

    // ─── Bottom Bar: Session & Power ─────────────────────────────────────────
    Item {
        id: bottomBar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 24
        height: 48

        // Left: Session switcher
        Rectangle {
            id: sessionBtn
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            height: 36
            width: sessionRow.implicitWidth + 24
            color: mouseSession.containsMouse ? "#1A1A1A" : "transparent"
            radius: 8
            border.color: mouseSession.containsMouse ? root.borderFocus : root.borderNormal
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
                    color: mouseSession.containsMouse ? root.textPrimary : root.textSecondary
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
                        sessionText.text = root.getSessionName(root.sessionIndex)
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
                width: 38; height: 38; radius: 19
                color: mouseSuspend.containsMouse ? "#2A2A2A" : "transparent"
                border.color: mouseSuspend.containsMouse ? root.borderFocus : root.borderNormal
                border.width: 1
                Text {
                    anchors.centerIn: parent
                    text: "🌙"
                    font.pixelSize: 15
                }
                MouseArea {
                    id: mouseSuspend; anchors.fill: parent
                    hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: sddm.suspend()
                }
            }

            // Reboot
            Rectangle {
                width: 38; height: 38; radius: 19
                color: mouseReboot.containsMouse ? "#2A2A2A" : "transparent"
                border.color: mouseReboot.containsMouse ? root.borderFocus : root.borderNormal
                border.width: 1
                Text {
                    anchors.centerIn: parent
                    text: "🔄"
                    font.pixelSize: 15
                }
                MouseArea {
                    id: mouseReboot; anchors.fill: parent
                    hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: sddm.reboot()
                }
            }

            // Power Off
            Rectangle {
                width: 38; height: 38; radius: 19
                color: mousePower.containsMouse ? "#FFFFFF" : "transparent"
                border.color: mousePower.containsMouse ? "#FFFFFF" : root.borderNormal
                border.width: 1
                Text {
                    anchors.centerIn: parent
                    text: "⏻"
                    color: mousePower.containsMouse ? "#000000" : root.textSecondary
                    font.pixelSize: 16
                }
                MouseArea {
                    id: mousePower; anchors.fill: parent
                    hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                    onClicked: sddm.powerOff()
                }
            }
        }
    }

    // ─── SDDM Event Handlers ─────────────────────────────────────────────────
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
