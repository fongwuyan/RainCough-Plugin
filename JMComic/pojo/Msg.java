
/**
 * QQ 消息封装类
 */
public class Msg {
    /** 消息来源类型（1:私聊, 2:群聊, 100:陌生人） */
    public int type;
    /** 消息类型 */
    public int msgType;
    /** 来源号（群号或好友QQ） */
    public String peerUin;
    /** 发送者QQ */
    public String sendUin;
    /** 消息内容 */
    public String msg;
    /** 消息时间戳 */
    public long time;
    /** 原始消息对象 */
    public Object data;
    /** 艾特列表 */
    public List atList;
    /** 文件路径 */
    public String path;
}
