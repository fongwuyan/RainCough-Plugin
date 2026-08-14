public void download(String url, String filepath) throws Exception {
    InputStream input = null;
    try {
        URL urlObj = new URL(url);
        HttpURLConnection urlConn = (HttpURLConnection) urlObj.openConnection();
        input = urlConn.getInputStream();
        byte[] bs = new byte[1024];
        int len;
        FileOutputStream out = new FileOutputStream(filepath, false);
        while ((len = input.read(bs)) != -1) {
            out.write(bs, 0, len);
        }
        out.close();
        input.close();
    } catch (IOException e) {
        showToast("文件下载出错：" + e);
    } finally {
        try {
            if (input != null) {
                input.close();
            }
        } catch (IOException e) {
            showToast("文件下载出错：" + e);
        }
    }
}

public void jump(String url) {
    ((IJumpApi) QRoute.api(IJumpApi.class)).doJumpAction(context, url);
}

public String get(String url) {
    StringBuffer buffer = new StringBuffer();
    InputStreamReader isr = null;
    try {
        URL urlObj = new URL(url);
        URLConnection uc = urlObj.openConnection();
        uc.setConnectTimeout(20000);
        uc.setReadTimeout(20000);
        uc.setRequestProperty("User-Agent", "Mozilla/4.0 compatible; MSIE 5.0;Windows NT; DigExt)");
        String contentType = uc.getHeaderField("Content-Type");
        if (contentType == null) return "";
        isr = new InputStreamReader(uc.getInputStream(), "utf-8");
        BufferedReader reader = new BufferedReader(isr);
        String line;
        while ((line = reader.readLine()) != null) {
            buffer.append(line + "\n");
        }
    } catch (Exception e) {
    } finally {
        try {
            if (isr != null) {
                isr.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    if (buffer.length() == 0) return buffer.toString();
    buffer.delete(buffer.length() - 1, buffer.length());
    return buffer.toString();
}


public boolean unzip(String zipFilePath, String destDir) throws Exception {
    File dir = new File(destDir);
    if (!dir.exists()) {
        dir.mkdirs();
    }
    
    FileInputStream fis = null;
    ZipInputStream zipIn = null;
    
    try {
        fis = new FileInputStream(zipFilePath);
        zipIn = new ZipInputStream(fis);
        
        ZipEntry entry = zipIn.getNextEntry();
        while (entry != null) {
            String entryName = entry.getName();
            
            // 防止路径遍历攻击
            if (entryName.contains("..")) {
                // 跳过或记录，不处理包含..的路径
                zipIn.closeEntry();
                entry = zipIn.getNextEntry();
                continue;
            }
            
            String filePath = destDir + File.separator + entryName;
            
            if (!entry.isDirectory()) {
                // 创建父目录
                File outputFile = new File(filePath);
                File parentDir = outputFile.getParentFile();
                if (parentDir != null && !parentDir.exists()) {
                    parentDir.mkdirs();
                }
                
                FileOutputStream fos = null;
                try {
                    fos = new FileOutputStream(outputFile);
                    byte[] buffer = new byte[4096]; // 增大缓冲区
                    int length;
                    while ((length = zipIn.read(buffer)) > 0) {
                        fos.write(buffer, 0, length);
                    }
                } finally {
                    if (fos != null) {
                        try {
                            fos.close();
                        } catch (IOException e) {
                            // 忽略关闭异常
                        }
                    }
                }
            } else {
                // 创建目录
                File dirFile = new File(filePath);
                if (!dirFile.exists()) {
                    dirFile.mkdirs();
                }
            }
            
            zipIn.closeEntry();
            entry = zipIn.getNextEntry();
        }
        
        return true;
        
    }catch(e){
    log(e);
    } finally {
        // 确保资源被关闭
        if (zipIn != null) {
            try {
                zipIn.close();
            } catch (IOException e) {
                // 忽略关闭异常
            }
        }
        if (fis != null) {
            try {
                fis.close();
            } catch (IOException e) {
                // 忽略关闭异常
            }
        }
    }
}


public void createParentDirectory(String filePath) {
    File file = new File(filePath);
    File parentDir = file.getParentFile();
    if (!parentDir.exists()) {
        parentDir.mkdirs();
    }
}

public void delete(String path) {
    File folder = new File(path);
    if (folder.isDirectory()) {
        File[] files = folder.listFiles();
        if (files != null) {
            for (File f : files) {
                deleteFolder(f);
            }
        }
    }
    folder.delete();
}

public void zip(String sourceDirectory, String zipFilePath) throws IOException {
    File sourceDir = new File(sourceDirectory);
    FileOutputStream fos = new FileOutputStream(zipFilePath);
    ZipOutputStream zipOut = new ZipOutputStream(fos);
    zipFile(sourceDir, sourceDir.getName(), zipOut);
    zipOut.close();
    fos.close();
}

public void zipFile(File fileToZip, String fileName, ZipOutputStream zipOut) throws IOException {
    if (fileToZip.isHidden()) {
        return;
    }
    if (fileToZip.isDirectory()) {
        if (fileName.endsWith("/")) {
            zipOut.putNextEntry(new ZipEntry(fileName));
            zipOut.closeEntry();
        } else {
            zipOut.putNextEntry(new ZipEntry(fileName + "/"));
            zipOut.closeEntry();
        }
        File[] children = fileToZip.listFiles();
        for (File childFile : children) {
            zipFile(childFile, fileName + "/" + childFile.getName(), zipOut);
        }
        return;
    }
    FileInputStream fis = new FileInputStream(fileToZip);
    ZipEntry zipEntry = new ZipEntry(fileName);
    zipOut.putNextEntry(zipEntry);
    byte[] bytes = new byte[1024];
    int length;
    while ((length = fis.read(bytes)) >= 0) {
        zipOut.write(bytes, 0, length);
    }
    fis.close();
}

public void styleDialog(AlertDialog dialog) {
    GradientDrawable gradientDrawable = new GradientDrawable();
    gradientDrawable.setColor(Color.WHITE);
    gradientDrawable.setCornerRadius(24);

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
        dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        dialog.getWindow().setBackgroundDrawable(gradientDrawable);
        dialog.getWindow().setDimAmount(0.4f);
    } else {
        dialog.getWindow().setBackgroundDrawable(gradientDrawable);
    }

    WindowManager.LayoutParams params = dialog.getWindow().getAttributes();
    params.alpha = 1.0f;
    dialog.getWindow().setAttributes(params);

    dialog.setOnShowListener(new DialogInterface.OnShowListener() {
        public void onShow(DialogInterface dialogInterface) {
            dialog.getButton(DialogInterface.BUTTON_NEGATIVE).setTextColor(Color.parseColor("#2979FF"));
            dialog.getButton(DialogInterface.BUTTON_POSITIVE).setTextColor(Color.parseColor("#2979FF"));
        }
    });
}
showToast(s){toast(s);};