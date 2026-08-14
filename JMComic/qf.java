loginUser = myUin;
path = pluginPath + "/";

public void java(String path) {
    loadJava(path);
}

public void showToast(String s) {
    toast(s);
}

public void item(String name, String call) {
    addItem(name, call);
}

public void menu(String name, String call) {
    addMenuItem(name, call);
}

public void help(int type, String peerUin, String name) {
    help();
}

public void like(String uin) {
    sendZan(uin, 50);
}

public void sMsg(String uin, String msg, int type) {
    if (type == 1 || type == 100) {
        sendMsg(uin, msg, type);
    } else if (type == 2) {
        sendMsg(uin, msg, 2);
    } else {
        sendMsg(uin, msg, 1);
    }
}

public void sCard(String uin, String card, int type) {
    if (type == 1 || type == 100) {
        sendCard(uin, card, type);
    } else if (type == 2) {
        sendCard(uin, card, 2);
    } else {
        sendCard(uin, card, 1);
    }
}

public void sFile(String uin, String path, int type) {
    if (type == 1 || type == 100) {
        sendFile(uin, path, type);
    } else if (type == 2) {
        sendFile(uin, path, type);
    }
}

public void sPic(String uin, String picPath, int type) {
    if (type == 1 || type == 100) {
        sendPic(uin, picPath, type);
    } else if (type == 2) {
        sendPic(uin, picPath, 2);
    }
}

public Msg msg(Object o) {
    Msg m = new Msg();
    m.type    = o.type;
    m.msgType = o.msgType;
    m.msg     = o.msg;
    m.time    = o.time;
    m.sendUin = o.userUin;
    m.peerUin = o.peerUin;
    m.path    = o.path;
    m.data    = o.data;
    m.atList  = o.atList;
    return m;
}

public void jar(String path) {
    loadJar(path);
}

public Object getActivity() {
    return getNowActivity();
}

public void setEnabled(int t, String u, boolean v) {
    showToast(v?"已开启":"已关闭");
    putBoolean("lazy-43", "enable_" + t + "_" + u, v);
}

public boolean isEnabled(int type, String uin) {
    return getBoolean("lazy-43", "enable_" + type + "_" + uin, false);
}

public void enable(int t, String u, String n) {
    setEnabled(t, u, !isEnabled(t, u));
}

public void setDrawCover(int t, String u, boolean v) {
    showToast(v?"已开启":"已关闭");
    putBoolean("lazy-43", "enable_dc_" + t + "_" + u, v);
}

public boolean getDrawCover(int type, String uin) {
    return getBoolean("lazy-43", "enable_dc_" + type + "_" + uin, false);
}

public void drawCover(int t, String u, String n) {
    setDrawCover(t, u, !getDrawCover(t, u));
}
