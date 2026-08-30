import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#12151D"

    property string bgSource: config.background || "/usr/share/wallpapers/Zelix/ZelixOS Aurora.png"
    property string logoSource: config.logo || "/usr/share/zelix/zelix-icon.png"
    property color accentCol: config.accentColor || "#1A4D8F"
    property color accentHov: config.accentHover || "#4A90E2"
    property color cardBg: config.cardBackground || "#12151D"
    property real cardOp: Number(config.cardOpacity) || 0.85
    property color textPrimary: config.textColor || "#FFFFFF"
    property color textSecondary: config.textSecondary || "#B0B5C0"

    // Background Image
    Image {
        id: bgImage
        anchors.fill: parent
        source: root.bgSource
        fillMode: Image.PreserveAspectCrop
        smooth: true
        asynchronous: true
    }

    // Subtle dark overlay to enhance contrast
    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.25
    }

    // Top Clock & Date Container
    Column {
        id: clockContainer
        anchors.top: parent.top
        anchors.topMargin: root.height * 0.08
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 6

        Text {
            id: clockText
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatTime(new Date(), config.clockFormat || "HH:mm")
            color: root.textPrimary
            font.pixelSize: 64
            font.weight: Font.DemiBold
            font.family: "Noto Sans"
            style: Text.DropShadow
            styleColor: "#66000000"
        }

        Text {
            id: dateText
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatDate(new Date(), config.dateFormat || "dddd, d MMMM yyyy")
            color: root.textSecondary
            font.pixelSize: 18
            font.family: "Noto Sans"
            style: Text.DropShadow
            styleColor: "#66000000"
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
        height: 420
        anchors.centerIn: parent
        radius: 16
        color: root.cardBg
        opacity: root.cardOp
        border.color: Qt.rgba(1, 1, 1, 0.12)
        border.width: 1

        // Drop shadow effect simulation
        Rectangle {
            anchors.fill: parent
            anchors.margins: -1
            radius: parent.radius + 1
            color: "transparent"
            border.color: Qt.rgba(0, 0, 0, 0.3)
            border.width: 1
            z: -1
        }

        Column {
            anchors.fill: parent
            anchors.margins: 30
            spacing: 20

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
                    }
                }
            }

            // User Name or Selection
            Item {
                width: parent.width
                height: 38

                ComboBox {
                    id: userSelect
                    anchors.fill: parent
                    model: userModel
                    textRole: "name"
                    currentIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
                    visible: userModel.count > 1

                    background: Rectangle {
                        color: "#1E222D"
                        radius: 8
                        border.color: userSelect.activeFocus ? root.accentCol : "#303542"
                        border.width: 1
                    }

                    contentItem: Text {
                        leftPadding: 12
                        text: userSelect.displayText
                        color: root.textPrimary
                        font.pixelSize: 14
                        font.family: "Noto Sans"
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                Text {
                    id: singleUserText
                    anchors.fill: parent
                    visible: userModel.count <= 1
                    text: userModel.lastUser || (userModel.count > 0 ? userModel.data(userModel.index(0, 0), Qt.DisplayRole) : "zelix")
                    color: root.textPrimary
                    font.pixelSize: 16
                    font.weight: Font.Medium
                    font.family: "Noto Sans"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            // Password Field
            Item {
                width: parent.width
                height: 44

                Rectangle {
                    id: passBg
                    anchors.fill: parent
                    color: "#1E222D"
                    radius: 8
                    border.color: passwordInput.activeFocus ? root.accentCol : "#303542"
                    border.width: 1

                    TextField {
                        id: passwordInput
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 44
                        echoMode: showPassBtn.checked ? TextInput.Normal : TextInput.Password
                        placeholderText: "Parola / Password"
                        placeholderTextColor: root.textSecondary
                        color: root.textPrimary
                        font.pixelSize: 14
                        font.family: "Noto Sans"
                        background: null
                        focus: true

                        onAccepted: loginAction()
                        onTextChanged: errorMessage.visible = false
                    }

                    // Eye Icon Toggle
                    Rectangle {
                        id: showPassBtn
                        width: 32
                        height: 32
                        radius: 6
                        anchors.right: parent.right
                        anchors.rightMargin: 6
                        anchors.verticalCenter: parent.verticalCenter
                        color: mouseShowPass.containsMouse ? Qt.rgba(1, 1, 1, 0.1) : "transparent"
                        property bool checked: false

                        Text {
                            anchors.centerIn: parent
                            text: showPassBtn.checked ? "👁" : "🔒"
                            font.pixelSize: 14
                            color: root.textSecondary
                        }

                        MouseArea {
                            id: mouseShowPass
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: showPassBtn.checked = !showPassBtn.checked
                        }
                    }
                }
            }

            // Error Message
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
                id: loginButton
                width: parent.width
                height: 42
                radius: 8
                color: mouseLogin.containsMouse ? root.accentHov : root.accentCol

                Text {
                    anchors.centerIn: parent
                    text: "Giriş Yap / Login →"
                    color: "#FFFFFF"
                    font.pixelSize: 14
                    font.weight: Font.Bold
                    font.family: "Noto Sans"
                }

                MouseArea {
                    id: mouseLogin
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: loginAction()
                }
            }
        }
    }

    // Bottom Bar: Session & Power Options
    Item {
        id: bottomBar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 24
        height: 48

        // Left: Session selector
        Row {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            spacing: 12

            ComboBox {
                id: sessionSelect
                width: 180
                height: 36
                model: sessionModel
                textRole: "name"
                currentIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0

                background: Rectangle {
                    color: Qt.rgba(0.07, 0.08, 0.11, 0.85)
                    radius: 8
                    border.color: "#303542"
                    border.width: 1
                }

                contentItem: Text {
                    leftPadding: 10
                    text: sessionSelect.displayText
                    color: root.textSecondary
                    font.pixelSize: 12
                    font.family: "Noto Sans"
                    verticalAlignment: Text.AlignVCenter
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
                width: 36
                height: 36
                radius: 18
                color: mouseSuspend.containsMouse ? root.accentCol : Qt.rgba(0.07, 0.08, 0.11, 0.85)
                border.color: "#303542"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "🌙"
                    font.pixelSize: 14
                }

                ToolTip.visible: mouseSuspend.containsMouse
                ToolTip.text: "Uyut / Suspend"

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
                width: 36
                height: 36
                radius: 18
                color: mouseReboot.containsMouse ? root.accentCol : Qt.rgba(0.07, 0.08, 0.11, 0.85)
                border.color: "#303542"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "🔄"
                    font.pixelSize: 14
                }

                ToolTip.visible: mouseReboot.containsMouse
                ToolTip.text: "Yeniden Başlat / Reboot"

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
                width: 36
                height: 36
                radius: 18
                color: mousePower.containsMouse ? "#E53935" : Qt.rgba(0.07, 0.08, 0.11, 0.85)
                border.color: "#303542"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "⏻"
                    color: mousePower.containsMouse ? "#FFFFFF" : root.textSecondary
                    font.pixelSize: 15
                }

                ToolTip.visible: mousePower.containsMouse
                ToolTip.text: "Kapat / Shutdown"

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

    // Login action function
    function loginAction() {
        var user = userModel.count > 1 ? userSelect.currentText : (singleUserText.text || "zelix")
        var pass = passwordInput.text
        var sess = sessionSelect.currentIndex
        sddm.login(user, pass, sess)
    }

    // SDDM Event Handlers
    Connections {
        target: sddm
        function onLoginFailed() {
            errorMessage.visible = true
            passwordInput.selectAll()
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
