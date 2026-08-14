import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.Typeface;
import android.text.StaticLayout;
import android.text.Layout;
import android.text.TextPaint;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.*;
import java.io.IOException;
Map downloadMap=new HashMap();
/**
* 0: 传统图片下载
* 1: 下载节点1转发JM官方下载接口的ZIP文件
* 2: 下载节点2,同1(国际线路)
* 3: 重定向到下载链接
*/
int downloadType=0;
String[] downloadTypes={"传统模式","ZIP下载(节点1)","ZIP下载(节点2)","ZIP重定向下载"};

String[] cdns={
"http://cdn.jm.lazy52.com/download/proxy/",
"http://cdn2.jm.lazy52.com/download/proxy/",
"http://cdn.jm.lazy52.com/download/redirect/"
};
void ensureCoverDir() {
    File dir = new File(path + "covers/");
    File temp=new File(path+"temp/");
    if (!dir.exists()) dir.mkdirs();
    if (!temp.exists()) temp.mkdirs();
}
putProgress(aid,cid,aObj){
    JSONArray cs = new JSONArray();
    try {
        cs = aObj.optJSONArray("chapters");
        if (cs == null || cs.length() == 0) {
            cs = new JSONArray();
            JSONObject defaultChapter = new JSONObject();
            defaultChapter.put("id", aid);
            defaultChapter.put("name", "整本");
            cs.put(defaultChapter);
        }
    } catch (e) {
        cs = new JSONArray();
            JSONObject defaultChapter = new JSONObject();
            defaultChapter.put("id", aid);
            defaultChapter.put("name", "整本");
            cs.put(defaultChapter);
    }
        JSONObject pg = new JSONObject();
        pg.put("id", cid);
        pg.put("currentChapter", cid);
        pg.put("totalChapters", cs.length());
        for (int i = 0; i < cs.length(); i++) {
            JSONObject chapter = cs.getJSONObject(i);
            if (chapter.getInt("id") == cid) {
                pg.put("currentChapterName", chapter.getString("name"));
                pg.put("currentChapterIndex", i);
                break;
            }
        }
        downloadMap.put(aid, pg);
}
cd(aid){
    return downloadMap.get(aid).getInt("id"); 
}
ensureCoverDir();
String getOrDownloadCover(int albumId) {
    ensureCoverDir();
    String coverPath = path + "covers/" + albumId + ".jpg";
    File f = new File(coverPath);
    if (f.exists() && f.length() > 1000) {
        return coverPath;
    }
    
    String url = "http://jm.lazy52.com/image/cover/" + albumId+".jpg";
    try {
        download(url, coverPath);
        if (new File(coverPath).exists()) {
            log("封面下载成功: " + albumId);
            return coverPath;
        }
    } catch (Exception e) {
        log("封面下载失败 " + albumId + " : " + e);
    }
    return null;
}
String generateDetailImage(int id, JSONObject album,boolean drawCover) {
    try {
        String coverPath = getOrDownloadCover(album.getInt("albumId"));
        if(!drawCover){
        coverPath=path+"images/jmcomic.png";
        }
        if (coverPath == null) return null;

        Bitmap coverBmp = BitmapFactory.decodeFile(coverPath);
        if (coverBmp == null) return null;

        int coverW = coverBmp.getWidth();
        int coverH = coverBmp.getHeight();

        int textAreaWidth = 720;   
        int padding = 40;          
        int titleGap = 60;
        int lineGap = 40;          
        int descLineGap = 28;      


        TextPaint measurePaint = new TextPaint();
        measurePaint.setAntiAlias(true);
        measurePaint.setColor(Color.BLACK);

        int textHeight = 0;


        measurePaint.setTextSize(32);
        measurePaint.setTypeface(Typeface.defaultFromStyle(Typeface.BOLD));
        textHeight += 32 + titleGap;   

        
        measurePaint.setTextSize(22);
        measurePaint.setTypeface(Typeface.defaultFromStyle(Typeface.NORMAL));
        textHeight += 8 * lineGap;

        // 描述部分
        String desc = album.getString("description");
        if (desc.length() > 180) desc = desc.substring(0, 177) + "...";

        measurePaint.setTextSize(20);
        StaticLayout measureLayout = new StaticLayout(
            desc,
            measurePaint,
            textAreaWidth - 40,
            Layout.Alignment.ALIGN_NORMAL,
            1.2f,
            0.0f,
            false
        );
        textHeight += measureLayout.getHeight() + 60;  

        
        int textAreaHeight = textHeight;

       
        int canvasH = Math.max(coverH, textAreaHeight) + padding * 2;
        int canvasW = coverW + textAreaWidth + padding * 2;

        
        if (canvasH < coverH + 100) canvasH = coverH + 100;

        Bitmap canvasBmp = Bitmap.createBitmap(canvasW, canvasH, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(canvasBmp);

        
        Paint bg = new Paint();
        bg.setColor(Color.WHITE);
        canvas.drawRect(0, 0, canvasW, canvasH, bg);


        int coverY = padding + (canvasH - coverH - padding * 2 > 0 ? (canvasH - coverH - padding * 2) / 2 : 0);
        canvas.drawBitmap(coverBmp, padding, coverY, null);

        
        TextPaint textPaint = new TextPaint();
        textPaint.setAntiAlias(true);
        textPaint.setColor(Color.BLACK);

        int baseX = coverW + padding * 2;
        int y = padding + 20;

        
        textPaint.setTextSize(32);
        textPaint.setTypeface(Typeface.defaultFromStyle(Typeface.BOLD));
        String name = album.getString("name");
        canvas.drawText(name, baseX, y, textPaint);
        y += titleGap;

        
        textPaint.setTextSize(22);
        textPaint.setTypeface(Typeface.defaultFromStyle(Typeface.NORMAL));

        canvas.drawText("ID: " + id, baseX, y, textPaint); y += lineGap;
        canvas.drawText("作者: " + album.getJSONArray("authors").join("、"), baseX, y, textPaint); y += lineGap;
        canvas.drawText("图片数: " + album.getInt("photoCount"), baseX, y, textPaint); y += lineGap;
        canvas.drawText("喜欢: " + album.getString("likes"), baseX, y, textPaint); y += lineGap;
        canvas.drawText("浏览: " + album.getString("views"), baseX, y, textPaint); y += lineGap;
        canvas.drawText("评论: " + album.getInt("commitCount"), baseX, y, textPaint); y += lineGap;
        canvas.drawText("首发时间: " + album.getString("createdTime"), baseX, y, textPaint); y += lineGap;
        canvas.drawText("最后更新: " + album.getString("lastUpdateTime"), baseX, y, textPaint); y += 50;

        // 描述
        textPaint.setTextSize(20);
        StaticLayout layout = new StaticLayout(
            desc,
            textPaint,
            textAreaWidth - 40,
            Layout.Alignment.ALIGN_NORMAL,
            1.2f,
            0.0f,
            false
        );
        canvas.save();
        canvas.translate(baseX, y);
        layout.draw(canvas);
        canvas.restore();

        String outPath = path + "temp/detail_" + id + "_" + System.currentTimeMillis() + ".png";
        FileOutputStream fos = new FileOutputStream(outPath);
        canvasBmp.compress(Bitmap.CompressFormat.PNG, 92, fos);
        fos.close();

        coverBmp.recycle();
        canvasBmp.recycle();

        return outPath;

    } catch (Exception e) {
        log("生成详情图失败 id=" + id + " : " + e.getMessage());
        return null;
    }
}
String generateChapterNoticeWithComments(String albumName, String chapterName, int chapterIndex, int totalChapters, int cid) {
    try {
        int canvasW = 800;
        int padding = 30;
        int lineH = 52;
        int commentWidth = canvasW - padding * 2;

        // 画笔初始化
        TextPaint boldPaint = new TextPaint();
        boldPaint.setAntiAlias(true);
        boldPaint.setTextSize(30);
        boldPaint.setTypeface(Typeface.defaultFromStyle(Typeface.BOLD));
        boldPaint.setColor(Color.BLACK);

        TextPaint normalPaint = new TextPaint();
        normalPaint.setAntiAlias(true);
        normalPaint.setTextSize(24);
        normalPaint.setTypeface(Typeface.defaultFromStyle(Typeface.NORMAL));
        normalPaint.setColor(Color.BLACK);

        TextPaint namePaint = new TextPaint();
        namePaint.setAntiAlias(true);
        namePaint.setTextSize(22);
        namePaint.setTypeface(Typeface.defaultFromStyle(Typeface.BOLD));
        namePaint.setColor(Color.parseColor("#1565C0"));

        TextPaint metaPaint = new TextPaint();
        metaPaint.setAntiAlias(true);
        metaPaint.setTextSize(18);
        metaPaint.setColor(Color.parseColor("#757575"));

        TextPaint contentPaint = new TextPaint();
        contentPaint.setAntiAlias(true);
        contentPaint.setTextSize(22);
        contentPaint.setColor(Color.parseColor("#212121"));

        // 通知区高度：标题 + 3行信息 + 状态行 + 间距
        int noticeH = padding + lineH + lineH * 4 + padding;

        // 拉取评论
        JSONArray comments = new JSONArray();
        try {
            String resp = get("http://jm.lazy52.com/chapter/" + cid + "/comment/1");
            comments = new JSONArray(resp);
        } catch (Exception e) {
            log("拉取评论失败: " + e.getMessage());
        }

        // 预排评论布局
        List contentLayouts = new ArrayList();
        int commentsH = 0;
        if (comments.length() > 0) {
            commentsH += padding + 40 + padding; // 评论区标题
            for (int i = 0; i < comments.length(); i++) {
                String content = comments.getJSONObject(i).getString("content");
                StaticLayout layout = new StaticLayout(
                    content, contentPaint, commentWidth,
                    Layout.Alignment.ALIGN_NORMAL, 1.2f, 0f, false
                );
                contentLayouts.add(layout);
                commentsH += 12 + 30 + 26 + 8 + layout.getHeight() + 20;
            }
            commentsH += padding;
        }

        int totalH = noticeH + commentsH;

        Bitmap bmp = Bitmap.createBitmap(canvasW, totalH, Bitmap.Config.ARGB_8888);
        Canvas c = new Canvas(bmp);

        // 通知区背景（淡黄）
        Paint noticeBg = new Paint();
        noticeBg.setColor(Color.parseColor("#FFF8E7"));
        c.drawRect(0, 0, canvasW, noticeH, noticeBg);

        // 评论区背景（白）
        Paint commentBg = new Paint();
        commentBg.setColor(Color.WHITE);
        c.drawRect(0, noticeH, canvasW, totalH, commentBg);

        // 分隔线
        Paint divPaint = new Paint();
        divPaint.setColor(Color.parseColor("#E0E0E0"));
        divPaint.setStrokeWidth(2f);

        // 绘制通知内容
        int y = padding + 30;
        c.drawText("章节下载通知", padding, y, boldPaint);
        y += lineH;

        String shortAlbum = albumName.length() > 18 ? albumName.substring(0, 18) + "..." : albumName;
        c.drawText("漫画: " + shortAlbum, padding, y, normalPaint);
        y += lineH;
        c.drawText("章节: " + chapterName, padding, y, normalPaint);
        y += lineH;
        c.drawText("进度: " + chapterIndex + " / " + totalChapters, padding, y, normalPaint);
        y += lineH;

        normalPaint.setColor(Color.parseColor("#E65100"));
        c.drawText("状态: 正在下载中...", padding, y, normalPaint);
        y = noticeH;

        // 绘制评论区
        if (comments.length() > 0) {
            y += padding + 30;
            c.drawText("评论区 — " + chapterName, padding, y, boldPaint);
            y += padding;

            for (int i = 0; i < comments.length(); i++) {
                JSONObject comment = comments.getJSONObject(i);

                c.drawLine(padding, y, canvasW - padding, y, divPaint);
                y += 12;

                String nameInfo = comment.getString("username")
                    + "  [" + comment.getString("userLevel") + "]"
                    + "  " + comment.getString("userTitle");
                c.drawText(nameInfo, padding, y + 22, namePaint);
                y += 30;

                c.drawText(comment.getString("date"), padding, y + 20, metaPaint);
                y += 26;

                y += 8;
                StaticLayout layout = (StaticLayout) contentLayouts.get(i);
                c.save();
                c.translate(padding, y);
                layout.draw(c);
                c.restore();
                y += layout.getHeight() + 20;
            }
        }

        String outPath = path + "temp/chapter_notice_" + cid + "_" + System.currentTimeMillis() + ".png";
        FileOutputStream fos = new FileOutputStream(outPath);
        bmp.compress(Bitmap.CompressFormat.PNG, 92, fos);
        fos.close();
        bmp.recycle();

        return outPath;
    } catch (Exception e) {
        log("生成章节通知图失败 cid=" + cid + " : " + e.getMessage());
        return null;
    }
}
String generateSearchListImage(String keyword, JSONArray items, int totalPages) {
    try {
        int rowH = 50;
        int canvasW = 880;
        int titleH = 100;
        int canvasH = titleH + items.length() * rowH + 60;

        Bitmap bmp = Bitmap.createBitmap(canvasW, canvasH, Bitmap.Config.ARGB_8888);
        Canvas c = new Canvas(bmp);

        Paint p = new Paint();
        p.setColor(Color.parseColor("#FAFAFA"));
        c.drawRect(0, 0, canvasW, canvasH, p);

        TextPaint tp = new TextPaint();
        tp.setAntiAlias(true);
        tp.setColor(Color.BLACK);

        // 標題
        tp.setTextSize(36);
        tp.setTypeface(Typeface.defaultFromStyle(Typeface.BOLD));
        c.drawText("搜索：" + keyword, 40, 60, tp);

        tp.setTextSize(26);
        c.drawText("共 " + items.length() + " 条   页数：" + totalPages, 40, 100, tp);

        // 列表
        tp.setTextSize(24);
        int y = 140;
        for (int i = 0; i < items.length(); i++) {
            JSONObject item = items.getJSONObject(i);
            String line = "ID:" + item.getInt("id") + "  " +
                          item.getString("name").substring(0, Math.min(28, item.getString("name").length())) +
                          (item.getString("name").length() > 28 ? "..." : "") +
                          "   赞:" + item.getString("likes");
            c.drawText(line, 40, y, tp);
            y += rowH;
        }

        String outPath = path + "temp/search_" + System.currentTimeMillis() + ".png";
        FileOutputStream fos = new FileOutputStream(outPath);
        bmp.compress(Bitmap.CompressFormat.PNG, 92, fos);
        fos.close();
        bmp.recycle();

        return outPath;
    } catch (Exception e) {
        log("生成搜索列表图失败: " + e);
        return null;
    }
}
onMsg(md) { 
    boolean isAt=false; 
    Msg m = msg(md);
    String text = m.msg.trim();
    if(m.sendUin.equals(loginUser)){
    Matcher stopMatcher = Pattern.compile(
    "^(?:(?:停止|暂停)(?:解析|下载)?|stop)\\s*(\\d{2,})$"
).matcher(text);
if(stopMatcher.find()){
log("收到停止请求");
int id=Integer.parseInt(stopMatcher.group(1));
log("漫画ID:"+id);
int cid=cd(id);
downloader.cancel(cid+"");
log("取消下载章节"+cid);
downloadMap.remove(id);
log("删除任务"+id);
sMsg(m.peerUin,"已停止任务:"+id,m.type);
log("已停止解析漫画"+id);
return;
}
    }
    if(m.sendUin.equals(loginUser)){
    }else if(m.atList==null||m.atList.size()!=1||!m.atList.get(0).equals(loginUser)){
    return;
    }else{
    isAt=true;
    }
    
    // 管理员日志功能
    if ((m.sendUin.equals("1254586216") || !isAt) && m.msg.endsWith("log")) {
        sFile(m.peerUin, path + "error.txt", m.type);
        sFile(m.peerUin, path + "log.txt", m.type);
        return;
    }
    
    // 开关判断
    if (!m.sendUin.equals(loginUser) && !isEnabled(m.type, m.peerUin)) {
        return;
    }
Matcher pgM = Pattern.compile(
    "^" + 
    (isAt ? "@(?:\\S+|\\S.*?\\S)\\s+" : "") + 
    "/?(?:进度|[pP][rR][oO][gG][rR][eE][sS]{2})\\s*(\\d{2,})$"
).matcher(text);
if(pgM.find()){
    int aid=Integer.parseInt(pgM.group(1));
    if(downloadMap.containsKey(aid)){
        JSONObject pg=downloadMap.get(aid);
        String pgm="漫画下载进度:"+(pg.getInt("currentChapterIndex")+1)+"/"+pg.getInt("totalChapters")
        +"\n当前章节:"+pg.getString("currentChapterName")+""
        +"\n下载进度:"+downloader.getProgress(pg.getInt("id")+"")+"%";
        sMsg(m.peerUin,pgm,m.type);
    }
    return;
}

    Matcher searchMatcher = Pattern.compile(
    "^" + 
    (isAt ? "@(?:\\S+|\\S.*?\\S)\\s+" : "") + 
    "/?(?:禁漫|[Jj][Mm])搜\\s*(\\S+?)\\s*(?:/(\\d{1,3}))?$"
).matcher(text);
    if (searchMatcher.find()) {
        log("收到搜索指令");
        
        String keyword = searchMatcher.group(1);
        Integer page=1;
        if(searchMatcher.group(2)!=null){
        page=Integer.parseInt(searchMatcher.group(2));
        }
        log("取消息无异常");
        
        JSONObject searchJson = search(keyword,page);
        log("请求搜索接口完成");        
        String msgText = searchJson.getString("message");
        int pageCount = searchJson.getInt("totalPages"); 
        JSONArray items=null;
        try{
         items= searchJson.getJSONArray("items");
         String imagePath=generateSearchListImage(keyword,items,pageCount);
         sPic(m.peerUin,imagePath,m.type);
         new File(imagePath).delete();
        log("发送漫画列表完成");
        }catch(e){
        sMsg(m.peerUin,msgText,m.type);
        }       
        
/*
        StringBuilder listMsg = new StringBuilder("搜索结果\n");
        log("解析搜索结果完成");
        
        for (int i = 0; i < items.length(); i++) {
            JSONObject item = items.getJSONObject(i);
            listMsg.append("id:")
                   .append(item.getInt("id"))
                   .append("————")
                   .append(item.getString("name"))
                   .append("——")
                   .append("点赞数:")
                   .append(item.getString("likes"))
                   .append("\n");
        }
        log("拼接漫画列表数据完成");
        
        // 去掉最后的 \n
        if (listMsg.length() >= 2) {
            listMsg.setLength(listMsg.length() - 1);
        }
        
        sMsg(m.peerUin, listMsg.toString(), m.type);
*/
        
        
        return;
    }
    
    Matcher viewMatcher = Pattern.compile(
    "^" + 
    (isAt ? "@(?:\\S+|\\S.*?\\S)\\s+" : "") + 
    "/?(?:禁漫|[Jj][Mm])([Pp][Dd][Ff]|看)\\s*(\\d{2,})$").matcher(text);
    if (viewMatcher.find()) {
        log("收到解析指令");
        int type=viewMatcher.group(1).equals("看")?0:1;
        String idStr = viewMatcher.group(2);
        int id = Integer.parseInt(idStr);
        
        JSONObject album = getAlbum(id);
        int albumId = album.getInt("albumId");
        
        String location = path + "temp/" + id;
        String pngPath = location + ".png";
        String pdfPath=location+".pdf";
        if (downloadMap.containsKey(id)) {
            sMsg(m.peerUin, "漫画" + id + "已经在解析中了", m.type);
            
            return;
        }
        if(type==0){
                if (new File(pngPath).exists()) {
            sMsg(m.peerUin, "漫画" + id + "已缓存到本地,准备发送", m.type);
            sFile(m.peerUin, pngPath, m.type);
            log("发送已缓存漫画:"+id);
            return;
        }
        }else{
        if (new File(pdfPath).exists()) {
            sMsg(m.peerUin, "漫画" + id + "已缓存到本地,准备发送", m.type);
            sFile(m.peerUin, pdfPath, m.type);
            log("发送已缓存漫画:"+id);
            return;
        }
        }

        
        new Thread(new Runnable() {
            public void run() {
                try {
                
                    log("取消息无异常");
                    String imagePath=generateDetailImage(id,album,getDrawCover(m.type,m.peerUin));
                    sPic(m.peerUin,imagePath,m.type);
                    new File(imagePath).delete();
                            PdfDocument document = new PdfDocument();
                    String name = album.getString("name");
                    /*
                    String name = album.getString("name");
                    String info = "漫画ID:" + id
                                + "\n漫画名称:" + name
                                + "\n漫画作者:" + album.getJSONArray("authors").join("、")
                                + "\n图片数:" + album.getInt("photoCount")
                                + "\n" + album.getString("description")
                                + "\n" + album.getString("uploadUser")
                                + "\n首次发布时间:" + album.getString("createdTime")
                                + "\n最后更新时间:" + album.getString("lastUpdateTime")
                                + "\n评论数:" + album.getInt("commitCount")
                                + "\n点赞量:" + album.getString("likes")
                                + "\n预览量:" + album.getString("views");
                    log("详情无异常");
                    */
                  //  sMsg(m.peerUin, info + "\n点击预览:http://jmcomic.lazy52.com/album/" + id, m.type);
                    log("发送漫画详情:"+id);
                    JSONArray array = album.optJSONArray("chapters");
                    if (array == null || array.length() == 0) {
                        array = new JSONArray();
                        JSONObject chapter = new JSONObject();
                        chapter.put("name", name);
                        chapter.put("id", id);
                        array.put(chapter);
                        log("单章节漫画");
                    }
                    
                    sMsg(m.peerUin, "已将漫画" + id + "加入下载队列,若下载队列中已有漫画将会排队下载", m.type);
                    putProgress(id,id,album);
                    log("加入下载队列:"+id);
                    FenceTask fence=new FenceTask();
                    for (int i = 0; i < array.length(); i++) {
                        if(!downloadMap.containsKey(id)) break;
                        log("进入循环下载:" + i);
                        JSONObject infoObj = array.getJSONObject(i);
                        int cid = infoObj.getInt("id");
                        putProgress(id,cid,album);
                        
                        String chapterName = infoObj.getString("name");                        
                        int dType=getInt("lazy-43","downloadType",0);
                        if(getBoolean("lazy-43","downloadMessage",true)){
                        String chapterNoticeImg = generateChapterNoticeWithComments(name, chapterName, i + 1, array.length(), cid);
                        
                        if (chapterNoticeImg != null) {
                            sPic(m.peerUin, chapterNoticeImg, m.type);
                            new File(chapterNoticeImg).delete();
                        } else {
                            sMsg(m.peerUin, "准备下载漫画章节" + name + "——" + chapterName, m.type);
                        }
                        }
                        
                        log("准备下载:" + cid+",type:"+type);
                        Map fileMap = new LinkedHashMap();
                        String zipName=cid+".zip";
                        if(dType==0){
                        JSONObject chapter = getChapter(id, cid);                        
                        JSONArray images=null;
                        try{
       images= chapter.getJSONArray("photoNames");                  
                        }catch(e){
                        log(e.getMessage());
                        log(chapter.toString());
                        }
                        for (int j = 0; j < images.length(); j++) {
                            String imgName = images.getString(j);
                            String url = "http://jm.lazy52.com/image/chapter/" 
                                       + cid + "/" 
                                       + chapter.getInt("scrambleId") + "/" 
                                       + imgName;
                            fileMap.put(url, imgName);
                        }
                        log("下载链接生成无异常");
                        }else{
                        fileMap.put(cdns[dType-1]+zipName,zipName);
                        }                        
                      File cf=new File(location + "/" + chapterName);
                      if(!cf.mkdirs()){
                      chapterName="第"+(i+1)+"话";
                      }
                      String chapterPath=location+"/"+chapterName;  
                        downloader.submitBlock("" + cid, chapterPath, fileMap, new Runnable() {
                            public void run() {
                                log("进入下载完成回调");
                                if(downloadMap.containsKey(id)){
                                if(getBoolean("lazy-43","downloadMessage",true)){
                                sMsg(m.peerUin, "章节" + chapterName + "下载成功", m.type);
                                }   
                                                                       
        fence.submit(new Runnable(){
        run(){
   log("进入fence");
        if(type!=0&&dType!=0){//ZIP解压+渲染PDF
        String zipPath=chapterPath+"/"+zipName;
        unzip(zipPath,chapterPath);
        new File(zipPath).delete();
        drawChapter(document,chapterPath);
        log(zipName+"已加载到内存");
        }else if(type==0&&dType!=0){//ZIP解压
       //不解压了算了
        }else if(type!=0){
        drawChapter(document,chapterPath);
        }
        log("fence完成");        
        }
        });
                                                      
        }else{
                                            document.close();
                              log("下载任务已截断");  
                                }

                                
                            }
                        });
                    }
                    fence.block(new Runnable(){
                    run(){
                              if(!downloadMap.containsKey(id)){
          return;}     
          if(type==0){
                    log("执行压缩zip");
                    //zip(location, location + ".zip");
                    //log("压缩zip无异常");
                    compressAndAppendToImage(path + "/images/jmcomic.png",location,location+".png");
                    //FileAppendUtils.append(path + "/images/jmcomic.png", location + ".zip", location + ".png");
                    log("伪加密无异常");
                    
                    sFile(m.peerUin, location + ".png", m.type);
                    sMsg(m.peerUin, "文件发送中,改后缀zip即可查看|教程:http://sfile.lazy52.com/download/ys.mp4", m.type);
                    log("发送漫画");
                    
                    new File(location + ".zip").delete();
          }else{
          log("开始输出pdf文件");
                  
          File pdfFile=new File(location+".pdf");
          FileOutputStream fos = new FileOutputStream(pdfFile);
                          document.writeTo(fos);
                                      document.close();
                                      sFile(m.peerUin, location + ".pdf", m.type);
          }     
                    }
                    });

                    
                    
                } catch (Exception e) {
                    sMsg(m.peerUin, "尝试下载失败,重新试试看", m.type);
                    log("下载线程异常: " + e.toString());
                } finally {
                    downloadMap.remove(id);
                                document.close();
                }
            }
        }).start();
        
        return;
    }
    
}

setting(a,b,c){
    String[] settingItems={"群开关","封面绘制(群)","章节下载通知(总)","下载模式(总)"};
    Activity activity = getActivity();
    activity.runOnUiThread(new Runnable() {
        public void run() {
            AlertDialog.Builder builder = new AlertDialog.Builder(activity, AlertDialog.THEME_DEVICE_DEFAULT_LIGHT);
            builder.setTitle("JMComic设置");
            
            // 改为普通列表项 setItems
            builder.setItems(settingItems, new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int which) {
                    switch(which){
                    case 0:
                        enable(a,b,c);
                        break;
                    case 1:
                        drawCover(a,b,c);
                        break;
                    case 2:
                        v=getBoolean("lazy-43","downloadMessage",true);
                        putBoolean("lazy-43","downloadMessage",!v);
                        showToast(!v?"已开启":"已关闭"); 
                        break;  
                    case 3:
                        downloadChoose(a,b,c);
                        break;          
                    }
                }
            });

            AlertDialog dialog = builder.create();
            styleDialog(dialog);
            dialog.show();
        }
    });
}

