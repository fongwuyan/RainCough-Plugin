final String author = "lazy";
final String name = "JMComic";
final int scriptId = 43;
final double version = 2.78;

public void updateAlert(String download, String title, String content) {
    getActivity().runOnUiThread(new Runnable() {
        public void run() {
            AlertDialog.Builder builder = new AlertDialog.Builder(getActivity(), AlertDialog.THEME_DEVICE_DEFAULT_LIGHT)
                .setTitle(title)
                .setMessage(content)
                .setNegativeButton("更新", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        new Thread(new Runnable() {
                            public void run() {
                                download(download, downloadPath + name + ".zip");
                                unzip(downloadPath + name + ".zip", scriptPath);
                                getActivity().runOnUiThread(new Runnable() {
                                    public void run() {
                                        showToast("更新成功，请重新加载脚本");
                                    }
                                });
                            }
                        }).start();
                    }
                });
            AlertDialog dialog = builder.create();
            styleDialog(dialog);
            dialog.show();
        }
    });
}

public void update(int type) {
    new Thread(new Runnable() {
        public void run() {
            try {
                JSONObject jsonObject = new JSONObject(get("http://sapi.lazy52.com/script/update/" + scriptId + "?version=" + version));
                double lastVersion = jsonObject.getDouble("lastVersion");
                String log = jsonObject.getString("log");
                String download = jsonObject.getString("download");
                String name = jsonObject.getString("name");
                if (lastVersion > version) {
                    updateAlert(download, "有新版本——" + lastVersion, name + "更新日志:\n" + log.replace("\t", ""));
                } else {
                    if (type != 0) showToast("已经是最新版本了!");
                }
            } catch (Exception e) {
                showToast(e.getMessage());
            }
        }
    }).start();
}

update(0);
