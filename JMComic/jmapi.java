search(keyword,page){
        return new JSONObject(get("http://jm.lazy52.com/album/search?keyword="+keyword+"&page="+page));
}
getAlbum(id){
return new JSONObject(get("http://jm.lazy52.com/album/"+id));
}
getChapter(aid,cid){
resp=null;

gc=0;
resp=null;
while((resp==null||resp.isEmpty())&&gc<5){
gc++;
try{
resp=get("http://jm.lazy52.com/chapter/"+cid);
}catch(e){
log("尝试拉取章节失败:"+cid+","+resp);
}
}
if(resp==null||resp.isEmpty()){
log("最终拉取失败:"+cid);
}
JSONObject rj=new JSONObject(resp);
try{
JSONArray rjpa=rj.optJSONArray("photoNames");
if(rj==null||rj.length()==0){
log("photoNames为空:"+cid);
return getChapter(aid,cid);
}
return rj;
}catch(e){
log("章节数据异常:"+e.getMessage());
return getChapter(aid,cid);
}
return new JSONObject(resp);
}