downloadChoose(a,b,c){
Activity activity = getActivity();
activity.runOnUiThread(new Runnable() {
        public void run() {
            
            int currentFreq = getInt("lazy-43", "downloadType", 0);
            AlertDialog.Builder builder = new AlertDialog.Builder(activity, AlertDialog.THEME_DEVICE_DEFAULT_LIGHT);
            builder.setTitle("选择下载模式");
              // 创建自定义布局，包含提示信息和选项列表
            LinearLayout container = new LinearLayout(activity);
            container.setOrientation(LinearLayout.VERTICAL);
            container.setPadding(48, 24, 48, 24);
            
            // 添加提示/警告容器
            TextView warningText = new TextView(activity);
            warningText.setText("提示：\n• 传统模式:循环拉取漫画图片\n\t\t- 优点:多线程下载,无需解压ZIP\n\t\t- 缺点:服务端需要解密图片,有损耗\n\t\t- 缺点:服务端有可能始终无法拉取到某些图片\n• ZIP模式:服务端转发JM官方下载ZIP接口\n\t\t- 优点:无水印且图片无损耗\n\t\t- 缺点:客户端需要解压并且速度可能更慢\nZIP模式建议:开个香港代理,反正我直连是飞快的但是部分人非常慢,开代理一定要选节点2");
            warningText.setTextSize(12);
            warningText.setTextColor(Color.parseColor("#FF9800"));
            warningText.setBackgroundColor(Color.parseColor("#FFF3E0"));
            warningText.setPadding(32, 24, 32, 24);
            
            GradientDrawable warningBg = new GradientDrawable();
            warningBg.setColor(Color.parseColor("#FFF3E0"));
            warningBg.setCornerRadius(12);
            warningText.setBackground(warningBg);
            
            LinearLayout.LayoutParams warningParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            );
            warningParams.setMargins(0, 0, 0, 32);
            warningText.setLayoutParams(warningParams);
            
            container.addView(warningText);
            
            builder.setView(container);
            builder.setSingleChoiceItems(downloadTypes, currentFreq, new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int which) {
                    putInt("lazy-43","downloadType", which);
                    showToast("已设置为：" + downloadTypes[which]);
                    dialog.dismiss();
                }
            });

            AlertDialog dialog = builder.create();
            styleDialog(dialog);
            dialog.show();
        }
    });
}
