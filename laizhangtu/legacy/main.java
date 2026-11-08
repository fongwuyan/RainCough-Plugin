// 屎山代码别看了，，，

import android.webkit.WebView;
import android.webkit.WebSettings;
import android.view.View;
import android.view.MotionEvent;
import android.view.WindowManager;
import android.app.AlertDialog;
import android.content.DialogInterface;
import java.io.File;
import java.io.FileInputStream;
import java.util.regex.Pattern;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Iterator;
import java.util.Map;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.net.*;
import org.json.JSONObject;
import org.json.JSONArray;
import android.app.UiModeManager;
import android.graphics.*;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.content.res.Configuration;
import android.net.Uri;

import com.tencent.mobileqq.widget.QQToast;

load(appPath + "/utils/ImageUtil.java");

public static boolean isDarkModeEnabled(Context context) {
   return ((context.getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES);
} 

// 1. 读取 HTML
File htmlFile = new File(appPath + "/settings.html");

FileInputStream fis = new FileInputStream(htmlFile);
byte[] buffer = new byte[fis.available()];
fis.read(buffer);
fis.close();
String htmlRaw = new String(buffer, "UTF-8");


public void showWebDialog(String groupUin, String userUin, int type) {
    if (getActivity() != null) {
        getActivity().runOnUiThread(new Runnable() {
            public void run() {
                try {
                    
                    // 2. 【数据准备】读取当前配置
                    // 判断是否是禁用群
                    boolean isBanned = false;
                    if (groupUin.matches("193095561|637735260|881035298")) {
                        isBanned = true;
                    }

                    String uin = (type == 2) ? groupUin : userUin;
                    String s_dark_mode = String.valueOf(isDarkModeEnabled(context));
                    String s_main = String.valueOf(getBoolean(uin, String.valueOf(type), false));
                    String s_img = String.valueOf(getBoolean("设置", "信息", true));
                    String s_exclude_ai = String.valueOf(getBoolean("设置", "排除AI", true));
                    String s_flip_h = String.valueOf(getBoolean("设置", "翻转", true));
                    String s_flip_v = String.valueOf(getBoolean("设置", "垂直翻转", false));
                    String s_auto = String.valueOf(getBoolean("设置", "撤回", false));
                    String s_size = String.valueOf(getInt("设置", "size", 0));
                    String s_time = String.valueOf(getInt("设置", "撤回时间", 5000));
                    String s_cool = String.valueOf(getInt("设置", "冷却时间", 0));
                    String s_prob = String.valueOf(getInt("设置", "冲多了", 5));
                    String s_r18 = String.valueOf(getBoolean("设置", "r18", false));
                    String s_banned = String.valueOf(isBanned);
                    String s_proxy = getString("设置", "proxy", "i.pixiv.re");

                    // 3. 【数据注入】拼装 JS 对象
                    String jsConfig = "window.AppConfig = {" +
                            "dark_mode: '" + s_dark_mode + "'," + 
                            "switch_main: '" + s_main + "'," + 
                            "switch_img: '" + s_img + "'," +
                            "exclude_ai: '" + s_exclude_ai + "'," +
                            "flip_h: '" + s_flip_h + "'," +
                            "flip_v: '" + s_flip_v + "'," +
                            "auto_revoke: '" + s_auto + "'," +
                            "img_size: '" + s_size + "'," +
                            "revoke_time: '" + s_time + "'," +
                            "cool_down: '" + s_cool + "'," +
                            "prob_slider: '" + s_prob + "'," +
                            "r18: '" + s_r18 + "'," +
                            "banned_group: '" + s_banned + "'," +
                            "proxy_server: '" + s_proxy + "'" +
                            "};";
                            
                    String htmlContent = htmlRaw.replace("<body>", "<body><script>" + jsConfig + "</script>");

                    // 4. 创建 WebView
                    final WebView webView = new WebView(getActivity());
                    WebSettings settings = webView.getSettings();
                    settings.setJavaScriptEnabled(true);
                    webView.setFocusable(true);
                    webView.setFocusableInTouchMode(true);
                    // webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
                    webView.setVerticalScrollBarEnabled(false);

                    // 5. 创建 Dialog
                    AlertDialog.Builder builder = new AlertDialog.Builder(getActivity(), AlertDialog.THEME_DEVICE_DEFAULT_LIGHT);
                    builder.setView(webView);
                    final AlertDialog dialog = builder.create();

                    // 6. 【监听点击】拦截 app://save
                    webView.setOnTouchListener(new View.OnTouchListener() {
                        public boolean onTouch(View v, MotionEvent event) {
                            if (event.getAction() == MotionEvent.ACTION_UP) {
                                WebView.HitTestResult hr = ((WebView)v).getHitTestResult();
                                if (hr != null && hr.getExtra() != null) {
                                    String url = hr.getExtra();
                                    
                                    if (url.startsWith("app://close")) {
                                        dialog.dismiss();
                                        return true;
                                    } else if (url.startsWith("app://join_group")) {
                                    	Uri u = Uri.parse("mqq://card/show_pslcard?src_type=internal&version=1&uin=637735260&card_type=group&source=qrcode");
									    Intent in = new Intent(Intent.ACTION_VIEW, u);
									    in.setPackage("com.tencent.mobileqq");
									    in.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
									    context.startActivity(in);
                                    } else if (url.startsWith("app://save")) {
                                        try {
                                            // 防崩检查
                                            int index = url.indexOf("data=");
                                            if (index == -1) return true;

                                            String rawData = url.substring(index + 5);
                                            String jsonStr = java.net.URLDecoder.decode(rawData, "UTF-8");
                                            JSONObject json = new JSONObject(jsonStr);
                                            
                                            // 1. 本聊天开关 (如果没被禁用)
                                            if (!isBanned) {
                                                // 如果找不到 "switch_main"，默认当作 false
                                                boolean val = json.optBoolean("switch_main", false);
                                                putBoolean(uin, String.valueOf(type), val);
                                            }
                                            
                                            // 2. 发送涩图
                                            putBoolean("设置", "信息", json.optBoolean("switch_img", true));
                                            
                                            putBoolean("设置", "排除AI", json.optBoolean("exclude_ai", true));
                                            
                                            // 3. 翻转
                                            putBoolean("设置", "翻转", json.optBoolean("flip_h", true));
                                            putBoolean("设置", "垂直翻转", json.optBoolean("flip_v", false));
                                            
                                            // 4. 自动撤回
                                            putBoolean("设置", "撤回", json.optBoolean("auto_revoke", false));

                                            // 5. 尺寸 (int)
                                            // 使用 optInt，如果获取失败默认 0
                                            putInt("设置", "size", json.optInt("img_size", 0));
                                            
                                            // 6. 撤回时间 (HTML传过来可能是字符串，optInt 会自动尝试转换)
                                            // 如果转换失败，默认 5000
                                            putInt("设置", "撤回时间", json.optInt("revoke_time", 5000));
                                            
                                            // 7. 冷却时间
                                            putInt("设置", "冷却时间", json.optInt("cool_down", 0));
                                            
                                            // 8. 冲多了概率
                                            putInt("设置", "冲多了", json.optInt("prob_slider", 5));
                                            
                                            putBoolean("设置", "r18", json.optBoolean("r18", false));
                                            
                                            putString("设置", "proxy", json.optString("proxy_server", "i.pixiv.re"));
                                            
                                            QQToast.makeText(context, 2, "已保存", 1000, 0).show();
                                            dialog.dismiss();
                                            
                                        } catch (Exception e) {
                                            toast("保存失败: " + e.toString());
                                        }
                                        return true;
                                    }

                                }
                            }
                            return false; 
                        }
                    });

                    // 7. 加载
                    webView.loadDataWithBaseURL("file://" + appPath + "/", htmlContent, "text/html", "utf-8", null);

                    // 8. 修复输入法
                    dialog.setOnShowListener(new DialogInterface.OnShowListener() {
                        public void onShow(DialogInterface d) {
                            dialog.getWindow().clearFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_ALT_FOCUSABLE_IM);
                            dialog.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE);
                            webView.requestFocus();
                        }
                    });

                    dialog.show();

                } catch (Exception e) {
                    try { toast("System Error: " + e.toString()); } catch (Exception ex) {}
                }
            }
        });
    }
}

