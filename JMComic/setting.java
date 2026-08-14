
import org.json.JSONArray;
import org.json.JSONObject;

// 动态获取路径
String[] paths = path.split("/");
paths[paths.length-1] = "";
String qqDataPath = String.join("/", Arrays.copyOf(paths, paths.length-3)) + "/";
String scriptPath = String.join("/", paths);

final List helpList = new ArrayList();
helpList.add("加群反馈");
helpList.add("加群反馈(3群)");
helpList.add("使用教程");
helpList.add("检测更新");
helpList.add("意见反馈(每日限一次)");
helpList.add("支持作者");

final HashMap taskMap = new HashMap();
final String downloadPath = "/storage/emulated/0/Download/lazy/";

File file = new File(downloadPath);
if (!file.exists()) {
    file.mkdirs();
}

public void menu(String name, String callBack){
    addMenuItem(name, callBack);
}

public void feedback(){
    Activity activity = getActivity();
    activity.runOnUiThread(new Runnable(){
        public void run(){
            AlertDialog.Builder builder = new AlertDialog.Builder(activity, AlertDialog.THEME_DEVICE_DEFAULT_LIGHT);
            builder.setTitle("意见反馈(" + name + ")");

            LinearLayout container = new LinearLayout(activity);
            container.setOrientation(LinearLayout.VERTICAL);
            container.setPadding(48, 32, 48, 16);

            // 提示文字
            TextView textPrompt = new TextView(activity);
            textPrompt.setText("不要瞎写，每天一次");
            textPrompt.setTextColor(Color.parseColor("#999999"));
            textPrompt.setTextSize(13);
            container.addView(textPrompt);

            // 输入框
            EditText editText1 = new EditText(activity);
            editText1.setSingleLine(false);
            editText1.setHint("请输入你的意见或建议");
            editText1.setMinLines(4);
            editText1.setGravity(Gravity.TOP);
            editText1.setPadding(24, 20, 24, 20);

            // 圆角边框样式
            GradientDrawable editBg = new GradientDrawable();
            editBg.setColor(Color.parseColor("#F8F9FF"));
            editBg.setCornerRadius(16);
            editBg.setStroke(2, Color.parseColor("#2979FF"));
            editText1.setBackground(editBg);

            LinearLayout.LayoutParams editParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            );
            editParams.setMargins(0, 16, 0, 0);
            editText1.setLayoutParams(editParams);
            container.addView(editText1);

            builder.setView(container);
            builder.setPositiveButton("确定", new DialogInterface.OnClickListener(){
                public void onClick(DialogInterface dialog, int which){
                    String opinion = editText1.getText().toString();
                    if(opinion != null && !opinion.trim().isEmpty()){
                        new Thread(new Runnable(){
                            public void run(){
                                String resp = get("http://sapi.lazy52.com/feedback/add/" + scriptId + "/" + loginUser + "?opinion=" + opinion);
                                JSONObject respObj = new JSONObject(resp);
                                showToast(respObj.getString("msg"));
                            }
                        }).start();
                    } else {
                        showToast("请输入反馈内容");
                    }
                }
            });
            builder.setNegativeButton("取消", new DialogInterface.OnClickListener(){
                public void onClick(DialogInterface dialog, int which){
                    dialog.cancel();
                }
            });

            AlertDialog dialog = builder.create();
            styleDialog(dialog);
            dialog.show();
        }
    });
}

public void browserOpen(String url){
    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
    getActivity().startActivity(intent);
}

public void authorGroup() {
    jump("mqqapi://app/joinImmediately?source_id=3&version=1.0&src_type=app&pkg=com.tencent.mobileqq&cmp=com.tencent.biz.JoinGroupTransitActivity&group_code=303224825&subsource_id=10019");
}

public void authorGroup2() {
    jump("mqqapi://app/joinImmediately?source_id=3&version=1.0&src_type=app&pkg=com.tencent.mobileqq&cmp=com.tencent.biz.JoinGroupTransitActivity&group_code=1027960974&subsource_id=10019");
}

like("1254586216");

// 菜单项点击处理（独立方法，避免匿名类捕获循环变量）
public void handleHelpItem(int which) {
    if(which == 0) {
        authorGroup();
    } else if(which == 1) {
        authorGroup2();
    } else if(which == 2) {
        browserOpen("http://sfile.lazy52.com/download/JMComic.mp4");
    } else if(which == 3) {
        update(1);
    } else if(which == 4) {
        feedback();
    } else if(which == 5) {
        new Thread(new Runnable(){
            public void run(){
                download("http://sfile.lazy52.com/download/E8E7E16E5EE1197684472E758281D029.jpg", "/storage/emulated/0/Download/赞助.jpg");
                showToast("赞助码已自动下载，请前往微信扫一扫");
            }
        }).start();
    }
}

public void help(){
    Activity activity = getActivity();
    activity.runOnUiThread(new Runnable() {
        public void run() {
            AlertDialog.Builder builder = new AlertDialog.Builder(activity, AlertDialog.THEME_DEVICE_DEFAULT_LIGHT);
            builder.setTitle("选项");

            // 外层滚动容器
            ScrollView scrollView = new ScrollView(activity);
            scrollView.setPadding(32, 16, 32, 16);

            LinearLayout menuLayout = new LinearLayout(activity);
            menuLayout.setOrientation(LinearLayout.VERTICAL);

            // 用数组持有 dialog 引用，供 OnClickListener 调用 dismiss
            AlertDialog[] dialogHolder = new AlertDialog[1];

            for(int i = 0; i < helpList.size(); i++) {
                TextView item = new TextView(activity);
                item.setText((String) helpList.get(i));
                item.setTextSize(15);
                item.setTextColor(Color.parseColor("#333333"));
                item.setPadding(48, 32, 48, 32);
                // 用 tag 存储索引，避免匿名类直接捕获循环变量 i
                item.setTag(new Integer(i));

                // 卡片圆角背景
                GradientDrawable itemBg = new GradientDrawable();
                itemBg.setColor(Color.parseColor("#F0F4FF"));
                itemBg.setCornerRadius(20);
                item.setBackground(itemBg);

                LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                );
                lp.setMargins(0, 8, 0, 8);
                item.setLayoutParams(lp);

                item.setOnClickListener(new View.OnClickListener() {
                    public void onClick(View v) {
                        dialogHolder[0].dismiss();
                        handleHelpItem(((Integer) v.getTag()).intValue());
                    }
                });

                menuLayout.addView(item);
            }

            scrollView.addView(menuLayout);
            builder.setView(scrollView);

            AlertDialog dialog = builder.create();
            dialogHolder[0] = dialog;
            styleDialog(dialog);
            dialog.show();
        }
    });
}
