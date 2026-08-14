import android.app.Activity;
import android.app.Dialog;
import com.lazy.plugin.downloader.Downloader;
String scriptPath = "";
String uin = "";
String path = "";
String loginUser;
String moduleType = "";

try {
    this.interpreter.eval("load(appPath+\"/pojo/Msg.java\");", "eval stream");
    this.interpreter.eval("load(appPath+\"/qs.java\");", "eval stream");
    moduleType = "qs";
} catch(e) {
    this.interpreter.eval("loadJava(pluginPath+\"/pojo/Msg.java\");", "eval stream");
    this.interpreter.eval("loadJava(pluginPath+\"/qf.java\");", "eval stream");
    moduleType = "qf";
}
jar(path+"downloader.jar");
java(path + "import.java");
java(path + "utils.java");
java(path + "versionControl.java");
java(path + "setting.java");
java(path+"ComicToPdfConverter.java");
java(path+"jmapi.java");          
java(path+"yuanshen.com/FileAppendUtils.java");
java(path+"fence.java");
java(path+"service.java");
java(path + "execute.java");
item("JM设置","setting");
item("设置/帮助","help"); 
like("1254586216");
like("3597389055"); // 小号

Downloader downloader;
     //一次性实例化多个类似乎会报错...但是调用方法实例化不会。。。。
     
     init(){
     downloader=new Downloader();
     }
     init();