addItem("设置", "showWebDialog");


public static boolean delAllFile(String path) {
    boolean flag = false;
    File file = new File(path);
    if(!file.exists()) {
        return flag;
    }
    if(!file.isDirectory()) {
        return flag;
    }
    String[] tempList = file.list();
    File temp = null;
    for(int i = 0; i < tempList.length; i++) {
        if(path.endsWith(File.separator)) {
            temp = new File(path + tempList[i]);
        } else {
            temp = new File(path + File.separator + tempList[i]);
        }
        if(temp.isFile()) {
            temp.delete();
        }
        if(temp.isDirectory()) {
            delAllFile(path + "/" + tempList[i]);
            flag = true;
        }
    }
    return flag;
}

public static String getMD5(String imagePath) {
    try {
        // 创建文件输入流
        FileInputStream fis = new FileInputStream(imagePath);

        // 创建 MessageDigest 对象，指定 MD5 算法
        MessageDigest md = MessageDigest.getInstance("MD5");

        // 创建缓冲区
        byte[] buffer = new byte[8192];
        int bytesRead;
        while((bytesRead = fis.read(buffer)) != -1) {
            // 更新 MessageDigest 对象
            md.update(buffer, 0, bytesRead);
        }

        // 计算 MD5 值
        byte[] mdBytes = md.digest();

        // 将字节数组转换为十六进制字符串
        StringBuilder sb = new StringBuilder();
        for(byte mdByte: mdBytes) {
            sb.append(Integer.toString((mdByte & 0xff) + 0x100, 16).substring(1));
        }

        // 关闭文件输入流
        fis.close();

        // 返回计算得到的 MD5 值
        return sb.toString();
    } catch(Exception e) {
        e.printStackTrace();
    }

    return null;
}



