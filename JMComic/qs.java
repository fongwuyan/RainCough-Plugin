path = appPath + "/";
loginUser = myUin;

public void java(String name) {
    load(name);
}

public void sCard(String uin, String card, int type) {
    if (type == 1) {
        sendCard("", uin, card);
    } else {
        sendCard(uin, "", card);
    }
}

public void sMsg(String uin, String msg, int type) {
    if (type == 1) {
        sendMsg("", uin, msg);
    } else {
        sendMsg(uin, "", msg);
    }
}

public void sFile(String uin, String path, int type) {
    if (type == 1) {
        sendFile("", uin, path);
    } else {
        sendFile(uin, "", path);
    }
}

public void sPic(String uin, String path, int type) {
    if (type == 1) {
        sendPic("", uin, path);
    } else {
        sendPic(uin, "", path);
    }
}

public void item(String name, String callback) {
    addItem(name, callback);
}

public void like(String uin) {
    sendLike(uin, 50);
}

public void showToast(String s) {
    toast(s);
}

public void help(String groupUin, String uin, int chatType) {
    help();
}

public void jar(String s) {
    loadJar(s);
}

public Msg msg(Object o) {
    Msg msg = new Msg();
    msg.type    = o.IsGroup ? 2 : 1;
    msg.msgType = o.MessageType;
    msg.msg     = o.MessageContent;
    msg.time    = o.MessageTime;
    msg.sendUin = o.UserUin;
    msg.peerUin = o.IsGroup ? o.GroupUin : o.PeerUin;
    msg.path    = o.LocalPath;
    msg.data    = o.msg;
    msg.atList  = o.mAtList;
    return msg;
}

public void setEnable(int t, String u, boolean v) {
    showToast(v?"已开启":"已关闭");
    putBoolean("lazy-43", "enable_" + t + "_" + u, v);
}

public boolean isEnabled(int type, String uin) {
    return getBoolean("lazy-43", "enable_" + type + "_" + uin, false);
}

public void enable(String g, String u, int t) {
    if (t == 1) {
        setEnable(t, u, !isEnabled(t, u));
    } else if (t == 2) {
        setEnable(t, g, !isEnabled(t, g));
    }
}

public void setDrawCover(int t, String u, boolean v) {
    showToast(v?"已开启":"已关闭");
    putBoolean("lazy-43", "enable_dc_" + t + "_" + u, v);
}

public boolean getDrawCover(int type, String uin) {
    return getBoolean("lazy-43", "enable_dc_" + type + "_" + uin, false);
}

public void drawCover(String g, String u, int t) {
    if (t == 1) {
        setDrawCover(t, u, !getDrawCover(t, u));
    } else if (t == 2) {
        setDrawCover(t, g, !getDrawCover(t, g));
    }
}
