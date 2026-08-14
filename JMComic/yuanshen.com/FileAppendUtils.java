import java.io.*;
import java.util.zip.*;

void compressAndAppendToImage(String imagePath, String comicDir, String outputPath) {
    FileOutputStream fos = null;
    FileInputStream imageIs = null;
    ZipOutputStream zos = null;
    
    try {
        fos = new FileOutputStream(outputPath);
        imageIs = new FileInputStream(imagePath);
        
        // 1. 先写入图片数据
        byte[] buffer = new byte[8192];
        int bytesRead;
        while ((bytesRead = imageIs.read(buffer)) != -1) {
            fos.write(buffer, 0, bytesRead);
        }
        
        // 2. 在同一输出流上创建 ZipOutputStream，直接追加 ZIP 数据
        zos = new ZipOutputStream(fos);
        
        File comicFolder = new File(comicDir);
        addFilesToZip(comicFolder, "", zos);
        zos.close();
        zos = null; 
                
    } catch (Exception e) {
        log("错误: " + e.getMessage());
        e.logStackTrace();
    } finally {
        // 手动关闭流
        try {
            if (zos != null) zos.close();
            if (imageIs != null) imageIs.close();
            if (fos != null) fos.close();
        } catch (Exception e) {
            // 忽略关闭异常
        }
    }
}

// 添加文件夹内容到 ZIP
void addFilesToZip(File folder, String parentPath, ZipOutputStream zos) throws Exception {
    File[] files = folder.listFiles();
    if (files == null) return;
    
    byte[] buffer = new byte[8192];
    
    for (File file : files) {
        if (file.isDirectory()) {
            String subPath = parentPath + file.getName() + "/";
            addFilesToZip(file, subPath, zos);
        } else {
            String entryName = parentPath + file.getName();
            ZipEntry entry = new ZipEntry(entryName);
            zos.putNextEntry(entry);
            
            FileInputStream fis = null;
            try {
                fis = new FileInputStream(file);
                int length;
                while ((length = fis.read(buffer)) > 0) {
                    zos.write(buffer, 0, length);
                }
            } finally {
                if (fis != null) fis.close();
            }
            zos.closeEntry();
        }
    }
}