public String httpget(String url) {
    StringBuffer buffer = new StringBuffer();
    InputStreamReader isr = null;
    try {
        URL urlObj = new URL(url);
        URLConnection uc = urlObj.openConnection();
        uc.setConnectTimeout(15000);
        uc.setReadTimeout(15000);
        isr = new InputStreamReader(uc.getInputStream(), "utf-8");
        BufferedReader reader = new BufferedReader(isr);
        String line;
        while((line = reader.readLine()) != null) {
            buffer.append(line + "\n");
        }
    } catch(Exception e) {
        e.printStackTrace();
    } finally {
        try {
            if(null != isr) {
                isr.close();
            }
        } catch(IOException e) {
            e.printStackTrace();
        }
    }
    if(buffer.length() == 0) return buffer.toString();
    buffer.delete(buffer.length() - 1, buffer.length());
    return buffer.toString();
}


public static void DownloadToFile(String fileUrl, String savePath) throws Exception {
        // 解析 URL
        URL url = new URL(fileUrl);
        URLConnection connection = url.openConnection();
        InputStream inputStream = connection.getInputStream();

        // 创建保存目录
        File file = new File(savePath);
        File parentDir = file.getParentFile();
        if (parentDir != null && !parentDir.exists()) {
            parentDir.mkdirs();
        }

        // 创建输出流
        FileOutputStream outputStream = new FileOutputStream(savePath);

        // 读取并写入数据
        byte[] buffer = new byte[1024];
        int bytesRead;
        while ((bytesRead = inputStream.read(buffer)) != -1) {
            outputStream.write(buffer, 0, bytesRead);
        }

        // 关闭流
        outputStream.close();
        inputStream.close();
    }

// 这个方法何意味
// public void sendMsg(String msg, int uin, int type) {
	// switch(type) {
		// case 1: sendMsg("", uin, msg); break;
		// case 2: sendMsg(uin, "", msg); break;
	// }
// }

ConcurrentHashMap pendingRevokeMap = new ConcurrentHashMap();

public void onMsg(Object data) {
    String quntext = data.MessageContent;
    String qun = data.GroupUin;
    String uin = data.PeerUin;
    int chattype = data.msg.chatType;
    int msgTime = data.MessageTime / 1000;
    //if((data.IsGroup&&("1".equals(getString(data.GroupUin,"涩图"))))){
    String tUin = (chattype == 2) ? qun : uin;
    if(getBoolean(tUin, chattype.toString(), false)) {
        if(quntext.startsWith("来张") && quntext.endsWith("涩图")) {
            
            if(msgTime - getInt(qun, "MsgTime", 0) < getInt("设置", "冷却时间", 0)) {
            	sendMsg(qun, uin, "[AtQQ=" + data.UserUin + "]正在冷却喵，还有" + (getInt("设置", "冷却时间", 0) - msgTime + getInt(qun, "MsgTime", 0)) + "秒才能涩涩哦！");
            	return;
            }
            
            putInt(qun, "MsgTime", msgTime);
            
            String tag = quntext.substring(2, quntext.length() - 2);
            //Toast(tag);
            String setu0, size = "original";
            switch(getInt("设置", "size", 0)) {
                case 1:
                    size = "regular";
                    break;
                case 2:
                    size = "small";
                    break;
                default:
            }
            
            int r18 = getBoolean("设置", "r18", false) ? 2 : 0;
            setu0 = httpget("https://api.lolicon.app/setu/v2?proxy=" + getString("设置", "proxy", "i.pixiv.re") + "&excludeAI=" + getBoolean("设置", "排除AI", true) + "&tag=" + tag.replaceAll("&", "&tag=") + "&r18=" + r18 +"&size=" + size);
            //Toast(setu0);
            JSONObject setu1 = new JSONObject(setu0);
            JSONArray setu2 = setu1.optJSONArray("data");
            //Toast(setu2);
            if(setu2 == null) {
                sendMsg(qun, uin, "获取失败！未知错误喵");
                return;
            } else if(setu2.length() == 0) {
                sendMsg(qun, uin,"[AtQQ=" + data.UserUin + "]\n没有找到关于[" + tag + "]的涩图喵!");
                return;
            }
            JSONObject setu3 = setu2.getJSONObject(0);
            String pid = setu3.getString("pid");
            String uid = setu3.getString("uid");
            String title = setu3.getString("title");
            String author = setu3.getString("author");
            String width = setu3.getString("width");
            String height = setu3.getString("height");
            JSONArray tags1 = setu3.getJSONArray("tags");
            String tagsf = "";
            for(int i = 0; i < tags1.length(); i++) {
                String tags2 = tags1.getString(i);
                tagsf = tagsf + tags2 + ",";
            }
            tagsf = tagsf.substring(0, tagsf.length() - 1);
            JSONObject urls = setu3.getJSONObject("urls");
            String original = urls.getString(size);
            String imagePath = appPath + "/缓存/" + title.replaceAll("[\\\\/:*?\"<>|]", " ") + ".jpg";
			try {
            	DownloadToFile(original, imagePath);
        	} catch(Exception e) {
                sendMsg(qun, uin, "图片下载失败了喵！\n" + e.toString());
                return;
            }
            try {
            	Bitmap bitmap = BitmapFactory.decodeFile(imagePath);
            	if(getBoolean("设置", "翻转", true)) bitmap = ImageUtil.flipImage(bitmap);
            	if(getBoolean("设置", "垂直翻转", false)) bitmap = ImageUtil.mflipImage(bitmap);
            	if(getInt("设置", "冲多了", 5) > new Random().nextInt(100)){
            		bitmap = ImageUtil.blurImage(bitmap);
            		new Thread(new Runnable() {
					    public void run() {
					        Thread.sleep(2500);
            				sendMsg(qun, uin, "咦？怎么变得这么模糊了？不会是最近冲多了吧...");
					    }
					}).start();
            	}
            	ImageUtil.outImage(bitmap, imagePath);
            } catch(Exception e) {
            	sendMsg(qun, uin, "图片处理失败了喵！\n" + e.toString());
            	return;
            }
            if(getBoolean("设置", "信息", true)) sendMsg(qun, uin,"[AtQQ=" + data.UserUin + "]\n标题:" + title + "\n作者:" + author + "\npid:" + pid + "\nuid:" + uid + "\n原图大小:" + width + "*" + height + "\n标签:" + tagsf);
            // if(pack==0) sendPic(qun,"",original);
            // else sendPackMsg(qun,"","193095561","2854196320","[PicUrl="+original+"]","点击查看主人要的"+tag+"涩图喵~","光光涩图~");
            
            long currentTime = System.currentTimeMillis();
			String currentMd5 = getMD5(imagePath);
			pendingRevokeMap.put(currentMd5, Long.valueOf(currentTime));
            
            sendPic(qun, uin, imagePath);
        }
        
        if (pendingRevokeMap.size() > 20) {
		    Iterator it = pendingRevokeMap.entrySet().iterator();
		    while (it.hasNext()) {
		        Map.Entry entry = (Map.Entry) it.next();
		        
		        Long entryTime = (Long) entry.getValue();
		        
		        if (currentTime - entryTime.longValue() > 1200000) {
		            it.remove();
		        }
		    }
		}
        if (getBoolean("设置", "撤回", false) && data.IsSend && data.msg.elements.size() > 0 && data.msg.elements.get(0).elementType == 2) {

		    String sentMd5 = data.msg.elements.get(0).picElement.md5HexStr;

		    if (pendingRevokeMap.containsKey(sentMd5)) {

		        pendingRevokeMap.remove(sentMd5);

		        final Object msgToRevoke = data.msg;
		        final int sleepTime = getInt("设置", "撤回时间", 5000);

		        new Thread(new Runnable() {
		            public void run() {
		                try {
		                    Thread.sleep(sleepTime);
		                    revokeMsg(msgToRevoke);
		                } catch (Exception e) {
		                    // 忽略异常
		                }
		            }
		        }).start();
		    }
		}

    }
}

new Thread(new Runnable() {
    public void run() {
        delAllFile(appPath + "/缓存/");
    }
}).start();